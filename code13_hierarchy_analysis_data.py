import os
import json
import re
import time
from collections import Counter
import networkx as nx

from shared_utils import (
    get_central_districts_graph_by_segment_logic,
    get_all_routes_as_lists,
    build_high_order_network_from_motif
)

BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

TRANSLATION_CACHE_FILE = os.path.join(CACHE_DIR, 'translation_cache.json')
FUNCTIONAL_HIERARCHY_DATA = os.path.join(CACHE_DIR, 'functional_hierarchy_data.json')
STRUCTURAL_HIERARCHY_DATA = os.path.join(CACHE_DIR, 'structural_hierarchy_data.json')


def load_translation_cache():
    if os.path.exists(TRANSLATION_CACHE_FILE):
        with open(TRANSLATION_CACHE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    return {}


def save_translation_cache(cache):
    with open(TRANSLATION_CACHE_FILE, 'w', encoding='utf-8') as f: json.dump(cache, f, ensure_ascii=False, indent=4)


def contains_chinese(text):
    return bool(re.search('[\u4e00-\u9fa5]', text)) if isinstance(text, str) else False


def get_english_name_mock(name, cache):
    if not contains_chinese(name) or name in cache:
        return cache.get(name, name)
    try:
        from pypinyin import pinyin, Style
        translated_name = ' '.join([word[0].capitalize() for word in pinyin(name, style=Style.NORMAL)])
    except ImportError:
        translated_name = ''.join(name.split()).title().replace('(', '').replace(')', '')
    time.sleep(0.01)
    cache[name] = translated_name
    return translated_name


# --- Function Fixed (v2.2) ---
def calculate_functional_hierarchy(G, all_routes_info, translation_cache):
    print("\n> Calculating functional hierarchy (weighted path frequency)...")
    MODE_WEIGHTS = {'地铁': 20, '公交': 1, '轮渡': 8, '铁路': 8, '未知': 1}
    MODE_TRANSLATIONS = {'公交': 'Bus', '地铁': 'Metro', '轮渡': 'Ferry', '铁路': 'Railway', '未知': 'Unknown'}
    MODE_CN_TO_KEY = {'公交': 'bus', '地铁': 'metro', '轮渡': 'ferry', '铁路': 'railway'}

    path_counts = Counter()
    for route_info in all_routes_info:
        mode_cn = route_info.get('mode', '未知')
        path_names = route_info.get('path', [])
        weight = MODE_WEIGHTS.get(mode_cn, 1)
        mode_key = MODE_CN_TO_KEY.get(mode_cn)
        if not mode_key: continue

        for i in range(len(path_names) - 1):
            u_name, v_name = path_names[i], path_names[i + 1]
            u_id, v_id = f"{mode_key}_{u_name}", f"{mode_key}_{v_name}"
            if u_id in G and v_id in G:
                path_counts[(u_name, v_name)] += weight

    plot_data = []
    node_id_to_name = nx.get_node_attributes(G, 'name')
    node_id_to_mode = nx.get_node_attributes(G, 'mode')

    for path_tuple, score in path_counts.most_common(10):
        start_cn, end_cn = path_tuple

        found_start_id = next((f"{mkey}_{start_cn}" for mkey in MODE_CN_TO_KEY.values() if f"{mkey}_{start_cn}" in G),
                              None)
        found_end_id = next((f"{mkey}_{end_cn}" for mkey in MODE_CN_TO_KEY.values() if f"{mkey}_{end_cn}" in G), None)
        if not found_start_id or not found_end_id: continue

        mode_start_cn = node_id_to_mode.get(found_start_id, '未知')
        mode_end_cn = node_id_to_mode.get(found_end_id, '未知')
        mode_start_en = MODE_TRANSLATIONS.get(mode_start_cn, 'Unknown')
        path_type = 'Inter-modal Transfer' if mode_start_cn != mode_end_cn else f'Intra-modal ({mode_start_en})'

        plot_data.append({
            'start': get_english_name_mock(start_cn, translation_cache),
            'end': get_english_name_mock(end_cn, translation_cache),
            'score': score,
            'type': path_type
        })
    return plot_data


# --- Function Fixed (v2.2) ---
def calculate_structural_hierarchy(G, translation_cache):
    print("\n> Calculating structural hierarchy (FFL motif participation)...")
    node_id_to_name = nx.get_node_attributes(G, 'name')
    if not G.is_directed(): G = G.to_directed()

    high_order_weights = build_high_order_network_from_motif(G)

    plot_data = []
    for edge, count in high_order_weights.most_common(10):
        start_id, end_id = edge
        start_cn = node_id_to_name.get(start_id, start_id)
        end_cn = node_id_to_name.get(end_id, end_id)
        plot_data.append({
            'start': get_english_name_mock(start_cn, translation_cache),
            'end': get_english_name_mock(end_cn, translation_cache),
            'score': count,
            'type': 'Structural Link (FFL)'
        })
    return plot_data


if __name__ == "__main__":
    try:
        import pypinyin
    except ImportError:
        print("[Info] `pypinyin` not found. For better results: pip install pypinyin")

    print("--- Part 1: Generating Hierarchy Data (v2.2) ---")
    translation_cache = load_translation_cache()

    print("> Loading master network graph from shared_utils...")
    G_master = get_central_districts_graph_by_segment_logic()
    print(f"> Master network loaded: |V|={G_master.number_of_nodes()}, |E|={G_master.number_of_edges()}")

    all_routes_info = get_all_routes_as_lists()
    functional_data = calculate_functional_hierarchy(G_master, all_routes_info, translation_cache)
    with open(FUNCTIONAL_HIERARCHY_DATA, 'w', encoding='utf-8') as f:
        json.dump(functional_data, f, ensure_ascii=False, indent=4)
    print(f"> Functional hierarchy data cached to {os.path.basename(FUNCTIONAL_HIERARCHY_DATA)}")

    structural_data = calculate_structural_hierarchy(G_master, translation_cache)
    with open(STRUCTURAL_HIERARCHY_DATA, 'w', encoding='utf-8') as f:
        json.dump(structural_data, f, ensure_ascii=False, indent=4)
    print(f"> Structural hierarchy data cached to {os.path.basename(STRUCTURAL_HIERARCHY_DATA)}")

    save_translation_cache(translation_cache)
    print("\n--- Hierarchy data generation complete. ---")
