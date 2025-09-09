import networkx as nx
import numpy as np
import pandas as pd
import random
from multiprocessing import Pool, cpu_count
from tqdm import tqdm


# ============================================================================
#       Engine 1: Node Ordering and Resilience Calculation
# ============================================================================

def get_node_removal_order(G, strategy='random', seed=42):
    """
    Returns a list of nodes for removal based on the specified strategy.
    - 'random' strategy is now determined by a controllable random seed.
    - Approximate calculation for 'betweenness' strategy also uses a fixed seed.
    """
    if strategy == 'random':
        nodes = list(G.nodes())
        random.Random(seed).shuffle(nodes)
        return nodes

    if strategy == 'degree':
        degree_func = lambda n: G.in_degree(n) + G.out_degree(n) if G.is_directed() else G.degree(n)
        return sorted(G.nodes(), key=degree_func, reverse=True)

    if strategy == 'betweenness':
        print("    > Calculating betweenness centrality (may be very time-consuming)...")
        k = int(0.1 * len(G)) if len(G) > 2000 else None
        centrality = nx.betweenness_centrality(G, k=k, normalized=True, seed=42)
        print("    > ...Betweenness centrality calculation complete.")
        return sorted(centrality, key=centrality.get, reverse=True)

    raise ValueError(f"Unknown attack strategy: {strategy}")


def _run_single_attack_simulation(args):
    """
    Internal function for multiprocessing single attack simulations. This is the core worker function for resilience calculation.
    """
    G_original, nodes_to_attack, removal_steps = args
    G = G_original.copy()
    n_nodes_initial = G.number_of_nodes()

    get_components = nx.weakly_connected_components if G.is_directed() else nx.connected_components

    try:
        s0 = len(max(get_components(G), key=len))
    except ValueError:
        return []  # Graph is empty or has no edges
    if s0 == 0: s0 = 1  # Avoid division by zero

    results = [(1.0, 0.0)]  # (S_fraction, q_fraction)
    step_size = max(1, n_nodes_initial // removal_steps)

    for i in range(0, n_nodes_initial, step_size):
        nodes_to_remove_this_step = nodes_to_attack[i: i + step_size]
        G.remove_nodes_from([n for n in nodes_to_remove_this_step if n in G])

        if G.number_of_nodes() == 0:
            if results[-1][1] < 1.0:
                results.append((0.0, 1.0))
            break

        try:
            s_current = len(max(get_components(G), key=len))
        except ValueError:
            s_current = 0

        S_fraction = s_current / s0
        q_fraction = (n_nodes_initial - G.number_of_nodes()) / n_nodes_initial
        results.append((S_fraction, q_fraction))

    return results


def run_resilience_analysis(G, attack_scenario, num_tests=1, removal_steps=50):
    """
    Unified resilience analysis function (Version 2.2 - Interface Alignment).
    Focuses on receiving pre-ordered attack lists and executing simulations.
    """
    # Unify input format: ensure attack_scenario is a list of lists
    if not isinstance(attack_scenario, list):
        raise TypeError("attack_scenario must be a list or list of lists.")
    if not attack_scenario or not isinstance(attack_scenario[0], list):
        attack_scenario = [attack_scenario] * num_tests

    actual_num_tests = len(attack_scenario)

    # Prepare parameters for multiprocessing tasks
    args_list = [(G, single_list, removal_steps) for single_list in attack_scenario]

    print(f"  > Launching {actual_num_tests} simulations using {min(cpu_count(), actual_num_tests)} CPU cores...")
    with Pool(min(cpu_count(), actual_num_tests)) as p:
        # Use tqdm to display progress bar
        all_results = list(
            tqdm(p.imap(_run_single_attack_simulation, args_list), total=actual_num_tests, desc="  - Simulation Progress"))

    # Standardize and average results
    q_base = np.linspace(0, 1, removal_steps + 2)
    s_matrix = np.zeros((actual_num_tests, len(q_base)))

    for i, res in enumerate(all_results):
        if not res: continue
        s_res, q_res = zip(*res)
        # Use interpolation to align all results to the same q-axis
        s_matrix[i, :] = np.interp(q_base, q_res, s_res)

    mean_S = np.mean(s_matrix, axis=0)
    std_S = np.std(s_matrix, axis=0)

    # --- Interface Alignment: Return column names consistent with downstream scripts ---
    return pd.DataFrame({
        'nodes_removed_fraction': q_base,
        'mean': mean_S,
        'std': std_S
    })


# ============================================================================
#       Engine 2: Unified Benchmark Graph Generator
# ============================================================================

def generate_benchmark_graph(G_real, seed):
    """
    Generates an ER random graph as a benchmark for a given real network.
    This benchmark graph preserves the number of nodes, edges, and geospatial attributes of the real network.
    """
    n = G_real.number_of_nodes()
    m = G_real.number_of_edges()
    is_directed = G_real.is_directed()

    if n < 2 or m == 0:
        return G_real.copy()

    G_bench = nx.gnm_random_graph(n, m, directed=is_directed, seed=seed)
    pos_info = {node: data for node, data in G_real.nodes(data=True) if 'lon' in data and 'lat' in data}
    if not pos_info:
        return G_bench

    real_nodes_with_pos = list(pos_info.keys())
    random.seed(seed)
    nodes_to_map = random.sample(real_nodes_with_pos, min(len(real_nodes_with_pos), n))
    mapping = {bench_node: real_node for bench_node, real_node in zip(G_bench.nodes(), nodes_to_map)}
    for bench_node, real_node in mapping.items():
        for key, value in pos_info[real_node].items():
            G_bench.nodes[bench_node][key] = value

    return G_bench
