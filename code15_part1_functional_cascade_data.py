import os
import time
import networkx as nx
import pandas as pd
from collections import Counter
from tqdm import tqdm
import random

# --- Import Project Modules ---
from shared_utils import get_central_districts_graph_by_segment_logic, get_config

# --- Global Configuration ---
CACHE_DIR = get_config('CACHE_DIR')
RESULTS_CACHE_FILE = os.path.join(CACHE_DIR, 'functional_cascade_results.csv')

# Parameters
BETA = 0.085
FLOW_SAMPLE_SIZE = 20000


def calculate_initial_load(G, flow_sample_size):
    """Calculates initial load (traffic flow based on shortest paths)"""
    edge_load = Counter()
    nodes = list(G.nodes())
    if len(nodes) < 2: return edge_load

    random.seed(42)
    od_pairs = [random.sample(nodes, 2) for _ in range(flow_sample_size)]

    # Use a copy of tqdm to avoid being silenced in simulate_functional_cascade
    _tqdm = tqdm
    for source, target in _tqdm(od_pairs, desc="Calculating initial load"):
        try:
            path = nx.shortest_path(G, source=source, target=target, weight='length')
            for i in range(len(path) - 1):
                if G.has_edge(path[i], path[i + 1]):
                    edge_load[(path[i], path[i + 1])] += 1
        except nx.NetworkXNoPath:
            continue
    return edge_load


def simulate_functional_cascade(G, capacity, initial_failure_nodes):
    """Simulates functional cascading failure"""
    G_sim = G.copy()
    failed_nodes = set(initial_failure_nodes)
    failed_edges = set()
    G_sim.remove_nodes_from(list(failed_nodes))

    for iteration in range(10):
        # Inside this function, we don't want to see a progress bar, so use a dummy tqdm
        class TqdmSilent:
            def __init__(self, iterable, *args, **kwargs): self.iterable = iterable

            def __iter__(self): return iter(self.iterable)

        global tqdm
        original_tqdm = tqdm
        tqdm = TqdmSilent

        current_load = calculate_initial_load(G_sim, FLOW_SAMPLE_SIZE // 2)

        tqdm = original_tqdm  # Restore tqdm

        newly_failed_edges = {edge for edge, load in current_load.items() if
                              edge not in failed_edges and load > capacity.get(edge, 0)}

        if not newly_failed_edges:
            break

        failed_edges.update(newly_failed_edges)
        G_sim.remove_edges_from(list(newly_failed_edges))

    return len(failed_nodes) + len(failed_edges), len(failed_nodes), len(failed_edges)


if __name__ == '__main__':
    if os.path.exists(RESULTS_CACHE_FILE):
        print(f"--- Deleting old cache file: {RESULTS_CACHE_FILE} ---")
        os.remove(RESULTS_CACHE_FILE)

    print("--- Part 1: Generating Data for Functional Cascade Analysis (Corrected Structure) ---")

    # Step 1: Load unified master network
    print("> Loading master network graph from shared_utils...")
    G_master = get_central_districts_graph_by_segment_logic()
    if not G_master.is_directed():
        G_master = G_master.to_directed()
    print(f"> Master network loaded: |V|={G_master.number_of_nodes()}, |E|={G_master.number_of_edges()}")

    # Step 2: Calculate initial load and capacity
    print("\n> Calculating initial load and capacity...")
    initial_load = calculate_initial_load(G_master, FLOW_SAMPLE_SIZE)
    capacity = {edge: (1 + BETA) * load for edge, load in initial_load.items()}

    # --- Core Fix: Must define the variable before using it ---
    # Step 3: Calculate betweenness centrality and define top_5_bc_nodes based on it
    print("\n> Identifying top 5 betweenness centrality nodes as attack targets...")
    bc = nx.betweenness_centrality(G_master, k=int(0.2 * len(G_master)), seed=42)
    top_5_bc_nodes = sorted(bc, key=bc.get, reverse=True)[:5]
    print(f"  - Targets: {top_5_bc_nodes}")

    # Step 4: Now top_5_bc_nodes can be safely used for looping and simulation
    results = []
    # tqdm here uses the global scope, so it will display a progress bar
    for node in tqdm(top_5_bc_nodes, desc="Simulating attacks on top nodes"):
        print(f"\n--- Simulating attack on node: {node} ---")
        total_damage, node_damage, edge_damage = simulate_functional_cascade(G_master, capacity, [node])

        results.append({
            'Initial_Node': node,
            'Total_Damage': total_damage,
            'Failed_Nodes': node_damage,
            'Failed_Edges': edge_damage,
            'Betweenness': bc[node],
            'Beta_Value': BETA
        })

    df_results = pd.DataFrame(results)
    df_results.to_csv(RESULTS_CACHE_FILE, index=False)
    print(f"\n--- Functional cascade data (with Beta) saved to: {os.path.basename(RESULTS_CACHE_FILE)} ---")
