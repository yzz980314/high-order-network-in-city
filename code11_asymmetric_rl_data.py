import os
import pandas as pd
import networkx as nx

# --- 1. Import Project Modules (using new architecture functions) ---
from shared_utils import get_central_districts_graph_by_segment_logic, haversine_distance

# --- 2. Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

CACHE_FILE = os.path.join(CACHE_DIR, 'asymmetric_rl_analysis_data.csv')
# Note: The Chinese names here must exactly match the 'mode' attribute values in G_master
SUBSYSTEM_CN = ['地铁', '公交']
SUBSYSTEM_EN = ['Metro', 'Bus']
RELOCATION_DISTANCES = [750, 1600]


# --- 3. Core Calculation Function (excellent logic, kept as is) ---
def calculate_asymmetric_rl(G, nodes_to_evaluate, d_max):
    """Core calculation function: Calculates asymmetric Rl with penalties"""
    if G.number_of_nodes() < 2: return 0.0
    nodes_in_graph = [node for node in nodes_to_evaluate if node in G]
    if not nodes_in_graph: return 0.0

    pos_dict = {n: (G.nodes[n]['lon'], G.nodes[n]['lat']) for n in G.nodes if 'lon' in G.nodes[n]}
    neighbors_dict = {n: set(G.neighbors(n)) for n in G.nodes}
    modes_dict = nx.get_node_attributes(G, 'mode')
    total_node_rl = 0

    for v in nodes_in_graph:
        try:
            reachable_nodes_from_v = nx.descendants(G, v)
            if not reachable_nodes_from_v: continue
        except nx.NetworkXError:
            continue

        G_disrupted = G.copy()
        G_disrupted.remove_node(v)
        candidate_hubs = neighbors_dict.get(v, set())
        reachable_from_hubs = {u: nx.descendants(G_disrupted, u) for u in candidate_hubs if u in G_disrupted}

        total_decay_factor = 0
        for n in reachable_nodes_from_v:
            if n == v: continue
            min_weighted_dist = float('inf')
            for u in candidate_hubs:
                if u in G_disrupted and n in reachable_from_hubs.get(u, set()):
                    dist = haversine_distance(pos_dict[v][0], pos_dict[v][1], pos_dict[u][0], pos_dict[u][1])
                    penalty = 1.0
                    if modes_dict.get(v) == '地铁' and modes_dict.get(u) == '公交':
                        penalty = 1.5
                    elif modes_dict.get(v) == '公交' and modes_dict.get(u) == '地铁':
                        penalty = 0.8
                    if dist * penalty < min_weighted_dist:
                        min_weighted_dist = dist * penalty

            if min_weighted_dist <= d_max:
                total_decay_factor += (1.0 - (min_weighted_dist / d_max))

        total_node_rl += total_decay_factor / len(reachable_nodes_from_v) if reachable_nodes_from_v else 0

    return total_node_rl / len(nodes_in_graph) if nodes_in_graph else 0.0


# --- 4. Main Execution Flow (fully refactored) ---
if __name__ == '__main__':
    if os.path.exists(CACHE_FILE):
        print(f"--- Data already exists at {CACHE_FILE}. Skipping generation. ---")
        # exit() # Uncomment this line if you want to force regeneration

    print("--- Part 1: Generating Asymmetric Relocation Rate (Rl) Data (v2.0) ---")
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

            # Calculate asymmetric Rl for the isolated state
            rate_iso = calculate_asymmetric_rl(G_isolated, list(subsystem_nodes), d_max)
            results.append({'Subsystem': name_en, 'Distance': d_max, 'Type': 'Isolated', 'Value': rate_iso})
            print(f"    - Isolated Asymmetric Rl: {rate_iso:.4f}")

            # Calculate asymmetric Rl for the interconnected state
            rate_conn = calculate_asymmetric_rl(G_interconnected, list(subsystem_nodes), d_max)
            results.append({'Subsystem': name_en, 'Distance': d_max, 'Type': 'Interconnected', 'Value': rate_conn})
            print(f"    - Interconnected Asymmetric Rl: {rate_conn:.4f}")

    df_asymmetric = pd.DataFrame(results)
    df_asymmetric.to_csv(CACHE_FILE, index=False)
    print(f"\n--- Asymmetric Rl data saved to cache: {CACHE_FILE} ---")
