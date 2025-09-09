import os
import networkx as nx
import time
import pandas as pd

# --- 1. Import Project Modules (using new architecture functions) ---
from shared_utils import get_central_districts_graph_by_segment_logic, NAMES
from analysis_engines import generate_benchmark_graph, run_resilience_analysis

# --- 2. Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

NUM_BENCHMARKS = 50
REMOVAL_STEPS = 50
ATTACK_SCENARIOS = {'rnd': 'random', 'nd': 'degree', 'bc': 'betweenness'}


# --- 3. Core Function (no modification needed) ---
def run_benchmark_analysis_for_graph(G_real, step_index, imt_distance):
    """Generates and analyzes all benchmark models for a given real network G_real."""
    if G_real.number_of_nodes() < 2 or G_real.number_of_edges() < 1:
        print(f"  > Real network is too small, skipping benchmark analysis.")
        return

    print(f"  > Starting generation of {NUM_BENCHMARKS} benchmark models and analysis for this network...")

    for nb in range(NUM_BENCHMARKS):
        print(f"    - Processing benchmark model {nb + 1}/{NUM_BENCHMARKS} (seed={nb})...")
        start_time_bm = time.time()

        BG = generate_benchmark_graph(G_real, seed=nb)

        for short_name, full_name in ATTACK_SCENARIOS.items():
            num_tests = 1 if short_name != 'rnd' else 50
            df_results = run_resilience_analysis(
                BG, attack_scenario=full_name, num_tests=num_tests, removal_steps=REMOVAL_STEPS
            )

            filename = f"benchmark_imt_{imt_distance}_step_{step_index}_attack_{short_name}_run_{nb}.csv"
            filepath = os.path.join(CACHE_DIR, filename)
            df_results[['mean', 'nodes_removed_fraction', 'std']].to_csv(filepath, index=False, header=False)

        print(f"    - Benchmark model {nb + 1} analysis complete (Time: {time.time() - start_time_bm:.2f}s)")


# --- 4. Main Execution Flow (fully refactored) ---
if __name__ == "__main__":
    print("=" * 60)
    print("      Part 1: Benchmark Model Resilience Data Generation (v2.0 New Architecture)")
    print("=" * 60)

    # --- Step 1: Load unified master network, the sole data source for all analyses ---
    print("  > Loading master network graph from shared_utils...")
    G_master = get_central_districts_graph_by_segment_logic()
    print("  > Master network loaded.")

    # --- Step 2: Perform incremental analysis ---
    for i in range(len(NAMES)):
        step_index = i + 1
        modes_for_step = NAMES[:i + 1]
        network_name_cn = " + ".join(modes_for_step)
        print(f"\n{'=' * 20} Preparing real network for Step {step_index}: 【{network_name_cn}】 {'=' * 20}")

        # --- Step 3: Extract subgraph for the current step from the master network ---
        nodes_for_step = {n for n, d in G_master.nodes(data=True) if d.get('mode') in modes_for_step}
        G_subgraph_for_step = G_master.subgraph(nodes_for_step).copy()

        # --- Step 4: Process both isolated and interconnected scenarios ---
        for imt_distance in [0, 100]:
            G_to_benchmark = G_subgraph_for_step.copy()

            if imt_distance == 0:
                print(f"\n--- Analyzing Isolated Network (D_IMT = {imt_distance}m) Benchmark ---")
                # Remove inter-modal walk edges to get a purely isolated network
                walk_edges = [(u, v) for u, v, d in G_to_benchmark.edges(data=True) if d.get('type') == 'walk']
                G_to_benchmark.remove_edges_from(walk_edges)
            else:
                print(f"\n--- Analyzing Interconnected Network (D_IMT = {imt_distance}m) Benchmark ---")
                # The interconnected network is the subgraph extracted from the master network, already containing walk edges
                pass

            run_benchmark_analysis_for_graph(G_to_benchmark, step_index=step_index, imt_distance=imt_distance)

    print("\n\nAll benchmark model resilience analyses complete!")
