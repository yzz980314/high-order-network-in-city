import time
import os
import networkx as nx
import numpy as np

# --- 1. Import Project Modules (using new architecture functions) ---
from shared_utils import (
    get_central_districts_graph_by_segment_logic,
    add_intermodal_edges,
    _calculate_all_metrics,
    calculate_relocation_rate_from_paper,
    NAMES
)
# Ensure this file exists in your project
from analysis_engines import generate_benchmark_graph

# --- 2. Global Configuration (consistent with old version) ---
METRIC_ORDER_AND_FORMAT = {
    '|V|': '.0f', '|E|': '.0f', 'IMT edges': '.0f', '<k_out>': '.2f',
    'S0': '.3f', 'l_max': '.2f', '<l>': '.2f', 'E': '.4f',
    'Z-score (E)': '.2f',
    'E_geospatial': '.4f',
    'Z-score (E_geospatial)': '.2f',
    '<l_e>': '.2f', 'σ(le)': '.2f',
    'Gini (ND)': '.3f', 'Gini (BC)': '.3f',
    'Relocation rate (d=750m)': '.4f',
    'Relocation rate (d=1600m)': '.4f'
}


# --- 3. Helper Functions (largely unchanged) ---
def analyze_benchmarks(G_real, num_benchmarks=10):
    benchmark_e_values = []
    benchmark_e_geo_values = []
    print(f"    > [Unified Engine] Analyzing {num_benchmarks} ER random graphs...")
    for i in range(num_benchmarks):
        G_bench = generate_benchmark_graph(G_real, seed=i)
        if G_bench.number_of_nodes() > 1:
            components = nx.weakly_connected_components(G_bench) if G_bench.is_directed() else nx.connected_components(
                G_bench)
            largest_component_nodes = max(components, key=len, default=set())
            if not largest_component_nodes: continue
            G_lcc = G_bench.subgraph(largest_component_nodes)
            metrics_bench = _calculate_all_metrics(G_lcc)
            benchmark_e_values.append(metrics_bench.get('E', 0))
            benchmark_e_geo_values.append(metrics_bench.get('E_geospatial', 0))
    stats = {
        'E_mean': np.mean(benchmark_e_values) if benchmark_e_values else 0.0,
        'E_std': np.std(benchmark_e_values) if benchmark_e_values else 0.0,
        'E_geo_mean': np.mean(benchmark_e_geo_values) if benchmark_e_geo_values else 0.0,
        'E_geo_std': np.std(benchmark_e_geo_values) if benchmark_e_geo_values else 0.0
    }
    print(f"    > [Unified Engine] Benchmark analysis complete. E_mean={stats['E_mean']:.4f}, E_geo_mean={stats['E_geo_mean']:.4f}")
    return stats


def calculate_z_score(value, mean, std):
    if value is None or mean is None or std is None or std == 0: return 0.0
    return (value - mean) / std


def print_table_format(results_iso, results_conn, names_cn):
    headers = ["Observables"] + [f"Step {i + 1}\n+ {names_cn[i]}" for i in range(len(names_cn))]

    def print_section(title, data):
        print(f"\n\n--- {title} ---")
        header_line_1 = f"{headers[0]:<35}"
        header_line_2 = f"{'':<35}"
        for h in headers[1:]:
            parts = h.split('\n');
            header_line_1 += f"{parts[0]:>24}";
            header_line_2 += f"{parts[1]:>24}"
        print(header_line_1);
        print(header_line_2);
        print("-" * len(header_line_1))
        for metric, fmt in METRIC_ORDER_AND_FORMAT.items():
            if metric not in data or not any(v is not None for v in data[metric]): continue
            row_str = f"{metric:<35}"
            for step_values in data[metric]:
                if step_values is None:
                    row_str += f"{'N/A':>24}"
                else:
                    row_str += f"{step_values:>{24}{fmt}}"
            print(row_str)

    print_section("Property of the MPTN - DIMT=0m (Isolated)", results_iso)
    print_section("Property of the MPTN - DIMT=100m (Interconnected)", results_conn)


# --- 4. Main Analysis Flow (fully refactored) ---
def run_incremental_analysis(num_benchmarks=10):
    print(f"\n{'=' * 30}\nSTARTING INCREMENTAL ANALYSIS (v2.0)\n{'=' * 30}")

    # --- Step 1: Load unified master network, the sole data source for all analyses ---
    print("  > Loading master network graph from shared_utils...")
    G_master = get_central_districts_graph_by_segment_logic()
    print("  > Master network loaded.")

    results_iso = {key: [] for key in METRIC_ORDER_AND_FORMAT}
    results_conn = {key: [] for key in METRIC_ORDER_AND_FORMAT}

    # --- Step 2: Perform incremental analysis ---
    for i in range(len(NAMES)):
        names_to_build = NAMES[:i + 1]
        network_name_cn = " + ".join(names_to_build)
        print(f"\n\n{'#' * 20} Analyzing Step {i + 1}: 【{network_name_cn}】 {'#' * 20}")

        # --- Step 3: Extract subgraph for the current step from the master network ---
        nodes_for_step = {n for n, d in G_master.nodes(data=True) if d.get('mode') in names_to_build}
        # G_subgraph_with_walk contains nodes of these modes, and existing walk transfer edges between them in the master network
        G_subgraph_with_walk = G_master.subgraph(nodes_for_step).copy()

        # --- ISOLATED (Isolated Network) ---
        # Definition: Only contains intra-modal transportation connections, no inter-modal walk transfers
        print("  Calculating for ISOLATED network (DIMT=0m)...")
        G_iso = G_subgraph_with_walk.copy()
        walk_edges = [(u, v) for u, v, d in G_iso.edges(data=True) if d.get('type') == 'walk']
        G_iso.remove_edges_from(walk_edges)

        metrics_iso = _calculate_all_metrics(G_iso)
        benchmark_stats_iso = analyze_benchmarks(G_iso, num_benchmarks)
        metrics_iso['Z-score (E)'] = calculate_z_score(metrics_iso.get('E'), benchmark_stats_iso['E_mean'],
                                                       benchmark_stats_iso['E_std'])
        metrics_iso['Z-score (E_geospatial)'] = calculate_z_score(metrics_iso.get('E_geospatial'),
                                                                  benchmark_stats_iso['E_geo_mean'],
                                                                  benchmark_stats_iso['E_geo_std'])
        metrics_iso['Relocation rate (d=750m)'] = calculate_relocation_rate_from_paper(G_iso, list(G_iso.nodes()),
                                                                                       d_max=750)
        metrics_iso['Relocation rate (d=1600m)'] = calculate_relocation_rate_from_paper(G_iso, list(G_iso.nodes()),
                                                                                        d_max=1600)
        metrics_iso['IMT edges'] = 0
        for key in METRIC_ORDER_AND_FORMAT: results_iso[key].append(metrics_iso.get(key))

        # --- INTERCONNECTED (Interconnected Network) ---
        # Definition: Contains intra-modal transportation connections, and inter-modal walk transfers between them
        # Note: We directly use the subgraph extracted from the master network, as it already contains 100m walk transfers
        print("  Calculating for INTERCONNECTED network (DIMT=100m)...")
        G_conn = G_subgraph_with_walk

        metrics_conn = _calculate_all_metrics(G_conn)
        benchmark_stats_conn = analyze_benchmarks(G_conn, num_benchmarks)
        metrics_conn['Z-score (E)'] = calculate_z_score(metrics_conn.get('E'), benchmark_stats_conn['E_mean'],
                                                        benchmark_stats_conn['E_std'])
        metrics_conn['Z-score (E_geospatial)'] = calculate_z_score(metrics_conn.get('E_geospatial'),
                                                                   benchmark_stats_conn['E_geo_mean'],
                                                                   benchmark_stats_conn['E_geo_std'])
        metrics_conn['Relocation rate (d=750m)'] = calculate_relocation_rate_from_paper(G_conn, list(G_conn.nodes()),
                                                                                        d_max=750)
        metrics_conn['Relocation rate (d=1600m)'] = calculate_relocation_rate_from_paper(G_conn, list(G_conn.nodes()),
                                                                                         d_max=1600)
        metrics_conn['IMT edges'] = len(walk_edges)  # The number of IMT edges is those we just removed
        for key in METRIC_ORDER_AND_FORMAT: results_conn[key].append(metrics_conn.get(key))

    print_table_format(results_iso, results_conn, NAMES)


# --- 5. Entry Point ---
if __name__ == '__main__':
    run_incremental_analysis(num_benchmarks=50)
