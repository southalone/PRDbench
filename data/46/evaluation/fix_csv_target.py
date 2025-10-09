#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正CSV文件的目标变量列名
"""

import pandas as pd

# 读取当前的CSV文件
df = pd.read_csv('evaluation/test_data_csv.csv')

# 将target列重命名为"目标变量"
if 'target' in df.columns:
    df = df.rename(columns={'target': '目标变量'})
    print("已将target列重命名为'目标变量'")

# 保存修正后的文件
df.to_csv('evaluation/test_data_csv.csv', index=False)

print(f"修正完成: {len(df)} 行数据")
print(f"列名: {list(df.columns)}")