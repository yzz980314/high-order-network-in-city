import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_STEPS = 4
STEP_LABELS = ['Step 1: Metro', 'Step 2: + Bus', 'Step 3: + Ferry', 'Step 4: + Railway']
ATTACK_SCENARIOS = {'rnd': 'Random Failure', 'nd': 'Degree Attack', 'bc': 'Betweenness Attack'}
COLORS = ['#d62728', '#1f77b4', '#2ca02c', '#ff7f0e']
# --- Core Change 1: Define independent linewidths for each integration step ---
LINEWIDTHS = [1.5, 3.0, 2.0, 1]


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


def load_robustness_data(step_index, imt_distance, scenario_short_name):
    filename = f"evolution_imt_{imt_distance}_step_{step_index + 1}_attack_{scenario_short_name}.csv"
    filepath = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(filepath): return None, None
    try:
        df = pd.read_csv(filepath, header=None, names=['mean', 'nodes_removed_fraction', 'std'])
        return df['nodes_removed_fraction'].values, df['mean'].values
    except (pd.errors.EmptyDataError, ValueError):
        return None, None


def calculate_rb_value(q, S):
    if q is None or S is None or len(q) < 2: return 0.0
    return np.trapz(y=S[np.argsort(q)], x=q[np.argsort(q)])


if __name__ == '__main__':
    set_unified_style()
    print("--- Part 2: Plotting Robustness Evolution (Controllable Linewidth) ---")
    fig, axs = plt.subplots(2, 3, figsize=(20, 11), sharex=True, sharey=True)
    scenarios = list(ATTACK_SCENARIOS.keys())

    for row_idx, imt_distance in enumerate([0, 100]):
        print(f"\n> Plotting for IMT Distance = {imt_distance}m")
        for col_idx, scenario in enumerate(scenarios):
            ax = axs[row_idx, col_idx]
            for step in range(NUM_STEPS):
                q, S = load_robustness_data(step, imt_distance, scenario)
                if q is not None:
                    rb_value = calculate_rb_value(q, S)
                    label = f"{STEP_LABELS[step]} ($R_b={rb_value:.3f}$)"

                    # --- Core Change 2: Use defined linewidth when plotting ---
                    ax.plot(q, S,
                            color=COLORS[step],
                            linewidth=LINEWIDTHS[step],
                            marker='o',
                            label=label,
                            markevery=max(1, len(q) // 10))

            if row_idx == 0: ax.set_title(ATTACK_SCENARIOS[scenario], fontsize=18)
            ax.legend(loc='upper right')

            for spine in ax.spines.values():
                spine.set_linewidth(1.5)

    fig.supxlabel('Fraction of Nodes Removed ($q$)', fontsize=16)
    fig.supylabel('Relative Size of LCC ($S$)', fontsize=16)
    axs[0, 0].text(-0.15, 0.5, 'Isolated Network\n($D_{IMT}=0$m)', transform=axs[0, 0].transAxes, ha='center',
                   va='center', rotation='vertical', fontsize=16)
    axs[1, 0].text(-0.15, 0.5, 'Interconnected Network\n($D_{IMT}=100$m)', transform=axs[1, 0].transAxes, ha='center',
                   va='center', rotation='vertical', fontsize=16)

    plt.tight_layout(rect=[0.02, 0.01, 1, 0.98])

    output_filename = os.path.join(OUTPUT_DIR, "Network robustness Steps.pdf")
    plt.savefig(output_filename)
    print(f"\n--- Robustness evolution plot saved to: {output_filename} ---")
    plt.show()
