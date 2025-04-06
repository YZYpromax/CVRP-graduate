# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 16:37:13 2025

@author: YZY
"""
import random
import numpy as np

class PSO:
    def __init__(self, data, 
                 num_particles=30,
                 w=0.8, 
                 c1=1.5, 
                 c2=1.5,
                 max_iter=100):
        self.data = data
        self.num_particles = num_particles
        self.w = w      # 惯性权重
        self.c1 = c1    # 个体学习因子
        self.c2 = c2    # 社会学习因子
        self.max_iter = max_iter
        
        # 问题参数
        self.num_customers = len(data['customers'])
        self.capacity = data['capacity']
        self.demands = data['demands']
        self.distance_matrix = data['distance_matrix']
        self.id_to_index = data['id_to_index']
        
        # 编码参数
        self.position_min = -5   # 位置向量最小值
        self.position_max = 5    # 位置向量最大值
        self.history = []
    def _initialize_particle(self):
        """初始化粒子（连续向量）"""
        position = np.random.uniform(self.position_min, self.position_max, self.num_customers)
        velocity = np.random.uniform(-1, 1, self.num_customers)
        return {
            'position': position,
            'velocity': velocity,
            'best_position': position.copy(),
            'best_score': float('inf')
        }
    
    def _convert_to_route(self, position_vector):
        """将连续向量转换为离散路径"""
        sorted_indices = np.argsort(position_vector)
        return [self.data['customers'][i] for i in sorted_indices]
    
    def _evaluate(self, position_vector):
        route = self._convert_to_route(position_vector)
        total_distance = 0
        prev_index = 0  # 仓库索引
        current_load = 0
        
        for customer in route:
            demand = self.demands[customer]
            customer_index = self.id_to_index[customer]
            
            if current_load + demand > self.capacity:
                # 返回仓库并重新出发
                total_distance += self.distance_matrix[prev_index][0]  # 到仓库
                total_distance += self.distance_matrix[0][customer_index]  # 从仓库到当前客户
                current_load = demand
                prev_index = customer_index
            else:
                total_distance += self.distance_matrix[prev_index][customer_index]
                current_load += demand
                prev_index = customer_index
        
        # 最后返回仓库（无论是否满载）
        total_distance += self.distance_matrix[prev_index][0]
        return total_distance
    
    def _update_velocity(self, particle, gbest_position):
        """速度更新（连续空间）"""
        r1 = np.random.rand(self.num_customers)
        r2 = np.random.rand(self.num_customers)
        new_velocity = (
            self.w * particle['velocity'] +
            self.c1 * r1 * (particle['best_position'] - particle['position']) +
            self.c2 * r2 * (gbest_position - particle['position'])
        )
        return np.clip(new_velocity, -5, 5)
    
    def _update_position(self, position, velocity):
        """位置更新（连续空间）"""
        new_position = position + velocity
        return np.clip(new_position, self.position_min, self.position_max)
    
    def run(self):
        particles = [self._initialize_particle() for _ in range(self.num_particles)]
        gbest_position = None
        gbest_score = float('inf')
        self.history = []
        for iter in range(self.max_iter):
            for p in particles:
                score = self._evaluate(p['position'])
                
                # 更新个体最优
                if score < p['best_score']:
                    p['best_score'] = score
                    p['best_position'] = p['position'].copy()
                
                # 更新全局最优
                if score < gbest_score:
                    gbest_score = score
                    gbest_position = p['position'].copy()
            
            # 更新粒子状态
            for p in particles:
                p['velocity'] = self._update_velocity(p, gbest_position)
                p['position'] = self._update_position(p['position'], p['velocity'])
            self.history.append(gbest_score)
            print(f"Iteration {iter+1}, Best Distance: {gbest_score:.2f}")
        
        # 获取最优解
        best_route = self._convert_to_route(gbest_position)
        
        return best_route, gbest_score