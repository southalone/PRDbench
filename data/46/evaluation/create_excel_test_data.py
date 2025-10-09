#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建Excel格式的测试数据文件
"""

import pandas as pd
import numpy as np

# 创建Excel测试数据
np.random.seed(42)
data = []
for i in range(120):  # 超过100行要求
    record = {
        'age': np.random.randint(18, 70),
        'income': np.random.randint(20000, 150000),
        'employment_years': np.random.randint(0, 30),
        'debt_ratio': max(0.05, np.random.random() * 0.8),
        'credit_history': np.random.choice(['excellent', 'good', 'fair', 'poor']),
        '目标变量': np.random.choice([0, 1])
    }
    data.append(record)

df = pd.DataFrame(data)

# 保存为Excel文件
df.to_excel('evaluation/test_data_excel.xlsx', index=False)

print(f"已创建Excel测试数据: {len(df)} 行")
print(f"文件: evaluation/test_data_excel.xlsx")
print(f"列名: {list(df.columns)}")