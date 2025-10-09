#!/usr/bin/env python3
"""
测试PNG格式图表导出功能
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def export_chart_png():
    """导出PNG格式图表"""
    try:
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 模拟技能得分数据
        skills = ['领导与激励', '计划组织', '决策创新', '专业控制']
        scores = [4.2, 3.9, 4.1, 4.0]
        
        # 创建柱状图
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(skills, scores, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        
        # 设置图表样式
        ax.set_title('管理技能得分分析', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('技能得分', fontsize=12)
        ax.set_ylim(0, 5)
        
        # 添加数值标签
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                   f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # 添加网格
        ax.grid(True, alpha=0.3, axis='y')
        
        # 设置x轴标签旋转
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # 保存为PNG格式
        output_path = 'evaluation/test_chart.png'
        plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ PNG格式图表已导出: {output_path}")
        
        # 验证文件是否存在且格式正确
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   文件大小: {file_size} bytes")
            
            # 检查文件扩展名
            assert output_path.endswith('.png')
            
            # 检查文件不为空
            assert file_size > 0
            
            print("   文件验证通过")
            return True
        else:
            print("❌ PNG文件生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 导出PNG图表时出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = export_chart_png()
    sys.exit(0 if success else 1)