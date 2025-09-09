import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Import Project Modules ---
from shared_utils import get_config

# --- Global Configuration ---
CACHE_DIR = get_config('CACHE_DIR')
OUTPUT_DIR = get_config('OUTPUT_DIR')
CACHE_FILE_BETA = os.path.join(CACHE_DIR, 'nonlinear_beta_sweep_results.csv')
CACHE_FILE_K = os.path.join(CACHE_DIR, 'nonlinear_k_attack_results.csv')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Nonlinear_Dynamics_of_System_Collapse.pdf')


def find_elbow_point(x, y):
    """Uses the "farthest point from diagonal" method to find the elbow point of a curve."""
    if len(x) < 3 or len(y) < 3: return -1
    # Normalize data
    x_norm = (x - x.min()) / (x.max() - x.min()) if (x.max() - x.min()) > 0 else np.zeros_like(x)
    y_norm = (y - y.min()) / (y.max() - y.min()) if (y.max() - y.min()) > 0 else np.zeros_like(y)
    # Calculate distance of each point to the diagonal (0,1) -> (1,0)
    distances = np.abs(x_norm + y_norm - 1)
    return np.argmax(distances)


def set_unified_style(font_name='Times New Roman'):
    """Sets a unified, publication-ready plot style"""
    try:
        # Try to set the specified font
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = font_name
        # Create a tiny test plot to verify font availability, preventing program crash if font is missing
        fig_test = plt.figure(figsize=(0.1, 0.1));
        plt.text(0, 0, "Test");
        plt.close(fig_test)
    except Exception:
        # If font is not found, print a warning and fall back to generic serif font
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
    print("--- Part 2: Plotting Nonlinear Dynamics (No Main Title) ---")

    try:
        df_beta = pd.read_csv(CACHE_FILE_BETA).sort_values(by='beta').reset_index(drop=True)
        df_k = pd.read_csv(CACHE_FILE_K).sort_values(by='k').reset_index(drop=True)
    except FileNotFoundError as e:
        print(f"[Error] Cache file not found: {e}. Please run part1 first.")
        exit()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

    # --- Core Change: Commented out or deleted this line to remove the main title ---
    # fig.suptitle('Non-Linear Dynamics of System Collapse', fontsize=20, weight='bold')

    # --- Plot 1: System Tolerance vs. Cascade Size ---
    ax1.plot(df_beta['beta'], df_beta['cascade_size'], marker='o', color='#d62728', linestyle='-')
    ax1.set_xlabel('System Tolerance Parameter (β)')
    ax1.set_ylabel('Final Cascade Size (Failed Components)')
    ax1.set_title('(a) Cascade Size as a Function of System Tolerance')

    critical_index = find_elbow_point(df_beta['beta'].values, df_beta['cascade_size'].values)
    if critical_index != -1:
        critical_beta = df_beta['beta'].iloc[critical_index]
        ax1.axvline(x=critical_beta, color='black', linestyle='--', linewidth=1.5, zorder=0)
        ax1.text(critical_beta + 0.01, ax1.get_ylim()[1] * 0.9,
                 f'Critical Threshold\nβc ≈ {critical_beta:.2f}',
                 fontsize=12, style='italic', ha='left', va='top',
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=0.5, alpha=0.8))

    # --- Plot 2: Initial Shock Size vs. Cascade Size ---
    # Use rolling mean to smooth data, better showing the trend
    y_smooth = df_k['cascade_size'].rolling(window=3, center=True, min_periods=1).mean()

    # Plot raw data points, using transparency to make them less prominent
    ax2.plot(df_k['k'], df_k['cascade_size'],
             marker='o', color='#1f77b4', linestyle=':',
             label='Raw Data', alpha=0.6)

    # Plot smoothed trend line
    ax2.plot(df_k['k'], y_smooth, color='#1f77b4', label='Smoothed Trend', marker='o', linestyle='-')

    ax2.set_xlabel('Initial Shock Size (k highest BC nodes removed)')
    # Y-axis label is the same as the left plot, can be omitted
    ax2.set_title('(b) Cascade Size as a Function of Initial Shock')

    # Find the "inflection point" of the smoothed curve, approximated here by the point of maximum second derivative
    second_derivative = np.gradient(np.gradient(y_smooth))
    tipping_point_index = np.argmax(second_derivative)
    if tipping_point_index > 0:
        tipping_k = df_k['k'].iloc[tipping_point_index]
        ax2.axvline(x=tipping_k, color='black', linestyle='--', linewidth=1.5, zorder=0)
        ax2.text(tipping_k - 0.5, ax2.get_ylim()[1] * 0.9,
                 f'Tipping Point\nk ≈ {tipping_k}',
                 fontsize=12, style='italic', ha='right', va='top',
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=0.5, alpha=0.8))

    # Display legend
    ax2.legend(loc='lower right', frameon=False)

    # Set consistent linewidth for spines of both subplots
    for ax_sub in [ax1, ax2]:
        for spine in ax_sub.spines.values():
            spine.set_linewidth(1.5)

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE)
    print(f"\n--- Nonlinear dynamics plot saved to: {OUTPUT_FILE} ---")
    plt.show()
