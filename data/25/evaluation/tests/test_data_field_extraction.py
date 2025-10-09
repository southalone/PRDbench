# -*- coding: utf-8 -*-
"""
数据字段提取与验证单元测试
测试DataProcessor类中关键字段提取功能
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processing import DataProcessor


class TestDataFieldExtraction:
    """数据字段提取与验证测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.processor = DataProcessor()
        
    def test_key_field_extraction_and_validation(self):
        """测试关键字段提取与验证
        
        验证：
        1. 提取的字段数量为4个
        2. 字段名称正确
        3. 数据类型转换准确（日期为datetime类型，数值为int或float类型）
        4. 无缺失值处理错误
        """
        
        # 创建示例数据进行测试
        self.processor.create_sample_data()
        
        # 验证原始数据已加载
        assert self.processor.raw_data is not None, "原始数据应该被成功创建"
        
        # 验证关键字段存在
        required_fields = [
            'date',
            'cumulative_confirmed', 
            'cumulative_deaths',
            'cumulative_recovered'
        ]
        
        # 检查字段数量
        actual_key_fields = [col for col in self.processor.raw_data.columns 
                           if col in required_fields]
        assert len(actual_key_fields) == 4, f"应该有4个关键字段，实际有{len(actual_key_fields)}个"
        
        # 检查字段名称正确性
        for field in required_fields:
            assert field in self.processor.raw_data.columns, f"缺少必要字段: {field}"
        
        # 验证数据类型
        # 日期字段应该是datetime类型
        date_series = self.processor.raw_data['date']
        assert pd.api.types.is_datetime64_any_dtype(date_series), \
            f"日期字段类型错误，期望datetime，实际{date_series.dtype}"
        
        # 数值字段应该是数值类型（int或float）
        numeric_fields = ['cumulative_confirmed', 'cumulative_deaths', 'cumulative_recovered']
        for field in numeric_fields:
            field_series = self.processor.raw_data[field]
            assert pd.api.types.is_numeric_dtype(field_series), \
                f"数值字段{field}类型错误，期望数值类型，实际{field_series.dtype}"
        
        # 验证无缺失值处理错误
        for field in required_fields:
            field_series = self.processor.raw_data[field]
            nan_count = field_series.isna().sum()
            assert nan_count == 0, f"字段{field}存在{nan_count}个缺失值"
        
        # 验证数值字段的基本逻辑性（非负数等）
        for field in numeric_fields:
            values = self.processor.raw_data[field].values
            
            # 检查非负数
            assert np.all(values >= 0), f"字段{field}包含负值"
            
            # 检查数据范围合理性（不应该有异常大的值）
            max_reasonable_value = 1e8  # 设定一个合理的上限
            assert np.all(values <= max_reasonable_value), \
                f"字段{field}包含异常大的值: max={np.max(values)}"
        
        print("关键字段提取与验证测试通过")
        
    def test_field_extraction_with_real_data(self):
        """测试使用真实数据文件的字段提取（如果文件存在）"""
        
        # 尝试加载真实数据
        data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'epidemic_data.xlsx')
        
        if os.path.exists(data_file):
            success = self.processor.load_raw_data(data_file)
            
            if success:
                # 执行数据验证
                validation_result = self.processor.validate_data()
                assert validation_result, "数据验证应该成功"
                
                # 检查数据形状
                assert len(self.processor.raw_data) > 0, "数据应该包含行"
                assert len(self.processor.raw_data.columns) > 0, "数据应该包含列"
                
                print(f"真实数据文件测试通过，数据形状: {self.processor.raw_data.shape}")
            else:
                print("真实数据文件存在但加载失败，跳过此测试")
        else:
            print("真实数据文件不存在，跳过此测试")
    
    def test_data_type_conversion_accuracy(self):
        """测试数据类型转换的准确性"""
        
        # 创建包含不同数据类型的测试数据
        test_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=10),
            'cumulative_confirmed': range(0, 100, 10),  # 整数
            'cumulative_deaths': [float(x) for x in range(0, 10)],  # 浮点数
            'cumulative_recovered': np.array(range(0, 50, 5))  # numpy数组
        })
        
        self.processor.raw_data = test_data
        
        # 验证数据类型转换
        assert pd.api.types.is_datetime64_any_dtype(test_data['date']), "日期类型转换失败"
        assert pd.api.types.is_integer_dtype(test_data['cumulative_confirmed']), "整数类型保持正确"
        assert pd.api.types.is_float_dtype(test_data['cumulative_deaths']), "浮点数类型保持正确"
        assert pd.api.types.is_numeric_dtype(test_data['cumulative_recovered']), "数值数组类型转换正确"
        
        print("数据类型转换准确性测试通过")
    
    def test_missing_value_handling(self):
        """测试缺失值处理"""
        
        # 创建包含缺失值的测试数据
        test_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=5),
            'cumulative_confirmed': [10, 20, np.nan, 40, 50],
            'cumulative_deaths': [1, 2, 3, np.nan, 5],
            'cumulative_recovered': [8, 15, 25, 35, np.nan]
        })
        
        self.processor.raw_data = test_data
        
        # 执行数据验证，应该检测到缺失值
        validation_result = self.processor.validate_data()
        
        # 验证缺失值被正确识别
        for col in ['cumulative_confirmed', 'cumulative_deaths', 'cumulative_recovered']:
            has_missing = test_data[col].isna().any()
            assert has_missing, f"应该检测到字段{col}中的缺失值"
        
        print("缺失值处理测试通过")


if __name__ == "__main__":
    # 运行测试
    test_instance = TestDataFieldExtraction()
    test_instance.setup_method()
    
    try:
        test_instance.test_key_field_extraction_and_validation()
        test_instance.test_field_extraction_with_real_data()
        test_instance.test_data_type_conversion_accuracy()
        test_instance.test_missing_value_handling()
        print("\n所有测试通过！")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")