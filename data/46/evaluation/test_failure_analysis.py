#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试失败原因分析工具
分析部分通过和失败的测试，并提供具体修复方案
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def analyze_neural_network_issues():
    """分析神经网络相关问题"""
    print("=== 神经网络模块问题分析 ===")
    
    try:
        import torch
        print("[INFO] PyTorch版本: {}".format(torch.__version__))
        
        # 测试torch.optim.lr_scheduler.ReduceLROnPlateau
        from torch.optim import lr_scheduler
        import torch.nn as nn
        import torch.optim as optim
        
        # 创建简单的测试模型和优化器
        model = nn.Linear(5, 1)
        optimizer = optim.Adam(model.parameters())
        
        # 测试新版本的ReduceLROnPlateau（去掉verbose参数）
        try:
            # 旧版本有verbose参数
            scheduler = lr_scheduler.ReduceLROnPlateau(
                optimizer, mode='min', patience=5, factor=0.5, verbose=True
            )
            print("[ISSUE] 使用了已废弃的verbose参数")
            return "verbose_parameter_deprecated"
        except TypeError as e:
            if 'verbose' in str(e):
                print("[DETECTED] verbose参数在新版PyTorch中已移除")
                # 测试修复方案
                scheduler = lr_scheduler.ReduceLROnPlateau(
                    optimizer, mode='min', patience=5, factor=0.5
                )
                print("[FIX] 移除verbose参数后正常工作")
                return "verbose_parameter_fix_needed"
            else:
                print("[ERROR] 其他PyTorch兼容性问题: {}".format(e))
                return "other_pytorch_issue"
        
    except ImportError as e:
        print("[ERROR] PyTorch导入失败: {}".format(e))
        return "pytorch_import_error"
    except Exception as e:
        print("[ERROR] 未知神经网络问题: {}".format(e))
        return "unknown_neural_issue"

def analyze_pandas_warnings():
    """分析pandas警告问题"""
    print("\n=== Pandas警告问题分析 ===")
    
    try:
        import pandas as pd
        print("[INFO] Pandas版本: {}".format(pd.__version__))
        
        # 创建测试数据
        df = pd.DataFrame({'A': [1, 2, None, 4], 'B': [1, None, 3, 4]})
        
        # 测试问题代码模式
        try:
            # 这种写法在pandas 2.0+会产生FutureWarning
            # df['A'].fillna(0, inplace=True)  # 旧写法
            
            # 新的推荐写法
            df['A'] = df['A'].fillna(0)
            print("[FIX] 使用新的pandas语法避免FutureWarning")
            return "pandas_inplace_warning"
            
        except Exception as e:
            print("[ERROR] pandas测试失败: {}".format(e))
            return "pandas_test_error"
            
    except ImportError as e:
        print("[ERROR] Pandas导入失败: {}".format(e))
        return "pandas_import_error"

def analyze_file_generation_issues():
    """分析文件生成问题"""
    print("\n=== 文件生成问题分析 ===")
    
    # 检查当前目录的图表文件
    chart_files = [
        'feature_importance_top5.png',
        'ks_curve.png', 
        'ks_curve_with_max_distance.png',
        'lift_chart.png',
        'lift_layered_display.png'
    ]
    
    missing_files = []
    existing_files = []
    
    for file_name in chart_files:
        if os.path.exists(file_name):
            existing_files.append(file_name)
            file_size = os.path.getsize(file_name)
            print("[FOUND] {}: {}KB".format(file_name, file_size//1024))
        else:
            missing_files.append(file_name)
            print("[MISSING] {}".format(file_name))
    
    # 检查HTML报告文件
    html_files = ['evaluation_report.html', 'outputs/report.html', 'src/outputs/report.html']
    html_found = False
    for html_file in html_files:
        if os.path.exists(html_file):
            html_found = True
            print("[FOUND] HTML报告: {}".format(html_file))
            break
    
    if not html_found:
        print("[MISSING] HTML报告文件未找到")
        return "html_report_missing"
    
    if missing_files:
        print("[ISSUE] 部分图表文件缺失: {}".format(', '.join(missing_files)))
        return "partial_file_generation"
    
    print("[PASS] 所有必需文件都已生成")
    return "files_complete"

def main():
    """主分析函数"""
    print("开始分析测试失败和部分通过的原因...")
    
    # 分析各种问题
    neural_issue = analyze_neural_network_issues()
    pandas_issue = analyze_pandas_warnings()  
    file_issue = analyze_file_generation_issues()
    
    print("\n=== 修复建议汇总 ===")
    
    # 神经网络问题修复
    if neural_issue == "verbose_parameter_fix_needed":
        print("1. 神经网络修复方案:")
        print("   - 问题：PyTorch新版本移除了verbose参数")
        print("   - 修复：在neural_network.py中移除scheduler的verbose=True参数")
        print("   - 文件：src/credit_assessment/algorithms/neural_network.py:207")
    
    # Pandas警告修复
    if pandas_issue == "pandas_inplace_warning":
        print("2. Pandas警告修复方案:")
        print("   - 问题：使用了废弃的inplace=True链式调用")
        print("   - 修复：改为 df[col] = df[col].fillna(value) 语法")
        print("   - 文件：src/credit_assessment/data/preprocessor.py:154")
    
    # 文件生成问题修复
    if file_issue == "html_report_missing":
        print("3. HTML报告修复方案:")
        print("   - 问题：报告生成路径不正确或功能未完整实现")
        print("   - 修复：检查report_generator.py的文件保存路径")
    
    print("\n=== 优先级建议 ===")
    print("P1 (高优先级)：修复神经网络PyTorch兼容性问题")
    print("P2 (中优先级)：修复pandas FutureWarning")  
    print("P3 (低优先级)：优化HTML报告生成路径")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)