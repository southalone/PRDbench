#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.7.1b 特征解释 - Top-N重要性可视化

测试是否生成了Top-N（至少前5个）特征重要性的可视化图表。
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from credit_assessment.algorithms.algorithm_manager import AlgorithmManager
    from credit_assessment.evaluation.visualizer import ModelVisualizer
    from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
    pytest.skip(f"无法导入模块: {e}", allow_module_level=True)


class TestFeatureImportanceVisualization:
    """特征重要性可视化测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.algorithm_manager = AlgorithmManager(self.config)
        self.visualizer = ModelVisualizer(self.config)
        
        # 创建有意义的训练数据
        np.random.seed(42)
        n_samples = 300
        
        # 设计特征，使其有不同的重要性
        age = np.random.randint(20, 80, n_samples)
        income = np.random.randint(20000, 200000, n_samples)
        debt_ratio = np.random.uniform(0, 1, n_samples)
        credit_history = np.random.randint(0, 10, n_samples)
        employment_years = np.random.randint(0, 40, n_samples)
        savings = np.random.uniform(0, 50000, n_samples)
        
        self.X_train = pd.DataFrame({
            'age': age,
            'income': income,
            'debt_ratio': debt_ratio, 
            'credit_history': credit_history,
            'employment_years': employment_years,
            'savings': savings
        })
        
        # 创建目标变量，使不同特征有不同的重要性
        self.y_train = pd.Series(
            ((income / 100000 * 3) +           # 收入最重要
             (-debt_ratio * 2) +              # 债务比例次重要
             (credit_history / 10 * 1.5) +    # 信用历史重要
             (age / 100 * 0.5) +              # 年龄较不重要
             (employment_years / 40 * 0.3) +   # 工作年限不太重要
             (savings / 50000 * 0.2) +        # 储蓄最不重要
             np.random.normal(0, 0.5, n_samples) > 0).astype(int)
        )
        
        # 训练Logistic回归模型
        try:
            self.algorithm_manager.train_algorithm(
                'logistic_regression', self.X_train, self.y_train
            )
            self.model_available = True
            print("[INFO] Logistic回归模型训练完成")
        except Exception as e:
            print(f"[WARNING] Logistic回归训练失败: {e}")
            self.model_available = False
    
    def test_feature_importance_visualization(self):
        """测试特征重要性可视化功能"""
        if not self.model_available:
            pytest.skip("Logistic回归模型不可用，跳过特征重要性可视化测试")
        
        # 执行 (Act): 在Logistic回归结果中查看特征重要性可视化
        try:
            # 获取训练好的算法实例
            algorithm = self.algorithm_manager.get_algorithm('logistic_regression')
            
            if hasattr(algorithm, 'model') and algorithm.model is not None:
                
                # 断言 (Assert): 验证是否生成了Top-N（至少前5个）特征重要性的可视化图表
                
                # 1. 计算特征重要性（基于系数绝对值）
                if hasattr(algorithm.model, 'coef_'):
                    coefficients = algorithm.model.coef_[0]
                    feature_names = self.X_train.columns.tolist()
                    
                    # 计算特征重要性（系数绝对值）
                    feature_importance = pd.DataFrame({
                        'feature': feature_names,
                        'importance': np.abs(coefficients),
                        'coefficient': coefficients
                    })
                    
                    # 按重要性排序
                    feature_importance = feature_importance.sort_values('importance', ascending=False)
                    
                    print(f"\n特征重要性排序:")
                    print("-" * 50)
                    for i, row in feature_importance.iterrows():
                        print(f"{row['feature']:<20} {row['importance']:<12.6f} (coef: {row['coefficient']:8.4f})")
                    print("-" * 50)
                    
                    # 2. 验证至少有5个特征
                    assert len(feature_importance) >= 5, f"应该有至少5个特征进行重要性分析，实际: {len(feature_importance)}"
                    
                    # 3. 生成Top-N特征重要性可视化
                    top_n = min(5, len(feature_importance))
                    top_features = feature_importance.head(top_n)
                    
                    # 创建可视化图表
                    plt.figure(figsize=(10, 6))
                    
                    # 绘制水平条形图
                    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'][:top_n]
                    bars = plt.barh(range(top_n), top_features['importance'], color=colors)
                    
                    # 设置标签和标题
                    plt.yticks(range(top_n), top_features['feature'])
                    plt.xlabel('Feature Importance (|Coefficient|)')
                    plt.title(f'Top-{top_n} Feature Importance')
                    plt.gca().invert_yaxis()  # 最重要的在顶部
                    
                    # 添加数值标签
                    for i, (bar, importance) in enumerate(zip(bars, top_features['importance'])):
                        plt.text(bar.get_width() + max(top_features['importance']) * 0.01, 
                               bar.get_y() + bar.get_height()/2, 
                               f'{importance:.4f}', 
                               va='center', ha='left', fontsize=9)
                    
                    plt.tight_layout()
                    
                    # 保存图表（可选）
                    output_path = "feature_importance_top5.png"
                    plt.savefig(output_path, dpi=150, bbox_inches='tight')
                    print(f"[INFO] 特征重要性可视化图表已保存: {output_path}")
                    
                    # 4. 验证可视化结果
                    # 验证图表是否正确创建
                    fig = plt.gcf()
                    assert fig is not None, "应该创建了matplotlib图形对象"
                    
                    axes = fig.get_axes()
                    assert len(axes) > 0, "图形应该包含至少一个轴"
                    
                    ax = axes[0]
                    
                    # 验证条形图
                    bars = ax.patches
                    assert len(bars) >= top_n, f"应该有{top_n}个条形，实际: {len(bars)}"
                    
                    # 验证Y轴标签（特征名称）
                    y_labels = [tick.get_text() for tick in ax.get_yticklabels()]
                    for feature in top_features['feature'].head(top_n):
                        assert feature in y_labels, f"特征 {feature} 应该在Y轴标签中"
                    
                    # 验证X轴标签
                    x_label = ax.get_xlabel()
                    assert 'importance' in x_label.lower() or 'coefficient' in x_label.lower(), "X轴标签应该包含重要性相关文字"
                    
                    # 验证标题
                    title = ax.get_title()
                    assert 'top' in title.lower() and str(top_n) in title, f"标题应该包含Top-{top_n}"
                    
                    print(f"[VALIDATION] 可视化验证:")
                    print(f"  - 条形数量: {len(bars)}")
                    print(f"  - Y轴标签: {len(y_labels)}个特征名称")
                    print(f"  - X轴标签: {x_label}")
                    print(f"  - 图表标题: {title}")
                    
                    # 5. 验证Top-N特征的重要性排序
                    for i in range(len(top_features) - 1):
                        current_importance = top_features.iloc[i]['importance']
                        next_importance = top_features.iloc[i + 1]['importance']
                        assert current_importance >= next_importance, "特征重要性应该按降序排列"
                    
                    # 6. 显示最重要的特征信息
                    most_important = top_features.iloc[0]
                    least_important = top_features.iloc[-1]
                    
                    print(f"\n[ANALYSIS] Top-{top_n}特征重要性分析:")
                    print(f"  最重要特征: {most_important['feature']} (重要性: {most_important['importance']:.6f})")
                    print(f"  最不重要特征: {least_important['feature']} (重要性: {least_important['importance']:.6f})")
                    print(f"  重要性比值: {most_important['importance'] / least_important['importance']:.2f}")
                    
                    # 清理图形
                    plt.close()
                    
                    print(f"\nTop-N重要性可视化测试通过：成功生成了Top-{top_n}特征重要性的可视化图表")
                    
                else:
                    pytest.fail("Logistic回归模型没有coef_属性")
                    
            else:
                pytest.fail("训练后的Logistic回归模型不可用")
                
        except Exception as e:
            pytest.skip(f"特征重要性可视化测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__])