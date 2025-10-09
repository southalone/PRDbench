#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析file_comparison测试中expected_output_files是否正确
"""

import json
import os

def analyze_expected_files():
    """分析期望输出文件的正确性"""
    
    with open('detailed_test_plan.json', 'r', encoding='utf-8') as f:
        tests = json.load(f)
    
    file_comparison_tests = [test for test in tests if test.get('type') == 'file_comparison']
    
    print("分析file_comparison测试的expected_output_files")
    print("="*80)
    
    for i, test in enumerate(file_comparison_tests, 1):
        metric = test['metric']
        expected_files = test.get('expected_output_files', [])
        test_command = test['testcases'][0].get('test_command', '')
        
        print(f"\n{i}. {metric}")
        print(f"   期望输出文件: {expected_files}")
        print(f"   测试命令: {test_command}")
        
        # 分析每个测试应该生成的实际文件
        analysis = ""
        suggested_file = ""
        
        if "CSV数据导出" in metric:
            analysis = "应该导出实际的CSV文件"
            suggested_file = "exported_users.csv 或类似的导出文件"
            
        elif "TF-IDF矩阵转化" in metric:
            analysis = "应该生成实际的TF-IDF矩阵文件"
            suggested_file = "tfidf_matrix.csv 或 results/tfidf_output.csv"
            
        elif "用户属性偏好建模" in metric:
            analysis = "应该生成实际的用户偏好文件"
            suggested_file = "user_preferences.json 或 models/user_preferences.json"
            
        elif "稀疏矩阵处理" in metric:
            analysis = "应该生成实际的稀疏矩阵报告文件"
            suggested_file = "sparse_report.txt 或 results/sparse_analysis.txt"
            
        elif "matplotlib图表生成" in metric:
            analysis = "应该生成实际的图表文件"
            suggested_file = "algorithm_comparison_chart.png 或 results/*.png"
            
        elif "决策复杂度评估" in metric:
            analysis = "应该生成实际的复杂度报告文件"
            suggested_file = "complexity_report.json 或 results/complexity_analysis.json"
            
        elif "核心操作日志" in metric:
            analysis = "应该检查实际的日志文件 - 已修正"
            suggested_file = "logs/system.log - 已正确"
            
        elif "权限管理" in metric:
            analysis = "应该生成实际的权限测试记录文件"
            suggested_file = "permission_log.json 或 logs/permission_test.json"
        
        print(f"   分析: {analysis}")
        print(f"   建议文件: {suggested_file}")
        
        # 检查当前expected文件是否为"期望模板"还是"实际输出"
        if expected_files:
            for expected_file in expected_files:
                if expected_file.startswith('expected_'):
                    print(f"   [需要修正] {expected_file} 似乎是期望模板，应该改为实际生成的文件路径")
                elif expected_file.startswith('logs/'):
                    print(f"   [正确] {expected_file} 是实际文件路径")
                else:
                    print(f"   [检查] {expected_file} 需要确认是否为程序实际生成的文件")
        
        print("   " + "-"*70)

if __name__ == "__main__":
    analyze_expected_files()