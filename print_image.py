# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 21:42:56 2025

@author: YZY
"""

from ga1 import GeneticAlgorithm
from aco1 import ACO
from pso1 import PSO
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from datetime import datetime
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
# ====================== 核心函数 ======================
def run_algorithm(data, algo_name, run_times=1):
    """运行指定算法多次并收集结果"""
    results = {
        'dists': [],        # 每次运行的最优距离
        'times': [],        # 每次运行的耗时
        'histories': [],    # 每次运行的收敛历史
        'individuals': []   # 每次运行的最佳个体
    }
    
    config = ALGO_CONFIG[algo_name]
    for _ in range(run_times):
        # 初始化算法
        solver = config['class'](data, **config['params'])
        
        # 运行计时
        start_time = time.time()
        best_ind, best_dist = solver.run()
        elapsed = time.time() - start_time
        
        # 记录结果
        results['dists'].append(best_dist)
        results['times'].append(elapsed)
        results['histories'].append(solver.history)
        results['individuals'].append(best_ind)
    
    return results

def print_statistics(algo_name, results):
    """打印算法统计信息并返回统计字典"""
    dists = results['dists']
    times = results['times']
    
    stats = {
        '算法': algo_name,
        '运行次数': len(dists),
        '最优距离': np.min(dists),
        '最差距离': np.max(dists),
        '平均距离': np.mean(dists),
        '标准差': np.std(dists),
        '平均耗时(s)': np.mean(times)
    }
    
    print(f"\n=== {algo_name} 算法统计 ===")
    print(f"运行次数: {stats['运行次数']}")
    print(f"最优距离: {stats['最优距离']:.2f}")
    print(f"最差距离: {stats['最差距离']:.2f}")
    print(f"平均距离: {stats['平均距离']:.2f} ± {stats['标准差']:.2f}")
    print(f"平均耗时: {stats['平均耗时(s)']:.2f}s")
    
    return stats

def plot_best_convergence(results_dict):
    """绘制各算法最佳运行的收敛曲线"""
    plt.figure(figsize=(12, 6))
    
    for algo_name, results in results_dict.items():
        best_idx = np.argmin(results['dists'])
        best_history = results['histories'][best_idx]
        
        plt.plot(best_history, 
                linewidth=2,
                label=f"{algo_name} (Best: {results['dists'][best_idx]:.2f})")  # 修正括号
    
    plt.title("Convergence Comparison of Best Runs", fontsize=14)
    plt.xlabel("Iteration", fontsize=12)
    plt.ylabel("Distance", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
def save_to_excel(statistics, input_file_path):
    """保存统计结果到Excel（新增创建结果文件夹功能）"""
    # 创建结果文件夹
    base_dir = os.path.dirname(input_file_path)  # 获取输入文件所在目录
    result_dir = os.path.join(base_dir, "计算结果")  # 创建结果文件夹名称
    
    # 自动创建文件夹（如果不存在）
    os.makedirs(result_dir, exist_ok=True)  # exist_ok=True 如果文件夹存在不会报错

    # 生成带时间戳的文件名
    base_name = os.path.basename(input_file_path)
    file_name = f"{os.path.splitext(base_name)[0]}_结果_{datetime.now().strftime('%Y%m%d%H%M')}.xlsx"
    
    # 完整保存路径
    save_path = os.path.join(result_dir, file_name)

    # 转换数据格式
    df = pd.DataFrame.from_dict(statistics, orient='index').reset_index(drop=True)
    
    # 确保列存在（防止KeyError）
    expected_columns = ['算法', '运行次数', '最优距离', '最差距离', '平均距离', '标准差', '平均耗时(s)']
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    # 格式化数值
    with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        
    print(f"\n✅ 统计结果已保存到：\n{os.path.abspath(save_path)}")