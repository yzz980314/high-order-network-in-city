import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, 'distance_optimization_summary.csv')


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


def find_and_annotate_intersection(ax, df_pivot, styles):
    if 'ND' not in df_pivot.columns or 'BC' not in df_pivot.columns: return
    x = df_pivot.index.to_numpy();
    y_nd = df_pivot['ND'].to_numpy();
    y_bc = df_pivot['BC'].to_numpy()
    diff = y_nd - y_bc
    sign_change_indices = np.where(np.diff(np.sign(diff)))[0]
    if len(sign_change_indices) == 0: return
    idx = sign_change_indices[0]
    x1, x2 = x[idx], x[idx + 1];
    y_nd1, y_nd2 = y_nd[idx], y_nd[idx + 1];
    y_bc1, y_bc2 = y_bc[idx], y_bc[idx + 1]
    m_nd = (y_nd2 - y_nd1) / (x2 - x1);
    m_bc = (y_bc2 - y_bc1) / (x2 - x1)
    if abs(m_nd - m_bc) < 1e-9: return
    x_intersect = x1 + (y_bc1 - y_nd1) / (m_nd - m_bc)
    y_intersect = y_nd1 + m_nd * (x_intersect - x1)
    shift_style = styles['SHIFT']
    ax.plot(x_intersect, y_intersect, marker=shift_style['marker'], color=shift_style['color'], markersize=15,
            zorder=10, label=shift_style['label'])
    ax.vlines(x=x_intersect, ymin=ax.get_ylim()[0], ymax=y_intersect, colors='grey', linestyles='--', linewidth=1.2,
              zorder=1)
    ax.hlines(y=y_intersect, xmin=ax.get_xlim()[0], xmax=x_intersect, colors='grey', linestyles='--', linewidth=1.2,
              zorder=1)
    annotation_text = f'Vulnerability Shift\n~{x_intersect:.0f} m'
    ax.text(x_intersect, y_intersect + 0.015, annotation_text, fontsize=12, fontstyle='italic', color='black',
            ha='center', va='bottom')


def plot_robustness_vs_distance(df):
    fig, ax = plt.subplots(figsize=(12, 7))
    df_pivot = df.pivot(index='IMT_Distance', columns='Attack_Scenario', values='Robustness_Rb')

    # --- Core Change 1: Added independent linewidth control for each line ---
    styles = {
        'RND': {'color': '#1f77b4', 'marker': 'o', 'linewidth': 2.5, 'label': 'Random Failure'},
        'ND': {'color': '#ff7f0e', 'marker': 'o', 'linewidth': 2.0, 'label': 'Degree Attack'},
        'BC': {'color': '#2ca02c', 'marker': 'o', 'linewidth': 1.5, 'label': 'Betweenness Attack'},
        'SHIFT': {'color': '#d62728', 'marker': '*', 'label': 'Vulnerability Shift Point'}
    }

    for scenario in ['RND', 'ND', 'BC']:
        if scenario in df_pivot.columns:
            # --- Core Change 2: Use defined linewidth when plotting ---
            ax.plot(df_pivot.index, df_pivot[scenario],
                    color=styles[scenario]['color'],
                    linewidth=styles[scenario]['linewidth'],
                    marker=styles[scenario]['marker'],
                    markersize=8,
                    label=styles[scenario]['label'])

    find_and_annotate_intersection(ax, df_pivot, styles)
    ax.set_title('Robustness Response to Intermodal Transfer Distance')
    ax.set_ylabel('Robustness ($R_b$)')
    ax.set_xlabel('Intermodal Transfer Distance (meters)')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, title='Attack Scenario', loc='upper left')
    for spine in ax.spines.values(): spine.set_linewidth(1.5)
    output_file = os.path.join(OUTPUT_DIR, 'MPTN_Robustness_by_Transfer_Distance.pdf')
    plt.savefig(output_file)
    plt.show()


def plot_connectivity_vs_distance(df):
    fig, ax1 = plt.subplots(figsize=(12, 7))
    df_edges = df[['IMT_Distance', 'Num_IMT_Edges', 'Total_Edges']].drop_duplicates().set_index('IMT_Distance')
    ax2 = ax1.twinx()
    line1, = ax1.plot(df_edges.index, df_edges['Total_Edges'], color='#1f77b4', marker='o', linewidth=2.5,
                      label='Total Edges')
    line2, = ax2.plot(df_edges.index, df_edges['Num_IMT_Edges'], color='#ff7f0e', marker='o', linewidth=1.2,
                      label='Intermodal Edges')
    ax1.set_ylabel('Total Network Edges', color='#1f77b4');
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    ax1.get_yaxis().set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax2.set_ylabel('Number of Intermodal Edges', color='#ff7f0e');
    ax2.tick_params(axis='y', labelcolor='#ff7f0e')
    ax2.get_yaxis().set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax1.set_title('Connectivity Growth with Increasing Transfer Distance')
    ax1.set_xlabel('Intermodal Transfer Distance (meters)')
    ax1.legend(handles=[line1, line2], labels=[h.get_label() for h in [line1, line2]], loc='upper left')
    for spine in ax1.spines.values(): spine.set_linewidth(1.5)
    for spine in ax2.spines.values(): spine.set_linewidth(1.5)
    output_file = os.path.join(OUTPUT_DIR, 'MPTN_Connectivity_Analysis.pdf')
    plt.savefig(output_file)
    plt.show()


if __name__ == "__main__":
    set_unified_style()
    try:
        df_main = pd.read_csv(CACHE_FILE)
    except FileNotFoundError:
        print(f"[Error] Cache file not found at {CACHE_FILE}. Please run part1 first.")
        exit()
    plot_robustness_vs_distance(df_main)
    plot_connectivity_vs_distance(df_main)
