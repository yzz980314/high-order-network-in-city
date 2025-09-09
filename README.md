# Higher-order Network Phenomena of Cascading Failures in Resilient Cities

This repository contains the complete source code and analytical framework for the research paper titled "Higher-order Network phenomena of cascading failures in resilient cities". The study investigates the complex interplay between network integration, higher-order structures, and dynamic cascading failures within the Wuhan multimodal public transport network (MPTN).

---

## Abstract

Modern urban resilience is threatened by cascading failures in multimodal transport networks, where localized shocks trigger widespread paralysis. Existing models, limited by their focus on pairwise interactions, often underestimate this systemic risk. To address this, we introduce a framework that confronts higher-order network theory with empirical data from the Wuhan multimodal transport network. Our findings confirm a fundamental duality: network integration enhances static robustness metrics but simultaneously creates the structural pathways for catastrophic cascades. Crucially, we uncover the source of this paradox: a profound disconnect between static network structure and dynamic functional failure. We provide strong evidence that both traditional metrics (e.g., betweenness centrality, with a correlation of $r=0.090$ to functional failure) and higher-order metrics (motif participation, $r=0.066$) are remarkably poor predictors of a system's ability to contain real-world cascading failures. This result highlights the inherent limitations of static analysis and underscores the need for a paradigm shift towards dynamic models to design and manage truly resilient urban systems.

## Key Contributions

1.  **Integrated Analytical Framework**: We develop and apply a framework that integrates traditional resilience assessment, higher-order network analysis, and dynamic failure models to examine systemic risk in an urban context.
2.  **Duality of Integration**: Our analysis reveals a fundamental duality in network integration—enhancing traditional resilience ($r_b$, $R_l$) while creating systemic fragility—and develops a theoretical framework that formalizes this trade-off by proving the existence of an optimal integration level.
3.  **Insufficiency of Static Metrics**: We provide strong empirical evidence that static network metrics are poor predictors of dynamic resilience, finding near-zero correlations between a node's ability to contain a functional cascade and its traditional centrality ($r=0.090$) or higher-order motif participation ($r=0.066$).
4.  **Quantitative Planning Tool**: The construction of a cost-benefit Pareto frontier provides a quantitative tool based on the "Safe-to-Fail" philosophy to guide network integration strategies.

---

## Repository Structure

```
high-order-network-in-city/
├── data/                 # Input data files (.shp, .xlsx)
├── *.py                  # All Python source code and analysis scripts
├── README.md             # This file
└── LICENSE               # Project license
```

---

## Setup and Installation

This project uses Python 3.8+ and relies on several data science and geospatial libraries. Using a virtual environment is strongly recommended.

### 1. Prerequisites
- [Git](https://git-scm.com/)
- [Python 3.8](https://www.python.org/downloads/) or newer

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/high-order-network-in-city.git
cd high-order-network-in-city
```

### 3. Create and Activate a Virtual Environment
```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the environment
# On Windows (CMD/PowerShell):
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```
After activation, your terminal prompt should start with `(venv)`.

### 4. Install Dependencies
All required libraries are listed in `requirements.txt`. Install them with a single command:
```bash
pip install -r requirements.txt
```
The content of `requirements.txt` is as follows:
```
adjustText==0.8
certifi==2024.7.4
charset-normalizer==3.3.2
click==8.1.7
click-plugins==1.1.1
cligj==0.7.2
contourpy==1.2.1
cycler==0.12.1
fiona==1.9.6
fonttools==4.53.0
geopandas==0.14.4
idna==3.7
kiwisolver==1.4.5
matplotlib==3.9.0
networkx==3.3
numpy==1.26.4
openpyxl==3.1.5
packaging==24.1
pandas==2.2.2
pillow==10.3.0
pypinyin==0.51.0
pyparsing==3.1.2
pyproj==3.6.1
python-dateutil==2.9.0.post0
pytz==2024.1
requests==2.32.3
scipy==1.14.0
seaborn==0.13.2
shapely==2.0.4
six==1.16.0
tqdm==4.66.4
tzdata==2024.1
urllib3==2.2.2
```
*(Note: The versions listed are confirmed to be compatible. Newer versions may also work but are not guaranteed.)*

---

## Data Preparation

The analysis requires specific geospatial and tabular data. Please ensure the following files are placed in the `/data` directory before running any scripts:

*   `wuhan_stations_by_route.xlsx`
*   `wuhan_district_boundaries.shp` (and its associated `.dbf`, `.shx`, `.prj` files)
*   `wuhan_city_boundaries.shp` (and its associated files)
*   `wuhan_railway_stations.shp` (and its associated files)
*   `wuhan_railway_lines.shp` (and its associated files)
*   `wuhan_ferry_wharves.shp` (and its associated files)
*   `wuhan_metro_stations.shp` (and its associated files)
*   `wuhan_metro_lines.shp` (and its associated files)
*   `wuhan_bus_stations.shp` (and its associated files)
*   `wuhan_bus_lines.shp` (and its associated files)

---

## Execution Workflow

The scripts are designed to be run sequentially. The workflow is divided into two main stages: **Data Generation** and **Plotting/Visualization**. All scripts should be run from the project's root directory.

### Stage 1: Data Generation and Analysis

These scripts perform the core computations and save intermediate results to a `/cache` directory (which will be created automatically). They can be time-consuming.

1.  **`code2_subsystem_topology.py`**: Analyzes and prints the basic topological properties of each individual transport subsystem (Metro, Bus, Ferry, Railway).
2.  **`code3_part1_subsystem_resilience_data.py`**: Calculates the structural resilience (robustness curves) for each individual subsystem under various attack scenarios.
3.  **`code4_incremental_analysis.py`**: Performs an incremental analysis of the MPTN, calculating a wide range of metrics as each subsystem is progressively added.
4.  **`code5_benchmark_resilience_data.py`**: Generates resilience data for the randomized null models (benchmarks) corresponding to each step of the network integration.
5.  **`code6_robustness_evolution_data.py`**: Calculates the structural resilience of the integrated MPTN at each evolutionary step.
6.  **`code7_zscore_data.py`**: Compares the real network's resilience against the benchmark models to compute Z-scores.
7.  **`code8_distance_optimization_data.py`**: Generates data for the Pareto frontier analysis by simulating network resilience across a range of intermodal transfer distances.
8.  **`code9_relocation_rate_data.py`**: Calculates the symmetric relocation rate ($R_l$) for each subsystem in both isolated and interconnected states.
9.  **`code10_cascade_data.py`**: Runs a simplified cascading failure simulation to analyze the "first wave" vs. "subsequent cascade" damage.
10. **`code11_asymmetric_rl_data.py`**: Calculates the asymmetric relocation rate ($R_l$) considering penalties for certain intermodal transfers.
11. **`code13_hierarchy_analysis_data.py`**: Generates data for comparing the network's functional (usage-based) and structural (motif-based) hierarchies.
12. **`code14_part1_motif_attack_data.py`**: Generates resilience data for the network under a novel "Motif Importance Attack".
13. **`code15_part1_functional_cascade_data.py`**: Runs a high-fidelity functional cascade simulation to determine the total damage caused by failures at top hub nodes.
14. **`code16_part1_recoverability_correlation_data.py`**: Generates the core dataset for correlating static network metrics with dynamic functional recoverability.
15. **`code17_part1_NonlinearDynamics_data.py`**: Runs extensive simulations to generate data demonstrating the system's non-linear dynamics (phase transitions and non-monotonicity).

### Stage 2: Plotting and Visualization

These scripts load the cached data from Stage 1 and generate the final figures and tables found in the paper. The results are saved to an `/output` directory (which will be created automatically).

- **Map Generation**:
    - `generate_mptn_map.py`: Generates the main MPTN map (Fig 5b).
    - `code1_urbanization_heatmap.py`: Generates the urbanization heatmap (Fig 5a).
    - `metro_map_central_viewlocked.py`: Generates the Metro map (Fig 5c).
    - `bus_map_central_viewlocked.py`: Generates the Bus map (Fig 5d).
    - `ferry_map_central_viewlocked.py`: Generates the Ferry map (Fig 5e).
    - `railway_map_central_viewlocked.py`: Generates the Railway map (Fig 5f).

- **Analysis Plots**:
    - `code3_part2_subsystem_resilience_plot.py`: Plots subsystem resilience curves (Fig 6).
    - `code6_part2_robustness_evolution_plot.py`: Plots the evolution of network robustness (Fig 7).
    - `code7_part2_zscore_plot.py`: Plots the Z-score analysis results (Fig 8).
    - `code8_part2_distance_optimization_plot.py`: Plots the Pareto frontier and connectivity cost (Fig 11 & 12).
    - `code10_part2_cascade_simulation_plot.py`: Creates the donut charts for cascade anatomy analysis.
    - `code12_pareto_plot.py`: Creates the final, annotated Pareto frontier plot.
    - `code13_part2_hierarchy_plot.py`: Plots the functional vs. structural hierarchy heatmap (Fig 9).
    - `code14_part2_motif_attack_plot.py`: Plots the resilience curves comparing motif attack to traditional attacks (Fig 14).
    - `code15_part2_functional_cascade_plot.py`: Creates the dumbbell plot for hub vulnerability.
    - `code16_part2_recoverability_correlation_plot.py`: Plots the metric correlation heatmap (Fig 13).
    - `code17_part2_NonlinearDynamics_plot.py`: Plots the non-linear dynamics of system collapse (Fig 10).

- **Table Generation**:
    - `code_fix_consolidate_rl_table.py`: Generates the LaTeX code for the consolidated relocation rate table (Table 4).
    - `code_fix_consolidate_damage_tables.py`: Generates LaTeX code for the cascade anatomy and hub vulnerability tables (Table 5 & 6).

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
