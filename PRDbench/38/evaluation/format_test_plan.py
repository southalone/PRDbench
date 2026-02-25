#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试计划格式转换脚本
只保留标准格式字段，移除运行时生成的字段
"""

import json
import os

def format_test_plan():
    """格式化测试计划，只保留标准字段"""
    
    # 读取原始测试计划
    input_file = 'detailed_test_plan.json'
    output_file = 'detailed_test_plan_fixed.json'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # 标准格式字段
    standard_fields = [
        'metric',
        'description', 
        'type',
        'testcases',
        'input_files',
        'expected_output_files',
        'expected_output'
    ]
    
    # 转换数据
    formatted_data = []
    
    for item in original_data:
        # 只保留标准字段
        formatted_item = {}
        for field in standard_fields:
            if field in item:
                formatted_item[field] = item[field]
        
        formatted_data.append(formatted_item)
    
    # 保存格式化后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)
    
    print(f"格式转换完成!")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"处理项目数: {len(formatted_data)}")
    
    # 显示移除的字段
    removed_fields = set()
    for item in original_data:
        for field in item.keys():
            if field not in standard_fields:
                removed_fields.add(field)
    
    if removed_fields:
        print(f"移除字段: {', '.join(removed_fields)}")

if __name__ == '__main__':
    format_test_plan()