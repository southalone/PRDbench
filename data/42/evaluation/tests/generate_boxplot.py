#!/usr/bin/env python3
"""
生成箱型图测试脚本
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def generate_boxplot():
    """生成技能得分箱型图"""
    try:
        # 模拟不同管理层级的技能得分数据
        np.random.seed(42)  # 确保结果可重现
        
        # 生成不同层级的数据
        junior_data = {
            'leadership': np.random.normal(3.2, 0.4, 30),
            'planning': np.random.normal(3.4, 0.3, 30),
            'decision': np.random.normal(3.1, 0.5, 30),
            'professional': np.random.normal(3.3, 0.4, 30)
        }
        
        middle_data = {
            'leadership': np.random.normal(3.9, 0.3, 25),
            'planning': np.random.normal(4.0, 0.4, 25),
            'decision': np.random.normal(3.8, 0.3, 25),
            'professional': np.random.normal(4.1, 0.3, 25)
        }
        
        senior_data = {
            'leadership': np.random.normal(4.5, 0.3, 20),
            'planning': np.random.normal(4.4, 0.2, 20),
            'decision': np.random.normal(4.3, 0.4, 20),
            'professional': np.random.normal(4.6, 0.2, 20)
        }
        
        # 限制得分在1-5范围内
        for data_dict in [junior_data, middle_data, senior_data]:
            for skill in data_dict:
                data_dict[skill] = np.clip(data_dict[skill], 1, 5)
        
        # 创建箱型图
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('不同管理层级技能得分箱型图对比', fontsize=16, fontweight='bold')
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 技能维度信息
        skills_info = [
            ('leadership', '领导与激励技能'),
            ('planning', '计划组织与协调技能'),
            ('decision', '决策与创新技能'),
            ('professional', '专业与控制技能')
        ]
        
        # 绘制每个技能维度的箱型图
        for i, (skill_key, skill_name) in enumerate(skills_info):
            row = i // 2
            col = i % 2
            
            # 准备数据
            data_to_plot = [
                junior_data[skill_key],
                middle_data[skill_key],
                senior_data[skill_key]
            ]
            
            # 绘制箱型图
            box_plot = axes[row, col].boxplot(data_to_plot, 
                                            labels=['初级', '中级', '高级'],
                                            patch_artist=True)
            
            # 设置颜色
            colors = ['lightblue', 'lightgreen', 'lightcoral']
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            axes[row, col].set_title(skill_name, fontweight='bold')
            axes[row, col].set_xlabel('管理层级')
            axes[row, col].set_ylabel('技能得分')
            axes[row, col].grid(True, alpha=0.3)
            axes[row, col].set_ylim(1, 5)
        
        plt.tight_layout()
        
        # 保存图表
        output_path = 'evaluation/test_boxplot.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 箱型图已生成: {output_path}")
        
        # 验证文件是否存在
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   文件大小: {file_size} bytes")
            
            # 验证数据趋势
            print("   数据验证:")
            for skill_key, skill_name in skills_info:
                junior_mean = np.mean(junior_data[skill_key])
                middle_mean = np.mean(middle_data[skill_key])
                senior_mean = np.mean(senior_data[skill_key])
                
                print(f"   {skill_name}: 初级({junior_mean:.2f}) < 中级({middle_mean:.2f}) < 高级({senior_mean:.2f})")
                
                # 验证层级间的得分递增趋势
                assert junior_mean < middle_mean < senior_mean
            
            return True
        else:
            print("❌ 箱型图生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 生成箱型图时出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = generate_boxplot()
    sys.exit(0 if success else 1)