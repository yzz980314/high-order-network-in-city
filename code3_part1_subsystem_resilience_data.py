import os
import time
import random
import numpy as np
import pandas as pd
import networkx as nx

# --- Import Project Modules (using new architecture functions) ---
from shared_utils import get_central_districts_graph_by_segment_logic, NAMES, calculate_relocation_rate_from_paper
# Assuming analysis_engines.py still exists and is available
from analysis_engines import run_resilience_analysis

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# English names list, for filenames
SUBSYSTEM_EN = ['Metro', 'Bus', 'Ferry', 'Railway']


def calculate_rb_from_df(df):
    """Calculates Rb value from DataFrame"""
    if df.empty or len(df) < 2: return 0.0
    # Ensure q and S are sorted by q
    df_sorted = df.sort_values('nodes_removed_fraction')
    return np.trapz(y=df_sorted['mean'], x=df_sorted['nodes_removed_fraction'])


if __name__ == "__main__":
    np.random.seed(42)
    random.seed(42)

    print("--- Part 1: Generating Resilience Data for Each Subsystem (v2.0) ---")

    # 1. --- New Workflow: Load master network once ---
    print("  > Loading master network graph...")
    G_master = get_central_districts_graph_by_segment_logic()
    print("  > Master network loaded.")

    # 2. Loop through each subsystem
    for i, network_name_cn in enumerate(NAMES):
        network_name_en = SUBSYSTEM_EN[i]

        # 3. --- New Workflow: Extract subgraph from master network ---
        print(f"\n--- Extracting and Analyzing【{network_name_cn}】Subsystem ---")
        subsystem_nodes = {n for n, d in G_master.nodes(data=True) if d.get('mode') == network_name_cn}
        G = G_master.subgraph(subsystem_nodes).copy()

        # Remove intra-subsystem walk edges for pure intra-modal analysis
        walk_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'walk']
        G.remove_edges_from(walk_edges)

        if G.number_of_nodes() < 2:
            print(f"  > Skipping【{network_name_cn}】due to small size or no connections.")
            continue

        start_time = time.time()

        # 4. Run resilience simulations (logic unchanged)
        print("  > Running resilience simulations...")
        df_rnd = run_resilience_analysis(G, 'random', num_tests=50)
        df_nd = run_resilience_analysis(G, 'degree', num_tests=1)
        df_bc = run_resilience_analysis(G, 'betweenness', num_tests=1)

        # 5. Calculate scalar metrics (Rb and Rl) (logic unchanged)
        print("  > Calculating scalar metrics (Rb and Rl)...")
        rb_rnd = calculate_rb_from_df(df_rnd)
        rb_nd = calculate_rb_from_df(df_nd)
        rb_bc = calculate_rb_from_df(df_bc)

        # Call the function we just restored to shared_utils
        rl_750 = calculate_relocation_rate_from_paper(G, list(G.nodes()), d_max=750)
        rl_1600 = calculate_relocation_rate_from_paper(G, list(G.nodes()), d_max=1600)

        # 6. Print summary data (logic unchanged)
        prop = [
            ['Rb (Random)', f"{rb_rnd:.4f}"],
            ['Rb (ND-targeted)', f"{rb_nd:.4f}"],
            ['Rb (BC-targeted)', f"{rb_bc:.4f}"],
            ['Relocation rate (d=750m)', f"{rl_750:.4f}"],
            ['Relocation rate (d=1600m)', f"{rl_1600:.4f}"]
        ]
        print("\n" + "=" * 20 + f" {network_name_cn} Resilience Summary " + "=" * 20)
        for p in prop: print(f"{p[0]:<35} | {p[1]}")
        print("=" * (58 + len(network_name_cn)))

        # 7. Save all data to cache (logic unchanged)
        print("  > Caching results...")
        df_rnd[['mean', 'nodes_removed_fraction', 'std']].to_csv(os.path.join(CACHE_DIR, f'code3_{network_name_en}_rnd_curve.csv'), index=False, header=False)
        df_nd[['mean', 'nodes_removed_fraction', 'std']].to_csv(os.path.join(CACHE_DIR, f'code3_{network_name_en}_nd_curve.csv'), index=False, header=False)
        df_bc[['mean', 'nodes_removed_fraction', 'std']].to_csv(os.path.join(CACHE_DIR, f'code3_{network_name_en}_bc_curve.csv'), index=False, header=False)
        scalar_data = {
            'rb_rnd': rb_rnd, 'rb_nd': rb_nd, 'rb_bc': rb_bc,
            'rl_750': rl_750, 'rl_1600': rl_1600
        }
        pd.Series(scalar_data).to_json(os.path.join(CACHE_DIR, f'code3_{network_name_en}_scalars.json'))

        print(f"--- 【{network_name_cn}】Data Generation Complete. Time: {time.time() - start_time:.2f}s ---")

    print("\n--- All subsystem data generation finished. ---")
