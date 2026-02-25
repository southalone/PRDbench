#!/usr/bin/env python3
"""
生成雷达图测试脚本
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from math import pi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def generate_radar():
    """生成技能得分雷达图"""
    try:
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 技能维度和数据
        skills = ['领导与激励', '计划组织', '决策创新', '专业控制']
        
        # 不同管理层级的平均得分
        junior_scores = [3.2, 3.4, 3.1, 3.3]
        middle_scores = [3.9, 4.0, 3.8, 4.1]
        senior_scores = [4.5, 4.4, 4.3, 4.6]
        
        # 计算角度
        angles = [n / float(len(skills)) * 2 * pi for n in range(len(skills))]
        angles += angles[:1]  # 闭合图形
        
        # 创建雷达图
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # 绘制三个层级的雷达图
        datasets = [
            (junior_scores, '初级管理者', 'blue', 'o'),
            (middle_scores, '中级管理者', 'green', 's'),
            (senior_scores, '高级管理者', 'red', '^')
        ]
        
        for scores, label, color, marker in datasets:
            # 闭合数据
            scores_closed = scores + scores[:1]
            
            # 绘制雷达图
            ax.plot(angles, scores_closed, 'o-', linewidth=2, label=label, 
                   color=color, marker=marker, markersize=8)
            ax.fill(angles, scores_closed, alpha=0.25, color=color)
        
        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(skills, fontsize=12)
        
        # 设置y轴范围和标签
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=10)
        ax.grid(True)
        
        # 添加标题和图例
        plt.title('管理技能雷达图对比\n(按管理层级)', size=16, fontweight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        
        # 保存图表
        output_path = 'evaluation/test_radar.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 雷达图已生成: {output_path}")
        
        # 验证文件是否存在
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   文件大小: {file_size} bytes")
            
            # 验证数据合理性
            print("   数据验证:")
            for i, skill in enumerate(skills):
                junior_score = junior_scores[i]
                middle_score = middle_scores[i]
                senior_score = senior_scores[i]
                
                print(f"   {skill}: 初级({junior_score}) < 中级({middle_score}) < 高级({senior_score})")
                
                # 验证层级间的得分递增趋势
                assert junior_score < middle_score < senior_score
                assert 1 <= junior_score <= 5
                assert 1 <= middle_score <= 5
                assert 1 <= senior_score <= 5
            
            return True
        else:
            print("❌ 雷达图生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 生成雷达图时出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = generate_radar()
    sys.exit(0 if success else 1)