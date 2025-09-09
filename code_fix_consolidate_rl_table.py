import os
import pandas as pd

# --- Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

ASYMMETRIC_CACHE_FILE = os.path.join(CACHE_DIR, 'asymmetric_rl_analysis_data.csv')
SYMMETRIC_CACHE_FILE = os.path.join(CACHE_DIR, 'relocation_rate_analysis_data.csv')
LATEX_OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'consolidated_rl_table.tex')


def generate_latex_table_fixed(df_sym, df_asym):
    """(Fixed Version) Generates a comprehensive LaTeX table for all subsystems based on two DataFrames"""

    # --- Data Preparation ---
    df_sym['Model'] = 'Symmetric'
    df_asym['Model'] = 'Asymmetric'

    # --- Core Fix 1: Combine all data and prepare for systems without asymmetric data ---
    df_combined = pd.concat([df_sym, df_asym])

    pivot_df = df_combined.pivot_table(
        index=['Subsystem', 'Model'],
        columns=['Distance', 'Type'],
        values='Value'
    )

    # Reindex to include all subsystems and models, even if data is missing
    subsystems = ['Metro', 'Bus', 'Ferry', 'Railway']
    models = ['Symmetric', 'Asymmetric']
    new_index = pd.MultiIndex.from_product([subsystems, models], names=['Subsystem', 'Model'])
    pivot_df = pivot_df.reindex(new_index)

    # --- LaTeX Code Generation ---
    latex_string = r"""
% ★★★ NEW CONSOLIDATED TABLE 1 (Replaces Figure 7 and 8) ★★★
\begin{table}[htbp]
    \centering
    \captionsetup{labelsep=colon, labelfont=bf, textfont=bf}
    \caption{Consolidated Relocation Rate ($R_l$) Analysis Across Models}
    \label{tab:consolidated_rl}
    \resizebox{\columnwidth}{!}{%
    \begin{tabular}{l l cc cc}
        \toprule
        \multirow{2}{*}{\textbf{Subsystem}} & \multirow{2}{*}{\textbf{Model}} & \multicolumn{2}{c}{\textbf{$d_{\max}=750$m}} & \multicolumn{2}{c}{\textbf{$d_{\max}=1600$m}} \\
        \cmidrule(lr){3-4} \cmidrule(lr){5-6}
        & & \textbf{Isolated} & \textbf{Interconnected} & \textbf{Isolated} & \textbf{Interconnected} \\
        \midrule
"""

    # --- Core Fix 2: Iterate through all subsystems, gracefully handling missing values ---
    for subsystem in subsystems:
        latex_string += f"        \\multirow{{2}}{{*}}{{{subsystem}}}"
        for model in models:
            row_data = pivot_df.loc[(subsystem, model)]
            iso_750 = f"{row_data.get((750, 'Isolated'), 0):.4f}" if not pd.isna(
                row_data.get((750, 'Isolated'))) else "N/A"
            conn_750 = f"{row_data.get((750, 'Interconnected'), 0):.4f}" if not pd.isna(
                row_data.get((750, 'Interconnected'))) else "N/A"
            iso_1600 = f"{row_data.get((1600, 'Isolated'), 0):.4f}" if not pd.isna(
                row_data.get((1600, 'Isolated'))) else "N/A"
            conn_1600 = f"{row_data.get((1600, 'Interconnected'), 0):.4f}" if not pd.isna(
                row_data.get((1600, 'Interconnected'))) else "N/A"

            row_color = r"\rowcolor{tablegray}" if model == 'Symmetric' else ""

            latex_string += f" & {model} & {iso_750} & {conn_750} & {iso_1600} & {conn_1600} \\\\\n"
        if subsystem != subsystems[-1]:
            latex_string += r"        \addlinespace"

    latex_string += r"""
        \bottomrule
    \end{tabular}%
    }
    \begin{minipage}{\columnwidth}
    \vspace{\smallskipamount}
    \small
    Note: "N/A" indicates that the Asymmetric model is not applicable to single-mode systems like Ferry and Railway.
    \end{minipage}
\end{table}
"""
    return latex_string


if __name__ == '__main__':
    print("--- (Fixed Version) Starting integration of relocation rate data into LaTeX table ---")
    try:
        df_sym = pd.read_csv(SYMMETRIC_CACHE_FILE)
        df_asym = pd.read_csv(ASYMMETRIC_CACHE_FILE)
    except FileNotFoundError as e:
        print(f"[Error] Cache file not found: {e}.")
        exit()

    latex_code = generate_latex_table_fixed(df_sym, df_asym)

    with open(LATEX_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    print(f"\n🎉 Fixed LaTeX table successfully generated! File path: {LATEX_OUTPUT_FILE}")
