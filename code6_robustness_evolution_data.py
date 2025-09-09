import os
import time
import networkx as nx
import pandas as pd

# --- 1. Import Project Modules (using new architecture functions) ---
from shared_utils import get_central_districts_graph_by_segment_logic, NAMES
from analysis_engines import run_resilience_analysis, get_node_removal_order

# --- 2. Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

NUM_TESTS_RND = 50
NUM_TESTS_INTENTIONAL = 1
REMOVAL_STEPS = 50
ATTACK_SCENARIOS = {'bc': 'betweenness', 'nd': 'degree', 'rnd': 'random'}

# --- 3. Main Execution Flow (fully refactored) ---
if __name__ == '__main__':
    print("=" * 60)
    print("      Part 1: Network Robustness Evolution Data Generation (v2.2 Column Name Sync)")
    print("=" * 60)

    print("  > Loading master network graph from shared_utils...")
    G_master = get_central_districts_graph_by_segment_logic()
    print("  > Master network loaded.")

    for i in range(len(NAMES)):
        step_index = i + 1
        modes_for_step = NAMES[:i + 1]
        network_name_cn = " + ".join(modes_for_step)
        print(f"\n{'=' * 20} Preparing network for Step {step_index}: 【{network_name_cn}】 {'=' * 20}")

        nodes_for_step = {n for n, d in G_master.nodes(data=True) if d.get('mode') in modes_for_step}
        G_subgraph_for_step = G_master.subgraph(nodes_for_step).copy()

        for imt_distance in [0, 100]:
            G_to_analyze = G_subgraph_for_step.copy()

            if imt_distance == 0:
                print(f"\n--- Analyzing Isolated Network (D_IMT = {imt_distance}m) ---")
                walk_edges = [(u, v) for u, v, d in G_to_analyze.edges(data=True) if d.get('type') == 'walk']
                G_to_analyze.remove_edges_from(walk_edges)
            else:
                print(f"\n--- Analyzing Interconnected Network (D_IMT = {imt_distance}m) ---")
                pass

            if G_to_analyze.number_of_nodes() < 2:
                print("  > Network size is too small, skipping resilience analysis.")
                continue

            for short_name, full_name in ATTACK_SCENARIOS.items():
                num_tests = NUM_TESTS_RND if short_name == 'rnd' else NUM_TESTS_INTENTIONAL
                start_time = time.time()

                print(f"    > Preparing attack sequence for '{full_name.upper()}'...")
                if short_name == 'rnd':
                    attack_sequences = [get_node_removal_order(G_to_analyze, 'random', seed=s) for s in
                                        range(num_tests)]
                else:
                    attack_sequences = get_node_removal_order(G_to_analyze, strategy=full_name)

                df_results = run_resilience_analysis(
                    G_to_analyze,
                    attack_scenario=attack_sequences,
                    num_tests=num_tests,
                    removal_steps=REMOVAL_STEPS
                )

                filename = f"evolution_imt_{imt_distance}_step_{step_index}_attack_{short_name}.csv"
                filepath = os.path.join(CACHE_DIR, filename)

                # --- Core Fix: Use new column names to save results ---
                df_results[['mean', 'nodes_removed_fraction', 'std']].to_csv(filepath, index=False, header=False)

                print(
                    f"    > {full_name.upper()} analysis complete, results saved to {os.path.basename(filepath)} (Time: {time.time() - start_time:.2f} seconds)")

    print("\n\nAll incremental resilience analyses complete!")
