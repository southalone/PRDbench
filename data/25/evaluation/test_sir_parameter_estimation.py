# -*- coding: utf-8 -*-
"""测试 SIR模型参数估计"""
import sys; sys.path.append('src')
from parameter_estimation import ParameterEstimator

print("测试: 真实数据建模验证 → SIR模型参数估计")
estimator = ParameterEstimator()
result = estimator.estimate_sir_parameters()
if result:
    print("[成功] SIR参数估计完成!")
else:
    print("[失败] SIR参数估计失败")