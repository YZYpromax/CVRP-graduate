# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 21:32:20 2025

@author: YZY
"""
import math
import pandas as pd

# ———— 1. 两种解析器分别设置 is_geographical ————
def parse_cvrp_vrp(file_path):
    """原来的 VRP 格式解析（.vrp 文件）"""
    nodes = {}
    demands = {}
    capacity = 0
    depot_id = None
    reading_nodes = False
    reading_demands = False
    reading_depot = False

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('CAPACITY'):
                capacity = int(line.split(':')[1].strip())
            elif line.startswith('NODE_COORD_SECTION'):
                reading_nodes = True; reading_demands = False; reading_depot = False
                continue
            elif line.startswith('DEMAND_SECTION'):
                reading_demands = True; reading_nodes = False; reading_depot = False
                continue
            elif line.startswith('DEPOT_SECTION'):
                reading_depot = True; reading_nodes = False; reading_demands = False
                continue
            elif line == 'EOF':
                break

            if reading_nodes:
                parts = line.split()
                nid = int(parts[0]); x, y = float(parts[1]), float(parts[2])
                nodes[nid] = (x, y)
            elif reading_demands:
                parts = line.split()
                nid = int(parts[0]); demands[nid] = float(parts[1])
            elif reading_depot:
                if line == '-1': break
                depot_id = int(line)

    # 筛出客户
    customers = [nid for nid in nodes if nid != depot_id and demands.get(nid, 0) > 0]
    sorted_cust = sorted(customers)
    id_to_index = {nid: i+1 for i, nid in enumerate(sorted_cust)}
    print(id_to_index)
    print(customers)
    return {
        'capacity': capacity,
        'depot': nodes[depot_id],
        'customers': sorted_cust,
        'coordinates': {nid: nodes[nid] for nid in sorted_cust},
        'demands': {nid: demands[nid] for nid in sorted_cust},
        'id_to_index': id_to_index,
        'is_geographical': False
    }
def parse_cvrp_excel(file_path, sheet_name=0, depot_id=None):
    """
    从 Excel 读取 CVRP 数据。
    假设表里至少有列 ['id','x','y','demand','capacity']，
    其中 x=经度，y=纬度。
    
    参数:
      - file_path: Excel 文件路径
      - sheet_name: 要读取的 sheet（名字或索引）
      - depot_id: （可选）直接告诉函数哪个 id 是 depot；
                  如果不传，就沿用“capacity 列非空那一行”。
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # 强制把经度／纬度列重命名，确保 x=lon, y=lat
    df = df.rename(columns={'x':'lon','y':'lat'})

    # 如果调用者没给 depot_id，就用 capacity 不为空的那个 row
    if depot_id is None:
        depots = df[df['capacity'].notna()]
        if len(depots) != 1:
            raise ValueError(f"找到 {len(depots)} 条 capacity 非空记录，无法唯一定位 depot，请传入 depot_id")
        depot_row = depots.iloc[0]
        depot_id = int(depot_row['id'])
    else:
        # 找到这行确认一下
        depot_row = df[df['id']==depot_id]
        if depot_row.empty:
            raise KeyError(f"你指定的 depot_id={depot_id} 不在表中")
        depot_row = depot_row.iloc[0]

    # 车辆容量
    capacity = float(depot_row['capacity'])

    # 构造 coords 和 demands
    coords = {int(r['id']): (float(r['lon']), float(r['lat']))  # 注意顺序 ( lon,lat)
              for _, r in df.iterrows()}
    demands = {int(r['id']): float(r['demand']) for _, r in df.iterrows()}

    # 筛出客户：去除 depot，且需求>0
    customers = [nid for nid,d in demands.items() if nid!=depot_id and d>0]
    customers.sort()
    id_to_index = {nid:i+1 for i,nid in enumerate(customers)}

    return {
        'capacity': capacity,
        'depot': coords[depot_id],          # (lat, lon)
        'customers': customers,
        'coordinates': {nid: coords[nid] for nid in customers},
        'demands': {nid: demands[nid] for nid in customers},
        'id_to_index': id_to_index,
        'is_geographical': True
    }

def haversine(p1, p2):
    R = 6378137
    lon1, lat1 = p1;  lon2, lat2 = p2
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = φ2 - φ1
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(Δλ/2)**2
    return int(round(2 * R * math.asin(math.sqrt(a))))#地球并非完美的球形  大多数精确到迷已经够用，保留小数意义有限

def euclidean(p1, p2):
    x1, y1 = p1; x2, y2 = p2
    return int(round(math.hypot(x1-x2, y1-y2)))

def compute_distance_matrix(data):
    depot = data['depot']
    custs = data['customers']
    coords = data['coordinates']
    geo = data.get('is_geographical', False)

    nodes = [depot] + [coords[c] for c in custs]
    n = len(nodes)
    dist = [[0]*n for _ in range(n)]
    func = haversine if geo else euclidean

    for i in range(n):
        for j in range(n):
            if i!=j:
                dist[i][j] = func(nodes[i], nodes[j])

    data['distance_matrix'] = dist
    return data

def parse_cvrp(file_path, **kwargs):
    if file_path.lower().endswith(('.xlsx','.xls')):
        return parse_cvrp_excel(file_path, **kwargs)
    else:
        return parse_cvrp_vrp(file_path)   
