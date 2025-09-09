import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shared_utils import get_config

# --- Global Configuration ---
OUTPUT_DIR = get_config('OUTPUT_DIR')
CACHE_DIR = get_config('CACHE_DIR')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Resilience_under_Motif-based_vs_Traditional_Attacks.pdf')


# --- Core Fix 1: Define a unified plotting style function ---
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


if __name__ == "__main__":
    set_unified_style()
    print("--- Part 2: Plotting Motif Attack Comparison (Unified Style Final) ---")

    PLOT_CONFIG = {
        'random': {'label': 'Random Failure', 'color': '#1f77b4'},
        'degree': {'label': 'Degree Attack', 'color': '#ff7f0e'},
        'betweenness': {'label': 'Betweenness Attack', 'color': '#2ca02c'},
        'motif': {'label': 'Motif Importance Attack', 'color': '#d62728'}
    }
    fig, ax = plt.subplots(figsize=(10, 7))

    for name, config in PLOT_CONFIG.items():
        try:
            filepath = os.path.join(CACHE_DIR, f'code14_attack_{name}_curve.csv')
            df = pd.read_csv(filepath)
            y_values, x_values = df['mean'], df['nodes_removed_fraction']
            rb_value = np.trapz(y=y_values, x=x_values)

            # --- Core Change 2: Update plotting style ---
            ax.plot(x_values, y_values,
                    label=f"{config['label']} ($R_b={rb_value:.3f}$)",
                    color=config['color'],
                    marker='o',
                    linestyle='-',
                    markevery=max(1, len(x_values) // 10))

        except FileNotFoundError:
            print(f"[Warning] Cache file not found, skipping: {os.path.basename(filepath)}")
            continue

    ax.set_title('Resilience under Motif-based vs. Traditional Attacks')
    ax.set_xlabel('Fraction of Nodes Removed ($q$)')
    ax.set_ylabel('Relative LCC Size ($S$)')
    ax.legend(frameon=False)
    ax.set_xlim(0, 1);
    ax.set_ylim(0, 1)

    # --- Core Change 3: Explicitly bold all spines ---
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    plt.savefig(OUTPUT_FILE)
    print(f"\n--- Motif attack comparison plot saved to: {OUTPUT_FILE} ---")
    plt.show()
