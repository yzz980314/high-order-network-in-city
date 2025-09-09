import os
import pandas as pd

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

CASCADE_WAVE_FILE = os.path.join(CACHE_DIR, 'cascade_first_wave_results.csv')
FUNCTIONAL_DAMAGE_FILE = os.path.join(CACHE_DIR, 'functional_cascade_results.csv')
LATEX_OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'consolidated_damage_tables.tex')


def generate_cascade_anatomy_table_fixed(df):
    """(Fixed Version) Generates a cascade failure decomposition table, including node names and correct data"""
    df['Subsequent_Cascade_Damage'] = df['Loss_Total_Cascade'] - df['Loss_First_Wave']

    latex_string = r"""
% ★★★ NEW CONSOLIDATED TABLE 2 (Replaces Figure 12) - FIXED ★★★
\begin{table}[htbp]
    \centering
    \captionsetup{labelsep=colon, labelfont=bf, textfont=bf}
    \caption{Anatomy of Failure: First Wave vs. Subsequent Cascade}
    \label{tab:cascade_anatomy}
    \begin{tabular}{lrr}
        \toprule
        \textbf{Node Archetype (Target)} & \textbf{First Wave (\%)} & \textbf{Subsequent Cascade (\%)} \\
        \midrule
"""
    # --- Core Fix 1: Process data row by row, ensuring correct percentages and adding node names ---
    for _, row in df.iterrows():
        total_damage = row['Loss_Total_Cascade']
        if total_damage == 0:
            first_wave_pct, subsequent_pct = 0, 0
        else:
            first_wave_pct = (row['Loss_First_Wave'] / total_damage) * 100
            subsequent_pct = (row['Subsequent_Cascade_Damage'] / total_damage) * 100

        # Format node type and name
        node_name_mapping = { # Added mapping for consistency with plot
            '徐家棚': 'Xujiapeng', '武珞路阅马场': 'Wuluo Rd. Yuemachang', '祥丰路青州花园': 'Xiangfeng Rd. Qingzhou Garden'
        }
        english_node_name = node_name_mapping.get(row['NodeName'], row['NodeName'])
        archetype_text = f"{row['NodeType'].split('(')[0].strip()} ({english_node_name})"

        latex_string += f"        {archetype_text} & {first_wave_pct:.1f}\\% & {subsequent_pct:.1f}\\% \\\\\n"

    latex_string += r"""
        \bottomrule
    \end{tabular}
\end{table}
"""
    return latex_string


def generate_hub_vulnerability_table_fixed(df):
    """(Fixed Version) Generates Top Hubs damage table, adding Damage Level column"""
    df_sorted = df.sort_values(by='Betweenness', ascending=False).reset_index()

    # --- Core Fix 2: Add Damage Level logic ---
    max_damage_idx = df_sorted['Total_Damage'].idxmax()
    min_damage_idx = df_sorted['Total_Damage'].idxmin()

    damage_levels = []
    for i in range(len(df_sorted)):
        if i == max_damage_idx:
            damage_levels.append('Highest Damage')
        elif i == min_damage_idx:
            damage_levels.append('Lowest Damage')
        else:
            damage_levels.append('Intermediate')
    df_sorted['Damage_Level'] = damage_levels

    # Map node IDs to English names for the table
    node_name_mapping = { # Added mapping for consistency with plot
        'metro_琴台': 'Qintai', 'bus_三阳路': 'Sanyang Road', 'metro_螃蟹岬': 'Pangxiejia',
        'metro_徐家棚': 'Xujiapeng', 'bus_武珞路丁字桥': 'Dingziqiao'
    }
    df_sorted['Initial_Node_EN'] = df_sorted['Initial_Node'].map(node_name_mapping).fillna(df_sorted['Initial_Node'])


    latex_string = r"""
% ★★★ NEW CONSOLIDATED TABLE 3 (Replaces Figure 16) - FIXED ★★★
\begin{table}[htbp]
    \centering
    \captionsetup{labelsep=colon, labelfont=bf, textfont=bf}
    \caption{Vulnerability of Top Hubs to Functional Cascade Failure}
    \label{tab:hub_vulnerability}
    \begin{tabular}{l l r}
        \toprule
        \textbf{Hub (Centrality Rank)} & \textbf{Damage Level} & \textbf{Total Damage} \\
        \midrule
"""
    for index, row in df_sorted.iterrows():
        node_name = row['Initial_Node_EN']
        damage_level = row['Damage_Level']
        total_damage = int(row['Total_Damage'])

        latex_string += f"        {node_name} (Rank {index + 1}) & {damage_level} & {total_damage:,} \\\\\n"

    latex_string += r"""
        \bottomrule
    \end{tabular}
    \begin{minipage}{\columnwidth}
    \vspace{\smallskipamount}
    \small
    Note: Total Damage refers to the number of failed components (nodes + edges).
    </minipage>
\end{table}
"""
    return latex_string


if __name__ == '__main__':
    print("--- (Fixed Version) Starting integration of cascading failure data into LaTeX tables ---")

    try:
        df_wave = pd.read_csv(CASCADE_WAVE_FILE)
        df_damage = pd.read_csv(FUNCTIONAL_DAMAGE_FILE)
    except FileNotFoundError as e:
        print(f"[Error] Cache file not found: {e}.")
        exit()

    latex_anatomy = generate_cascade_anatomy_table_fixed(df_wave)
    latex_hubs = generate_hub_vulnerability_table_fixed(df_damage)

    final_latex_code = f"{latex_anatomy}\n\n{latex_hubs}"

    with open(LATEX_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_latex_code)

    print(f"\n🎉 Two fixed LaTeX tables successfully generated!")
    print(f"File path: {LATEX_OUTPUT_FILE}")
