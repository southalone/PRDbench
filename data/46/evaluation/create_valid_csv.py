#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建符合系统验证要求的CSV测试数据
"""

import pandas as pd
import numpy as np

# 设置随机种子以确保可重现结果
np.random.seed(42)

# 生成符合验证要求的数据
data = []
for i in range(150):  # 生成150行数据（超过100行最小要求）
    record = {
        'age': np.random.randint(18, 70),
        'income': np.random.randint(20000, 150000),
        'employment_years': np.random.randint(0, 30),
        'debt_ratio': max(0.05, np.random.random() * 0.8),  # 确保大于0.01
        'credit_history': np.random.choice(['excellent', 'good', 'fair', 'poor']),
        'target': np.random.choice([0, 1])  # 添加目标变量
    }
    data.append(record)

# 创建DataFrame并保存
df = pd.DataFrame(data)
df.to_csv('evaluation/test_data_csv.csv', index=False)

print(f"已生成符合验证要求的CSV数据: {len(df)} 行")
print(f"列名: {list(df.columns)}")
print(f"debt_ratio范围: {df['debt_ratio'].min():.4f} - {df['debt_ratio'].max():.4f}")