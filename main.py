# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 16:35:14 2025

@author: YZY
"""
#from preprocess1 import parse_cvrp_file, compute_distance_matrix
from new_preprocess import parse_cvrp,compute_distance_matrix
from ga import GA
from aco import ACO
from pso import PSO
from draw_picture import plot_routes
import numpy as np
from print_image import run_algorithm, print_statistics, plot_best_convergence, save_to_excel
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
# ====================== 算法配置 ======================
ALGO_CONFIG = {
    'GA': {
        'class': GA,
        'params': {
            'population_size': 120,#125   B 78 10： 144   
            'crossover_rate': 0.85,#0.9  0.95| 0.71
            'mutation_rate': 0.15,#0.2       | 0.22
            'max_iter': 1000,#        |
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
            'max_iter': 500
        }
    },
    'PSO': {
        'class': PSO,
        'params': {
            'num_particles': 86,
            'w': 0.66,
            'c1': 2.28,
            'c2': 1.34,
            'max_iter': 100
        }
    }
}
# ====================== 主程序 ======================
def main():
    # 数据准备
    input_file = r"C:\Users\YZY\Desktop\毕业论文\苏宁数据整合_merged.xlsx"
    #"C:\Users\YZY\Desktop\毕业论文\苏宁数据.xlsx"
    data = parse_cvrp(input_file)
    data = compute_distance_matrix(data)
    
    # 实验参数
    run_mode = 'single' 
    time_limit = int(input("请输入时间限制（秒，0表示无限制）: ") or 0)
    RUN_TIMES = 1  # 每个算法运行次数
    SELECTED_ALGOS = ['GA', 'ACO', 'PSO']  # 要对比的算法
    statistics = {}  # 用于收集统计信息
    if run_mode == 'single':
    # 单算法模式
        algo_name = 'GA'
        results = run_algorithm(data, algo_name,RUN_TIMES,time_limit=time_limit if time_limit>0 else None)
        # 处理统计信息
        stats = print_statistics(algo_name, results)
        statistics[algo_name] = stats
        best_idx = np.argmin(results['dists'])
        plot_routes(data, results['individuals'][best_idx], results['dists'][0])
        # 可视化增强
        plt.figure(figsize=(10, 6),dpi=200)
        plt.plot(results['histories'][0])#, label=f'{algo_name}收敛曲线'
        if results['early_stop'][0]:
            stop_iter = len(results['histories'][0])
        plt.title(f'{algo_name}在规定运行时间内收敛曲线', 
                 fontsize=14, pad=20)
        plt.xlabel("迭代次数", fontsize=12)
        plt.ylabel("路径距离", fontsize=12)
        plt.show()
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