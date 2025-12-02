#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专用测试脚本：字段类型识别功能测试

直接调用数据预处理功能，测试数值型和分类型字段识别能力
"""

import sys
import os
from pathlib import Path
import pandas as pd

# 添加项目路径
project_root = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(project_root))

try:
    from credit_assessment.data import DataPreprocessor
    from credit_assessment.utils import ConfigManager
    
    def test_field_type_recognition():
        """测试字段类型识别功能"""
        print("=== 字段类型识别测试 ===")
        
        # 初始化预处理器
        config = ConfigManager()
        preprocessor = DataPreprocessor(config)
        
        # 加载测试数据
        csv_file = Path(__file__).parent.parent / "test_data_csv.csv"
        
        if not csv_file.exists():
            print(f"错误：测试数据文件不存在 - {csv_file}")
            return False
        
        try:
            # 读取数据
            print(f"加载测试数据：{csv_file}")
            data = pd.read_csv(csv_file)
            
            print("\n字段类型识别结果：")
            
            # 测试数值型字段识别
            numeric_fields = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
            print(f"识别的数值型字段: {numeric_fields}")
            
            # 验证预期的数值型字段
            expected_numeric = ['age', 'income', 'employment_years', 'debt_ratio', 'target']
            recognized_numeric = set(numeric_fields)
            expected_numeric_set = set(expected_numeric)
            
            # 测试分类型字段识别
            categorical_fields = data.select_dtypes(include=['object']).columns.tolist()
            print(f"识别的分类型字段: {categorical_fields}")
            
            # 验证预期的分类型字段
            expected_categorical = ['credit_history']
            recognized_categorical = set(categorical_fields)
            expected_categorical_set = set(expected_categorical)
            
            # 验证识别准确性
            numeric_correct = len(expected_numeric_set.intersection(recognized_numeric))
            categorical_correct = len(expected_categorical_set.intersection(recognized_categorical))
            
            print(f"\n识别准确性验证：")
            print(f"数值型字段正确识别: {numeric_correct}/{len(expected_numeric_set)}")
            print(f"分类型字段正确识别: {categorical_correct}/{len(expected_categorical_set)}")
            
            if numeric_correct >= len(expected_numeric_set) * 0.8:
                print("✓ 数值型字段识别准确")
                numeric_pass = True
            else:
                print("✗ 数值型字段识别不准确")
                numeric_pass = False
            
            if categorical_correct >= len(expected_categorical_set) * 0.8:
                print("✓ 分类型字段识别准确")
                categorical_pass = True
            else:
                print("✗ 分类型字段识别不准确") 
                categorical_pass = False
            
            return numeric_pass and categorical_pass
                
        except Exception as e:
            print(f"✗ 字段类型识别测试失败: {str(e)}")
            return False
    
    # 执行测试
    if __name__ == "__main__":
        success = test_field_type_recognition()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"模块导入失败: {str(e)}")
    sys.exit(1)