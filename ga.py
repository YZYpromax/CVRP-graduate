# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 16:35:14 2025

@author: YZY
"""
import random
import math
import time

class GA:
    def __init__(self, data, 
                 population_size=50, 
                 crossover_rate=0.8, 
                 mutation_rate=0.1, 
                 max_iter=100,
                 tournament_size=2):
        """
        self可理解为当前实例的代表意义sample
        参数说明：
        - data: 预处理后的数据字典
        - population_size: 种群规模
        - crossover_rate: 交叉概率
        - mutation_rate: 变异概率
        - max_iter: 最大迭代次数
        - tournament_size: 锦标赛选择的参赛者数量
        """
        self.data = data  #实例的属性
        self.population_size = population_size  #决定生成个体的个数
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.max_iter = max_iter
        self.tournament_size = tournament_size
        self.history=[]
    def generate_individual(self):#方法
        """生成随机个体（客户排列）"""
        customers = self.data['customers'].copy()#先保留原始数据
        random.shuffle(customers)#打乱列表中的数据序列
        return customers

    def generate_population(self):
        """初始化种群
            [
        [元素1, 元素2, ...],  # 第1个个体
        [元素1, 元素2, ...],  # 第2个个体
        ...
            ]
        """
        return [self.generate_individual() for _ in range(self.population_size)]

    def calculate_total_distance(self, individual):
        """计算个体对应的总行驶距离"""
        total_distance = 0
        current_load = 0
        prev_index = 0  # 仓库索引
        capacity = self.data['capacity']
        demands = self.data['demands']
        distance_matrix = self.data['distance_matrix']
        id_to_index = self.data['id_to_index']

        for customer in individual:#遍历个体中的每一个元素 即 当前序列中的客户点
            demand = demands[customer]
            if current_load + demand > capacity:
                # 返回仓库并开始新路线
                total_distance += distance_matrix[prev_index][0]  # 返回仓库  仓库的索引为0
                total_distance += distance_matrix[0][id_to_index[customer]]  # 新路线出发
                current_load = demand
                prev_index = id_to_index[customer]
            else:
                total_distance += distance_matrix[prev_index][id_to_index[customer]]
                current_load += demand
                prev_index = id_to_index[customer]
        # 最后返回仓库
        total_distance += distance_matrix[prev_index][0]
        return total_distance

    def fitness(self, individual):
        """适应度函数（距离倒数）"""
        return 1 / self.calculate_total_distance(individual)

    def selection(self, population, fitnesses):
        """锦标赛选择：数据合并加选择"""
        selected = []
        for _ in range(self.population_size):
            # 随机选择k个参赛者
            contestants = random.sample(list(zip(population, fitnesses)), 
                                      self.tournament_size)
            # zip将种群中的每个个体与其对应的适应度值组合成元组
            # 例如，若 population = [ind1, ind2, ...] 且 fitnesses = [fit1, fit2, ...]，
            # 则结果为 [(ind1, fit1), (ind2, fit2), ...]
            # 选择适应度最高的个体
            winner = max(contestants, key=lambda x: x[1])[0]
            # 其中参数和结果之间用冒号隔开，冒号前为参数(arg)，冒号后为具体表达(expression)。
            # 根据实际情况，冒号前的参数可以有多个。
            # 匿名表达式lambda arg1,arg2...argn:expression 
            # contestants元组元素中的第一个值  此处为顾客编号 
            selected.append(winner)
        return selected

    def crossover(self, parent1, parent2):
        """顺序交叉（OX）"""
        if random.random() < self.crossover_rate:
            size = len(parent1)
            start, end = sorted(random.sample(range(size), 2))#确保start<end
            child1 = parent1[start:end+1]#切片操作 [start:end] 是左闭右开区间
            child2 = parent2[start:end+1]#end+1确保截取s到e的片段
            
            # 填充剩余基因到子代末尾
            for gene in parent2:#根据循环变量gene 遍历取parents的值
                if gene not in child1:#直接not in对比
                    child1.append(gene)
            for gene in parent1:
                if gene not in child2:
                    child2.append(gene)
            return child1, child2
        else:
            return parent1.copy(), parent2.copy()

    def mutate(self, individual):
        """交换变异"""
        if random.random() < self.mutation_rate:
            idx1, idx2 = random.sample(range(len(individual)), 2)
            individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
        return individual

    def run(self,time_limit=None):
        """执行遗传算法优化"""
        population = self.generate_population()#初始化  
        best_individual = None
        best_fitness = 0
        best_iter = 0
        start_time = time.time()
        for generation in range(self.max_iter):
            # 计算适应度
            if time_limit and(time.time()-start_time>time_limit):
                print(f"已运行{generation+1}代")
                break
            fitnesses = [self.fitness(ind) for ind in population]#individual
            
            # 更新最佳个体
            current_best = max(fitnesses)
            if current_best > best_fitness:
                best_fitness = current_best
                best_individual = population[fitnesses.index(current_best)]
                best_iter = generation + 1
            # 选择
            selected = self.selection(population, fitnesses)
            
            # 交叉和变异
            next_population = []
            for i in range(0, self.population_size, 2):#左闭右开 0-size-1 步长为2遍历0，2...
                # 选择双亲
                p1 = selected[i]
                p2 = selected[i+1] if i+1 < len(selected) else selected[i]#p1=p2
                
                # 交叉
                c1, c2 = self.crossover(p1, p2)
                
                # 变异
                c1 = self.mutate(c1)
                c2 = self.mutate(c2)
                
                next_population.extend([c1, c2])#将c1 c2元素添加到列表末尾
            
            # 保留精英
            next_population = next_population[:self.population_size]#list[:n]返回列表的前n个元素
            next_fitness = [self.fitness(ind) for ind in next_population]
            min_idx = next_fitness.index(min(next_fitness))
            next_population[min_idx] = best_individual#用当代的最优值替换下一代的最小值
            population = next_population
        
            print(f"Generation {generation+1}: Best Distance = {1/best_fitness:.2f}")
            self.history.append(1 / best_fitness)
        return best_individual, 1 / best_fitness,best_iter