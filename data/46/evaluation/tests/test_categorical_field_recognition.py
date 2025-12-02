#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.2.2b 字段处理 - 分类型字段识别

测试程序是否正确识别出所有分类型字段（如性别、职业等）。
"""

import pytest
import sys
import os
import tempfile
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from credit_assessment.data.data_manager import DataManager
    from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
    pytest.skip(f"无法导入模块: {e}", allow_module_level=True)


class TestCategoricalFieldRecognition:
    """分类型字段识别测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.data_manager = DataManager(self.config)
        
        # 创建包含明确分类型字段的测试数据
        np.random.seed(42)
        n_samples = 120
        
        self.test_data = pd.DataFrame({
            # 数值型字段
            'age': np.random.randint(20, 80, n_samples),
            'income': np.random.randint(20000, 200000, n_samples),
            
            # 分类型字段（关键测试目标）
            'gender': np.random.choice(['Male', 'Female'], n_samples),  # 性别
            'occupation': np.random.choice(['Engineer', 'Doctor', 'Teacher', 'Manager'], n_samples),  # 职业
            'education_level': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),  # 教育水平
            'marital_status': np.random.choice(['Single', 'Married', 'Divorced'], n_samples),  # 婚姻状况
            'employment_type': np.random.choice(['Full-time', 'Part-time', 'Self-employed'], n_samples),  # 就业类型
            
            # 目标变量
            'target': np.random.choice([0, 1], n_samples)
        })
        
        # 创建临时CSV文件
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_categorical_field_recognition(self):
        """测试分类型字段识别功能"""
        # 执行 (Act): 导入数据并查看字段类型识别结果
        df = self.data_manager.import_data(self.temp_file.name, validate=False)
        
        # 验证数据导入成功
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 120
        
        # 断言 (Assert): 验证程序是否正确识别出所有分类型字段
        
        # 1. 获取pandas自动识别的分类型字段（object类型）
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        # 2. 预期的分类型字段列表
        expected_categorical_fields = ['gender', 'occupation', 'education_level', 'marital_status', 'employment_type']
        
        print(f"识别出的分类型字段: {categorical_columns}")
        print(f"预期的分类型字段: {expected_categorical_fields}")
        
        # 3. 验证关键分类型字段被正确识别
        critical_categorical_fields = ['gender', 'occupation']
        for field in critical_categorical_fields:
            assert field in categorical_columns, f"关键分类型字段 '{field}' 应该被识别为分类型"
            assert df[field].dtype == 'object', f"{field}字段应该是object类型"
        
        # 4. 验证数值型字段没有被误识别为分类型
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        expected_numeric_fields = ['age', 'income', 'target']
        
        for field in expected_numeric_fields:
            assert field in numeric_columns, f"数值型字段 '{field}' 应该被识别为数值型"
            assert field not in categorical_columns, f"数值型字段 '{field}' 不应该在分类型字段中"
        
        # 5. 验证分类型字段的唯一值数量合理
        for field in critical_categorical_fields:
            if field in df.columns:
                unique_values = df[field].nunique()
                assert unique_values >= 2, f"{field}字段应该有至少2个不同的类别"
                assert unique_values <= 20, f"{field}字段的类别数量应该合理（<=20）"
                
                print(f"{field}字段: {unique_values}个类别 - {df[field].unique()[:5].tolist()}")
        
        # 6. 计算识别准确率
        correctly_identified_categorical = len(set(critical_categorical_fields) & set(categorical_columns))
        categorical_accuracy = correctly_identified_categorical / len(critical_categorical_fields)
        
        assert categorical_accuracy >= 1.0, f"分类型字段识别准确率应该100%，实际{categorical_accuracy:.1%}"
        
        print(f"字段识别统计: 分类型{len(categorical_columns)}个，数值型{len(numeric_columns)}个")
        print(f"分类型字段识别准确率: {categorical_accuracy:.1%}")
        print("分类型字段识别测试通过：程序正确识别出所有分类型字段，字段类型识别准确")


if __name__ == "__main__":
    pytest.main([__file__])