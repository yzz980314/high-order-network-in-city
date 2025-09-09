import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from adjustText import adjust_text

# --- 1. Global Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

SHP_FILE_PATH = os.path.join(DATA_DIR, 'wuhan_district_boundaries.shp')
MEDIUM_COLORS = {'blue': '#74a9cf', 'orange': '#fd8d3c', 'red': '#ef3b2c'}
urbanization_data_2023 = {
    'ENG_NAME': ['Jiangan', 'Jianghan', 'Qiaokou', 'Hanyang', 'Wuchang', 'Qingshan', 'Hongshan', 'Dongxihu', 'Hannan',
                 'Caidian', 'Jiangxia', 'Huangpi', 'Xinzhou'],
    'LABEL_NAME': ['Jiangan', 'Jianghan', 'Qiaokou', 'Hanyang', 'Wuchang', 'Qingshan', 'Hongshan', 'Dongxihu', 'Hannan',
                   'Caidian', 'Jiangxia', 'Huangpi', 'Xinzhou'],
    'urbanization_rate': [100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 98.39, 77.62, 73.71, 67.52, 69.08, 54.76,
                          55.23]
}


# --- Core Fix 1: Define a unified plotting style function ---
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
        'font.size': 14, 'axes.titlesize': 20, 'axes.labelsize': 16,
        'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 12,
        'figure.dpi': 300, 'savefig.bbox': 'tight', 'savefig.transparent': True,
        'axes.linewidth': 1.5, 'xtick.major.width': 1.2, 'ytick.major.width': 1.2,
        'axes.grid': False,
    })


def plot_heatmap(gdf, column, title, legend_label, output_path, district_label_col, cmap):
    """Generic heatmap plotting function."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 12))
    gdf.plot(column=column, cmap=cmap, linewidth=1.5, ax=ax, edgecolor='white', legend=False)
    city_boundary = gdf.unary_union
    boundary_gdf = gpd.GeoDataFrame(geometry=[city_boundary], crs=gdf.crs)
    boundary_gdf.plot(ax=ax, edgecolor='black', linewidth=2.0, facecolor='none')

    mappable_artist = ax.collections[0]
    texts = []
    for idx, row in gdf.iterrows():
        label_text = f"{row[district_label_col]}\n{row[column]:.2f}%"
        centroid = row.geometry.centroid
        texts.append(ax.text(centroid.x, centroid.y, label_text, fontsize=11, color='black', ha='center', va='center'))

    adjust_text(texts, ax=ax, force_text=(0.5, 0.8), arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))

    fig.canvas.draw()
    pos = ax.get_position()
    cax = fig.add_axes([pos.x0, pos.y0 - 0.08, pos.width, 0.03])
    fig.colorbar(mappable_artist, cax=cax, orientation='horizontal', label=legend_label)
    ax.set_axis_off()
    plt.subplots_adjust(left=0.04, right=0.96, top=0.98, bottom=0.05)
    plt.savefig(output_path)
    print(f"✅ Chart successfully saved to: {output_path}")
    plt.show()


if __name__ == '__main__':
    set_unified_style()  # Call style function
    wuhan_gdf = gpd.read_file(SHP_FILE_PATH, encoding='utf-8', engine='fiona')
    df_urban = pd.DataFrame(urbanization_data_2023)
    merged_gdf = wuhan_gdf.merge(df_urban, on='ENG_NAME', how='left')
    colors_and_positions = [(0.0, MEDIUM_COLORS['blue']), (0.5, 'white'), (0.75, MEDIUM_COLORS['orange']),
                            (1.0, MEDIUM_COLORS['red'])]
    medium_cmap = LinearSegmentedColormap.from_list('custom_medium_diverging', colors_and_positions)
    plot_heatmap(
        gdf=merged_gdf, column='urbanization_rate', title='Wuhan District Urbanization Rate (2023)',
        legend_label='Urbanization Rate of Permanent Population (%)',
        output_path=os.path.join(OUTPUT_DIR, 'wuhan_urbanization_rate_2023.pdf'),
        district_label_col='LABEL_NAME', cmap=medium_cmap
    )
