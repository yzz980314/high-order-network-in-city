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
        CENTRAL_DISTRICTS, DISTRICT_BOUNDARY_PATH, METRO_STATION_PATH,
        METRO_LINE_PATH, EXCEL_DATA_PATH, OUTPUT_DIR, STYLES, DPI
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
def get_metro_data(station_path, line_path, excel_path, target_crs):
    try:
        metro_excel_df = pd.read_excel(excel_path, sheet_name='metro')
        all_stations_gdf = gpd.read_file(station_path).to_crs(target_crs)
        all_lines_gdf = gpd.read_file(line_path).to_crs(target_crs)
        desired_station_names = set(metro_excel_df['Name'].unique())
        station_name_field = next(
            (c for c in ['PointName', '站名', 'name', 'STATION'] if c in all_stations_gdf.columns), None)
        if not station_name_field: raise ValueError("Station Shapefile is missing a name field")
        filtered_stations_gdf = all_stations_gdf[all_stations_gdf[station_name_field].isin(desired_station_names)]
        station_line_name_field = next((f for f in ['LineName', '线路名称'] if f in filtered_stations_gdf.columns),
                                       None)
        if not station_line_name_field: raise ValueError("Station Shapefile is missing a line name field 'LineName'")
        line_names_to_keep = set(filtered_stations_gdf[station_line_name_field].unique())
        line_shapefile_name_field = next(
            (f for f in ['LineName', 'name', 'NAME', '线路名称'] if f in all_lines_gdf.columns), None)
        if not line_shapefile_name_field: raise ValueError("Line Shapefile is missing a name field")
        filtered_lines_gdf = all_lines_gdf[all_lines_gdf[line_shapefile_name_field].isin(line_names_to_keep)]
        return filtered_stations_gdf, filtered_lines_gdf
    except Exception as e:
        print(f"      - Fatal Error: {e}")
        sys.exit()


# ==============================================================================
# 3. Main Logic
# ==============================================================================
if __name__ == "__main__":
    set_unified_style()  # --- Core Fix 1 (cont.): Call the function ---
    print("--- Starting generation of view-locked central urban metro map (unified font) ---")

    all_districts_gdf = gpd.read_file(DISTRICT_BOUNDARY_PATH, encoding='utf-8')
    central_districts_gdf = all_districts_gdf[all_districts_gdf['ENG_NAME'].isin(CENTRAL_DISTRICTS)]
    central_area_boundary = central_districts_gdf.unary_union
    central_area_gdf = gpd.GeoDataFrame(geometry=[central_area_boundary], crs=all_districts_gdf.crs)
    minx, miny, maxx, maxy = central_area_gdf.total_bounds
    x_padding = (maxx - minx) * 0.05
    y_padding = (maxy - miny) * 0.05

    full_stations_gdf, full_lines_gdf = get_metro_data(METRO_STATION_PATH, METRO_LINE_PATH, EXCEL_DATA_PATH,
                                                       central_area_gdf.crs)
    lines_clipped_central = gpd.clip(full_lines_gdf, central_area_gdf)
    stations_clipped_central = gpd.clip(full_stations_gdf, central_area_gdf)

    fig, ax = plt.subplots(1, 1, figsize=(18, 15))
    central_area_gdf.plot(ax=ax, facecolor=STYLES['central_facecolor'], edgecolor='black', linewidth=1.5, zorder=1)
    full_lines_gdf.plot(ax=ax, color='#cccccc', linewidth=1.5, zorder=2)
    lines_clipped_central.plot(ax=ax, color=STYLES['metro']['line_color'], linewidth=1.5, label='Metro Line', zorder=3)
    stations_clipped_central.plot(ax=ax, color='black', markersize=16, label='Metro Station', zorder=4)

    ax.legend(loc='upper right', markerscale=3, frameon=False)
    ax.set_axis_off()
    ax.set_xlim(minx - x_padding, maxx + x_padding)
    ax.set_ylim(miny - y_padding, maxy + y_padding)
    plt.tight_layout()

    output_filename = 'Spatial distribution of Metro in Central Wuhan.pdf'
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"\n🎉 View-locked central urban metro map successfully saved to: {output_path}")
    plt.show()
