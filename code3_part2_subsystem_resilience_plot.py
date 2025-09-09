import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

SUBSYSTEM_EN = ['Metro', 'Bus', 'Ferry', 'Railway']

# --- Core Change 1: Added independent linewidth control for each attack strategy ---
PLOT_CONFIG = {
    'rnd': {'color': '#1f77b4', 'linewidth': 2.0, 'label': 'Random Failure'},
    'nd': {'color': '#ff7f0e', 'linewidth': 1.0, 'label': 'Degree Attack'},
    'bc': {'color': '#2ca02c', 'linewidth': 2.0, 'label': 'Betweenness Attack'}
}


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
        'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 11,
        'figure.dpi': 300, 'savefig.bbox': 'tight', 'savefig.transparent': True,
        'axes.linewidth': 1.5, 'xtick.major.width': 1.2, 'ytick.major.width': 1.2,
        'axes.grid': False,
    })


def plot_single_resilience_chart(ax, network_name_en, rb_rnd, rb_nd, rb_bc, df_rnd, df_nd, df_bc):
    """Plots the resilience curve for a single subsystem on the given ax"""
    mark_every = max(1, len(df_rnd) // 10)

    # --- Core Change 2: Use defined linewidth when plotting ---
    ax.plot(df_rnd['nodes_removed_fraction'], df_rnd['mean'],
            color=PLOT_CONFIG['rnd']['color'],
            linewidth=PLOT_CONFIG['rnd']['linewidth'],
            marker='o', markevery=mark_every,
            label=f"{PLOT_CONFIG['rnd']['label']} ($R_b={rb_rnd:.3f}$)", zorder=1)

    ax.plot(df_bc['nodes_removed_fraction'], df_bc['mean'],
            color=PLOT_CONFIG['bc']['color'],
            linewidth=PLOT_CONFIG['bc']['linewidth'],
            marker='o', markevery=mark_every,
            label=f"{PLOT_CONFIG['bc']['label']} ($R_b={rb_bc:.3f}$)", zorder=2)

    ax.plot(df_nd['nodes_removed_fraction'], df_nd['mean'],
            color=PLOT_CONFIG['nd']['color'],
            linewidth=PLOT_CONFIG['nd']['linewidth'],
            marker='o', markevery=mark_every,
            label=f"{PLOT_CONFIG['nd']['label']} ($R_b={rb_nd:.3f}$)", zorder=3)

    ax.set_title(f'{network_name_en} Network')
    ax.legend(loc='upper right')
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.05, 1.05)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)


if __name__ == "__main__":
    set_unified_style()
    fig, axs = plt.subplots(2, 2, figsize=(15, 10), sharex=True, sharey=True)
    axs = axs.flatten()

    print("--- Part 2: Plotting Resilience Curves (Controllable Linewidth) ---")

    for i, network_name_en in enumerate(SUBSYSTEM_EN):
        print(f"  > Plotting for {network_name_en}...")
        try:
            df_rnd = pd.read_csv(os.path.join(CACHE_DIR, f'code3_{network_name_en}_rnd_curve.csv'))
            df_nd = pd.read_csv(os.path.join(CACHE_DIR, f'code3_{network_name_en}_nd_curve.csv'))
            df_bc = pd.read_csv(os.path.join(CACHE_DIR, f'code3_{network_name_en}_bc_curve.csv'))
            scalars = pd.read_json(os.path.join(CACHE_DIR, f'code3_{network_name_en}_scalars.json'), typ='series')

            plot_single_resilience_chart(
                axs[i], network_name_en,
                scalars['rb_rnd'], scalars['rb_nd'], scalars['rb_bc'],
                df_rnd, df_nd, df_bc
            )
        except FileNotFoundError:
            axs[i].set_title(f'{network_name_en} Network\n(Data not found)')
            axs[i].text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14, color='red')
            continue

    fig.supxlabel('Fraction of Nodes Removed ($q$)', fontsize=16)
    fig.supylabel('Relative Size of LCC ($S$)', fontsize=16)

    plt.tight_layout(rect=[0.02, 0.0, 0.98, 0.98])

    output_filename = 'Resilience_Analysis_for_All_Networks.pdf'
    final_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(final_path)
    print(f"\n--- Combined plot saved to: {final_path} ---")
    plt.show()
