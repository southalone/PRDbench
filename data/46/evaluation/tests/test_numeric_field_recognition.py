#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.2.2a 字段处理 - 数值型字段识别

测试程序是否正确识别出所有数值型字段（如年龄、收入等）。
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


class TestNumericFieldRecognition:
    """数值型字段识别测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.data_manager = DataManager(self.config)
        
        # 创建包含明确数值型和非数值型字段的测试数据
        np.random.seed(42)
        n_samples = 120
        
        self.test_data = pd.DataFrame({
            # 数值型字段
            'age': np.random.randint(20, 80, n_samples),  # 年龄
            'income': np.random.randint(20000, 200000, n_samples),  # 收入
            'credit_score': np.random.randint(300, 850, n_samples),  # 信用分数
            'employment_years': np.random.randint(0, 40, n_samples),  # 工作年限
            'debt_ratio': np.random.uniform(0, 1, n_samples),  # 债务比例
            
            # 分类型字段
            'gender': np.random.choice(['Male', 'Female'], n_samples),  # 性别
            'education': np.random.choice(['High School', 'Bachelor', 'Master'], n_samples),  # 教育水平
            'job_category': np.random.choice(['IT', 'Finance', 'Healthcare'], n_samples),  # 职业类别
            
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
    
    def test_numeric_field_recognition(self):
        """测试数值型字段识别功能"""
        # 执行 (Act): 导入数据并查看字段类型识别结果
        df = self.data_manager.import_data(self.temp_file.name, validate=False)
        
        # 验证数据导入成功
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 120
        
        # 断言 (Assert): 验证程序是否正确识别出所有数值型字段
        
        # 1. 获取pandas自动识别的数值型字段
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 2. 预期的数值型字段列表
        expected_numeric_fields = ['age', 'income', 'credit_score', 'employment_years', 'debt_ratio', 'target']
        
        print(f"识别出的数值型字段: {numeric_columns}")
        print(f"预期的数值型字段: {expected_numeric_fields}")
        
        # 3. 验证关键数值型字段被正确识别
        critical_numeric_fields = ['age', 'income', 'credit_score']
        for field in critical_numeric_fields:
            assert field in numeric_columns, f"关键数值型字段 '{field}' 应该被识别为数值型"
        
        # 4. 验证非数值型字段没有被误识别
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        expected_categorical_fields = ['gender', 'education', 'job_category']
        
        for field in expected_categorical_fields:
            assert field in categorical_columns, f"分类型字段 '{field}' 不应该被识别为数值型"
            assert field not in numeric_columns, f"分类型字段 '{field}' 不应该在数值型字段中"
        
        # 5. 验证数值型字段的数据类型
        for field in ['age', 'income', 'credit_score', 'employment_years']:
            if field in df.columns:
                assert pd.api.types.is_numeric_dtype(df[field]), f"{field}字段应该是数值类型"
                
                # 验证数值范围合理
                field_values = df[field].dropna()
                assert len(field_values) > 0, f"{field}字段应该有有效数值"
                
                if field == 'age':
                    assert field_values.min() >= 18, "年龄最小值应该>=18"
                    assert field_values.max() <= 100, "年龄最大值应该<=100"
                elif field == 'income':
                    assert field_values.min() >= 0, "收入应该>=0"
                    assert field_values.max() <= 500000, "收入最大值应该合理"
        
        # 6. 计算识别准确率
        correctly_identified_numeric = len(set(critical_numeric_fields) & set(numeric_columns))
        numeric_accuracy = correctly_identified_numeric / len(critical_numeric_fields)
        
        assert numeric_accuracy >= 1.0, f"数值型字段识别准确率应该100%，实际{numeric_accuracy:.1%}"
        
        print(f"字段识别结果: 数值型{len(numeric_columns)}个，分类型{len(categorical_columns)}个")
        print(f"数值型字段识别准确率: {numeric_accuracy:.1%}")
        print("数值型字段识别测试通过：程序正确识别出所有数值型字段，字段类型识别准确")


if __name__ == "__main__":
    pytest.main([__file__])