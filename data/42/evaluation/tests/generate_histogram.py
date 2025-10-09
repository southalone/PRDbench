#!/usr/bin/env python3
"""
生成直方图测试脚本
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def generate_histogram():
    """生成技能得分直方图"""
    try:
        # 模拟技能得分数据
        np.random.seed(42)  # 确保结果可重现
        
        # 生成四个技能维度的得分数据
        leadership_scores = np.random.normal(4.0, 0.6, 100)
        planning_scores = np.random.normal(3.8, 0.5, 100)
        decision_scores = np.random.normal(3.9, 0.7, 100)
        professional_scores = np.random.normal(4.1, 0.4, 100)
        
        # 限制得分在1-5范围内
        leadership_scores = np.clip(leadership_scores, 1, 5)
        planning_scores = np.clip(planning_scores, 1, 5)
        decision_scores = np.clip(decision_scores, 1, 5)
        professional_scores = np.clip(professional_scores, 1, 5)
        
        # 创建2x2子图
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('管理技能得分分布直方图', fontsize=16, fontweight='bold')
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 绘制四个技能维度的直方图
        skills_data = [
            (leadership_scores, '领导与激励技能', 'skyblue'),
            (planning_scores, '计划组织与协调技能', 'lightgreen'),
            (decision_scores, '决策与创新技能', 'orange'),
            (professional_scores, '专业与控制技能', 'pink')
        ]
        
        for i, (scores, title, color) in enumerate(skills_data):
            row = i // 2
            col = i % 2
            
            axes[row, col].hist(scores, bins=20, alpha=0.7, color=color, edgecolor='black')
            axes[row, col].set_title(title, fontweight='bold')
            axes[row, col].set_xlabel('得分')
            axes[row, col].set_ylabel('频数')
            axes[row, col].grid(True, alpha=0.3)
            
            # 添加统计信息
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            axes[row, col].axvline(mean_score, color='red', linestyle='--', 
                                 label=f'均值: {mean_score:.2f}')
            axes[row, col].legend()
        
        plt.tight_layout()
        
        # 保存图表
        output_path = 'evaluation/test_histogram.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 直方图已生成: {output_path}")
        
        # 验证文件是否存在
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   文件大小: {file_size} bytes")
            return True
        else:
            print("❌ 直方图生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 生成直方图时出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = generate_histogram()
    sys.exit(0 if success else 1)