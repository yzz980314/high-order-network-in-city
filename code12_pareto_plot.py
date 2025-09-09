import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

CACHE_FILE = os.path.join(CACHE_DIR, 'distance_optimization_summary.csv')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Pareto_Frontier_Analysis.pdf')

COLOR_PALETTE = {
    'RND': '#1f77b4', 'ND': '#ff7f0e', 'BC': '#2ca02c', 'OPTIMAL': '#d62728'
}


# --- Core Change 1: Define a unified plotting style function ---
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


def find_pareto_optimal_point(df_scenario):
    if df_scenario.empty: return None, None
    x = df_scenario['Num_IMT_Edges'].values;
    y = df_scenario['Robustness_Rb'].values
    x_norm = (x - x.min()) / (x.max() - x.min());
    y_norm = (y - y.min()) / (y.max() - y.min())
    distances = np.sqrt(x_norm ** 2 + (y_norm - 1) ** 2)
    optimal_idx = np.argmin(distances)
    return x[optimal_idx], y[optimal_idx]


if __name__ == "__main__":
    set_unified_style()
    print("--- Part 2: Plotting Pareto Frontier (Unified Style Final) ---")

    try:
        df = pd.read_csv(CACHE_FILE)
    except FileNotFoundError:
        print(f"[Error] Cache file not found. Please run code8 script first.")
        exit()

    fig, ax = plt.subplots(figsize=(12, 8))

    styles = {
        'RND': {'color': COLOR_PALETTE['RND'], 'marker': 'o', 'label': 'Random Failure'},
        'ND': {'color': COLOR_PALETTE['ND'], 'marker': 'o', 'label': 'Degree Attack'},
        'BC': {'color': COLOR_PALETTE['BC'], 'marker': 'o', 'label': 'Betweenness Attack'}
    }

    for scenario in ['RND', 'ND', 'BC']:
        subset = df[df['Attack_Scenario'] == scenario].sort_values(by='Num_IMT_Edges')
        # --- Core Change 2: Update plotting style ---
        ax.plot(subset['Num_IMT_Edges'], subset['Robustness_Rb'],
                color=styles[scenario]['color'], marker=styles[scenario]['marker'],
                markersize=8, label=styles[scenario]['label'], linestyle='-')

    bc_subset = df[df['Attack_Scenario'] == 'BC'].sort_values(by='Num_IMT_Edges')
    optimal_x, optimal_y = find_pareto_optimal_point(bc_subset)

    if optimal_x is not None:
        diminishing_min_x = optimal_x * 2.5;
        new_xlim_max = diminishing_min_x * 1.5
        positive_costs = df[df['Num_IMT_Edges'] > 0]['Num_IMT_Edges']
        min_positive_cost = positive_costs.min() if not positive_costs.empty else 10
        new_xlim_min = min_positive_cost * 0.8
        ax.axvspan(new_xlim_min, optimal_x, color='grey', alpha=0.10, zorder=0)
        ax.axvspan(diminishing_min_x, new_xlim_max, color='grey', alpha=0.10, zorder=0)
        ax.text(optimal_x * 0.3, 0.35, 'Region of\nHigh ROI', fontsize=12, ha='center', style='italic')
        ax.text(diminishing_min_x * 1.2, 0.18, 'Region of\nDiminishing Returns', fontsize=12, ha='center',
                style='italic')
        ax.plot(optimal_x, optimal_y, marker='*', color=COLOR_PALETTE['OPTIMAL'], markersize=20, zorder=10,
                label='Optimal Trade-off (BC)', linestyle='none')
        ax.vlines(x=optimal_x, ymin=ax.get_ylim()[0], ymax=optimal_y, colors='grey', linestyles='--', linewidth=1.2)
        ax.hlines(y=optimal_y, xmin=new_xlim_min, xmax=optimal_x, colors='grey', linestyles='--', linewidth=1.2)
        annotation_text = f'Optimal Point\nCost: {optimal_x:,}\nBenefit: {optimal_y:.3f}'
        ax.text(optimal_x * 1.2, optimal_y * 1.05, annotation_text, fontsize=12, style='italic',
                color=COLOR_PALETTE['OPTIMAL'],
                bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="gray", lw=0.5, alpha=0.8))
        ax.set_xlim(left=new_xlim_min, right=new_xlim_max)

    ax.set_title('Cost-Benefit Pareto Frontier for Network Integration')
    ax.set_xlabel('Investment Cost (Number of Intermodal Edges)')
    ax.set_ylabel('Network Resilience ($R_b$)')
    ax.set_xscale('log')
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    # --- Core Change 3: Explicitly bold all spines ---
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, title='Attack Scenario', loc='upper left', frameon=False)
    plt.savefig(OUTPUT_FILE)
    print(f"\n--- Final Pareto Frontier plot saved to: {OUTPUT_FILE} ---")
    plt.show()
