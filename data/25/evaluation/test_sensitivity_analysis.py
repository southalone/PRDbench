# -*- coding: utf-8 -*-
"""测试 敏感性分析"""
import sys; sys.path.append('src')
from model_evaluation import ModelEvaluator

print("测试: 模型评估与分析 → 敏感性分析")
evaluator = ModelEvaluator()
evaluator.sensitivity_analysis()
print("[成功] 敏感性分析完成!")