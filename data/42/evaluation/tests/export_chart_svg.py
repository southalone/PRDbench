#!/usr/bin/env python3
"""
测试SVG格式图表导出功能
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from math import pi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def export_chart_svg():
    """导出SVG格式图表"""
    try:
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 模拟技能得分数据
        skills = ['领导与激励', '计划组织', '决策创新', '专业控制']
        scores = [4.2, 3.9, 4.1, 4.0]
        
        # 计算雷达图角度
        angles = [n / float(len(skills)) * 2 * pi for n in range(len(skills))]
        angles += angles[:1]  # 闭合图形
        scores_closed = scores + scores[:1]  # 闭合数据
        
        # 创建雷达图
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # 绘制雷达图
        ax.plot(angles, scores_closed, 'o-', linewidth=3, label='技能得分', 
               color='#FF6B6B', marker='o', markersize=10)
        ax.fill(angles, scores_closed, alpha=0.25, color='#FF6B6B')
        
        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(skills, fontsize=12)
        
        # 设置y轴范围和标签
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=10)
        ax.grid(True)
        
        # 添加数值标签
        for angle, score, skill in zip(angles[:-1], scores, skills):
            ax.text(angle, score + 0.1, f'{score:.1f}', 
                   horizontalalignment='center', fontweight='bold')
        
        # 添加标题
        plt.title('管理技能雷达图', size=16, fontweight='bold', pad=30)
        
        # 保存为SVG格式
        output_path = 'evaluation/test_chart.svg'
        plt.savefig(output_path, format='svg', bbox_inches='tight')
        plt.close()
        
        print(f"✅ SVG格式图表已导出: {output_path}")
        
        # 验证文件是否存在且格式正确
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   文件大小: {file_size} bytes")
            
            # 检查文件扩展名
            assert output_path.endswith('.svg')
            
            # 检查文件不为空
            assert file_size > 0
            
            # 验证SVG文件内容（简单检查）
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '<svg' in content  # SVG文件应包含svg标签
                assert '</svg>' in content
                assert 'polygon' in content or 'path' in content  # 应包含图形元素
            
            print("   SVG文件验证通过")
            return True
        else:
            print("❌ SVG文件生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 导出SVG图表时出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = export_chart_svg()
    sys.exit(0 if success else 1)