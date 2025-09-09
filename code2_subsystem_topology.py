import time
import networkx as nx
import numpy as np
import shared_utils


def analyze_and_print_results(network_name, G):
    """
    Calculates and prints topological analysis results for a single network (mimicking old v27.3 style and metrics).
    """
    print(f"\n--- Starting analysis for【{network_name}】(v42 Integrated Architecture) ---")
    start_time = time.time()

    if G.number_of_nodes() == 0:
        print(f"Network {network_name} is empty, skipping analysis.")
        return

    # Call the more powerful metric calculation function in shared_utils
    all_metrics = shared_utils._calculate_all_metrics(G)

    # Define all metrics and descriptions from the old version
    prop_definitions = {
        '|V|': 'number of stops',
        '|E|': 'number of links',
        '<k_out>': 'average out-degree',
        'S0': 'relative size of largest connected component',
        'l_max': 'maximal shortest path length (diameter)',
        '<l>': 'average shortest path length',
        'E': 'global efficiency',
        'E_geospatial': 'geospatial efficiency (detour index)',
        '<l_e>': 'average edge length (haversine)',
        'σ(le)': 'std deviation of edge lengths',
        'Gini (ND)': 'Gini coefficient of node degree',
        'Gini (BC)': 'Gini coefficient of node betweenness'
    }
    # Define formatting strings from the old version
    formats = {
        '<k_out>': '.2f', 'S0': '.3f', 'l_max': '.2f', '<l>': '.2f', 'E': '.4f',
        'E_geospatial': '.4f', '<l_e>': '.2f', 'σ(le)': '.2f', 'Gini (ND)': '.3f', 'Gini (BC)': '.3f'
    }

    network_title = f" {network_name} Network Analysis "
    print("\n" + "=" * 20 + network_title + "=" * 20)
    for key, description in prop_definitions.items():
        if key in all_metrics:
            value = all_metrics[key]
            fmt = formats.get(key, '')
            formatted_value = f"{value:{fmt}}" if fmt and isinstance(value, (int, float, np.number)) and value != float(
                'inf') else str(value)
            print(f"{key:<12} | {formatted_value:<12} | {description}")

    print("=" * (42 + len(network_title)))
    print(f"--- 【{network_name}】Analysis complete. Time: {time.time() - start_time:.2f} seconds ---")


if __name__ == "__main__":
    print("--- Using【v42.0 Ultimate Integrated Version】to load and analyze networks ---")

    # Step 1: Use the latest method to build a unified, precise core network graph with all modes
    G_master_central = shared_utils.get_central_districts_graph_by_segment_logic()
    print("\n--- Master network loaded. Starting analysis of each transportation subsystem ---")

    # Step 2: Loop through each transportation mode
    for name_cn in shared_utils.NAMES:
        # Extract the subgraph for this mode from the master network
        subsystem_nodes = {n for n, d in G_master_central.nodes(data=True) if d.get('mode') == name_cn}
        G_sub = G_master_central.subgraph(subsystem_nodes).copy()

        # Remove intra-subsystem walk edges (if any)
        walk_edges = [(u, v) for u, v, d in G_sub.edges(data=True) if d.get('type') == 'walk']
        G_sub.remove_edges_from(walk_edges)

        # Perform independent, detailed analysis and printing for this subgraph
        analyze_and_print_results(name_cn, G_sub)
