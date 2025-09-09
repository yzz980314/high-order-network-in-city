import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
from matplotlib.legend_handler import HandlerBase


class HandlerHatched(HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        facecolor = orig_handle.get_facecolor();
        hatch = orig_handle.get_hatch()
        p_bg = Rectangle([xdescent, ydescent], width, height, facecolor=facecolor, hatch=hatch, linewidth=0,
                         transform=trans)
        p_fg = Rectangle([xdescent, ydescent], width, height, facecolor='none', edgecolor='black', linewidth=0.7,
                         transform=trans)
        return [p_bg, p_fg]


# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)
ASYMMETRIC_CACHE_FILE = os.path.join(CACHE_DIR, 'asymmetric_rl_analysis_data.csv')
SYMMETRIC_CACHE_FILE = os.path.join(CACHE_DIR, 'relocation_rate_analysis_data.csv')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Asymmetric_Rl_Analysis.pdf')
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
        'xtick.labelsize': 14, 'ytick.labelsize': 12, 'legend.fontsize': 12,
        'figure.dpi': 300, 'savefig.bbox': 'tight', 'savefig.transparent': True,
        'axes.linewidth': 1.5, 'xtick.major.width': 1.2, 'ytick.major.width': 1.2,
        'axes.grid': False,
        'hatch.color': 'white', 'hatch.linewidth': 1.0
    })


if __name__ == '__main__':
    set_unified_style()
    print("--- Part 2: Plotting Symmetric vs Asymmetric Rl (No Edgecolor Final) ---")
    try:
        df_asym = pd.read_csv(ASYMMETRIC_CACHE_FILE)
        df_sym = pd.read_csv(SYMMETRIC_CACHE_FILE)
    except FileNotFoundError as e:
        print(f"[Error] Cache file not found: {e}. Please run part1 scripts first.")
        exit()

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)
    fig.suptitle('Comparison of Relocation Rate ($R_l$) Across Models', fontsize=20, weight='bold')
    subsystems = ['Metro', 'Bus'];
    x = np.arange(len(subsystems));
    bar_width = 0.2

    for ax_idx, dist in enumerate([750, 1600]):
        ax = axes[ax_idx]
        ax.set_title(f'Distance Limit: {dist}m')
        for i, sub in enumerate(subsystems):
            sym_iso = \
                df_sym[(df_sym['Subsystem'] == sub) & (df_sym['Distance'] == dist) & (df_sym['Type'] == 'Isolated')][
                    'Value'].iloc[0]
            sym_conn = \
                df_sym[
                    (df_sym['Subsystem'] == sub) & (df_sym['Distance'] == dist) & (df_sym['Type'] == 'Interconnected')][
                    'Value'].iloc[0]
            asym_iso = \
                df_asym[
                    (df_asym['Subsystem'] == sub) & (df_asym['Distance'] == dist) & (df_asym['Type'] == 'Isolated')][
                    'Value'].iloc[0]
            asym_conn = df_asym[
                (df_asym['Subsystem'] == sub) & (df_asym['Distance'] == dist) & (df_asym['Type'] == 'Interconnected')][
                'Value'].iloc[0]

            # --- Core Change: Removed all edgecolor and linewidth parameters for bars ---
            ax.bar(x[i] - 1.5 * bar_width, sym_iso, bar_width, color=COLORS['Isolated'])
            ax.bar(x[i] - 0.5 * bar_width, sym_conn, bar_width, color=COLORS['Interconnected'])
            ax.bar(x[i] + 0.5 * bar_width, asym_iso, bar_width, color=COLORS['Isolated'], hatch='//')
            ax.bar(x[i] + 1.5 * bar_width, asym_conn, bar_width, color=COLORS['Interconnected'], hatch='//')

            text_offset, text_fontsize = 0.015, 9
            ax.text(x[i] - 1.5 * bar_width, sym_iso + text_offset, f'{sym_iso:.2f}', ha='center', va='bottom',
                    fontsize=text_fontsize)
            ax.text(x[i] - 0.5 * bar_width, sym_conn + text_offset, f'{sym_conn:.2f}', ha='center', va='bottom',
                    fontsize=text_fontsize)
            ax.text(x[i] + 0.5 * bar_width, asym_iso + text_offset, f'{asym_iso:.2f}', ha='center', va='bottom',
                    fontsize=text_fontsize)
            ax.text(x[i] + 1.5 * bar_width, asym_conn + text_offset, f'{asym_conn:.2f}', ha='center', va='bottom',
                    fontsize=text_fontsize)
        ax.set_xticks(x);
        ax.set_xticklabels(subsystems)
        ax.set_ylim(-0.05, 1.05);
        ax.set_xlabel('Subsystem')
        for spine in ax.spines.values(): spine.set_linewidth(1.5)

    axes[0].set_ylabel('Relocation Rate ($R_l$)')

    # Legend patches retain edgecolor for clarity
    legend_handles = [Patch(facecolor=COLORS['Isolated'], edgecolor='black'),
                      Patch(facecolor=COLORS['Interconnected'], edgecolor='black'),
                      Patch(facecolor=COLORS['Isolated'], hatch='//', edgecolor='black'),
                      Patch(facecolor=COLORS['Interconnected'], hatch='//', edgecolor='black')]
    legend_labels = ['Symmetric, Isolated', 'Symmetric, Interconnected', 'Asymmetric, Isolated',
                     'Asymmetric, Interconnected']

    fig.legend(handles=legend_handles, labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0.94), ncol=4,
               frameon=False, handler_map={patch: HandlerHatched() for patch in legend_handles if patch.get_hatch()})

    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    plt.savefig(OUTPUT_FILE)
    print(f"\n--- Asymmetric Rl plot saved to: {OUTPUT_FILE} ---")
    plt.show()
