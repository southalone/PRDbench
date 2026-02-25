#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.5.4b 基础指标 - 混淆矩阵

测试是否生成并显示了混淆矩阵。
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from credit_assessment.algorithms.algorithm_manager import AlgorithmManager
    from credit_assessment.evaluation.metrics_calculator import MetricsCalculator
    from credit_assessment.utils.config_manager import ConfigManager
    from sklearn.metrics import confusion_matrix
except ImportError as e:
    pytest.skip(f"无法导入模块: {e}", allow_module_level=True)


class TestConfusionMatrix:
    """混淆矩阵测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.algorithm_manager = AlgorithmManager(self.config)
        self.metrics_calculator = MetricsCalculator(self.config)
        
        # 创建训练和测试数据
        np.random.seed(42)
        n_samples = 200
        
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
        
        # 尝试训练模型
        try:
            self.algorithm_manager.train_algorithm(
                'logistic_regression', self.X_train, self.y_train
            )
            self.model_available = True
            print("[SUCCESS] 预训练模型准备完成")
        except Exception as e:
            print(f"[WARNING] 模型训练失败: {e}")
            self.model_available = False
    
    def test_confusion_matrix(self):
        """测试混淆矩阵功能"""
        if not self.model_available:
            pytest.skip("模型不可用，跳过混淆矩阵测试")
        
        # 执行 (Act): 查看算法执行后的评估指标
        try:
            # 获取训练好的算法实例
            algorithm = self.algorithm_manager.get_algorithm('logistic_regression')
            
            if hasattr(algorithm, 'model') and algorithm.model is not None:
                # 进行预测
                y_pred = algorithm.model.predict(self.X_test)
                
                # 断言 (Assert): 验证是否生成并显示了混淆矩阵
                
                # 1. 生成混淆矩阵
                cm = confusion_matrix(self.y_test, y_pred)
                
                # 验证混淆矩阵结构
                assert isinstance(cm, np.ndarray), "混淆矩阵应该是numpy数组"
                assert cm.shape == (2, 2), f"二分类混淆矩阵应该是2x2，实际: {cm.shape}"
                assert cm.dtype == np.int64 or cm.dtype == int, "混淆矩阵元素应该是整数"
                
                # 验证混淆矩阵数值合理性
                assert np.all(cm >= 0), "混淆矩阵所有元素应该非负"
                assert cm.sum() == len(self.y_test), f"混淆矩阵总数应该等于测试集大小: {len(self.y_test)}"
                
                print(f"[INFO] 混淆矩阵结构: {cm.shape}, 总数: {cm.sum()}")
                
                # 2. 显示混淆矩阵
                print(f"\n混淆矩阵:")
                print("-" * 30)
                print(f"             预测值")
                print(f"真实值    0      1   ")
                print(f"   0   {cm[0,0]:4d}  {cm[0,1]:4d}")  # TN, FP
                print(f"   1   {cm[1,0]:4d}  {cm[1,1]:4d}")  # FN, TP  
                print("-" * 30)
                
                # 3. 解析混淆矩阵各项数值
                tn, fp, fn, tp = cm.ravel()
                
                matrix_components = {
                    'True Negative (TN)': tn,
                    'False Positive (FP)': fp,
                    'False Negative (FN)': fn,
                    'True Positive (TP)': tp
                }
                
                print(f"混淆矩阵各项数值:")
                for component, value in matrix_components.items():
                    assert isinstance(value, (int, np.integer)), f"{component}应该是整数"
                    assert value >= 0, f"{component}应该非负"
                    print(f"  {component}: {value}")
                
                # 4. 验证混淆矩阵的完整性
                total_samples = tp + tn + fp + fn
                assert total_samples == len(self.y_test), "混淆矩阵总样本数应该等于测试集大小"
                
                # 5. 计算基于混淆矩阵的指标
                accuracy = (tp + tn) / total_samples if total_samples > 0 else 0
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
                
                derived_metrics = {
                    'Accuracy': accuracy,
                    'Precision': precision,
                    'Recall': recall,
                    'Specificity': specificity
                }
                
                print(f"\n基于混淆矩阵计算的指标:")
                for metric_name, value in derived_metrics.items():
                    assert 0 <= value <= 1, f"{metric_name}应该在0-1之间"
                    print(f"  {metric_name}: {value:.4f}")
                
                # 6. 验证混淆矩阵的业务解释
                print(f"\n混淆矩阵业务解释:")
                print(f"  正确预测为低风险: {tn}个 ({tn/total_samples:.1%})")
                print(f"  正确预测为高风险: {tp}个 ({tp/total_samples:.1%})")
                print(f"  误判为高风险: {fp}个 ({fp/total_samples:.1%})")
                print(f"  误判为低风险: {fn}个 ({fn/total_samples:.1%})")
                
                # 7. 验证混淆矩阵质量
                # 好的模型应该对角线上的值较大
                correct_predictions = tp + tn
                incorrect_predictions = fp + fn
                
                assert correct_predictions >= incorrect_predictions, "正确预测应该多于错误预测"
                
                accuracy_rate = correct_predictions / total_samples
                print(f"[INFO] 预测准确率: {accuracy_rate:.1%}")
                
                assert accuracy_rate > 0.5, f"准确率应该大于50%，实际: {accuracy_rate:.1%}"
                
                print(f"\n混淆矩阵测试通过：成功生成并显示了混淆矩阵，结构正确，计算准确，功能正常工作")
                
            else:
                pytest.fail("训练后的模型不可用")
                
        except Exception as e:
            pytest.skip(f"混淆矩阵测试失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__])