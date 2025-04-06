# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 16:35:14 2025

@author: YZY
"""
from preprocess1 import parse_cvrp_file, compute_distance_matrix
from ga1 import GeneticAlgorithm
from aco1 import ACO
from pso1 import PSO
from draw_picture import plot_routes
import numpy as np
from print_image import run_algorithm, print_statistics, plot_best_convergence, save_to_excel
# ====================== 算法配置 ======================
ALGO_CONFIG = {
    'GA': {
        'class': GeneticAlgorithm,
        'params': {
            'population_size': 120,
            'crossover_rate': 0.90,
            'mutation_rate': 0.12,
            'max_generations': 6000,
            'tournament_size':5
        }
    },
    'ACO': {
        'class': ACO,
        'params': {
            'num_ants': 82,#82，0.31 0.7 2 1000
            'evaporation_rate': 0.31,
            'alpha': 0.7,
            'beta': 2,
            'Q': 1000,
            'max_iter': 6000
        }
    },
    'PSO': {
        'class': PSO,
        'params': {
            'num_particles': 86,
            'w': 0.66,
            'c1': 2.28,
            'c2': 1.34,
            'max_iter': 6000
        }
    }
}
# ====================== 主程序 ======================
def main():
    # 数据准备
    input_file = r"C:\Users\YZY\Desktop\毕业论文\A-n32-k5.vrp"
    data = parse_cvrp_file(input_file)
    data = compute_distance_matrix(data)
    
    # 实验参数
    run_mode = 'compare' 
    RUN_TIMES = 4            # 每个算法运行次数
    SELECTED_ALGOS = ['GA', 'ACO', 'PSO']  # 要对比的算法
    statistics = {}  # 用于收集统计信息
    if run_mode == 'single':
    # 单算法模式
        algo_name = 'GA'
        results = run_algorithm(data, algo_name,RUN_TIMES)
        # 处理统计信息
        stats = print_statistics(algo_name, results)
        statistics[algo_name] = stats
        best_idx = np.argmin(results['dists'])
        plot_routes(data, results['individuals'][best_idx], results['dists'][0])
        
    elif run_mode == 'compare':
    # 运行所有算法
        results_dict = {}
        for algo_name in SELECTED_ALGOS:
            print(f"\n正在运行 {algo_name}...")
            results = run_algorithm(data, algo_name, 1)
            stats = print_statistics(algo_name, results)
            statistics[algo_name] = stats
            results_dict[algo_name] = results
        
        # 绘制收敛曲线对比
        plot_best_convergence(results_dict)
     # 保存结果到Excel
    save_to_excel(statistics, input_file)
if __name__ == '__main__':
    main()