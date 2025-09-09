import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from matplotlib.patches import Patch

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, 'zscore_analysis_data.csv')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Z-Score_Analysis.pdf')
NUM_STEPS = 4
BAR_COLORS = {'RND': '#1f77b4', 'ND': '#ff7f0e', 'BC': '#2ca02c'}


def set_unified_style(font_name='Times New Roman'):
    """Sets a unified, publication-ready plot style"""
    try:
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = font_name
        fig_test = plt.figure(figsize=(0.1, 0.1));
        plt.text(0, 0, "Test");
        plt.close(fig_test)
    except Exception:
        print(f"Warning: Font '{font_name}' not found, falling back to default serif font.")
        plt.rcParams['font.family'] = 'serif'

    plt.rcParams.update({
        'font.size': 14, 'axes.titlesize': 18, 'axes.labelsize': 16,
        'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 12,
        'figure.dpi': 300, 'savefig.bbox': 'tight', 'savefig.transparent': True,
        'axes.linewidth': 1.5, 'xtick.major.width': 1.2, 'ytick.major.width': 1.2,
        'axes.grid': False,
    })


if __name__ == '__main__':
    set_unified_style()
    print("--- Part 2: Plotting Z-Score Analysis (No Explanation Text) ---")
    try:
        df = pd.read_csv(CACHE_FILE)
    except FileNotFoundError:
        print(f"[Error] Cache file not found at {CACHE_FILE}. Please run part1 first.")
        exit()

    fig, axs = plt.subplots(2, 2, figsize=(18, 9))  # Adjusted height to accommodate no explanation text
    network_types = [
        {'title': 'Isolated Network ($D_{IMT} = 0$m)', 'dist': 0},
        {'title': 'Interconnected Network ($D_{IMT} = 100$m)', 'dist': 100}
    ]

    for i, network in enumerate(network_types):
        ax_bar, ax_line = axs[i, 0], axs[i, 1]
        df_subset = df[df['IMT_Distance'] == network['dist']].sort_values(by='Step')
        x = np.arange(NUM_STEPS)
        bar_width = 0.25

        for j, scenario in enumerate(['RND', 'ND', 'BC']):
            scenario_data = df_subset[df_subset['Attack_Scenario'] == scenario]['Z_Score']
            position = x + (j - 1) * bar_width
            bars = ax_bar.bar(position, scenario_data, width=bar_width, label=scenario, color=BAR_COLORS[scenario])
            ax_bar.bar_label(bars, fmt='%.2e', fontsize=9, padding=3)
            ax_line.plot(x, scenario_data, color=BAR_COLORS[scenario], marker='o', markersize=8, label=scenario)

        min_val, max_val = df_subset['Z_Score'].min(), df_subset['Z_Score'].max()
        padding = (abs(max_val) + abs(min_val)) * 0.15
        y_limits = (min(0, min_val) - padding, max(0, max_val) + padding)
        ax_bar.set_ylim(y_limits);
        ax_line.set_ylim(y_limits)
        ax_bar.set_ylabel(network['title'] + '\n\nZ-Score', fontsize=16)
        ax_line.yaxis.set_tick_params(labelleft=False)

        for ax_sub in [ax_bar, ax_line]:
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_scientific(True);
            formatter.set_powerlimits((0, 0))
            ax_sub.yaxis.set_major_formatter(formatter)
            for spine in ax_sub.spines.values():
                spine.set_linewidth(1.5)

    for ax_sub in axs[1, :]:
        ax_sub.set_xlabel('Evolutionary Step', fontsize=16)
        ax_sub.set_xticks(x)
        ax_sub.set_xticklabels([f'Step {k + 1}' for k in range(NUM_STEPS)])

    axs[0, 0].set_title('Static Comparison', fontsize=18)
    axs[0, 1].set_title('Evolutionary Trend', fontsize=18)

    legend_elements = [Patch(facecolor=BAR_COLORS['RND'], label='RND'), Patch(facecolor=BAR_COLORS['ND'], label='ND'),
                       Patch(facecolor=BAR_COLORS['BC'], label='BC')]
    fig.legend(handles=legend_elements, loc='upper center', ncol=3, bbox_to_anchor=(0.5, 0.98), frameon=False)

    fig.tight_layout(rect=[0, 0.05, 1, 0.96])
    plt.savefig(OUTPUT_FILE)
    print(f"\n--- Z-Score plot (no explanation text) saved to: {OUTPUT_FILE} ---")
    plt.show()
