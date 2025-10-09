#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大批量测试数据生成脚本

生成用于批量评分和性能测试的标准数据集
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse

def generate_credit_data(num_records, seed=42, include_target=True):
    """
    生成信用评估测试数据
    
    Args:
        num_records: 生成的记录数
        seed: 随机种子
        include_target: 是否包含目标变量
    
    Returns:
        pandas.DataFrame: 生成的数据集
    """
    np.random.seed(seed)
    
    # 生成基础客户信息
    data = {
        'customer_id': [f'CUST_{str(i).zfill(6)}' for i in range(1, num_records + 1)],
        'age': np.random.normal(35, 10, num_records).astype(int).clip(18, 70),
        'income': np.random.lognormal(10.5, 0.5, num_records).astype(int),
        'employment_years': np.random.exponential(5, num_records).astype(int).clip(0, 30),
        'debt_ratio': np.random.beta(2, 5, num_records).clip(0, 1),
        'credit_history': np.random.choice(
            ['excellent', 'good', 'fair', 'poor'], 
            num_records, 
            p=[0.2, 0.4, 0.3, 0.1]
        )
    }
    
    # 如果需要目标变量，生成基于特征的合理目标
    if include_target:
        # 基于特征计算信用风险概率
        risk_score = (
            (data['age'] / 70) * 0.2 +
            (np.log(data['income']) / 12) * 0.3 +
            (data['employment_years'] / 30) * 0.2 +
            (1 - data['debt_ratio']) * 0.3
        )
        
        # 根据信用历史调整
        history_multiplier = {
            'excellent': 1.2, 'good': 1.0, 'fair': 0.8, 'poor': 0.5
        }
        risk_score *= [history_multiplier[h] for h in data['credit_history']]
        
        # 转换为二分类目标（0=高风险，1=低风险）
        data['target'] = (risk_score > np.median(risk_score)).astype(int)
    
    return pd.DataFrame(data)

def generate_batch_test_data():
    """生成批量评分测试数据（20条记录）"""
    print("生成批量评分测试数据...")
    batch_data = generate_credit_data(20, seed=123, include_target=False)
    
    output_path = Path(__file__).parent.parent / "test_data_batch.csv"
    batch_data.to_csv(output_path, index=False)
    
    print(f"[SUCCESS] 批量测试数据已生成: {output_path}")
    print(f"  - 记录数: {len(batch_data)}")
    print(f"  - 字段: {list(batch_data.columns)}")
    return output_path

def generate_performance_test_data():
    """生成性能测试数据（1000条记录）"""
    print("生成性能测试数据...")
    performance_data = generate_credit_data(1000, seed=456, include_target=True)
    
    output_path = Path(__file__).parent.parent / "test_data_performance.csv"
    performance_data.to_csv(output_path, index=False)
    
    print(f"[SUCCESS] 性能测试数据已生成: {output_path}")
    print(f"  - 记录数: {len(performance_data)}")
    print(f"  - 字段: {list(performance_data.columns)}")
    return output_path

def generate_anomaly_test_data():
    """生成包含异常数据的测试集"""
    print("生成异常数据测试集...")
    # 先生成正常数据
    normal_data = generate_credit_data(8, seed=789, include_target=True)
    
    # 添加异常数据
    anomaly_records = {
        'customer_id': ['CUST_999991', 'CUST_999992'],
        'age': [-5, 200],  # 异常年龄
        'income': [50000, 80000],
        'employment_years': [5, 3],
        'debt_ratio': [0.3, 0.4],
        'credit_history': ['good', 'fair'],
        'target': [0, 1]
    }
    
    anomaly_df = pd.DataFrame(anomaly_records)
    combined_data = pd.concat([normal_data, anomaly_df], ignore_index=True)
    
    output_path = Path(__file__).parent.parent / "test_data_anomaly.csv"
    combined_data.to_csv(output_path, index=False)
    
    print(f"[SUCCESS] 异常数据测试集已生成: {output_path}")
    print(f"  - 正常记录: {len(normal_data)}")
    print(f"  - 异常记录: {len(anomaly_df)}")
    return output_path

def generate_type_error_test_data():
    """生成包含类型错误的测试集"""
    print("生成类型错误测试集...")
    # 创建包含类型错误的数据
    type_error_data = {
        'customer_id': ['CUST_000001', 'CUST_000002', 'CUST_000003'],
        'age': [25, 'invalid_age', 35],  # 年龄字段包含文本
        'income': ['not_number', 55000, 75000],  # 收入字段包含文本
        'employment_years': [3, 5, 'unknown'],  # 工作年限包含文本
        'debt_ratio': [0.3, 0.2, 0.4],
        'credit_history': ['good', 'excellent', 'fair'],
        'target': [1, 0, 1]
    }
    
    type_error_df = pd.DataFrame(type_error_data)
    
    output_path = Path(__file__).parent.parent / "test_data_type_error.csv"
    type_error_df.to_csv(output_path, index=False)
    
    print(f"[SUCCESS] 类型错误测试集已生成: {output_path}")
    print(f"  - 记录数: {len(type_error_df)}")
    return output_path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生成测试数据')
    parser.add_argument('--type', choices=['batch', 'performance', 'anomaly', 'type_error', 'all'], 
                      default='all', help='生成数据类型')
    
    args = parser.parse_args()
    
    print("=== 大批量测试数据生成器 ===")
    
    if args.type in ['batch', 'all']:
        generate_batch_test_data()
        
    if args.type in ['performance', 'all']:
        generate_performance_test_data()
        
    if args.type in ['anomaly', 'all']:
        generate_anomaly_test_data()
        
    if args.type in ['type_error', 'all']:
        generate_type_error_test_data()
    
    print("\n数据生成完成！")

if __name__ == "__main__":
    main()