import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, 'relocation_rate_analysis_data.csv')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Relocation_Rate_of_Subsystems_PAPER_STANDARD.pdf')
SUBSYSTEM_EN = ['Metro', 'Bus', 'Ferry', 'Railway']
COLORS = {'Isolated': '#ff7f0e', 'Interconnected': '#1f77b4'}


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
    print("--- Part 2: Plotting Relocation Rate (No Edgecolor Final) ---")
    try:
        df = pd.read_csv(CACHE_FILE)
    except FileNotFoundError:
        print(f"[Error] Cache file not found at {CACHE_FILE}. Please run part1 first.")
        exit()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), sharey=True)
    fig.suptitle('Relocation Rate ($R_l$) Comparison', fontsize=20, weight='bold')
    ax1.set_title('Distance Limit: 750m');
    ax2.set_title('Distance Limit: 1600m')
    bar_width = 0.35
    x = np.arange(len(SUBSYSTEM_EN))
    df['Subsystem'] = pd.Categorical(df['Subsystem'], categories=SUBSYSTEM_EN, ordered=True)
    df = df.sort_values('Subsystem')
    df_750 = df[df['Distance'] == 750]

    # --- Core Change: Removed edgecolor and linewidth parameters ---
    bars1_iso = ax1.bar(x - bar_width / 2, df_750[df_750['Type'] == 'Isolated']['Value'], bar_width,
                        color=COLORS['Isolated'])
    bars1_conn = ax1.bar(x + bar_width / 2, df_750[df_750['Type'] == 'Interconnected']['Value'], bar_width,
                         color=COLORS['Interconnected'])

    df_1600 = df[df['Distance'] == 1600]
    # --- Core Change: Removed edgecolor and linewidth parameters ---
    bars2_iso = ax2.bar(x - bar_width / 2, df_1600[df_1600['Type'] == 'Isolated']['Value'], bar_width,
                        color=COLORS['Isolated'])
    bars2_conn = ax2.bar(x + bar_width / 2, df_1600[df_1600['Type'] == 'Interconnected']['Value'], bar_width,
                         color=COLORS['Interconnected'])

    for ax_sub in [ax1, ax2]:
        ax_sub.set_xticks(x);
        ax_sub.set_xticklabels(SUBSYSTEM_EN)
        for spine in ax_sub.spines.values(): spine.set_linewidth(1.5)

    ax1.set_ylabel('Relocation Rate ($R_l$)');
    ax1.set_ylim(0, 1.05)
    ax1.bar_label(bars1_iso, fmt='%.2f', padding=3, fontsize=10)
    ax1.bar_label(bars1_conn, fmt='%.2f', padding=3, fontsize=10)
    ax2.bar_label(bars2_iso, fmt='%.2f', padding=3, fontsize=10)
    ax2.bar_label(bars2_conn, fmt='%.2f', padding=3, fontsize=10)

    # Legend patches retain edgecolor for clarity
    legend_handles = [Patch(facecolor=COLORS['Isolated'], edgecolor='black', label='Isolated'),
                      Patch(facecolor=COLORS['Interconnected'], edgecolor='black', label='Interconnected')]
    fig.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 0.93), ncol=2, frameon=False)

    fig.supxlabel('Subsystem', fontsize=16, y=0.04)
    plt.tight_layout(rect=[0, 0.02, 1, 0.95])

    plt.savefig(OUTPUT_FILE)
    print(f"\n--- Relocation Rate plot saved to: {OUTPUT_FILE} ---")
    plt.show()
