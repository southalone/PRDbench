# -*- coding: utf-8 -*-
import pytest
import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from evaluator import RecommendationEvaluator

def test_precision_recall_f1():
    """测试准确率、召回率、F1分数计算"""
    config = {'evaluation': {'top_n': 5}}
    evaluator = RecommendationEvaluator(config)
    
    # 模拟测试数据
    y_true = [1, 1, 0, 1, 0]
    y_pred = [1, 0, 0, 1, 1]
    
    metrics = evaluator.calculate_basic_metrics(y_true, y_pred)
    
    # 断言：包含3项核心指标
    assert 'precision' in metrics, "应包含准确率"
    assert 'recall' in metrics, "应包含召回率"
    assert 'f1_score' in metrics, "应包含F1分数"
    return True

def test_coverage_diversity():
    """测试覆盖率和多样性指标"""
    config = {'evaluation': {'top_n': 5}}
    evaluator = RecommendationEvaluator(config)
    
    # 模拟推荐结果
    recommendations = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
    
    advanced_metrics = evaluator.calculate_advanced_metrics(recommendations)
    
    # 断言：包含3项高级指标
    assert 'coverage' in advanced_metrics, "应包含覆盖率"
    assert 'diversity' in advanced_metrics, "应包含多样性"
    assert 'cold_start_hit_rate' in advanced_metrics, "应包含冷启动命中率"
    return True
