import os
import pandas as pd
import matplotlib.pyplot as plt


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
        'font.size': 16, 'axes.titlesize': 18, 'axes.labelsize': 16,
        'xtick.labelsize': 14, 'ytick.labelsize': 14, 'legend.fontsize': 14,
        'figure.dpi': 300, 'savefig.bbox': 'tight', 'savefig.transparent': True,
    })


if __name__ == "__main__":
    set_unified_style()
    print("--- Part 2: Plotting Cascade Comparison (Manual Layout Control) ---")
    BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
    CACHE_DIR = os.path.join(BASE_DIR, 'cache')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    RESULTS_CACHE_FILE = os.path.join(CACHE_DIR, 'cascade_first_wave_results.csv')
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Cascading_Failure_Analysis.pdf')

    try:
        df = pd.read_csv(RESULTS_CACHE_FILE)
    except FileNotFoundError:
        print(f"[Error] Cache file '{RESULTS_CACHE_FILE}' not found. Please run 'code10_cascade_v2.py' first.")
        exit()

    node_name_mapping = {
        '徐家棚': 'Xujiapeng', '武珞路阅马场': 'Wuluo Rd. Yuemachang', '祥丰路青州花园': 'Xiangfeng Rd. Qingzhou Garden'
    }
    df['Subsequent_Cascade_Damage'] = df['Loss_Total_Cascade'] - df['Loss_First_Wave']

    # ▼▼▼ Core Change 1: Abandon subplots, manually create Figure object ▼▼▼
    fig = plt.figure(figsize=(20, 8))
    # ▲▲▲ Core Change 1 ▲▲▲

    colors = ['#ff7f0e', '#1f77b4']
    legend_labels = ['First Wave Damage', 'Subsequent Cascade']

    # ▼▼▼ Core Change 2: Define layout parameters ▼▼▼
    # --- Adjust layout here ---
    AXES_WIDTH = 0.25
    AXES_HEIGHT = 0.7
    HORIZONTAL_SPACING = 0.04
    BOTTOM_MARGIN = 0.15
    # --- End adjustment ---

    # Automatically calculate starting position to center the group of charts horizontally
    num_axes = len(df)
    total_group_width = num_axes * AXES_WIDTH + (num_axes - 1) * HORIZONTAL_SPACING
    start_x = (1.0 - total_group_width) / 2.0

    axes = []
    for i in range(num_axes):
        left = start_x + i * (AXES_WIDTH + HORIZONTAL_SPACING)
        bottom = BOTTOM_MARGIN
        rect = [left, bottom, AXES_WIDTH, AXES_HEIGHT]
        ax = fig.add_axes(rect)
        axes.append(ax)
    # ▲▲▲ Core Change 2 ▲▲▲

    for i, row in df.iterrows():
        ax = axes[i]
        sizes = [row['Loss_First_Wave'], row['Subsequent_Cascade_Damage']]
        if sum(sizes) > 0:
            wedges, texts, autotexts = ax.pie(
                sizes, autopct='%1.1f%%', startangle=90, colors=colors,
                pctdistance=0.85, wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2)
            )
            plt.setp(autotexts, size=14, weight="bold", color="white")
        else:
            ax.text(0, 0, 'No Damage', ha='center', va='center', fontsize=18)

        center_text = f"Total Loss\n{row['Loss_Total_Cascade']:.1%}"
        ax.text(0, 0, center_text, ha='center', va='center', fontsize=20, weight='bold')
        english_name = node_name_mapping.get(row['NodeName'], row['NodeName'])
        title_text = f"{row['NodeType']}\n(Target: {english_name})"
        ax.set_title(title_text, fontsize=18, pad=20)

    fig.suptitle('Anatomy of Failure: First Wave vs. Subsequent Cascade', fontsize=24, weight='bold', y=0.95)
    fig.legend(legend_labels, loc='lower center', bbox_to_anchor=(0.5, 0.08), ncol=2, frameon=False)

    # ▼▼▼ Core Change 3: Removed tight_layout as we are manually controlling the layout ▼▼▼
    # plt.tight_layout(...) # This line is removed
    # ▲▲▲ Core Change 3 ▲▲▲

    plt.savefig(OUTPUT_FILE)
    print(f"\n--- Plot saved successfully to: {OUTPUT_FILE} ---")
    plt.show()
