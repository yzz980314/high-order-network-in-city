import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, 'recoverability_correlation_data.csv')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Metrics_Recoverability_Correlation.pdf')
STANDARD_COLORS = {'blue': '#1f77b4', 'orange': '#ff7f0e', 'red': '#d62728'}


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
        'xtick.labelsize': 14, 'ytick.labelsize': 14, 'legend.fontsize': 12,
        'figure.dpi': 300, 'savefig.bbox': 'tight', 'savefig.transparent': True,
        'axes.linewidth': 1.5, 'xtick.major.width': 1.2, 'ytick.major.width': 1.2,
        'axes.grid': False,
    })


if __name__ == '__main__':
    set_unified_style()
    print("--- Part 2: Plotting Correlation Heatmap (Subtitle Only) ---")
    try:
        df = pd.read_csv(CACHE_FILE, index_col=0)
    except FileNotFoundError:
        print(f"[Error] Cache file not found at {CACHE_FILE}. Please run part1 first.")
        exit()

    beta_value = df['beta_used'].iloc[0] if 'beta_used' in df.columns else None
    if 'beta_used' in df.columns: df = df.drop(columns=['beta_used'])

    correlation_matrix = df.corr(method='pearson')
    label_mapping = {
        'degree': 'Degree', 'betweenness': 'Betweenness',
        'motif_score': 'Motif Score', 'recoverability': 'Recoverability'
    }
    correlation_matrix_display = correlation_matrix.rename(columns=label_mapping, index=label_mapping)
    colors_and_positions = [(0.0, STANDARD_COLORS['blue']), (0.5, 'white'), (0.75, STANDARD_COLORS['orange']),
                            (1.0, STANDARD_COLORS['red'])]
    custom_cmap = LinearSegmentedColormap.from_list('custom_diverging', colors_and_positions)
    plt.figure(figsize=(9, 7))
    ax = sns.heatmap(
        correlation_matrix_display, annot=True, cmap=custom_cmap, vmin=-1, vmax=1,
        fmt=".3f", linewidths=.5, annot_kws={"size": 16}
    )
    cbar = ax.collections[0].colorbar
    cbar.set_label('Pearson Correlation', rotation=270, labelpad=25, fontsize=14)
    cbar.outline.set_linewidth(1.5)
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    # --- Core Change: Modified title generation logic ---
    # 1. Initialize an empty title
    title_text = ''
    # 2. If beta value exists, use it as the title content
    if beta_value is not None:
        # Removed newline character \n, as there is only one line now
        title_text = f'(System Tolerance β = {beta_value:.3f})'

    # 3. Set the title, using a smaller font size to make it look more like a subtitle
    plt.title(title_text, fontsize=14, y=1.02)

    plt.xticks(rotation=0, ha='center');
    plt.yticks(rotation=0)
    plt.tight_layout(pad=1.5)
    plt.savefig(OUTPUT_FILE)
    print(f"\n--- Final correlation heatmap saved to: {OUTPUT_FILE} ---")
    plt.show()
