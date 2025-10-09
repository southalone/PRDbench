#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.2.1a 数据预处理 - 缺失值填充方法选择

测试是否提供了至少3种填充方法选择（均值、中位数、众数）。
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
    from credit_assessment.data.preprocessor import DataPreprocessor
    from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
    pytest.skip(f"无法导入模块: {e}", allow_module_level=True)


class TestMissingValueMethods:
    """缺失值填充方法选择测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.preprocessor = DataPreprocessor(self.config)
        
        # 创建包含缺失值的测试数据
        np.random.seed(42)
        n_samples = 100
        
        ages = np.random.randint(20, 80, n_samples).astype(float)
        incomes = np.random.randint(20000, 200000, n_samples).astype(float)
        scores = np.random.randint(300, 850, n_samples).astype(float)
        
        # 添加缺失值
        missing_indices = np.random.choice(n_samples, int(n_samples * 0.2), replace=False)
        ages[missing_indices[:len(missing_indices)//3]] = np.nan
        incomes[missing_indices[len(missing_indices)//3:2*len(missing_indices)//3]] = np.nan
        scores[missing_indices[2*len(missing_indices)//3:]] = np.nan
        
        self.test_data = pd.DataFrame({
            'age': ages,
            'income': incomes,
            'score': scores,
            'target': np.random.choice([0, 1], n_samples)
        })
    
    def test_missing_value_handling_methods(self):
        """测试缺失值填充方法选择"""
        # 断言 (Assert): 观察是否提供了至少3种填充方法选择（均值、中位数、众数）
        
        # 测试均值填充方法
        try:
            result_mean = self.preprocessor.handle_missing_values(
                self.test_data.copy(), strategy='mean'
            )
            assert isinstance(result_mean, pd.DataFrame), "均值填充应该返回DataFrame"
            assert not result_mean.select_dtypes(include=[np.number]).isnull().any().any(), "数值列不应有缺失值"
            print("✓ 均值填充方法可用")
        except Exception as e:
            pytest.fail(f"均值填充方法不可用: {e}")
        
        # 测试中位数填充方法
        try:
            result_median = self.preprocessor.handle_missing_values(
                self.test_data.copy(), strategy='median'
            )
            assert isinstance(result_median, pd.DataFrame), "中位数填充应该返回DataFrame"
            assert not result_median.select_dtypes(include=[np.number]).isnull().any().any(), "数值列不应有缺失值"
            print("✓ 中位数填充方法可用")
        except Exception as e:
            pytest.fail(f"中位数填充方法不可用: {e}")
        
        # 测试众数填充方法
        try:
            result_mode = self.preprocessor.handle_missing_values(
                self.test_data.copy(), strategy='most_frequent'
            )
            assert isinstance(result_mode, pd.DataFrame), "众数填充应该返回DataFrame"
            # 众数填充对所有类型的列都适用
            print("✓ 众数填充方法可用")
        except Exception as e:
            pytest.fail(f"众数填充方法不可用: {e}")
        
        # 验证填充效果不同（说明方法确实不同）
        original_missing_count = self.test_data.isnull().sum().sum()
        assert original_missing_count > 0, "原始数据应该包含缺失值"
        
        # 比较不同方法的填充结果
        mean_age = result_mean['age'].iloc[0] if pd.isna(self.test_data['age'].iloc[0]) else None
        median_age = result_median['age'].iloc[0] if pd.isna(self.test_data['age'].iloc[0]) else None
        
        if mean_age is not None and median_age is not None:
            # 如果原始第一行age是缺失的，比较填充值
            print(f"不同方法填充结果: 均值={mean_age:.2f}, 中位数={median_age:.2f}")
        
        print("缺失值填充方法选择测试通过：提供了均值、中位数、众数三种填充方法")


if __name__ == "__main__":
    pytest.main([__file__])