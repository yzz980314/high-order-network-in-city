import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shared_utils import get_config

# --- Global Configuration ---
CACHE_DIR = get_config('CACHE_DIR')
OUTPUT_DIR = get_config('OUTPUT_DIR')
RESULTS_CACHE_FILE = os.path.join(CACHE_DIR, 'functional_cascade_results.csv')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Functional_Cascade_Damage_Analysis.pdf')


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
        'xtick.labelsize': 12, 'ytick.labelsize': 13, 'legend.fontsize': 12,
        'figure.dpi': 300, 'savefig.bbox': 'tight', 'savefig.transparent': True,
        'axes.linewidth': 1.5, 'xtick.major.width': 1.2, 'ytick.major.width': 1.2,
        'axes.grid': False,
    })


if __name__ == '__main__':
    set_unified_style()
    print("--- Part 2: Generating Dumbbell Plot (Unified Style Final) ---")
    try:
        df = pd.read_csv(RESULTS_CACHE_FILE)
    except FileNotFoundError:
        print(f"[Error] Cache file not found at {RESULTS_CACHE_FILE}. Please run part 1 first.")
        exit()
    if df.empty:
        print("[Error] The results file is empty. Cannot generate plot.")
        exit()

    beta_value = df['Beta_Value'].iloc[0] if 'Beta_Value' in df.columns else None
    df['Cleaned_Node'] = df['Initial_Node'].str.replace('metro_', '').str.replace('bus_', '')
    df.rename(columns={'Betweenness': 'betweenness'}, inplace=True)
    node_name_mapping = {
        '汉口站': 'Hankou Station', '钓台道黄陂客运中心': 'Huangpi Bus Center', '汉口火车站': 'Hankou Railway Station',
        '武昌站': 'Wuchang Station', '天河机场交通中心': 'Tianhe Airport Hub', '循礼门': 'Xunlimen',
        '街道口': 'Jiedaokou',
        '中南路': 'Zhongnan Road', '香港路': 'Xianggang Road', '三阳路': 'Sanyang Road', '徐家棚': 'Xujiapeng',
        '武昌火车站': 'Wuchang Railway Station', '武汉站': 'Wuhan Station', '阅马场': 'Yuemachang',
        '螃蟹岬': 'Pangxiejia',
        '王家湾': 'Wangjiawan', '宗关': 'Zongguan', '三眼桥': 'Sanyanqiao', '马房山': 'Mafangshan', '琴台': 'Qintai',
        '十字桥': 'Shiziqiao', '鹦鹉大道地铁琴台站': 'Qintai Station', '武珞路阅马场': 'Yuemachang',
        '武珞路丁字桥': 'Dingziqiao'
    }
    df['Initial_Node_EN'] = df['Cleaned_Node'].map(node_name_mapping).fillna(df['Cleaned_Node'])
    df = df.sort_values('betweenness', ascending=False)
    min_bc, max_bc = df['betweenness'].min(), df['betweenness'].max()
    df['point_size'] = 50 + ((df['betweenness'] - min_bc) / (max_bc - min_bc)) * 350 if max_bc > min_bc else 200
    avg_damage = df['Total_Damage'].mean()
    max_val, min_val = df['Total_Damage'].max(), df['Total_Damage'].min()
    color_highest = '#d62728';
    color_lowest = '#1f77b4';
    color_intermediate = 'darkgray'
    fig, ax = plt.subplots(figsize=(12, 7))
    station_names = [];
    y_positions = [];
    y_spacing = 0.5
    for y_idx, (idx, row) in enumerate(df.reset_index().iterrows()):
        scaled_y_pos = y_idx * y_spacing
        station_names.append(row['Initial_Node_EN']);
        y_positions.append(scaled_y_pos)
        damage_val = row['Total_Damage'];
        point_size = row['point_size']
        ax.plot([avg_damage, damage_val], [scaled_y_pos, scaled_y_pos], color='darkgray', linewidth=1.5, zorder=1,
                alpha=0.7)
        point_color = color_highest if damage_val == max_val else color_lowest if damage_val == min_val else color_intermediate
        ax.scatter(damage_val, scaled_y_pos, s=point_size, facecolors=point_color, edgecolors='black', linewidths=1.5,
                   zorder=3)
        offset = -30 if damage_val < avg_damage else 30
        ax.text(damage_val + offset, scaled_y_pos, f'{damage_val:,.0f}', va='center',
                ha='right' if damage_val < avg_damage else 'left', fontsize=11)

    fig.text(0.5, 0.95, 'Vulnerability of Top Hubs to Functional Cascade Failure', ha='center', va='bottom',
             fontsize=20, fontweight='bold')
    subtitle_text = 'Sorted by structural importance (centrality); sized by centrality'
    if beta_value is not None:
        subtitle_text += f' (System Tolerance β = {beta_value:.3f})'
    fig.text(0.5, 0.92, subtitle_text, ha='center', va='bottom', fontsize=14)
    ax.set_yticks(y_positions);
    ax.set_yticklabels(station_names)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(axis='y', length=0, pad=40)
    if not df.empty:
        for label in ax.get_yticklabels():
            if label.get_text() == df.iloc[0]['Initial_Node_EN']: label.set_fontweight('bold')
    ax.invert_yaxis()
    bottom_lim, top_lim = ax.get_ylim()
    ax.set_ylim(bottom_lim + 0.4, top_lim - 0.4)
    ax.set_xlabel('Total Failed Components (Nodes + Edges)', fontsize=16, labelpad=15)
    ax.axvline(avg_damage, color='black', linestyle='--', linewidth=1.5, zorder=2)
    ax.text(avg_damage, ax.get_ylim()[1], f'Average Damage ({avg_damage:,.0f})', ha='center', va='bottom', fontsize=12,
            backgroundcolor='#FFFFFFE0')
    for spine in ax.spines.values(): spine.set_linewidth(1.5)

    # --- Manual Legend ---
    leg_x = 1.2;
    leg_text_offset = 0.05;
    y_step = 0.07;
    y_start_centrality = 0.6
    ax.text(leg_x, y_start_centrality, 'Centrality', transform=ax.transAxes, fontsize=14, fontweight='bold',
            va='bottom', clip_on=False)
    sizes = [('Low', 50), ('Medium', 225), ('High', 400)];
    current_y = y_start_centrality
    for i, (label, size) in enumerate(sizes):
        current_y -= y_step
        ax.scatter(leg_x, current_y, s=size, facecolors='white', edgecolors='black', linewidths=1.5,
                   transform=ax.transAxes, clip_on=False)
        ax.text(leg_x + leg_text_offset, current_y, label, transform=ax.transAxes, va='center', ha='left', fontsize=12,
                clip_on=False)
    y_start_damage = current_y - y_step * 1.5
    ax.text(leg_x, y_start_damage, 'Damage Level', transform=ax.transAxes, fontsize=14, fontweight='bold', va='bottom',
            clip_on=False)
    colors = [('Highest Damage', color_highest), ('Lowest Damage', color_lowest), ('Intermediate', color_intermediate)];
    current_y_damage = y_start_damage
    for i, (label, color) in enumerate(colors):
        current_y_damage -= y_step
        ax.scatter(leg_x, current_y_damage, s=100, color=color, transform=ax.transAxes, clip_on=False)
        ax.text(leg_x + leg_text_offset, current_y_damage, label, transform=ax.transAxes, va='center', ha='left',
                fontsize=12, clip_on=False)

    plt.subplots_adjust(left=0.25, right=0.7, top=0.9, bottom=0.15)
    plt.savefig(OUTPUT_FILE)
    print(f"\n--- Final plot saved to: {OUTPUT_FILE} ---")
    plt.show()
