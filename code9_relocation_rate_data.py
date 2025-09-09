import os
import pandas as pd
import networkx as nx

# --- 1. Import Project Modules (using new architecture functions) ---
from shared_utils import get_central_districts_graph_by_segment_logic, calculate_relocation_rate_from_paper

# --- 2. Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

CACHE_FILE = os.path.join(CACHE_DIR, 'relocation_rate_analysis_data.csv')
# Note: The Chinese names here must exactly match the 'mode' attribute values in G_master
SUBSYSTEM_CN = ['地铁', '公交', '轮渡', '铁路']
SUBSYSTEM_EN = ['Metro', 'Bus', 'Ferry', 'Railway']
RELOCATION_DISTANCES = [750, 1600]

# --- 3. Main Execution Flow (fully refactored) ---
if __name__ == "__main__":
    if os.path.exists(CACHE_FILE):
        print(f"--- Data already exists at {CACHE_FILE}. Skipping generation. ---")
        # exit() # Uncomment this line if you want to force regeneration

    print("--- Part 1: Generating Relocation Rate (Rl) Data (v2.0) ---")
    results = []

    # --- Step 1: Load unified master network, the sole data source for all analyses ---
    print("> Loading master network graph from shared_utils...")
    G_master = get_central_districts_graph_by_segment_logic()
    print(f"> Master network loaded: |V|={G_master.number_of_nodes()}, |E|={G_master.number_of_edges()}")

    # --- Step 2: Iterate and analyze each subsystem ---
    for i, name_cn in enumerate(SUBSYSTEM_CN):
        name_en = SUBSYSTEM_EN[i]
        print(f"\n--- Analyzing subsystem: {name_cn} ({name_en}) ---")

        # Filter nodes for the current subsystem from the master network
        subsystem_nodes = {n for n, d in G_master.nodes(data=True) if d.get('mode') == name_cn}
        if not subsystem_nodes:
            print(f"  > No nodes found for subsystem {name_cn}. Skipping.")
            continue

        # Create an "isolated network" containing only intra-subsystem connections
        G_isolated = G_master.subgraph(subsystem_nodes).copy()

        # The "interconnected network" is our master network itself
        G_interconnected = G_master

        for d_max in RELOCATION_DISTANCES:
            print(f"  > Analyzing relocation distance: {d_max}m")

            # Calculate Rl for the isolated state
            # In G_isolated, find alternative nodes for subsystem_nodes
            rate_isolated = calculate_relocation_rate_from_paper(G_isolated, list(subsystem_nodes), d_max)
            results.append({'Subsystem': name_en, 'Distance': d_max, 'Type': 'Isolated', 'Value': rate_isolated})
            print(f"    - Isolated Rl: {rate_isolated:.4f}")

            # Calculate Rl for the interconnected state
            # In G_interconnected (i.e., G_master), find alternative nodes for subsystem_nodes
            rate_interconnected = calculate_relocation_rate_from_paper(G_interconnected, list(subsystem_nodes), d_max)
            results.append(
                {'Subsystem': name_en, 'Distance': d_max, 'Type': 'Interconnected', 'Value': rate_interconnected})
            print(f"    - Interconnected Rl: {rate_interconnected:.4f}")

    df_results = pd.DataFrame(results)
    df_results.to_csv(CACHE_FILE, index=False)
    print(f"\n--- Data generation complete. Results saved to: {CACHE_FILE} ---")
