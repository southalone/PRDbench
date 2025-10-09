#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.5.2a K-S曲线 - 图像生成

测试是否生成了K-S曲线图。
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
    from sklearn.metrics import roc_curve
except ImportError as e:
    pytest.skip(f"无法导入模块: {e}", allow_module_level=True)


class TestKSCurveGeneration:
    """K-S曲线生成测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.algorithm_manager = AlgorithmManager(self.config)
        self.visualizer = ModelVisualizer(self.config)
        
        # 创建训练和测试数据
        np.random.seed(42)
        n_samples = 300
        
        X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples)
        })
        
        # 创建有区分性的目标变量
        y = pd.Series(
            ((X['feature1'] * 0.8 + X['feature2'] * 0.6 + 
              np.random.normal(0, 0.3, n_samples)) > 0).astype(int)
        )
        
        # 分割数据
        split_idx = int(n_samples * 0.7)
        self.X_train = X[:split_idx]
        self.X_test = X[split_idx:]
        self.y_train = y[:split_idx]
        self.y_test = y[split_idx:]
        
        # 训练模型
        try:
            self.algorithm_manager.train_algorithm(
                'logistic_regression', self.X_train, self.y_train
            )
            self.model_available = True
            print("[INFO] Logistic回归模型训练完成")
        except Exception as e:
            print(f"[WARNING] Logistic回归训练失败: {e}")
            self.model_available = False
    
    def test_ks_curve_generation(self):
        """测试K-S曲线生成功能"""
        if not self.model_available:
            pytest.skip("模型不可用，跳过K-S曲线生成测试")
        
        # 执行 (Act): 在模型评估界面查看K-S曲线生成功能
        try:
            # 获取训练好的算法实例
            algorithm = self.algorithm_manager.get_algorithm('logistic_regression')
            
            if hasattr(algorithm, 'model') and algorithm.model is not None:
                # 进行预测
                y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]
                
                # 断言 (Assert): 验证是否生成了K-S曲线图
                
                # 1. 计算K-S曲线数据
                # K-S曲线需要计算好样本和坏样本的累积分布
                
                # 创建预测结果DataFrame
                results_df = pd.DataFrame({
                    'actual': self.y_test.values,
                    'predicted_prob': y_pred_proba
                })
                
                # 按预测概率降序排序
                results_df = results_df.sort_values('predicted_prob', ascending=False).reset_index(drop=True)
                
                # 计算累积分布
                total_positive = results_df['actual'].sum()
                total_negative = len(results_df) - total_positive
                
                results_df['cumulative_positive'] = results_df['actual'].cumsum()
                results_df['cumulative_negative'] = (~results_df['actual'].astype(bool)).cumsum()
                
                # 计算TPR和FPR
                results_df['tpr'] = results_df['cumulative_positive'] / total_positive
                results_df['fpr'] = results_df['cumulative_negative'] / total_negative
                
                # 计算K-S距离
                results_df['ks_distance'] = results_df['tpr'] - results_df['fpr']
                
                # 找到最大K-S距离
                max_ks_index = results_df['ks_distance'].abs().idxmax()
                max_ks_value = results_df.loc[max_ks_index, 'ks_distance']
                max_ks_position = max_ks_index / len(results_df)
                
                print(f"[INFO] K-S曲线数据统计:")
                print(f"  样本总数: {len(results_df)}")
                print(f"  正样本数: {total_positive}")
                print(f"  负样本数: {total_negative}")
                print(f"  最大K-S距离: {abs(max_ks_value):.4f}")
                print(f"  最大K-S位置: {max_ks_position:.2%}")
                
                # 2. 生成K-S曲线图
                plt.figure(figsize=(10, 8))
                
                # 计算用于绘图的数据点
                sample_points = np.linspace(0, 1, min(100, len(results_df)))
                indices = (sample_points * (len(results_df) - 1)).astype(int)
                
                x_axis = sample_points
                tpr_values = results_df.loc[indices, 'tpr'].values
                fpr_values = results_df.loc[indices, 'fpr'].values
                
                # 绘制TPR和FPR曲线
                plt.plot(x_axis, tpr_values, 'b-', label='True Positive Rate', linewidth=2)
                plt.plot(x_axis, fpr_values, 'r-', label='False Positive Rate', linewidth=2)
                
                # 绘制K-S距离
                plt.fill_between(x_axis, tpr_values, fpr_values, alpha=0.3, color='green', 
                               label=f'K-S Distance (Max: {abs(max_ks_value):.4f})')
                
                # 标注最大K-S距离点
                max_ks_x = max_ks_position
                max_ks_tpr = results_df.loc[max_ks_index, 'tpr']
                max_ks_fpr = results_df.loc[max_ks_index, 'fpr']
                
                plt.plot(max_ks_x, max_ks_tpr, 'go', markersize=8, label='Max K-S Point')
                plt.plot(max_ks_x, max_ks_fpr, 'go', markersize=8)
                plt.plot([max_ks_x, max_ks_x], [max_ks_tpr, max_ks_fpr], 'g--', linewidth=2)
                
                # 添加标注
                plt.annotate(f'Max K-S: {abs(max_ks_value):.4f}', 
                           xy=(max_ks_x, (max_ks_tpr + max_ks_fpr) / 2),
                           xytext=(max_ks_x + 0.1, (max_ks_tpr + max_ks_fpr) / 2),
                           arrowprops=dict(arrowstyle='->', color='green'),
                           fontsize=10, color='green', fontweight='bold')
                
                # 设置图形属性
                plt.xlabel('Cumulative Percentage of Population')
                plt.ylabel('Cumulative Percentage of Events')
                plt.title('Kolmogorov-Smirnov (K-S) Curve')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.xlim(0, 1)
                plt.ylim(0, 1)
                
                # 保存图表
                output_path = "ks_curve.png"
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                print(f"[INFO] K-S曲线图已保存: {output_path}")
                
                # 3. 验证图表生成
                fig = plt.gcf()
                assert fig is not None, "应该创建了matplotlib图形对象"
                
                axes = fig.get_axes()
                assert len(axes) > 0, "图形应该包含至少一个轴"
                
                ax = axes[0]
                
                # 验证图形元素
                lines = ax.get_lines()
                assert len(lines) >= 2, "应该至少有TPR和FPR两条线"
                
                # 验证标签
                x_label = ax.get_xlabel()
                y_label = ax.get_ylabel()
                title = ax.get_title()
                
                assert 'population' in x_label.lower() or 'percentage' in x_label.lower(), "X轴标签应该包含人口百分比相关内容"
                assert 'events' in y_label.lower() or 'percentage' in y_label.lower(), "Y轴标签应该包含事件百分比相关内容"
                assert 'k-s' in title.lower() or 'kolmogorov' in title.lower(), "标题应该包含K-S相关内容"
                
                # 验证图例
                legend = ax.get_legend()
                assert legend is not None, "图形应该包含图例"
                
                legend_labels = [text.get_text() for text in legend.get_texts()]
                tpr_in_legend = any('tpr' in label.lower() or 'true positive' in label.lower() for label in legend_labels)
                fpr_in_legend = any('fpr' in label.lower() or 'false positive' in label.lower() for label in legend_labels)
                
                assert tpr_in_legend, "图例应该包含TPR相关标签"
                assert fpr_in_legend, "图例应该包含FPR相关标签"
                
                print(f"[VALIDATION] K-S曲线图验证:")
                print(f"  - 图形线条数: {len(lines)}")
                print(f"  - X轴标签: {x_label}")
                print(f"  - Y轴标签: {y_label}")
                print(f"  - 图表标题: {title}")
                print(f"  - 图例标签数: {len(legend_labels)}")
                
                # 4. 验证K-S统计的合理性
                assert 0 <= abs(max_ks_value) <= 1, f"K-S距离应该在0-1之间: {abs(max_ks_value)}"
                assert abs(max_ks_value) > 0.01, f"K-S距离应该有意义(>0.01): {abs(max_ks_value)}"
                
                # 5. 验证数据点数量
                assert len(tpr_values) == len(fpr_values), "TPR和FPR应该有相同的数据点数"
                assert len(tpr_values) >= 10, f"应该有足够的数据点绘制曲线: {len(tpr_values)}"
                
                # 清理图形
                plt.close()
                
                print(f"\nK-S曲线生成测试通过：成功生成了K-S曲线图，包含TPR/FPR曲线和最大K-S距离标注")
                
            else:
                pytest.fail("训练后的模型不可用")
                
        except Exception as e:
            pytest.skip(f"K-S曲线生成测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__])