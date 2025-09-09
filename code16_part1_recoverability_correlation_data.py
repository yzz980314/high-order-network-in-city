import os
import pandas as pd
import numpy as np
import networkx as nx
from tqdm import tqdm
from collections import Counter
import random

# --- Import Project Modules ---
import shared_utils

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

GRAPH_CACHE_FILE = os.path.join(CACHE_DIR, 'cascade_simulation_graph.graphml')
RESULTS_CACHE_FILE = os.path.join(CACHE_DIR, 'recoverability_correlation_data.csv')
NODE_SAMPLE_SIZE = 500
BETA = 0.1
FLOW_SAMPLE_SIZE = 1000


# --- Core Calculation Functions (kept as is) ---
def calculate_initial_load(G, flow_sample_size):
    """Estimates initial load on edges by routing traffic between random OD pairs."""
    edge_load = Counter()
    nodes = list(G.nodes())
    if len(nodes) < 2: return {}

    od_pairs = [random.sample(nodes, 2) for _ in range(flow_sample_size)]
    for source, target in od_pairs:
        try:
            path = nx.shortest_path(G, source=source, target=target, weight='length')
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge = tuple(sorted((u, v)))
                edge_load[edge] += 1
        except nx.NetworkXNoPath:
            continue
    final_load_dict = {}
    for u, v in G.edges():
        edge_key = tuple(sorted((u, v)))
        if edge_key in edge_load:
            final_load_dict[(u, v)] = edge_load[edge_key]
    return final_load_dict


def calculate_recoverability(G, node_to_remove, capacity):
    """Calculates functional recoverability for a single node"""
    G_sim = G.copy()
    G_sim.remove_node(node_to_remove)
    failed_edges = set()
    for _ in range(5):
        current_load = calculate_initial_load(G_sim, FLOW_SAMPLE_SIZE)
        newly_failed_edges = {edge for edge, load in current_load.items() if
                              edge not in failed_edges and load > capacity.get(edge, 0)}
        if not newly_failed_edges: break
        failed_edges.update(newly_failed_edges)
        G_sim.remove_edges_from(list(newly_failed_edges))
    return 1 - (len(failed_edges) / G.number_of_edges()) if G.number_of_edges() > 0 else 1.0


def get_all_node_metrics(G, sample_size=None):
    """Calculates various metrics for all nodes"""
    print("> Calculating node-level metrics (Degree, Betweenness, Motif Score)...")
    num_nodes = G.number_of_nodes()
    if sample_size and sample_size < num_nodes:
        nodes_to_analyze = random.sample(list(G.nodes()), sample_size)
    else:
        nodes_to_analyze = list(G.nodes())

    degrees = dict(G.degree())
    k_for_betweenness = min(int(0.1 * num_nodes), num_nodes - 1) if num_nodes > 1 else 0
    betweenness = nx.betweenness_centrality(G, k=k_for_betweenness, seed=42) if k_for_betweenness > 0 else {n: 0 for n
                                                                                                            in
                                                                                                            G.nodes()}

    edge_motif_weights = shared_utils.build_high_order_network_from_motif(G)
    node_motif_scores = Counter()
    for (u, v), weight in edge_motif_weights.items():
        node_motif_scores[u] += weight
        node_motif_scores[v] += weight

    df_metrics = pd.DataFrame(index=nodes_to_analyze)
    df_metrics['degree'] = df_metrics.index.map(degrees)
    df_metrics['betweenness'] = df_metrics.index.map(betweenness)
    df_metrics['motif_score'] = df_metrics.index.map(node_motif_scores).fillna(0)
    return df_metrics


if __name__ == '__main__':
    if os.path.exists(RESULTS_CACHE_FILE):
        print(f"--- Data already exists at {RESULTS_CACHE_FILE}. Skipping generation. ---")
        exit()

    print("--- Part 1: Generating Data for Recoverability Correlation Analysis (Corrected) ---")
    random.seed(42)

    try:
        G = nx.read_graphml(GRAPH_CACHE_FILE)
        if G.is_directed():
            G = G.to_undirected()
    except FileNotFoundError:
        print(f"[Error] Graph file not found at {GRAPH_CACHE_FILE}. Please run code10_part1 first.")
        exit()

    # --- Core Fix: Must call the function to create df_metrics first ---
    df_metrics = get_all_node_metrics(G, sample_size=NODE_SAMPLE_SIZE)

    print(f"> Pre-calculating edge capacity (BETA={BETA})...")
    initial_load = calculate_initial_load(G, FLOW_SAMPLE_SIZE)
    capacity = {edge: (1 + BETA) * load for edge, load in initial_load.items() if load > 0}

    # --- Now df_metrics can be safely used ---
    print(f"> Calculating recoverability for {len(df_metrics)} sampled nodes...")
    recoverability_scores = {}
    for node in tqdm(df_metrics.index, desc="Simulating Recoverability"):
        recoverability_scores[node] = calculate_recoverability(G, node, capacity)

    df_metrics['recoverability'] = df_metrics.index.map(recoverability_scores)
    df_metrics['beta_used'] = BETA  # Add beta value

    df_metrics.to_csv(RESULTS_CACHE_FILE)
    print(f"\n--- Recoverability correlation data saved to: {RESULTS_CACHE_FILE} ---")
    print("Output columns for Part 2: ", df_metrics.columns.tolist())
