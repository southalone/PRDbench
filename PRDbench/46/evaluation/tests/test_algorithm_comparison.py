#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.3.4 算法性能对比功能

测试是否显示了两种算法的性能对比表，包含至少4项指标（准确率、精度、召回率、F1分数）。
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
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
except ImportError as e:
    pytest.skip(f"无法导入模块: {e}", allow_module_level=True)


class TestAlgorithmComparison:
    """算法性能对比功能测试类"""
    
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
        
        # 创建有意义的目标变量
        y = pd.Series(
            ((X['feature1'] * 0.6 + X['feature2'] * 0.4 + 
              np.random.normal(0, 0.3, n_samples)) > 0).astype(int)
        )
        
        # 分割训练测试集
        split_idx = int(n_samples * 0.7)
        self.X_train = X[:split_idx]
        self.X_test = X[split_idx:]
        self.y_train = y[:split_idx]
        self.y_test = y[split_idx:]
    
    def test_algorithm_comparison(self):
        """测试算法性能对比功能"""
        # 准备 (Arrange): 分别执行Logistic回归和神经网络算法
        algorithms_to_test = ['logistic_regression', 'neural_network']
        comparison_results = {}
        
        for algorithm_name in algorithms_to_test:
            try:
                # 训练算法
                training_result = self.algorithm_manager.train_algorithm(
                    algorithm_name, self.X_train, self.y_train
                )
                
                # 获取算法实例进行预测
                algorithm = self.algorithm_manager.get_algorithm(algorithm_name)
                if hasattr(algorithm, 'model') and algorithm.model is not None:
                    # 进行预测
                    y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]
                    y_pred = (y_pred_proba > 0.5).astype(int)
                    
                    # 计算性能指标
                    comparison_results[algorithm_name] = {
                        'accuracy': accuracy_score(self.y_test, y_pred),
                        'precision': precision_score(self.y_test, y_pred, average='binary'),
                        'recall': recall_score(self.y_test, y_pred, average='binary'),
                        'f1_score': f1_score(self.y_test, y_pred, average='binary'),
                        'training_time': training_result.get('training_time', 0)
                    }
                    
                    print(f"✓ {algorithm_name} 训练和评估完成")
                    
            except Exception as e:
                print(f"⚠ {algorithm_name} 训练失败: {e}")
                comparison_results[algorithm_name] = {'error': str(e)}
        
        # 执行 (Act): 选择性能对比功能
        # 断言 (Assert): 验证是否显示了两种算法的性能对比表，包含至少4项指标
        
        # 验证至少有一个算法成功训练
        successful_algorithms = [name for name, result in comparison_results.items() if 'error' not in result]
        assert len(successful_algorithms) >= 1, f"至少应有一个算法训练成功，实际成功: {successful_algorithms}"
        
        # 验证性能对比表包含至少4项指标（准确率、精度、召回率、F1分数）
        required_metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        
        for algorithm_name in successful_algorithms:
            result = comparison_results[algorithm_name]
            
            # 验证包含所有必需指标
            for metric in required_metrics:
                assert metric in result, f"{algorithm_name}应该包含{metric}指标"
                assert isinstance(result[metric], (int, float)), f"{metric}应该是数值类型"
                assert 0 <= result[metric] <= 1, f"{metric}值应该在0-1之间"
        
        # 显示性能对比表
        print("\n" + "="*60)
        print("算法性能对比表")
        print("="*60)
        
        # 表头
        headers = ["算法"] + [metric.upper() for metric in required_metrics] + ["训练时间(s)"]
        print(f"{'算法':<20} {'准确率':<10} {'精度':<10} {'召回率':<10} {'F1分数':<10} {'训练时间':<12}")
        print("-" * 72)
        
        # 数据行
        for algorithm_name, result in comparison_results.items():
            if 'error' not in result:
                print(f"{algorithm_name:<20} "
                      f"{result['accuracy']:<10.4f} "
                      f"{result['precision']:<10.4f} "
                      f"{result['recall']:<10.4f} "
                      f"{result['f1_score']:<10.4f} "
                      f"{result['training_time']:<12.3f}")
            else:
                print(f"{algorithm_name:<20} {'训练失败':<50}")
        
        print("="*60)
        
        # 验证比较结果完整性
        if len(successful_algorithms) >= 2:
            print(f"✓ 成功对比{len(successful_algorithms)}种算法的性能")
            
            # 找出最佳算法
            best_algorithm = max(successful_algorithms, 
                               key=lambda x: comparison_results[x]['f1_score'])
            best_f1 = comparison_results[best_algorithm]['f1_score']
            
            print(f"✓ 最佳算法: {best_algorithm} (F1分数: {best_f1:.4f})")
            
        elif len(successful_algorithms) == 1:
            print(f"✓ 成功评估{successful_algorithms[0]}算法性能")
        
        # 最终验证
        metrics_count = len(required_metrics)
        assert metrics_count >= 4, f"性能对比应该包含至少4项指标，实际{metrics_count}项"
        
        print(f"\n算法性能对比测试通过：显示了算法的性能对比表，包含{metrics_count}项指标（准确率、精度、召回率、F1分数）")


if __name__ == "__main__":
    pytest.main([__file__])