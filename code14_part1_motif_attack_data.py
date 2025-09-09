import os
import networkx as nx
from collections import Counter

# --- Import Project Modules ---
from shared_utils import get_central_districts_graph_by_segment_logic, build_high_order_network_from_motif, get_config
import analysis_engines


def get_motif_based_node_scores(G):
    """Calculates node motif participation scores (FFL-based degree)"""
    print("  > Calculating FFL edge weights...")
    edge_motif_weights = build_high_order_network_from_motif(G)

    print("  > Aggregating edge weights into node scores...")
    node_motif_scores = Counter()
    for (u, v), weight in edge_motif_weights.items():
        node_motif_scores[u] += weight
        node_motif_scores[v] += weight
    print("  > Node motif scores calculation complete.")
    return node_motif_scores


if __name__ == "__main__":
    print("--- Part 1: Generating Resilience Analysis Data (Multiprocessing Version) ---")

    # --- Step 1: Load unified master network ---
    print("> Loading master network graph from shared_utils...")
    G_master = get_central_districts_graph_by_segment_logic()
    print(f"> Master network loaded: |V|={G_master.number_of_nodes()}, |E|={G_master.number_of_edges()}")

    if not G_master.is_directed():
        G_master = G_master.to_directed()

    # --- Step 2: Prepare node removal order for all attack strategies ---
    print("\n> Preparing attack sequences for all scenarios...")

    # 2a. Calculate time-consuming metrics: Betweenness and Motif Scores
    betweenness_order = analysis_engines.get_node_removal_order(G_master, 'betweenness')
    motif_scores = get_motif_based_node_scores(G_master)

    # 2b. Define all attack sequences
    attack_orders = {
        # --- Key: Generate 50 reproducible, different attack lists for random attacks ---
        'random': [analysis_engines.get_node_removal_order(G_master, 'random', seed=i) for i in range(50)],
        'degree': analysis_engines.get_node_removal_order(G_master, 'degree'),
        'betweenness': betweenness_order,
        'motif': sorted(motif_scores, key=motif_scores.get, reverse=True)
    }
    print("> All attack sequences are ready.")

    # --- Step 3: Call the analysis engine, run all attack scenarios ---
    print("\n> Starting resilience simulations for all scenarios...")
    for name, order in attack_orders.items():
        cache_path = os.path.join(get_config('CACHE_DIR'), f'code14_attack_{name}_curve.csv')

        if os.path.exists(cache_path):
            print(f"> Data for '{name}' attack already exists, skipping.")
            continue

        print(f"--- Running resilience analysis for '{name.upper()}' attack ---")

        # --- Key: Pass the prepared attack sequence directly to the engine ---
        # For random attacks, 'order' itself is a list of lists
        # For other attacks, 'order' is a single list, and the engine will handle it
        df_resilience = analysis_engines.run_resilience_analysis(
            G_master,
            attack_scenario=order,
            num_tests=50 if name == 'random' else 1,
            removal_steps=100
        )
        df_resilience.to_csv(cache_path, index=False)
        print(f"\n  - Results for '{name}' cached to {os.path.basename(cache_path)}")

    print("\n--- All attack data generation complete. ---")
