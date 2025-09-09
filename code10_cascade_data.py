import os
import pandas as pd
import networkx as nx
from tqdm import tqdm

# --- 1. Import Project Modules (using new architecture functions) ---
from shared_utils import get_central_districts_graph_by_segment_logic

# --- 2. Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

RESULTS_CACHE_FILE = os.path.join(CACHE_DIR, 'cascade_first_wave_results.csv')
GRAPH_CACHE_FILE = os.path.join(CACHE_DIR, 'cascade_simulation_graph.graphml')


# --- 3. Analysis Functions (logic unchanged, kept as is) ---
def calculate_lcc_loss(original_graph, damaged_graph):
    """Calculates the loss rate of the largest connected component"""
    try:
        lcc_original_len = len(max(nx.weakly_connected_components(original_graph), key=len))
        if len(damaged_graph) == 0: return 1.0
        lcc_damaged_len = len(max(nx.weakly_connected_components(damaged_graph), key=len))
        return 1 - lcc_damaged_len / lcc_original_len
    except (ValueError, nx.NetworkXError):
        return 1.0


def run_cascade_simulation_detailed(graph, initial_node, alpha=0.2):
    """Runs a cascading failure simulation and returns the graph after the first wave and in its final state"""
    g_cascade = graph.copy()
    initial_loads = nx.betweenness_centrality(g_cascade, k=int(0.2 * len(g_cascade)), normalized=True, seed=42)
    nx.set_node_attributes(g_cascade, initial_loads, 'load')
    capacities = {node: load * (1 + alpha) for node, load in initial_loads.items()}
    nx.set_node_attributes(g_cascade, capacities, 'capacity')

    nodes_to_remove = {initial_node}
    g_cascade.remove_nodes_from(list(nodes_to_remove))
    nodes_to_remove.clear()
    if len(g_cascade) < 2: return g_cascade.copy(), g_cascade.copy()

    current_loads = nx.betweenness_centrality(g_cascade, k=int(0.2 * len(g_cascade)), normalized=True, seed=42)
    first_wave_failures = {node for node in g_cascade.nodes() if
                           current_loads.get(node, 0) > g_cascade.nodes[node]['capacity']}
    g_after_first_wave = g_cascade.copy()
    g_after_first_wave.remove_nodes_from(list(first_wave_failures))

    nodes_to_remove.update(first_wave_failures)
    for _ in range(len(graph)):
        if not nodes_to_remove: break
        g_cascade.remove_nodes_from(list(nodes_to_remove))
        nodes_to_remove.clear()
        if len(g_cascade) < 2: break
        current_loads = nx.betweenness_centrality(g_cascade, k=int(0.2 * len(g_cascade)), normalized=True, seed=42)
        nodes_to_remove.update(
            {node for node in g_cascade.nodes() if current_loads.get(node, 0) > g_cascade.nodes[node]['capacity']})

    return g_after_first_wave, g_cascade


# --- 4. Main Execution Flow (fully refactored) ---
if __name__ == "__main__":
    print("--- Step 1: Building central urban network and running cascading failure simulation (v2.0 New Architecture) ---")

    if os.path.exists(GRAPH_CACHE_FILE):
        print(f"> Loading network from cache: {GRAPH_CACHE_FILE}")
        G_original = nx.read_graphml(GRAPH_CACHE_FILE)
    else:
        # --- Core Refactoring: Replace all local graph construction and filtering logic with a single function call ---
        print("> Loading unified, processed central urban network from shared_utils...")
        G_original = get_central_districts_graph_by_segment_logic()

        print(f"\n> Caching central urban network to: {GRAPH_CACHE_FILE}")
        nx.write_graphml(G_original, GRAPH_CACHE_FILE)
        print("> Network cached successfully.")

    print(f"\n> Final network size for analysis: |V|={G_original.number_of_nodes()}, |E|={G_original.number_of_edges()}")

    print("\n> Selecting target nodes for attack from the new network...")
    bc = nx.betweenness_centrality(G_original, k=int(0.2 * len(G_original)), seed=42)
    dc = nx.degree_centrality(G_original)

    unique_nodes_to_analyze = [
        {'type': 'Global Hub (Highest BC)', 'id': max(bc, key=bc.get)},
        {'type': 'Local Core (Highest Deg)', 'id': max(dc, key=dc.get)},
        {'type': 'Average Node (Median BC)', 'id': sorted(bc.items(), key=lambda item: item[1])[len(bc) // 2][0]},
    ]

    print("Selected target nodes for analysis:")
    for node in unique_nodes_to_analyze:
        print(f"  - {node['type']}: {G_original.nodes[node['id']].get('name', node['id'])}")

    print("\n> Running simulation...")
    results_list = []
    for node_info in tqdm(unique_nodes_to_analyze, desc="Simulating Node Failure"):
        node_id = node_info['id']
        G_first_wave, G_cascade_final = run_cascade_simulation_detailed(G_original, node_id, alpha=0.2)
        loss_first_wave = calculate_lcc_loss(G_original, G_first_wave)
        loss_total_cascade = calculate_lcc_loss(G_original, G_cascade_final)
        results_list.append({
            'NodeType': node_info['type'],
            'NodeName': G_original.nodes[node_id].get('name', node_id),
            'Loss_First_Wave': loss_first_wave,
            'Loss_Total_Cascade': loss_total_cascade
        })

    df_results = pd.DataFrame(results_list)
    df_results.to_csv(RESULTS_CACHE_FILE, index=False, encoding='utf-8-sig')

    print("\n--- Simulation Complete ---")
    print("Analysis results based on 'first wave' logic:")
    print(df_results)
    print(f"\n> Analysis results saved to: {RESULTS_CACHE_FILE}")
