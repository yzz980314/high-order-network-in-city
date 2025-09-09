import os
import sys
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# ==============================================================================
# 1. Dependency Imports
# ==============================================================================
try:
    from generate_mptn_map import (
        CENTRAL_DISTRICTS, DISTRICT_BOUNDARY_PATH, RAILWAY_STATION_PATH,
        RAILWAY_LINE_PATH, EXCEL_DATA_PATH, OUTPUT_DIR, STYLES, DPI
    )
except ImportError as e:
    print(f"Error: Import failed! {e}")
    sys.exit()


# --- Core Fix 1: Define and call a unified plotting style function ---
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
def get_railway_data(station_path, line_path, excel_path, boundary_gdf):
    target_crs = boundary_gdf.crs
    try:
        stations_df = pd.read_excel(excel_path, sheet_name='railway')
        stations_to_keep = stations_df['Name'].tolist()
    except Exception:
        stations_to_keep = ['武汉站', '武昌站', '汉口站', '汤逊湖站', '南湖东站', '纸坊东站', '庙山站', '山坡东站',
                            '天河机场站', '武汉东站']
    stations_gdf = gpd.read_file(station_path, encoding='utf-8').to_crs(target_crs)
    lines_gdf = gpd.read_file(line_path, encoding='utf-8').to_crs(target_crs)
    selected_stations = stations_gdf[stations_gdf['name'].isin(stations_to_keep)].copy()
    wuhan_lines_clipped = gpd.clip(lines_gdf, boundary_gdf)
    lines_to_keep = ['汉十高速铁路', '京广', '京广高速铁路', '武昌南', '武九', '武咸城际铁路']
    selected_lines = wuhan_lines_clipped[wuhan_lines_clipped['NAME'].isin(lines_to_keep)]
    return selected_stations, selected_lines


# ==============================================================================
# 3. Main Logic
# ==============================================================================
if __name__ == "__main__":
    set_unified_style()  # --- Core Fix 1 (cont.): Call the function ---
    print("--- Starting generation of view-locked central urban railway map (unified font) ---")

    all_districts_gdf = gpd.read_file(DISTRICT_BOUNDARY_PATH, encoding='utf-8')
    central_districts_gdf = all_districts_gdf[all_districts_gdf['ENG_NAME'].isin(CENTRAL_DISTRICTS)]
    central_area_boundary = central_districts_gdf.unary_union
    central_area_gdf = gpd.GeoDataFrame(geometry=[central_area_boundary], crs=all_districts_gdf.crs)
    minx, miny, maxx, maxy = central_area_gdf.total_bounds
    x_padding = (maxx - minx) * 0.05
    y_padding = (maxy - miny) * 0.05

    wuhan_boundary = gpd.read_file(os.path.join(r'D:\python-files\wuhan\high-order network in city\data', 'wuhan_city_boundaries.shp'), encoding='utf-8')
    wuhan_boundary = wuhan_boundary[wuhan_boundary['地名'] == '武汉市']
    full_stations_gdf, full_lines_gdf = get_railway_data(RAILWAY_STATION_PATH, RAILWAY_LINE_PATH, EXCEL_DATA_PATH,
                                                         wuhan_boundary)
    lines_clipped_central = gpd.clip(full_lines_gdf, central_area_gdf)
    stations_clipped_central = gpd.clip(full_stations_gdf, central_area_gdf)

    fig, ax = plt.subplots(1, 1, figsize=(18, 15))
    central_area_gdf.plot(ax=ax, facecolor=STYLES['central_facecolor'], edgecolor='black', linewidth=1.5, zorder=1)
    full_lines_gdf.plot(ax=ax, color='#cccccc', linewidth=1.5, zorder=2)
    lines_clipped_central.plot(ax=ax, color=STYLES['railway']['line_color'], linewidth=1.5, label='Railway Line',
                               zorder=3)
    stations_clipped_central.plot(ax=ax, color='black', markersize=80, edgecolor='white', label='Railway Station',
                                  zorder=4)

    ax.legend(loc='upper right', markerscale=1.6, frameon=False)
    ax.set_axis_off()
    ax.set_xlim(minx - x_padding, maxx + x_padding)
    ax.set_ylim(miny - y_padding, maxy + y_padding)
    plt.tight_layout()

    output_filename = 'Spatial distribution of Railway in Central Wuhan.pdf'
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"\n🎉 View-locked central urban railway map successfully saved to: {output_path}")
    plt.show()
