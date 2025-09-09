import os
import pandas as pd
import numpy as np
import networkx as nx
from tqdm import tqdm
from collections import Counter
import random
import time

# --- Import Project Modules ---
from shared_utils import get_central_districts_graph_by_segment_logic, get_config
import code15_part1_functional_cascade_data as code15_engine

# --- Core Change: Revert to publication-level high-fidelity simulation parameters ---
# Original value: 1000
FLOW_SAMPLE_SIZE = 10000  # Restore high-fidelity sample size
# Original value: np.linspace(0.05, 0.5, 15)
BETA_RANGE = np.linspace(0.05, 0.5, 30)  # Restore fine-grained step
# Original value: list(range(1, 11, 2)) + list(range(12, 21, 4))
K_RANGE = list(range(1, 11)) + list(range(12, 21, 2))  # Restore dense step

BASE_BETA_FOR_K_ATTACK = 0.15


# --- "Silent" Patch (kept as is) ---
class TqdmSilent:
    def __enter__(self):
        self.original_tqdm = code15_engine.tqdm
        code15_engine.tqdm = lambda *args, **kwargs: args[0]

    def __exit__(self, exc_type, exc_val, exc_tb):
        code15_engine.tqdm = self.original_tqdm


# --- Global Configuration (kept as is) ---
CACHE_DIR = get_config('CACHE_DIR')
CACHE_FILE_BETA = os.path.join(CACHE_DIR, 'nonlinear_beta_sweep_results.csv')
CACHE_FILE_K = os.path.join(CACHE_DIR, 'nonlinear_k_attack_results.csv')


def simulate_cascade_for_nonlinear_analysis(G, initial_load, beta, initial_failure_nodes):
    capacity = {edge: (1 + beta) * load for edge, load in initial_load.items()}
    G_sim = G.copy()
    failed_nodes = set(initial_failure_nodes)
    failed_edges = set()
    G_sim.remove_nodes_from(list(failed_nodes))

    for _ in range(10):
        if G_sim.number_of_edges() == 0: break
        with TqdmSilent():
            # Use half of the high-fidelity sample size for iteration
            current_load = code15_engine.calculate_initial_load(G_sim, FLOW_SAMPLE_SIZE // 2)

        newly_failed_edges = {edge for edge, load in current_load.items() if
                              edge not in failed_edges and load > capacity.get(edge, 0)}
        if not newly_failed_edges: break
        failed_edges.update(newly_failed_edges)
        G_sim.remove_edges_from(list(newly_failed_edges))

    return len(failed_nodes) + len(failed_edges)


if __name__ == '__main__':
    print("--- Part 1: Generating Data for Nonlinear Dynamics Analysis (PUBLICATION-READY VERSION) ---")
    print(f"--- NOTE: Using high-fidelity parameters. This will take a significant amount of time. ---")
    print(f"--- Flow Sample: {FLOW_SAMPLE_SIZE}, Beta Steps: {len(BETA_RANGE)}, K Steps: {len(K_RANGE)} ---")

    # --- IMPORTANT: Before running, it is recommended to delete old cache files to ensure regeneration ---
    if os.path.exists(CACHE_FILE_BETA):
        print(f"> Deleting old cache file: {os.path.basename(CACHE_FILE_BETA)}")
        os.remove(CACHE_FILE_BETA)
    if os.path.exists(CACHE_FILE_K):
        print(f"> Deleting old cache file: {os.path.basename(CACHE_FILE_K)}")
        os.remove(CACHE_FILE_K)

    random.seed(42)
    np.random.seed(42)

    # --- Step 1: Load and Pre-calculate ---
    print("> Loading master network graph...")
    G = get_central_districts_graph_by_segment_logic()
    if not G.is_directed(): G = G.to_directed()

    print("> Pre-calculating initial load (with high-fidelity sample size)...")
    initial_load = code15_engine.calculate_initial_load(G, FLOW_SAMPLE_SIZE)

    print("> Pre-calculating betweenness centrality...")
    bc = nx.betweenness_centrality(G, k=int(0.2 * len(G)), seed=42)
    sorted_nodes_by_bc = sorted(bc, key=bc.get, reverse=True)

    # --- Step 2: Create Task List ---
    tasks = []
    attack_node_beta = [sorted_nodes_by_bc[0]]
    for beta in BETA_RANGE:
        tasks.append({'type': 'beta_sweep', 'beta': beta, 'attack_nodes': attack_node_beta})
    for k in K_RANGE:
        tasks.append({'type': 'k_attack', 'k': k, 'attack_nodes': sorted_nodes_by_bc[:k]})

    # --- Step 3: Run Loop ---
    print(f"\n--- Running a total of {len(tasks)} simulation scenarios... ---")
    results = []
    start_time = time.time()
    for task in tqdm(tasks, desc="Overall Simulation Progress"):
        if task['type'] == 'beta_sweep':
            cascade_size = simulate_cascade_for_nonlinear_analysis(G, initial_load, task['beta'], task['attack_nodes'])
            results.append({'type': 'beta_sweep', 'beta': task['beta'], 'cascade_size': cascade_size})

        elif task['type'] == 'k_attack':
            cascade_size = simulate_cascade_for_nonlinear_analysis(G, initial_load, BASE_BETA_FOR_K_ATTACK,
                                                                   task['attack_nodes'])
            results.append({'type': 'k_attack', 'k': task['k'], 'cascade_size': cascade_size})

    end_time = time.time()
    print(f"\n--- High-fidelity simulation loop finished in {end_time - start_time:.2f} seconds. ---")

    # --- Step 4: Save Results ---
    results_beta = [r for r in results if r['type'] == 'beta_sweep']
    results_k = [r for r in results if r['type'] == 'k_attack']

    if results_beta:
        df_beta = pd.DataFrame(results_beta).drop(columns=['type'])
        df_beta.to_csv(CACHE_FILE_BETA, index=False)
        print(f"> High-fidelity beta sweep results saved to: {os.path.basename(CACHE_FILE_BETA)}")

    if results_k:
        df_k = pd.DataFrame(results_k).drop(columns=['type'])
        df_k.to_csv(CACHE_FILE_K, index=False)
        print(f"> High-fidelity k-attack results saved to: {os.path.basename(CACHE_FILE_K)}")

    print("\n--- All nonlinear dynamics data generation finished. ---")
