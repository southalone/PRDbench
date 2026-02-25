#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新剩余的unit_test命令

将详细测试计划中剩余的comprehensive_unit_tests.py命令更新为独立测试文件
"""

import json
import os

def update_test_commands():
    """更新测试命令"""
    
    # 读取测试计划
    with open('detailed_test_plan.json', 'r', encoding='utf-8') as f:
        test_plan = json.load(f)
    
    # 测试命令映射
    test_command_mapping = {
        # 已完成的独立测试文件
        "2.1.2a 数据校验 - 缺失值检测": "python -m pytest tests/test_missing_values_detection.py -v",
        "2.1.2b 数据校验 - 异常数据检测": "python -m pytest tests/test_anomaly_detection.py -v", 
        "2.1.2c 数据校验 - 类型不符提示": "python -m pytest tests/test_type_validation.py -v",
        "2.2.1a 数据预处理 - 缺失值填充方法选择": "python -m pytest tests/test_missing_value_methods.py -v",
        "2.2.1b 数据预处理 - 缺失值处理执行": "python -m pytest tests/test_missing_value_execution.py -v",
        "2.2.2a 字段处理 - 数值型字段识别": "python tests/test_numeric_field_recognition.py",
        "2.2.2b 字段处理 - 分类型字段识别": "python tests/test_categorical_field_recognition.py",
        "2.2.3a 数据编码 - 独热编码": "python tests/test_onehot_encoding.py",
        "2.3.3a 算法执行 - Logistic回归分析日志": "python tests/test_logistic_regression_analysis.py",
        "2.3.3b 算法执行 - 神经网络分析日志": "python tests/test_neural_network_analysis.py",
        "2.3.4 算法性能对比功能": "python tests/test_algorithm_comparison.py",
        "2.4.1a 评分预测 - 单条数据评分": "python tests/test_single_record_scoring.py",
        "2.4.1b 评分预测 - 批量数据评分": "python tests/test_batch_scoring.py",
        "2.5.1b ROC曲线 - AUC数值计算": "python tests/test_auc_calculation.py",
        "2.5.4a 基础指标 - 精度召回率F1计算": "python tests/test_basic_metrics.py",
        "2.5.4b 基础指标 - 混淆矩阵": "python tests/test_confusion_matrix.py",
        "2.6.2 模型效果总结": "python tests/test_model_effect_summary.py",
        "2.7.1a 特征解释 - Logistic回归系数输出": "python tests/test_logistic_coefficients.py",
        
        # 剩余的使用综合测试套件
        "2.2.3b 数据编码 - 标签编码": "python comprehensive_unit_tests.py",
        "2.2.4 特征选择 - 相关系数计算": "python comprehensive_unit_tests.py", 
        "2.3.1 算法选择 - Logistic回归": "python comprehensive_unit_tests.py",
        "2.3.2 算法选择 - 神经网络": "python comprehensive_unit_tests.py",
        "2.5.2a K-S曲线 - 图像生成": "python comprehensive_unit_tests.py",
        "2.5.2b K-S曲线 - 最大KS距离标注": "python comprehensive_unit_tests.py",
        "2.5.3a LIFT图 - 图像生成": "python comprehensive_unit_tests.py",
        "2.5.3b LIFT图 - 分层提升度显示": "python comprehensive_unit_tests.py",
        "2.6.1b 报告内容 - 统计图表包含": "python comprehensive_unit_tests.py",
        "2.7.1b 特征解释 - Top-N重要性可视化": "python comprehensive_unit_tests.py",
        "2.7.2a 神经网络解释 - 权重输出": "python comprehensive_unit_tests.py",
        "2.7.2b 神经网络解释 - 特征贡献可视化": "python comprehensive_unit_tests.py"
    }
    
    # 更新测试计划
    updated_count = 0
    for test_item in test_plan:
        metric = test_item.get('metric', '')
        test_type = test_item.get('type', '')
        
        if test_type == 'unit_test' and metric in test_command_mapping:
            current_command = test_item['testcases'][0]['test_command']
            new_command = test_command_mapping[metric]
            
            if current_command != new_command:
                test_item['testcases'][0]['test_command'] = new_command
                updated_count += 1
                print(f"[UPDATE] {metric}: {new_command}")
    
    # 保存更新后的测试计划
    with open('detailed_test_plan.json', 'w', encoding='utf-8') as f:
        json.dump(test_plan, f, indent=4, ensure_ascii=False)
    
    print(f"\n[SUMMARY] 总共更新了{updated_count}个测试命令")
    
    # 统计测试类型分布
    test_type_stats = {}
    for test_item in test_plan:
        test_type = test_item.get('type', 'unknown')
        test_type_stats[test_type] = test_type_stats.get(test_type, 0) + 1
    
    print(f"\n测试类型统计:")
    for test_type, count in test_type_stats.items():
        print(f"  {test_type}: {count}个")
    
    return updated_count

if __name__ == "__main__":
    updated_count = update_test_commands()
    print(f"\n批量更新完成！更新了{updated_count}个测试命令。")