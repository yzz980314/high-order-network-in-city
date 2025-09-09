import os
import sys
import geopandas as gpd
import matplotlib.pyplot as plt

try:
    from generate_mptn_map import (
        CENTRAL_DISTRICTS, DISTRICT_BOUNDARY_PATH, BUS_STATION_PATH,
        BUS_LINE_PATH, OUTPUT_DIR, STYLES, DPI
    )
except ImportError as e:
    print(f"Error: Import failed! {e}")
    sys.exit()


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


if __name__ == "__main__":
    set_unified_style()
    print("--- Starting generation of central urban bus map with view locked (unified font) ---")

    all_districts_gdf = gpd.read_file(DISTRICT_BOUNDARY_PATH, encoding='utf-8')
    central_districts_gdf = all_districts_gdf[all_districts_gdf['ENG_NAME'].isin(CENTRAL_DISTRICTS)]
    central_area_boundary = central_districts_gdf.unary_union
    central_area_gdf = gpd.GeoDataFrame(geometry=[central_area_boundary], crs=all_districts_gdf.crs)
    minx, miny, maxx, maxy = central_area_gdf.total_bounds
    x_padding = (maxx - minx) * 0.05
    y_padding = (maxy - miny) * 0.05

    full_stations_gdf = gpd.read_file(BUS_STATION_PATH).to_crs(central_area_gdf.crs)
    full_lines_gdf = gpd.read_file(BUS_LINE_PATH).to_crs(central_area_gdf.crs)
    full_stations_gdf = full_stations_gdf[~full_stations_gdf['name_st'].str.contains('临时站')]
    lines_clipped_central = gpd.clip(full_lines_gdf, central_area_gdf)
    stations_clipped_central = gpd.clip(full_stations_gdf, central_area_gdf)

    fig, ax = plt.subplots(1, 1, figsize=(18, 15))
    central_area_gdf.plot(ax=ax, facecolor=STYLES['central_facecolor'], edgecolor='black', linewidth=1.5, zorder=1)
    full_lines_gdf.plot(ax=ax, color='#cccccc', linewidth=0.8, zorder=2)
    lines_clipped_central.plot(ax=ax, color=STYLES['bus']['line_color'], linewidth=1.0, label='Bus Line', zorder=3)
    stations_clipped_central.plot(ax=ax, color='black', markersize=2.0, label='Bus Station', zorder=4)

    ax.legend(loc='upper right', markerscale=10, frameon=False)
    ax.set_axis_off()
    ax.set_xlim(minx - x_padding, maxx + x_padding)
    ax.set_ylim(miny - y_padding, maxy + y_padding)
    plt.tight_layout()

    output_filename = 'Spatial distribution of Bus in Central Wuhan.pdf'
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"\n🎉 View-locked central urban bus map successfully saved to: {output_path}")
    plt.show()
