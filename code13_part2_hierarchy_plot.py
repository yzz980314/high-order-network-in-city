import os
import json
import platform
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1 import make_axes_locatable

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)
FUNCTIONAL_HIERARCHY_DATA = os.path.join(CACHE_DIR, 'functional_hierarchy_data.json')
STRUCTURAL_HIERARCHY_DATA = os.path.join(CACHE_DIR, 'structural_hierarchy_data.json')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Hierarchies_Vertical_Heatmap.pdf')


def create_heatmap_panel(ax, data, config):
    TYPE_COLOR_PALETTE = {
        'Intra-modal (Bus)': '#1f77b4', 'Intra-modal (Metro)': '#2ca02c',
        'Structural Link (FFL)': '#ff7f0e', 'Inter-modal Transfer': '#d62728', 'Default': 'gray'
    }
    scores = [item['score'] for item in data]
    # Handle case where all scores are the same (e.g., min == max) to avoid division by zero
    if not scores or max(scores) == min(scores):  # Added check for empty scores list
        norm = mcolors.NoNorm()  # Use NoNorm if all values are identical or list is empty
    else:
        norm = mcolors.Normalize(vmin=min(scores), vmax=max(scores))

    gap = 0.1
    for j, item in enumerate(data):
        fill_color = config['cmap'](norm(item['score']))
        indicator_color = TYPE_COLOR_PALETTE.get(item['type'], 'gray')
        rect_x, rect_width = j + gap / 2, 1 - gap
        main_rect = plt.Rectangle((rect_x, 0), rect_width, 1, facecolor=fill_color, edgecolor='lightgray',
                                  linewidth=1.5, zorder=1)
        ax.add_patch(main_rect)
        if item['type'] != 'Structural Link (FFL)':
            indicator_height = 0.1
            indicator_bar = plt.Rectangle((rect_x, 0), rect_width, indicator_height, facecolor=indicator_color,
                                          edgecolor='none', zorder=2)
            ax.add_patch(indicator_bar)
        path_text = f"{item['start']} → {item['end']}"
        wrapped_path = textwrap.fill(path_text, width=12)
        score_text = f"Score: {item['score']}"
        text_color = 'white' if (isinstance(norm, mcolors.Normalize) and norm(item['score']) > 0.6) else 'black'
        ax.text(j + 0.5, 0.65, wrapped_path, ha='center', va='center', fontsize=13, color=text_color, weight='bold',
                linespacing=1.2, zorder=3)
        ax.text(j + 0.5, 0.25, score_text, ha='center', va='center', fontsize=10, color=text_color, zorder=3)
    ax.set_xlim(0, 10);
    ax.set_ylim(0, 1)
    ax.set_xticks([k + 0.5 for k in range(10)])
    ax.set_xticklabels([f"Rank #{k + 1}" for k in range(10)], rotation=0)
    ax.set_yticks([]);
    ax.tick_params(axis='x', length=0)
    for spine in ax.spines.values(): spine.set_visible(False)


def set_unified_style(font_name='Times New Roman'):
    """Sets a unified, publication-ready plot style"""
    plt.style.use('default')
    try:
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = font_name
        plt.rcParams['axes.unicode_minus'] = False
        fig_test = plt.figure(figsize=(0.1, 0.1));
        plt.text(0, 0, "Test");
        plt.close(fig_test)
    except Exception:
        print(f"Warning: Font '{font_name}' or Chinese support font not found.")

    plt.rcParams.update({
        'font.size': 14, 'axes.titlesize': 18, 'axes.labelsize': 16,
        'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 14,
        'figure.dpi': 300, 'savefig.bbox': 'tight', 'savefig.transparent': True,
        'figure.facecolor': 'white'
    })


if __name__ == "__main__":
    set_unified_style()
    print("--- Part 2: Generating Hierarchy Heatmap (No Super Title) ---")
    try:
        with open(FUNCTIONAL_HIERARCHY_DATA, 'r', encoding='utf-8') as f:
            functional_data = json.load(f)
        with open(STRUCTURAL_HIERARCHY_DATA, 'r', encoding='utf-8') as f:
            structural_data = json.load(f)
    except FileNotFoundError as e:
        print(f"[Error] Cache file not found: {e}. Aborting.")
        exit()

    fig, axes = plt.subplots(2, 1, figsize=(22, 7.5))
    light_blues = mcolors.ListedColormap(plt.cm.Blues(np.linspace(0.2, 0.85, 256)))
    light_oranges = mcolors.ListedColormap(plt.cm.Oranges(np.linspace(0.2, 0.85, 256)))
    create_heatmap_panel(axes[0], functional_data, {'cmap': light_blues})
    create_heatmap_panel(axes[1], structural_data, {'cmap': light_oranges})
    axes[0].set_ylabel('Functional\nLink', rotation=0, ha='right', va='center', fontsize=18, weight='bold', labelpad=20)
    axes[1].set_ylabel('Structural\nLink (FFL)', rotation=0, ha='right', va='center', fontsize=18, weight='bold',
                       labelpad=20)

    for i, (ax, data, cmap, label) in enumerate(
            zip(axes, [functional_data, structural_data], [light_blues, light_oranges],
                ['Functional Score', 'Structural Score'])):
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="2%", pad=0.1)
        scores = [item['score'] for item in data]
        # Handle case where all scores are the same for colorbar
        if not scores or max(scores) == min(scores):  # Added check for empty scores list
            norm_cb = mcolors.NoNorm()
        else:
            norm_cb = mcolors.Normalize(vmin=min(scores), vmax=max(scores))
        cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm_cb, cmap=cmap), cax=cax)
        cb.set_label(label, rotation=270, labelpad=25, fontsize=14)
        cb.outline.set_linewidth(1.5)

    TYPE_COLOR_PALETTE_LEGEND = {'Intra-modal (Bus)': '#1f77b4', 'Intra-modal (Metro)': '#2ca02c',
                                 'Inter-modal Transfer': '#d62728'}
    all_types_in_data = set(item['type'] for item in functional_data) | set(item['type'] for item in structural_data)
    legend_order = ['Intra-modal (Metro)', 'Intra-modal (Bus)', 'Inter-modal Transfer']
    legend_elements = [Patch(facecolor=TYPE_COLOR_PALETTE_LEGEND[path_type], label=path_type) for path_type in
                       legend_order if path_type in all_types_in_data and path_type in TYPE_COLOR_PALETTE_LEGEND]
    if legend_elements:
        fig.legend(handles=legend_elements, title='Path Type', loc='lower center', bbox_to_anchor=(0.5, 0.01),
                   ncol=len(legend_elements), frameon=False, title_fontsize=16)

    fig.tight_layout(rect=[0.05, 0.12, 0.95, 1.0])
    plt.savefig(OUTPUT_FILE)
    print(f"> Hierarchy heatmap (no super title) saved to {OUTPUT_FILE}")
    plt.show()
