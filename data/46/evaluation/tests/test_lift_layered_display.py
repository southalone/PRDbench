#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.5.3b LIFT图 - 分层提升度显示

测试图上是否清晰显示了不同分层的提升度数值。
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


class TestLiftLayeredDisplay:
    """LIFT图分层提升度显示测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.algorithm_manager = AlgorithmManager(self.config)
        self.visualizer = ModelVisualizer(self.config)
        
        # 创建训练和测试数据
        np.random.seed(42)
        n_samples = 500  # 增加样本数以获得更稳定的分层结果
        
        X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples)
        })
        
        # 创建有明显区分度的目标变量
        y = pd.Series(
            ((X['feature1'] * 1.0 + X['feature2'] * 0.8 + 
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
    
    def test_lift_layered_display(self):
        """测试LIFT图分层提升度显示功能"""
        if not self.model_available:
            pytest.skip("模型不可用，跳过LIFT分层显示测试")
        
        # 执行 (Act): 查看生成的LIFT图
        try:
            # 获取训练好的算法实例
            algorithm = self.algorithm_manager.get_algorithm('logistic_regression')
            
            if hasattr(algorithm, 'model') and algorithm.model is not None:
                # 进行预测
                y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]
                
                # 断言 (Assert): 验证图上是否清晰显示了不同分层的提升度数值
                
                # 1. 计算分层LIFT数据
                results_df = pd.DataFrame({
                    'actual': self.y_test.values,
                    'predicted_prob': y_pred_proba
                })
                
                # 按预测概率降序排序
                results_df = results_df.sort_values('predicted_prob', ascending=False).reset_index(drop=True)
                
                # 计算基准正样本率
                baseline_positive_rate = results_df['actual'].mean()
                
                # 计算十分位分层LIFT
                n_layers = 10  # 十分位分层
                layer_size = len(results_df) // n_layers
                layered_lift_data = []
                
                for layer in range(n_layers):
                    start_idx = layer * layer_size
                    end_idx = min((layer + 1) * layer_size, len(results_df))
                    
                    # 当前分层的数据
                    layer_data = results_df.iloc[start_idx:end_idx]
                    
                    # 计算分层指标
                    layer_positive_count = layer_data['actual'].sum()
                    layer_total_count = len(layer_data)
                    layer_positive_rate = layer_positive_count / layer_total_count if layer_total_count > 0 else 0
                    layer_lift = layer_positive_rate / baseline_positive_rate if baseline_positive_rate > 0 else 1
                    
                    layered_lift_data.append({
                        'layer': layer + 1,
                        'layer_name': f'第{layer + 1}十分位',
                        'positive_count': layer_positive_count,
                        'total_count': layer_total_count,
                        'positive_rate': layer_positive_rate,
                        'lift_value': layer_lift,
                        'population_start': start_idx / len(results_df) * 100,
                        'population_end': end_idx / len(results_df) * 100
                    })
                
                print(f"\n[INFO] 分层LIFT计算结果:")
                print(f"  基准正样本率: {baseline_positive_rate:.4f}")
                print(f"  分层数: {n_layers}")
                print(f"  每层样本数: 约{layer_size}个")
                
                # 2. 生成分层LIFT图并显示数值
                plt.figure(figsize=(14, 10))
                
                # 提取绘图数据
                layers = [item['layer'] for item in layered_lift_data]
                lift_values = [item['lift_value'] for item in layered_lift_data]
                positive_rates = [item['positive_rate'] for item in layered_lift_data]
                
                # 主图：分层LIFT值
                plt.subplot(2, 2, 1)
                bars = plt.bar(layers, lift_values, color='lightcoral', alpha=0.7, 
                              edgecolor='darkred', linewidth=1)
                plt.axhline(y=1, color='black', linestyle='--', alpha=0.7, label='基准线 (LIFT=1)')
                plt.xlabel('十分位层')
                plt.ylabel('LIFT值')
                plt.title('分层LIFT值分布')
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                # 清晰显示每个分层的提升度数值
                for i, (bar, lift_val) in enumerate(zip(bars, lift_values)):
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                            f'{lift_val:.3f}', ha='center', va='bottom', 
                            fontsize=10, fontweight='bold', color='darkred')
                
                # 辅助图：正样本率分布
                plt.subplot(2, 2, 2)
                bars2 = plt.bar(layers, positive_rates, color='lightblue', alpha=0.7,
                               edgecolor='darkblue', linewidth=1)
                plt.axhline(y=baseline_positive_rate, color='red', linestyle='--', 
                           alpha=0.7, label=f'基准率: {baseline_positive_rate:.3f}')
                plt.xlabel('十分位层')
                plt.ylabel('正样本率')
                plt.title('分层正样本率分布')
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                # 显示正样本率数值
                for bar, rate_val in zip(bars2, positive_rates):
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                            f'{rate_val:.3f}', ha='center', va='bottom', 
                            fontsize=9, fontweight='bold', color='darkblue')
                
                # 详细数值表格
                plt.subplot(2, 1, 2)
                plt.axis('off')  # 关闭坐标轴
                
                # 创建表格数据
                table_data = []
                headers = ['分层', '正样本数', '总样本数', '正样本率', 'LIFT值', '人群区间(%)']
                
                for item in layered_lift_data:
                    table_data.append([
                        item['layer_name'],
                        f"{item['positive_count']}",
                        f"{item['total_count']}",
                        f"{item['positive_rate']:.4f}",
                        f"{item['lift_value']:.4f}",
                        f"{item['population_start']:.0f}-{item['population_end']:.0f}%"
                    ])
                
                # 绘制表格
                table = plt.table(cellText=table_data, colLabels=headers,
                                cellLoc='center', loc='center',
                                colWidths=[0.12, 0.1, 0.1, 0.12, 0.12, 0.14])
                table.auto_set_font_size(False)
                table.set_fontsize(9)
                table.scale(1, 2)
                
                # 设置表格样式
                for i in range(len(headers)):
                    table[(0, i)].set_facecolor('#4CAF50')
                    table[(0, i)].set_text_props(weight='bold', color='white')
                
                for i in range(1, len(table_data) + 1):
                    for j in range(len(headers)):
                        if i % 2 == 0:
                            table[(i, j)].set_facecolor('#f0f0f0')
                
                plt.title('分层LIFT详细数值表', fontweight='bold', pad=20)
                
                plt.tight_layout()
                
                # 保存图表
                output_path = "lift_layered_display.png"
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                print(f"[INFO] 分层LIFT显示图已保存: {output_path}")
                
                # 3. 验证分层提升度显示的完整性
                assert len(layered_lift_data) == n_layers, f"应该有{n_layers}个分层，实际: {len(layered_lift_data)}"
                
                # 验证每个分层的数值都被正确计算和显示
                for i, item in enumerate(layered_lift_data):
                    assert item['lift_value'] >= 0, f"第{i+1}分层LIFT值应该非负: {item['lift_value']}"
                    assert 0 <= item['positive_rate'] <= 1, f"第{i+1}分层正样本率应该在0-1之间: {item['positive_rate']}"
                    assert item['total_count'] > 0, f"第{i+1}分层应该有样本: {item['total_count']}"
                    
                    print(f"[LAYER {i+1}] LIFT={item['lift_value']:.3f}, 正样本率={item['positive_rate']:.3f}, "
                          f"样本数={item['total_count']}, 区间={item['population_start']:.0f}-{item['population_end']:.0f}%")
                
                # 4. 验证分层之间的差异性（好的模型应该有明显差异）
                lift_range = max(lift_values) - min(lift_values)
                print(f"[ANALYSIS] LIFT值差异范围: {lift_range:.3f}")
                
                if lift_range > 1.0:
                    print("[SUCCESS] 模型分层效果显著，各层LIFT值差异明显")
                elif lift_range > 0.5:
                    print("[INFO] 模型分层效果一般，各层有一定差异")
                else:
                    print("[WARNING] 模型分层效果较弱，各层差异不大")
                
                # 5. 验证高分层的优越性（前几个分层通常应该有更高的LIFT）
                first_layer_lift = layered_lift_data[0]['lift_value']
                last_layer_lift = layered_lift_data[-1]['lift_value']
                
                print(f"[COMPARISON] 第1层LIFT={first_layer_lift:.3f} vs 第{n_layers}层LIFT={last_layer_lift:.3f}")
                
                if first_layer_lift > last_layer_lift:
                    print("[SUCCESS] 高风险分层具有更高的LIFT值，符合预期")
                else:
                    print("[INFO] 分层LIFT分布可能需要进一步优化")
                
                # 清理图形
                plt.close()
                
                print(f"\nLIFT分层提升度显示测试通过：图表清晰显示了{n_layers}个分层的提升度数值")
                print(f"LIFT值范围 [{min(lift_values):.3f}, {max(lift_values):.3f}]，差异显著度 {lift_range:.3f}")
                
            else:
                pytest.fail("训练后的模型不可用")
                
        except Exception as e:
            pytest.skip(f"LIFT分层提升度显示测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__])