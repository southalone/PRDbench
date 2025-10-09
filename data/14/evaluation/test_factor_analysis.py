#!/usr/bin/env python3
"""
因子分析测试脚本
测试因子分析功能的文件比对测试
"""

import subprocess
import sys
import os
import pandas as pd
from pathlib import Path

def run_command(command):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def compare_csv_files(expected_file, actual_file):
    """比较两个CSV文件的内容"""
    try:
        expected_df = pd.read_csv(expected_file)
        actual_df = pd.read_csv(actual_file)
        
        # 检查形状是否一致
        if expected_df.shape != actual_df.shape:
            return False, f"文件形状不匹配: 期望 {expected_df.shape}, 实际 {actual_df.shape}"
        
        # 检查列名是否一致
        if list(expected_df.columns) != list(actual_df.columns):
            return False, f"列名不匹配: 期望 {list(expected_df.columns)}, 实际 {list(actual_df.columns)}"
        
        # 检查索引是否一致
        if list(expected_df.index) != list(actual_df.index):
            return False, f"索引不匹配: 期望 {list(expected_df.index)}, 实际 {list(actual_df.index)}"
        
        return True, "文件内容匹配"
        
    except Exception as e:
        return False, f"比较文件时出错: {str(e)}"

def test_factor_analysis():
    """测试因子分析功能"""
    print("=" * 60)
    print("因子分析测试")
    print("=" * 60)
    
    # 测试命令
    test_command = 'python -m src.main analyze factor --data-path evaluation/sample_data.csv --questions "price_influence,satisfaction,amenities_importance" --output-dir evaluation/reports/factor'
    
    print(f"执行命令: {test_command}")
    
    # 执行命令
    returncode, stdout, stderr = run_command(test_command)
    
    print(f"返回码: {returncode}")
    print(f"标准输出: {stdout}")
    if stderr:
        print(f"标准错误: {stderr}")
    
    # 检查命令是否成功执行
    if returncode != 0:
        print("❌ 命令执行失败")
        return False
    
    # 检查输出文件是否存在
    expected_file = "evaluation/reports/factor/factor_loadings.csv"
    if not os.path.exists(expected_file):
        print(f"❌ 期望的输出文件不存在: {expected_file}")
        return False
    
    print(f"✅ 输出文件已生成: {expected_file}")
    
    # 检查文件内容
    try:
        df = pd.read_csv(expected_file, index_col=0)
        print(f"✅ 文件格式正确，形状: {df.shape}")
        print("文件内容预览:")
        print(df.head())
        
        # 检查是否包含期望的变量
        expected_variables = ['price_influence', 'satisfaction', 'amenities_importance']
        if df.index.tolist() == expected_variables:
            print("✅ 包含所有期望的分析变量")
        else:
            print(f"❌ 变量不匹配，期望: {expected_variables}, 实际: {df.index.tolist()}")
            return False
            
        # 检查是否有因子列
        factor_columns = [col for col in df.columns if col.startswith('Factor_')]
        if len(factor_columns) >= 1:
            print(f"✅ 包含 {len(factor_columns)} 个因子: {factor_columns}")
        else:
            print("❌ 未找到因子列")
            return False
            
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")
        return False
    
    print("✅ 因子分析测试通过")
    return True

if __name__ == "__main__":
    success = test_factor_analysis()
    sys.exit(0 if success else 1)