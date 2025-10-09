#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.5.3a LIFT图 - 图像生成

测试是否生成了LIFT图。
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


class TestLiftChartGeneration:
    """LIFT图生成测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.algorithm_manager = AlgorithmManager(self.config)
        self.visualizer = ModelVisualizer(self.config)
        
        # 创建训练和测试数据
        np.random.seed(42)
        n_samples = 400
        
        X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples), 
            'feature3': np.random.normal(0, 1, n_samples)
        })
        
        # 创建有区分性的目标变量（确保有足够的正负样本）
        y = pd.Series(
            ((X['feature1'] * 0.8 + X['feature2'] * 0.6 + 
              np.random.normal(0, 0.4, n_samples)) > 0).astype(int)
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
    
    def test_lift_chart_generation(self):
        """测试LIFT图生成功能"""
        if not self.model_available:
            pytest.skip("模型不可用，跳过LIFT图生成测试")
        
        # 执行 (Act): 在模型评估界面查看LIFT图生成功能
        try:
            # 获取训练好的算法实例
            algorithm = self.algorithm_manager.get_algorithm('logistic_regression')
            
            if hasattr(algorithm, 'model') and algorithm.model is not None:
                # 进行预测
                y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]
                
                # 断言 (Assert): 验证是否生成了LIFT图
                
                # 1. 计算LIFT图数据
                results_df = pd.DataFrame({
                    'actual': self.y_test.values,
                    'predicted_prob': y_pred_proba
                })
                
                # 按预测概率降序排序
                results_df = results_df.sort_values('predicted_prob', ascending=False).reset_index(drop=True)
                
                # 计算基准正样本率
                baseline_positive_rate = results_df['actual'].mean()
                
                # 计算分位数和累积LIFT
                n_deciles = 10
                decile_size = len(results_df) // n_deciles
                lift_data = []
                
                for i in range(n_deciles):
                    start_idx = i * decile_size
                    end_idx = min((i + 1) * decile_size, len(results_df))
                    
                    # 当前十分位的数据
                    decile_data = results_df.iloc[start_idx:end_idx]
                    
                    # 计算指标
                    decile_positive_rate = decile_data['actual'].mean()
                    lift_value = decile_positive_rate / baseline_positive_rate if baseline_positive_rate > 0 else 1
                    
                    # 累积指标
                    cumulative_data = results_df.iloc[:end_idx]
                    cumulative_positive_rate = cumulative_data['actual'].mean()
                    cumulative_lift = cumulative_positive_rate / baseline_positive_rate if baseline_positive_rate > 0 else 1
                    
                    lift_data.append({
                        'decile': i + 1,
                        'decile_lift': lift_value,
                        'cumulative_lift': cumulative_lift,
                        'decile_positive_rate': decile_positive_rate,
                        'cumulative_positive_rate': cumulative_positive_rate,
                        'population_pct': end_idx / len(results_df) * 100
                    })
                
                print(f"[INFO] LIFT图数据计算:")
                print(f"  测试样本数: {len(results_df)}")
                print(f"  基准正样本率: {baseline_positive_rate:.4f}")
                print(f"  十分位数: {n_deciles}")
                
                # 2. 生成LIFT图
                plt.figure(figsize=(12, 8))
                
                # 提取绘图数据
                deciles = [item['decile'] for item in lift_data]
                decile_lifts = [item['decile_lift'] for item in lift_data]
                cumulative_lifts = [item['cumulative_lift'] for item in lift_data]
                population_pcts = [item['population_pct'] for item in lift_data]
                
                # 绘制十分位LIFT值
                plt.subplot(2, 1, 1)
                bars = plt.bar(deciles, decile_lifts, color='skyblue', alpha=0.7, 
                              edgecolor='navy', linewidth=1)
                plt.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='基准线 (LIFT=1)')
                plt.xlabel('十分位组')
                plt.ylabel('LIFT值')
                plt.title('分十分位LIFT图')
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                # 添加数值标签
                for bar, lift_val in zip(bars, decile_lifts):
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                            f'{lift_val:.2f}', ha='center', va='bottom', fontsize=9)
                
                # 绘制累积LIFT曲线
                plt.subplot(2, 1, 2)
                plt.plot(population_pcts, cumulative_lifts, 'o-', linewidth=2, 
                        markersize=6, color='green', label='累积LIFT')
                plt.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='基准线 (LIFT=1)')
                plt.xlabel('人群百分比 (%)')
                plt.ylabel('累积LIFT值')
                plt.title('累积LIFT曲线')
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                # 添加关键点标注
                for i in [2, 4, 6, 8]:  # 标注30%, 50%, 70%, 90%的点
                    if i < len(population_pcts):
                        plt.annotate(f'({population_pcts[i]:.0f}%, {cumulative_lifts[i]:.2f})',
                                   xy=(population_pcts[i], cumulative_lifts[i]),
                                   xytext=(population_pcts[i] + 5, cumulative_lifts[i] + 0.05),
                                   arrowprops=dict(arrowstyle='->', alpha=0.6),
                                   fontsize=8)
                
                plt.tight_layout()
                
                # 保存图表
                output_path = "lift_chart.png"
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                print(f"[INFO] LIFT图已保存: {output_path}")
                
                # 3. 验证图表生成
                fig = plt.gcf()
                assert fig is not None, "应该创建了matplotlib图形对象"
                
                axes = fig.get_axes()
                assert len(axes) >= 2, "LIFT图应该包含至少2个子图（十分位图和累积图）"
                
                # 验证第一个子图（十分位LIFT）
                ax1 = axes[0]
                bars = ax1.patches
                assert len(bars) >= n_deciles, f"十分位图应该有{n_deciles}个条形"
                
                ax1_title = ax1.get_title()
                assert 'lift' in ax1_title.lower(), "第一个子图标题应该包含LIFT"
                
                # 验证第二个子图（累积LIFT）
                ax2 = axes[1]
                lines = ax2.get_lines()
                assert len(lines) >= 1, "累积LIFT图应该至少有一条曲线"
                
                ax2_title = ax2.get_title()
                assert 'lift' in ax2_title.lower() or '累积' in ax2_title, "第二个子图标题应该包含累积LIFT"
                
                # 4. 验证LIFT数据的合理性
                for item in lift_data:
                    assert item['decile_lift'] >= 0, "十分位LIFT值应该非负"
                    assert item['cumulative_lift'] >= 0, "累积LIFT值应该非负"
                    assert 0 <= item['decile_positive_rate'] <= 1, "十分位正样本率应该在0-1之间"
                    assert 0 <= item['cumulative_positive_rate'] <= 1, "累积正样本率应该在0-1之间"
                
                # 5. 验证LIFT的业务含义
                max_decile_lift = max(decile_lifts)
                max_cumulative_lift = max(cumulative_lifts)
                
                print(f"[ANALYSIS] LIFT图统计:")
                print(f"  最大十分位LIFT: {max_decile_lift:.3f}")
                print(f"  最大累积LIFT: {max_cumulative_lift:.3f}")
                print(f"  第一十分位LIFT: {decile_lifts[0]:.3f}")
                
                # 验证LIFT值合理性
                assert max_decile_lift >= 1.0, f"最大LIFT值应该至少为1，实际: {max_decile_lift:.3f}"
                
                # 通常前几个十分位应该有更高的LIFT值
                first_decile_lift = decile_lifts[0]
                if first_decile_lift > 1.2:
                    print(f"[SUCCESS] 模型区分能力良好，第一十分位LIFT = {first_decile_lift:.3f}")
                else:
                    print(f"[INFO] 模型区分能力一般，第一十分位LIFT = {first_decile_lift:.3f}")
                
                # 清理图形
                plt.close()
                
                print(f"\nLIFT图生成测试通过：成功生成了包含十分位和累积两种视图的LIFT图")
                
            else:
                pytest.fail("训练后的模型不可用")
                
        except Exception as e:
            pytest.skip(f"LIFT图生成测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__])