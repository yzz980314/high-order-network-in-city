import os
import numpy as np
import pandas as pd
import networkx as nx
import time

# --- 1. Import Project Modules (using new architecture functions) ---
from shared_utils import get_central_districts_graph_by_segment_logic, add_intermodal_edges
from analysis_engines import run_resilience_analysis

# --- 2. Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

DST_RANGE = list(range(0, 400, 50)) + list(range(400, 1701, 100))
ATTACK_SCENARIOS = {'rnd': 'random', 'nd': 'degree', 'bc': 'betweenness'}
CACHE_FILE = os.path.join(CACHE_DIR, 'distance_optimization_summary.csv')


def calculate_rb_from_df(df):
    """Calculates Rb value from DataFrame"""
    if df.empty or len(df) < 2: return 0.0
    df_sorted = df.sort_values('nodes_removed_fraction')
    return np.trapz(y=df_sorted['mean'], x=df_sorted['nodes_removed_fraction'])


# --- 3. Main Execution Flow (fully refactored) ---
if __name__ == "__main__":
    if os.path.exists(CACHE_FILE):
        print(f"--- Data already exists at {CACHE_FILE}. Skipping generation. ---")
        # exit() # Uncomment this line if you want to force regeneration

    print("--- Part 1: Generating Data for Distance Optimization Analysis (v2.0) ---")
    summary_results = []

    # --- Step 1: Load unified master network, the sole data source for all analyses ---
    print("  > Loading master network graph from shared_utils...")
    G_master = get_central_districts_graph_by_segment_logic()
    print("  > Master network loaded.")

    # --- Step 2: Create a 'pure' base network without any walk transfers from the master network ---
    print("  > Creating a 'pure' base graph by removing existing walk edges...")
    G_base = G_master.copy()
    walk_edges_in_master = [(u, v) for u, v, d in G_master.edges(data=True) if d.get('type') == 'walk']
    G_base.remove_edges_from(walk_edges_in_master)
    print(f"  > Pure base graph created. |V|={G_base.number_of_nodes()}, |E|={G_base.number_of_edges()}")

    # --- Step 3: Iterate through different transfer distances, add transfer edges to the pure network, and analyze ---
    for dst in DST_RANGE:
        print(f"\n--- Processing IMT Distance: {dst}m ---")
        G_current = G_base.copy()

        # Use our standardized function to add transfer edges
        G_with_imt = add_intermodal_edges(G_current, d_max_meters=dst)

        num_imt_edges = G_with_imt.number_of_edges() - G_base.number_of_edges()
        total_edges = G_with_imt.number_of_edges()

        print(f"    - Added {num_imt_edges} IMT edges. Total edges: {total_edges}.")

        for short_name, full_name in ATTACK_SCENARIOS.items():
            # Note: The number of tests for random attacks here is lower (10) for quick evaluation.
            # For final publication, consider increasing to 30 or 50.
            num_tests = 50 if short_name == 'rnd' else 1

            df_curve = run_resilience_analysis(G_with_imt, attack_scenario=full_name, num_tests=num_tests,
                                               removal_steps=50)
            rb = calculate_rb_from_df(df_curve)

            print(f"    - {full_name.upper()} attack: Rb = {rb:.4f}")

            summary_results.append({
                'IMT_Distance': dst,
                'Attack_Scenario': short_name.upper(),
                'Robustness_Rb': rb,
                'Num_IMT_Edges': num_imt_edges,
                'Total_Edges': total_edges
            })

    df_summary = pd.DataFrame(summary_results)
    df_summary.to_csv(CACHE_FILE, index=False)
    print(f"\n--- Data generation complete. Summary saved to: {CACHE_FILE} ---")
