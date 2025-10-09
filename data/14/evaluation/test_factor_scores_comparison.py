#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
因子得分输出文件比对测试脚本
用于验证 "[2.2.2b 因子分析 (因子得分输出)]" 测试用例
"""

import os
import sys
import subprocess
import pandas as pd
from pathlib import Path

def run_factor_analysis():
    """运行因子分析命令"""
    print("🔄 正在执行因子分析命令...")
    
    cmd = [
        "python", "-m", "src.main", "analyze", "factor",
        "--data-path", "evaluation/sample_data.csv",
        "--questions", "price_influence,satisfaction,amenities_importance",
        "--output-dir", "evaluation/reports/factor"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("✅ 因子分析命令执行成功")
            print(f"输出: {result.stdout}")
            return True
        else:
            print(f"❌ 因子分析命令执行失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 执行命令时发生错误: {e}")
        return False

def compare_factor_scores():
    """比较实际输出与期望输出"""
    print("🔍 正在比较因子得分文件...")
    
    actual_file = Path("evaluation/reports/factor/factor_scores.csv")
    expected_file = Path("evaluation/expected_factor_scores.csv")
    
    if not actual_file.exists():
        print(f"❌ 实际输出文件不存在: {actual_file}")
        return False
    
    if not expected_file.exists():
        print(f"❌ 期望输出文件不存在: {expected_file}")
        return False
    
    try:
        # 读取文件
        actual_df = pd.read_csv(actual_file)
        expected_df = pd.read_csv(expected_file)
        
        # 检查形状
        if actual_df.shape != expected_df.shape:
            print(f"❌ 文件形状不匹配: 实际 {actual_df.shape} vs 期望 {expected_df.shape}")
            return False
        
        # 检查列名
        if list(actual_df.columns) != list(expected_df.columns):
            print(f"❌ 列名不匹配: 实际 {list(actual_df.columns)} vs 期望 {list(expected_df.columns)}")
            return False
        
        # 检查数值（允许小的浮点数误差）
        if not actual_df.equals(expected_df):
            # 尝试数值比较（容忍浮点数误差）
            try:
                pd.testing.assert_frame_equal(actual_df, expected_df, rtol=1e-10, atol=1e-10)
                print("✅ 文件内容匹配（在数值误差容忍范围内）")
                return True
            except AssertionError as e:
                print(f"❌ 文件内容不匹配: {e}")
                return False
        else:
            print("✅ 文件内容完全匹配")
            return True
            
    except Exception as e:
        print(f"❌ 比较文件时发生错误: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 因子分析 (因子得分输出) 文件比对测试")
    print("=" * 60)
    
    # 确保在正确的工作目录
    if not Path("src/main.py").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 创建输出目录
    output_dir = Path("evaluation/reports/factor")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 运行因子分析
    if not run_factor_analysis():
        print("❌ 测试失败：因子分析命令执行失败")
        sys.exit(1)
    
    # 比较文件
    if not compare_factor_scores():
        print("❌ 测试失败：文件比对不通过")
        sys.exit(1)
    
    print("=" * 60)
    print("🎉 测试通过！因子得分输出文件与期望输出完全一致")
    print("=" * 60)

if __name__ == "__main__":
    main()