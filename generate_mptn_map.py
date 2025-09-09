import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString

# --- Configuration ---
BASE_DIR = r'D:\python-files\wuhan\high-order network in city'
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

BOUNDARY_PATH = os.path.join(DATA_DIR, 'wuhan_city_boundaries.shp')
DISTRICT_BOUNDARY_PATH = os.path.join(DATA_DIR, 'wuhan_district_boundaries.shp')
EXCEL_DATA_PATH = os.path.join(DATA_DIR, 'wuhan_stations_by_route.xlsx')
RAILWAY_STATION_PATH = os.path.join(DATA_DIR, 'wuhan_railway_stations.shp')
RAILWAY_LINE_PATH = os.path.join(DATA_DIR, 'wuhan_railway_lines.shp')
FERRY_WHARF_PATH = os.path.join(DATA_DIR, 'wuhan_ferry_wharves.shp')
METRO_STATION_PATH = os.path.join(DATA_DIR, 'wuhan_metro_stations.shp')
METRO_LINE_PATH = os.path.join(DATA_DIR, 'wuhan_metro_lines.shp')
BUS_STATION_PATH = os.path.join(DATA_DIR, 'wuhan_bus_stations.shp')
BUS_LINE_PATH = os.path.join(DATA_DIR, 'wuhan_bus_lines.shp')

CENTRAL_DISTRICTS = ['Jiangan', 'Jianghan', 'Qiaokou', 'Hanyang', 'Wuchang', 'Qingshan', 'Hongshan']
DPI = 300
STYLES = {
    'central_facecolor': '#e9e9e9', 'non_central_facecolor': 'white',
    'city_outline': {'edgecolor': 'black', 'linewidth': 3.0},
    'district_lines': {'edgecolor': 'gray', 'linewidth': 2.5},
    'railway': {'line_color': '#ff7f0e', 'line_width': 2.5, 'label': 'Railway Line'},
    'ferry': {'line_color': '#2ca02c', 'line_width': 3, 'label': 'Ferry Line'},
    'metro': {'line_color': '#d62728', 'line_width': 3, 'label': 'Metro Line'},
    'bus': {'line_color': '#1f77b4', 'line_width': 1, 'label': 'Bus Line'}
}

# --- Core Change 1: Define a unified font style ---
def set_unified_font(font_name='Times New Roman'):
    """Sets a unified font style"""
    try:
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = font_name
        fig_test = plt.figure(figsize=(0.1, 0.1)); plt.text(0, 0, "Test"); plt.close(fig_test)
    except Exception:
        print(f"Warning: Font '{font_name}' not found, falling back to default serif font.")
        plt.rcParams['font.family'] = 'serif'

# --- Data processing functions (kept as is) ---
def get_railway_data(station_path, line_path, boundary_gdf):
    print("   -> Processing railway data...")
    target_crs = boundary_gdf.crs
    try:
        stations_df = pd.read_excel(EXCEL_DATA_PATH, sheet_name='railway')
        stations_to_keep = stations_df['Name'].tolist()
    except Exception as e:
        print(f"      - Failed to read railway Excel, using default station list: {e}")
        stations_to_keep = ['武汉站', '武昌站', '汉口站', '汤逊湖站', '南湖东站', '纸坊东站', '庙山站', '山坡东站', '天河机场站', '武汉东站']
    stations_gdf = gpd.read_file(station_path, encoding='utf-8').to_crs(target_crs)
    lines_gdf = gpd.read_file(line_path, encoding='utf-8').to_crs(target_crs)
    selected_stations = stations_gdf[stations_gdf['name'].isin(stations_to_keep)].copy()
    wuhan_lines_clipped = gpd.clip(lines_gdf, boundary_gdf)
    lines_to_keep = ['汉十高速铁路', '京广', '京广高速铁路', '武昌南', '武九', '武咸城际铁路']
    selected_lines = wuhan_lines_clipped[wuhan_lines_clipped['NAME'].isin(lines_to_keep)]
    return selected_stations, selected_lines

def get_ferry_data(wharf_path, target_crs):
    print("   -> Processing ferry data...")
    try:
        ferry_df = pd.read_excel(EXCEL_DATA_PATH, sheet_name='ferry')
        ferry_routes_definition = {}
        for line_code in ferry_df['Line Code'].unique():
            line_stations = ferry_df[ferry_df['Line Code'] == line_code].sort_values('Sequence')
            ferry_routes_definition[line_code] = line_stations['Name'].tolist()
    except Exception as e:
        print(f"      - Failed to read ferry Excel, using default routes: {e}")
        ferry_routes_definition = {"武中线": ["武汉关码头(轮渡站)", "武汉轮渡黄鹤楼码头(临江大道)"], "集汉线": ["武汉轮渡集家嘴码头", "武汉关码头(轮渡站)"]}
    all_wharfs = gpd.read_file(wharf_path, encoding='utf-8').to_crs(target_crs)
    passenger_ferries = all_wharfs[all_wharfs['行业小'] == '人渡口']
    core_station_names = set(st for stations in ferry_routes_definition.values() for st in stations)
    route_lines_geom = []
    for r, s in ferry_routes_definition.items():
        points = [pt.geometry.iloc[0] for st in s if not (pt := passenger_ferries[passenger_ferries['name'] == st]).empty]
        if len(points) >= 2:
            route_lines_geom.append(LineString(points))
    lines_gdf = gpd.GeoDataFrame(geometry=route_lines_geom, crs=target_crs)
    stations_gdf = passenger_ferries[passenger_ferries['name'].isin(core_station_names)]
    return stations_gdf, lines_gdf

def get_metro_data(station_path, line_path, target_crs):
    print("   -> Processing metro data...")
    try:
        metro_df = pd.read_excel(EXCEL_DATA_PATH, sheet_name='metro')
        all_stations = gpd.read_file(station_path).to_crs(target_crs)
        all_lines = gpd.read_file(line_path).to_crs(target_crs)
        excluded_lines = ["地铁7号线北延线二期(横店-黄陂广场)", "地铁12号线武昌段(钢都花园-罗家村)", "地铁12号线江北段(钢都花园-罗家村)", "地铁12号线江北段(罗家村-钢都花园)", "地铁21号线(阳逻线)二期(中一路-后湖", "地铁11号线二期(武昌站东广场-武汉东", "地铁11号线二期(武汉东站-武昌站东广", "地铁11号线三期新汉阳火车站段(武汉", "地铁11号线三期新汉阳火车站段(黄金", "地铁7号线北延线一期(横店-园博园北)", "地铁10号线一期(武汉商务区-北洋桥)", "地铁10号线一期(北洋桥-武汉商务区)", "地铁10号线新港线一期(白玉山-北洋桥)", "地铁11号线四期(江安路-武汉西站)", "地铁10号线新港线一期(北洋桥-白玉山)", "地铁7号线北延线二期(黄陂广场-横店)", "地铁21号线(阳逻线)二期(后湖大道-中", "地铁12号线武昌段(罗家村-钢都花园)", "地铁11号线四期(武汉西站-江安路)", "地铁11号线三期(首开段)(武昌站东广场", "地铁11号线三期(首开段)(江安路-武昌"]
        line_name_field = next((f for f in ['LineName', 'name', 'NAME', '线路名称'] if f in all_lines.columns), None)
        if line_name_field:
            filtered_lines = all_lines[~all_lines[line_name_field].isin(set(excluded_lines))]
        else:
            filtered_lines = all_lines
        station_name_field = next(c for c in ['PointName', '站名', 'name', 'STATION'] if c in all_stations.columns)
        stations_gdf = all_stations[all_stations[station_name_field].isin(metro_df['Name'].unique())]
        return stations_gdf, filtered_lines
    except Exception as e:
        print(f"      - Error processing metro data, returning raw data: {e}")
        return gpd.read_file(station_path).to_crs(target_crs), gpd.read_file(line_path).to_crs(target_crs)

def get_bus_data(station_path, line_path, target_crs):
    print("   -> Processing bus data...")
    stations_gdf = gpd.read_file(station_path).to_crs(target_crs)
    lines_gdf = gpd.read_file(line_path).to_crs(target_crs)
    return stations_gdf, lines_gdf

def main():
    set_unified_font() # --- Core Change 2: Call the font setting function ---
    print("--- Starting generation of MPTN integrated map (unified font) ---")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    wuhan_boundary = gpd.read_file(BOUNDARY_PATH, encoding='utf-8')
    wuhan_boundary = wuhan_boundary[wuhan_boundary['地名'] == '武汉市']
    target_crs = wuhan_boundary.crs
    district_boundaries = gpd.read_file(DISTRICT_BOUNDARY_PATH, encoding='utf-8').to_crs(target_crs)
    railway_stations, railway_lines = get_railway_data(RAILWAY_STATION_PATH, RAILWAY_LINE_PATH, wuhan_boundary)
    ferry_stations, ferry_lines = get_ferry_data(FERRY_WHARF_PATH, target_crs)
    metro_stations, metro_lines = get_metro_data(METRO_STATION_PATH, METRO_LINE_PATH, target_crs)
    bus_stations, bus_lines = get_bus_data(BUS_STATION_PATH, BUS_LINE_PATH, target_crs)
    bus_lines_clipped = gpd.clip(bus_lines, wuhan_boundary)
    fill_colors = [STYLES['central_facecolor'] if district in CENTRAL_DISTRICTS else STYLES['non_central_facecolor'] for district in district_boundaries['ENG_NAME']]
    fig, ax = plt.subplots(1, 1, figsize=(20, 20))
    district_boundaries.plot(ax=ax, facecolor=fill_colors, edgecolor=STYLES['district_lines']['edgecolor'], linewidth=STYLES['district_lines']['linewidth'], zorder=1)
    wuhan_boundary.plot(ax=ax, facecolor='none', edgecolor=STYLES['city_outline']['edgecolor'], linewidth=STYLES['city_outline']['linewidth'], zorder=2)
    bus_lines_clipped.plot(ax=ax, color=STYLES['bus']['line_color'], linewidth=STYLES['bus']['line_width'], label=STYLES['bus']['label'], zorder=3)
    metro_lines.plot(ax=ax, color=STYLES['metro']['line_color'], linewidth=STYLES['metro']['line_width'], label=STYLES['metro']['label'], zorder=4)
    ferry_lines.plot(ax=ax, color=STYLES['ferry']['line_color'], linewidth=STYLES['ferry']['line_width'], label=STYLES['ferry']['label'], zorder=5)
    railway_lines.plot(ax=ax, color=STYLES['railway']['line_color'], linewidth=STYLES['railway']['line_width'], label=STYLES['railway']['label'], zorder=6)
    ax.set_axis_off()
    ax.legend(loc='upper right', fontsize=25, frameon=False)
    plt.tight_layout()
    output_filename = 'Spatial distribution of the MPTN in Wuhan.pdf'
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    print(f"\n🎉 MPTN integrated map successfully saved to: {output_path}")
    plt.show()

if __name__ == '__main__':
    main()
