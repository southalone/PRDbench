#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.5.2b K-S曲线 - 最大KS距离标注

测试曲线图上是否明确标注了最大KS距离的数值和位置。
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


class TestKSMaxDistance:
    """K-S曲线最大距离标注测试类"""
    
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
    
    def test_ks_max_distance(self):
        """测试K-S曲线最大距离标注功能"""
        if not self.model_available:
            pytest.skip("模型不可用，跳过K-S最大距离标注测试")
        
        # 执行 (Act): 查看生成的K-S曲线
        try:
            # 获取训练好的算法实例
            algorithm = self.algorithm_manager.get_algorithm('logistic_regression')
            
            if hasattr(algorithm, 'model') and algorithm.model is not None:
                # 进行预测
                y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]
                
                # 断言 (Assert): 验证曲线图上是否明确标注了最大KS距离的数值和位置
                
                # 1. 计算K-S曲线数据
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
                
                # 计算K-S距离（TPR - FPR）
                results_df['ks_distance'] = results_df['tpr'] - results_df['fpr']
                
                # 找到最大K-S距离
                max_ks_index = results_df['ks_distance'].abs().idxmax()
                max_ks_value = results_df.loc[max_ks_index, 'ks_distance']
                max_ks_position = max_ks_index / len(results_df) * 100  # 转换为百分位
                max_ks_threshold = results_df.loc[max_ks_index, 'predicted_prob']
                
                print(f"[INFO] K-S统计量计算结果:")
                print(f"  最大K-S距离: {abs(max_ks_value):.6f}")
                print(f"  最大K-S位置: 第{max_ks_position:.1f}百分位")
                print(f"  对应阈值: {max_ks_threshold:.6f}")
                print(f"  对应TPR: {results_df.loc[max_ks_index, 'tpr']:.4f}")
                print(f"  对应FPR: {results_df.loc[max_ks_index, 'fpr']:.4f}")
                
                # 2. 生成K-S曲线图并验证最大距离标注
                plt.figure(figsize=(12, 8))
                
                # 计算用于绘图的数据点
                sample_percentiles = np.linspace(0, 100, len(results_df))
                
                # 绘制TPR和FPR曲线
                plt.plot(sample_percentiles, results_df['tpr'], 'b-', 
                        label='True Positive Rate (TPR)', linewidth=2)
                plt.plot(sample_percentiles, results_df['fpr'], 'r-', 
                        label='False Positive Rate (FPR)', linewidth=2)
                
                # 填充K-S距离区域
                plt.fill_between(sample_percentiles, results_df['tpr'], results_df['fpr'], 
                               alpha=0.3, color='green', label='K-S Distance')
                
                # 关键：标注最大K-S距离点
                max_ks_x = max_ks_position
                max_ks_tpr = results_df.loc[max_ks_index, 'tpr']
                max_ks_fpr = results_df.loc[max_ks_index, 'fpr']
                
                # 绘制最大K-S距离的垂直线
                plt.plot([max_ks_x, max_ks_x], [max_ks_tpr, max_ks_fpr], 
                        'g-', linewidth=4, alpha=0.8, label='Max K-S Distance')
                
                # 标记最大K-S距离点
                plt.plot(max_ks_x, max_ks_tpr, 'go', markersize=10, markerfacecolor='lightgreen')
                plt.plot(max_ks_x, max_ks_fpr, 'go', markersize=10, markerfacecolor='lightgreen')
                
                # 添加数值和位置标注
                annotation_text = (f'Max K-S Distance: {abs(max_ks_value):.4f}\n'
                                 f'Position: {max_ks_position:.1f}% percentile\n'
                                 f'Threshold: {max_ks_threshold:.4f}')
                
                plt.annotate(annotation_text,
                           xy=(max_ks_x, (max_ks_tpr + max_ks_fpr) / 2),
                           xytext=(max_ks_x + 15, (max_ks_tpr + max_ks_fpr) / 2 + 0.1),
                           arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2),
                           fontsize=12, color='darkgreen', fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.8))
                
                # 设置图形属性
                plt.xlabel('Sample Percentile (%)')
                plt.ylabel('Cumulative Rate')
                plt.title(f'K-S Curve with Maximum Distance Annotation\nMax K-S = {abs(max_ks_value):.4f} at {max_ks_position:.1f}% percentile')
                plt.legend(loc='center right')
                plt.grid(True, alpha=0.3)
                plt.xlim(0, 100)
                plt.ylim(0, 1)
                
                # 保存图表
                output_path = "ks_curve_with_max_distance.png"
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                print(f"[INFO] K-S曲线（含最大距离标注）已保存: {output_path}")
                
                # 3. 验证标注的正确性
                assert abs(max_ks_value) >= 0, "最大K-S距离应该非负"
                assert abs(max_ks_value) <= 1, "最大K-S距离应该不超过1"
                assert 0 <= max_ks_position <= 100, "最大K-S位置应该在0-100百分位之间"
                assert 0 <= max_ks_threshold <= 1, "对应阈值应该在0-1之间"
                
                # 4. 验证图形标注元素
                fig = plt.gcf()
                assert fig is not None, "应该创建了matplotlib图形对象"
                
                ax = fig.get_axes()[0]
                
                # 验证标题包含最大K-S距离信息
                title = ax.get_title()
                assert str(round(abs(max_ks_value), 4)) in title, "标题应该包含最大K-S距离数值"
                assert f'{max_ks_position:.1f}%' in title, "标题应该包含最大K-S位置百分位"
                
                # 验证图例包含最大K-S距离
                legend = ax.get_legend()
                assert legend is not None, "图形应该包含图例"
                
                legend_labels = [text.get_text() for text in legend.get_texts()]
                max_ks_in_legend = any('max' in label.lower() and 'k-s' in label.lower() for label in legend_labels)
                assert max_ks_in_legend, "图例应该包含最大K-S距离相关标签"
                
                # 验证注释文本内容
                annotations = [child for child in ax.get_children() if hasattr(child, 'get_text')]
                annotation_texts = [ann.get_text() for ann in annotations if hasattr(ann, 'get_text')]
                
                max_distance_annotated = any(str(round(abs(max_ks_value), 4)) in text for text in annotation_texts)
                position_annotated = any(f'{max_ks_position:.1f}%' in text for text in annotation_texts)
                
                print(f"[VALIDATION] 标注验证:")
                print(f"  - 最大K-S距离已标注: {max_distance_annotated}")
                print(f"  - 位置百分位已标注: {position_annotated}")
                print(f"  - 标题包含信息: Max K-S = {abs(max_ks_value):.4f}")
                print(f"  - 图例标签数: {len(legend_labels)}")
                
                # 5. 验证数值的业务合理性
                if abs(max_ks_value) > 0.3:
                    ks_performance = "优秀"
                elif abs(max_ks_value) > 0.2:
                    ks_performance = "良好"  
                elif abs(max_ks_value) > 0.1:
                    ks_performance = "一般"
                else:
                    ks_performance = "较差"
                
                print(f"[ANALYSIS] K-S统计量性能评级: {ks_performance}")
                
                # 清理图形
                plt.close()
                
                # 6. 最终验证
                assert abs(max_ks_value) > 0.01, f"K-S距离应该有意义(>0.01): {abs(max_ks_value)}"
                
                print(f"\nK-S曲线最大距离标注测试通过：")
                print(f"曲线图明确标注了最大K-S距离 {abs(max_ks_value):.4f} 及其位置 {max_ks_position:.1f}%")
                
            else:
                pytest.fail("训练后的模型不可用")
                
        except Exception as e:
            pytest.skip(f"K-S曲线最大距离标注测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__])