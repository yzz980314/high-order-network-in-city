import os
import geopandas as gpd
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import pandas as pd

# ==============================================================================
# 1. Dependency Imports
# ==============================================================================
try:
    from generate_mptn_map import (
        CENTRAL_DISTRICTS, DISTRICT_BOUNDARY_PATH, FERRY_WHARF_PATH,
        EXCEL_DATA_PATH, OUTPUT_DIR, STYLES, DPI
    )
except ImportError as e:
    print(f"Error: Import failed! {e}")
    exit()


# --- Core Change 1: Define and call a unified plotting style function ---
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
        'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 18,
        'figure.dpi': 300, 'savefig.bbox': 'tight', 'savefig.transparent': True,
        'axes.linewidth': 1.5,
    })


# ==============================================================================
# 2. Data Processing Function (kept as is)
# ==============================================================================
def get_ferry_data(wharf_path, excel_path, target_crs):
    try:
        ferry_df = pd.read_excel(excel_path, sheet_name='ferry')
        ferry_routes_definition = {}
        for line_code in ferry_df['Line Code'].unique():
            line_stations = ferry_df[ferry_df['Line Code'] == line_code].sort_values('Sequence')
            ferry_routes_definition[line_code] = line_stations['Name'].tolist()
    except Exception:
        ferry_routes_definition = {"武中线": ["武汉关码头(轮渡站)", "武汉轮渡黄鹤楼码头(临江大道)"],
                                   "集汉线": ["武汉轮渡集家嘴码头", "武汉关码头(轮渡站)"]}
    all_wharfs = gpd.read_file(wharf_path, encoding='utf-8').to_crs(target_crs)
    passenger_ferries = all_wharfs[all_wharfs['行业小'] == '人渡口']
    core_station_names = set(st for stations in ferry_routes_definition.values() for st in stations)
    route_lines_geom = []
    for r, s in ferry_routes_definition.items():
        points = [pt.geometry.iloc[0] for st in s if
                  not (pt := passenger_ferries[passenger_ferries['name'] == st]).empty]
        if len(points) >= 2:
            route_lines_geom.append(LineString(points))
    lines_gdf = gpd.GeoDataFrame(geometry=route_lines_geom, crs=target_crs)
    stations_gdf = passenger_ferries[passenger_ferries['name'].isin(core_station_names)]
    return stations_gdf, lines_gdf


# ==============================================================================
# 3. Main Logic
# ==============================================================================
if __name__ == "__main__":
    set_unified_style()  # --- Core Change 1 (cont.): Call the function ---
    print("--- Starting generation of central urban ferry distribution map (unified font) ---")

    all_districts_gdf = gpd.read_file(DISTRICT_BOUNDARY_PATH, encoding='utf-8')
    central_districts_gdf = all_districts_gdf[all_districts_gdf['ENG_NAME'].isin(CENTRAL_DISTRICTS)]
    central_area_boundary = central_districts_gdf.unary_union
    central_area_gdf = gpd.GeoDataFrame(geometry=[central_area_boundary], crs=all_districts_gdf.crs)

    stations, lines = get_ferry_data(FERRY_WHARF_PATH, EXCEL_DATA_PATH, central_area_gdf.crs)
    lines_clipped_central = gpd.clip(lines, central_area_gdf)
    stations_clipped_central = gpd.clip(stations, central_area_gdf)

    fig, ax = plt.subplots(1, 1, figsize=(18, 15))
    central_area_gdf.plot(ax=ax, facecolor=STYLES['central_facecolor'], edgecolor='black', linewidth=1.5)
    lines_clipped_central.plot(ax=ax, color=STYLES['ferry']['line_color'], linewidth=2.5, label='Ferry Line', zorder=5)
    stations_clipped_central.plot(ax=ax, color='black', markersize=100, edgecolor='white', label='Ferry Station',
                                  zorder=10)

    ax.legend(loc='upper right', markerscale=1.5, frameon=False)
    ax.set_axis_off()
    plt.tight_layout()

    output_filename = 'Spatial distribution of Ferry in Central Wuhan.pdf'
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"\n🎉 Central urban ferry map successfully saved to: {output_path}")
    plt.show()
