#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建Excel期望输出文件
"""
import pandas as pd
import os

def create_expected_excel():
    """创建期望的Excel输出文件"""
    # 创建期望的Excel数据
    expected_data = pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5],
        'age': [25, 35, 45, 30, 55],
        'income': [50000, 75000, 60000, 80000, 45000],
        'credit_score': [650, 700, 620, 750, 580],
        'risk_score': [0.3, 0.2, 0.4, 0.1, 0.6],
        'target': [1, 0, 1, 0, 1]
    })
    
    # 保存为Excel文件
    output_path = "expected_excel_export.xlsx"
    expected_data.to_excel(output_path, index=False)
    
    print(f"期望Excel文件已创建: {output_path}")
    print(f"数据形状: {expected_data.shape}")
    return output_path

if __name__ == "__main__":
    create_expected_excel()