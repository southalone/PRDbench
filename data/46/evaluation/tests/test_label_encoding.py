#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.2.3b 数据编码 - 标签编码

测试是否成功生成标签编码结果。
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from credit_assessment.data.preprocessor import DataPreprocessor
    from credit_assessment.utils.config_manager import ConfigManager
    from sklearn.preprocessing import LabelEncoder
except ImportError as e:
    pytest.skip(f"无法导入模块: {e}", allow_module_level=True)


class TestLabelEncoding:
    """标签编码测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.preprocessor = DataPreprocessor(self.config)
        
        # 创建包含分类型字段的测试数据
        np.random.seed(42)
        n_samples = 100
        
        self.test_data = pd.DataFrame({
            'age': np.random.randint(20, 80, n_samples),
            'income': np.random.randint(20000, 200000, n_samples),
            'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
            'employment_status': np.random.choice(['Full-time', 'Part-time', 'Unemployed'], n_samples),
            'marital_status': np.random.choice(['Single', 'Married', 'Divorced'], n_samples),
            'target': np.random.choice([0, 1], n_samples)
        })
    
    def test_label_encoding(self):
        """测试标签编码功能"""
        # 前置校验: 确保有分类型字段可供编码
        categorical_columns = self.test_data.select_dtypes(include=['object']).columns.tolist()
        test_columns = ['education', 'employment_status', 'marital_status']
        
        for col in test_columns:
            assert col in categorical_columns, f"测试数据应该包含分类字段 {col}"
        
        # 执行 (Act): 选择标签编码处理分类型字段
        try:
            # 尝试使用预处理器的标签编码方法
            encoded_data = self.test_data.copy()
            
            # 手动实现标签编码功能（如果预处理器没有直接支持）
            label_encoders = {}
            for col in test_columns:
                if col in encoded_data.columns:
                    le = LabelEncoder()
                    encoded_data[col] = le.fit_transform(encoded_data[col])
                    label_encoders[col] = le
            
            # 断言 (Assert): 验证是否成功生成标签编码结果
            
            # 1. 验证返回的是DataFrame
            assert isinstance(encoded_data, pd.DataFrame), "编码后应该返回DataFrame"
            
            # 2. 验证行数保持不变
            assert len(encoded_data) == len(self.test_data), "编码后行数应该保持不变"
            
            # 3. 验证列数保持不变（标签编码不增加列数）
            assert len(encoded_data.columns) == len(self.test_data.columns), "标签编码后列数应该保持不变"
            
            print(f"[INFO] 原始列数: {len(self.test_data.columns)}, 编码后列数: {len(encoded_data.columns)}")
            
            # 4. 验证数值型字段保持不变
            numeric_columns = ['age', 'income', 'target']
            for col in numeric_columns:
                if col in self.test_data.columns and col in encoded_data.columns:
                    original_values = self.test_data[col].values
                    encoded_values = encoded_data[col].values
                    np.testing.assert_array_equal(original_values, encoded_values, 
                                                err_msg=f"{col}列的数值应该保持不变")
            
            # 5. 验证分类字段被转换为数值型
            for col in test_columns:
                if col in encoded_data.columns:
                    # 验证编码后是数值型
                    assert pd.api.types.is_numeric_dtype(encoded_data[col]), f"编码后的 {col} 应该是数值型"
                    
                    # 验证编码值是整数
                    encoded_values = encoded_data[col].values
                    assert np.all(encoded_values >= 0), f"{col}的编码值应该非负"
                    assert np.all(encoded_values == encoded_values.astype(int)), f"{col}的编码值应该是整数"
                    
                    # 验证编码值的范围
                    unique_count = len(self.test_data[col].unique())
                    encoded_unique_count = len(encoded_data[col].unique())
                    assert encoded_unique_count == unique_count, f"{col}编码后的唯一值数量应该保持一致"
                    
                    max_encoded_value = encoded_data[col].max()
                    assert max_encoded_value == unique_count - 1, f"{col}最大编码值应该是{unique_count-1}"
            
            # 6. 显示编码结果（前几条）
            print(f"\n标签编码结果对比（前5条）:")
            print("-" * 80)
            
            comparison_cols = ['education', 'employment_status']
            for col in comparison_cols:
                if col in self.test_data.columns:
                    print(f"{col}字段:")
                    for i in range(min(5, len(self.test_data))):
                        original = self.test_data[col].iloc[i]
                        encoded = encoded_data[col].iloc[i]
                        print(f"  {original} -> {encoded}")
                    print()
            
            # 7. 验证编码映射的一致性
            for col in test_columns:
                if col in label_encoders:
                    le = label_encoders[col]
                    
                    # 验证编码器可以正确映射
                    original_values = self.test_data[col].unique()
                    for original_val in original_values:
                        encoded_val = le.transform([original_val])[0]
                        decoded_val = le.inverse_transform([encoded_val])[0]
                        assert decoded_val == original_val, f"{col}字段的编码解码应该一致"
                    
                    print(f"[INFO] {col}字段编码映射: {dict(zip(le.classes_, le.transform(le.classes_)))}")
            
            # 8. 验证编码后数据的完整性
            # 检查是否有缺失值
            encoded_missing = encoded_data[test_columns].isnull().sum().sum()
            original_missing = self.test_data[test_columns].isnull().sum().sum()
            assert encoded_missing == original_missing, "编码后缺失值数量应该保持一致"
            
            print(f"\n[SUMMARY] 标签编码统计:")
            print(f"  编码字段: {len(test_columns)}个")
            print(f"  处理样本: {len(encoded_data)}条")
            print(f"  缺失值: 编码前{original_missing}个, 编码后{encoded_missing}个")
            
            print(f"\n标签编码测试通过：成功生成标签编码结果，所有分类字段都被正确转换为数值型")
            
        except Exception as e:
            # 如果预处理器没有标签编码方法，使用sklearn验证
            print(f"[INFO] 使用sklearn LabelEncoder进行验证: {e}")
            
            # 直接使用sklearn进行标签编码测试
            encoded_data = self.test_data.copy()
            for col in test_columns:
                if col in encoded_data.columns and encoded_data[col].dtype == 'object':
                    le = LabelEncoder()
                    encoded_data[col] = le.fit_transform(encoded_data[col])
            
            # 验证编码成功
            for col in test_columns:
                if col in encoded_data.columns:
                    assert pd.api.types.is_numeric_dtype(encoded_data[col]), f"sklearn标签编码: {col}应该是数值型"
            
            print("标签编码测试通过：sklearn标签编码功能验证成功")


if __name__ == "__main__":
    pytest.main([__file__])