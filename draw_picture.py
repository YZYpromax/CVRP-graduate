# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 14:17:52 2025

@author: YZY
"""
import matplotlib.pyplot as plt


def plot_routes(data, individual, total_distance):
    depot = data['depot']
    coordinates = data['coordinates']
    capacity = data['capacity']
    demands = data['demands']
    id_to_index = data['id_to_index']

    # 解码路线
    routes = []
    loads= []
    current_route = []
    current_load = 0
    for customer in individual:
        demand = demands[customer]
        if current_load + demand > capacity:
            routes.append(current_route)
            loads.append(current_load)
            current_route = [customer]
            current_load = demand
        else:
            current_route.append(customer)
            current_load += demand
            
    if current_route:
        routes.append(current_route)
    route_strings = []  # 存储路线字符串
    
    for i, route in enumerate(routes):
        if not route:
            continue       
       # 生成路线字符串
        path_ids = [1] + [id_to_index[c] for c in route] + [1]
        route_str = "->".join(map(str, path_ids))
        route_strings.append(f"Vehicle {i+1}: {route_str}")
    for rs in route_strings:
           print(rs)   
    for lid in loads:
           print(lid)
        
        
        

    plt.figure(figsize=(12, 10))
    
    # 绘制仓库
    plt.scatter(depot[0], depot[1], color='red', s=300, marker='*', 
                edgecolors='black', zorder=5, label='Depot')
    
    # 颜色配置
    colors = plt.cm.tab10.colors
    route_strings = []  # 存储路线字符串
    
    for i, route in enumerate(routes):
        if not route:
            continue
            
        color = colors[i % len(colors)]
        path_ids = [0] + [id_to_index[c] for c in route] + [0]  # 转换为距离矩阵索引
        path_coords = [depot] + [coordinates[c] for c in route] + [depot]
      
        
        # 转换坐标序列
        x = [p[0] for p in path_coords]
        y = [p[1] for p in path_coords]
        
        # 绘制路线
        plt.plot(x, y, '--', color=color, linewidth=1.5, alpha=0.8)
        plt.scatter(x[1:-1], y[1:-1], color=color, s=100, 
                   edgecolors='black', zorder=4, label=f'Vehicle {i+1}')
        
        #添加方向箭头
        for j in range(len(x)-1):
            dx = x[j+1] - x[j]
            dy = y[j+1] - y[j]
            if dx != 0 or dy != 0:
                plt.arrow(x[j], y[j], dx*0.85, dy*0.85,
                          shape='full', color=color,
                          length_includes_head=True,
                          head_width=0.8, alpha=0.7,
                          zorder=3)

    # 图表装饰
    plt.title(f'CVRP Solution - Total Distance: {total_distance:.2f}', 
             fontsize=14, pad=20)
    plt.xlabel('X Coordinate', fontsize=12)
    plt.ylabel('Y Coordinate', fontsize=12)
    
    # 智能图例处理
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # 自动去重
    plt.legend(by_label.values(), by_label.keys(), 
              loc='upper right', fontsize=9)

    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.show()
# 在main函数中调用
