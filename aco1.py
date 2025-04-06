# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 16:35:15 2025

@author: YZY
"""
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 15:35:18 2025

@author: YZY
"""
# ------------ aco.py ------------
import random
import math
class ACO:
    def __init__(self, data, 
                 num_ants=20, 
                 evaporation_rate=0.5,
                 alpha=1.0,
                 beta=2.0,
                 Q=100.0,  # 新增信息素强度参数
                 max_iter=100,):  
        self.data = data
        self.num_ants = num_ants
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.Q = Q  # 信息素强度参数
        self.max_iter = max_iter
        # 优化后的信息素初始化
        self._initialize_pheromone_matrix()
        self.history = []
    def _initialize_pheromone_matrix(self):
        """基于平均距离的经验公式初始化"""
        distance_matrix = self.data['distance_matrix']
        n = len(distance_matrix)
        
        # 计算有效平均距离
        total = 0.0
        count = 0
        for i in range(n):
            for j in range(n):
                if i != j and distance_matrix[i][j] > 1e-6:  # 排除对角线和零距离
                    total += distance_matrix[i][j]#将所有有效边累加
                    count += 1#对有效边进行计数
        avg_distance = total / count if count > 0 else 1.0#否则置1

        # 计算路径初始信息素值 τ0 = 1 / (n * avg_distance)
        self.num_nodes = n
        tau0 = 1 / (n * avg_distance)
# [
#     [tau0 if i != j else 0.0 for j in range(n)]
#     for i in range(n)
# ] 
        # 初始化信息素矩阵（对角线设为0）
        self.pheromone = []  # 初始化空矩阵
        for i in range(n):   # 遍历每一行
            row = []          # 初始化当前行
            for j in range(n):  # 遍历当前行的每一列
                if i != j:
                    row.append(tau0)  
                else:
                    row.append(0.0)   
            self.pheromone.append(row)  # 将当前行加入矩阵

    def _construct_solution(self):
        """路径构造（增加鲁棒性处理）"""
        capacity = self.data['capacity']
        demands = self.data['demands']
        unvisited = set(self.data['customers'])  # 使用集合提高查找效率
        distance_matrix = self.data['distance_matrix']
        id_to_index = self.data['id_to_index']

        routes = []
        while unvisited:
            current_load = 0
            route = []
            current_node = 0  # 仓库索引  当前节点 即每个ant从配送中心出发

            while True:
                # 获取可行节点（考虑负载约束）
                feasible = [
                    c for c in unvisited
                    if current_load + demands[c] <= capacity#只存储当前节点+下一个节点需求满足容量的节点
                ]
                if not feasible:
                    break

                # 计算概率分布（带异常处理）
                probabilities = []
                total = 0.0
                for c in feasible:
                    idx = id_to_index[c]
                    try:
                        tau = self.pheromone[current_node][idx]
                        eta = 1 / distance_matrix[current_node][idx]
                        prob = (tau ** self.alpha) * (eta ** self.beta)
                    except ZeroDivisionError:
                        prob = 1e-6  # 处理零距离异常
                    probabilities.append((c, prob))
                    total += prob

                # 处理全零概率情况
                if total < 1e-6:
                    selected = random.choice(feasible)
                else:
                    # 轮盘赌选择优化
                    rand = random.uniform(0, total)
                    cumulative = 0.0
                    for c, prob in probabilities:
                        cumulative += prob
                        if cumulative >= rand:
                            selected = c
                            break

                # 更新状态
                route.append(selected)
                current_load += demands[selected]
                current_node = id_to_index[selected]
                unvisited.remove(selected)#移除禁忌表

            if route:  # 跳过空路径
                routes.append(route)
        return routes

    def _update_pheromone(self, solutions):
        """信息素更新"""
        # 信息素挥发
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                self.pheromone[i][j] *= (1 - self.evaporation_rate)

        # 信息素增强
        for solution, distance in solutions:
            if distance < 1e-6:  # 过滤无效解
                continue
            delta = self.Q / distance  # 使用Q参数
            for route in solution:
                path = [0] + [self.data['id_to_index'][c] for c in route] + [0]
                for i in range(len(path)-1):
                    u, v = path[i], path[i+1]
                    self.pheromone[u][v] += delta

    def _calculate_distance(self, solution):
        """距离计算（优化空路径处理）"""
        total = 0.0
        distance_matrix = self.data['distance_matrix']
        id_to_index = self.data['id_to_index']
        
        for route in solution:
            if not route:  # 跳过空路径
                continue
            path = [0] + [id_to_index[c] for c in route] + [0]
            for i in range(len(path)-1):
                total += distance_matrix[path[i]][path[i+1]]
        return total

    def run(self):
        """执行优化"""
        best_solution = None
        best_distance = float('inf')
        for iter_num in range(self.max_iter):
            solutions = []
            for _ in range(self.num_ants):
                solution = self._construct_solution()
                distance = self._calculate_distance(solution)
                solutions.append((solution, distance))
                
                # 更新全局最优
                if distance < best_distance:
                    best_solution = solution
                    best_distance = distance

            # 信息素更新策略
                self._update_pheromone(solutions)

            # 进度输出
            print(f"Iteration {iter_num+1:03d} :Best Distance: {best_distance:.2f}")
            self.history.append(best_distance)
        # 结果格式化（保留路径结构）
        individual = []
        for route in best_solution:
            individual.extend(route)
        
        return individual, best_distance