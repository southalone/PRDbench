#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from evaluator import RecommendationEvaluator

def test_evaluation_metrics():
    """测试推荐算法性能评测指标"""
    try:
        config = {'evaluation': {'top_n': 5}}
        evaluator = RecommendationEvaluator(config)
        
        # 模拟测试数据
        y_true = [1, 1, 0, 1, 0, 1, 0, 1, 1, 0]
        y_pred = [1, 0, 0, 1, 1, 0, 0, 1, 1, 0]
        
        # 计算基础指标
        metrics = evaluator.calculate_basic_metrics(y_true, y_pred)
        
        # 检查核心指标
        required_metrics = ['precision', 'recall', 'f1_score']
        all_present = all(metric in metrics for metric in required_metrics)
        
        if all_present:
            print("SUCCESS: 准确率召回率F1指标计算成功")
            for metric in required_metrics:
                print(f"  {metric}: {metrics[metric]:.3f}")
        
        # 计算高级指标
        recommendations = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        advanced_metrics = evaluator.calculate_advanced_metrics(recommendations)
        
        advanced_required = ['coverage', 'diversity', 'cold_start_hit_rate']
        advanced_present = all(metric in advanced_metrics for metric in advanced_required)
        
        if advanced_present:
            print("SUCCESS: 覆盖率多样性指标计算成功")
            for metric in advanced_required:
                print(f"  {metric}: {advanced_metrics[metric]:.3f}")
        
        return all_present and advanced_present
        
    except Exception as e:
        print(f"ERROR: 评估指标计算失败: {e}")
        return False

if __name__ == "__main__":
    success = test_evaluation_metrics()
    sys.exit(0 if success else 1)
