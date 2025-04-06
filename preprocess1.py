# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 16:35:15 2025

@author: YZY
"""
import math

def parse_cvrp_file(file_path):
#     'capacity': 100,
#     'depot': (10, 20),
#     'customers': [2, 3],
#     'coordinates': {2: (30, 40), 3: (50, 60)},
#     'demands': {2: 30, 3: 10},
#     'id_to_index': {2: 1, 3: 2}
#     ​**capacity**: 车辆的容量（int）。
# ​**depot**: 仓库的坐标（数组）。
# ​**customers**: 客户节点的 ID 列表（list）。
# ​**coordinates**: 客户节点的坐标字典（dict）。
# ​**demands**: 客户节点的需求字典（dict）。
# ​**id_to_index**: 客户节点 ID 到索引的映射字典（dict）

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
                reading_nodes = True
                reading_demands = False
                reading_depot = False
                continue
            elif line.startswith('DEMAND_SECTION'):
                reading_demands = True
                reading_nodes = False
                reading_depot = False
                continue
            elif line.startswith('DEPOT_SECTION'):
                reading_depot = True
                reading_nodes = False
                reading_demands = False
                continue
            elif line == 'EOF':
                break

            if reading_nodes:
                parts = line.split()
                node_id = int(parts[0])
                x, y = float(parts[1]), float(parts[2])
                nodes[node_id] = (x, y)
            elif reading_demands:
                parts = line.split()
                node_id = int(parts[0])
                demand = float(parts[1])
                demands[node_id] = demand
            elif reading_depot:
                if line == '-1':
                    break
                depot_id = int(line)

    # 确定客户列表（排除仓库且需求>0）
    customers = [id for id in nodes if id != depot_id and demands.get(id, 0) > 0]
    sorted_customers = sorted(customers)
    id_to_index = {id: idx+1 for idx, id in enumerate(sorted_customers)}  # 仓库索引为0  逻辑索引 将客户ID从2开始映射为1.2.3
    print(id_to_index)
    print(customers)
    return {
        'capacity': capacity,
        'depot': nodes[depot_id],
        'customers': sorted_customers,
        'coordinates': {id: nodes[id] for id in sorted_customers},
        'demands': {id: demands[id] for id in sorted_customers},
        'id_to_index': id_to_index
    }

def compute_distance_matrix(data):
    depot = data['depot']
    customers = data['customers']
    coordinates = data['coordinates']
    id_to_index = data['id_to_index']

    # 创建包含仓库和客户的节点列表
    nodes = [depot]  # 仓库索引为0
    for cid in customers:
        nodes.append(coordinates[cid])

    # 计算距离矩阵
    num_nodes = len(nodes)
    distance_matrix = [[0]*num_nodes for _ in range(num_nodes)]
    for i in range(num_nodes):
        x1, y1 = nodes[i]
        for j in range(num_nodes):
            if i == j:
                distance_matrix[i][j] = 0
            else:
                x2, y2 = nodes[j]
                distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                distance_matrix[i][j] = int(round(distance))

    data['distance_matrix'] = distance_matrix
    return data