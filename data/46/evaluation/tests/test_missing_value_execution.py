#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试2.2.1b 数据预处理 - 缺失值处理执行

测试验证处理后的数据是否正确填充了缺失值，并显示处理结果统计。
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


class TestMissingValueExecution:
    """缺失值处理执行测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = ConfigManager()
        self.preprocessor = DataPreprocessor(self.config)
        
        # 准备 (Arrange): 选择一种填充方法（如均值填充）
        # 创建包含缺失值的测试数据
        np.random.seed(42)
        n_samples = 100
        
        ages = np.random.normal(40, 15, n_samples)
        incomes = np.random.normal(50000, 20000, n_samples)
        scores = np.random.normal(650, 100, n_samples)
        
        # 添加缺失值
        missing_indices_age = np.random.choice(n_samples, 15, replace=False)
        missing_indices_income = np.random.choice(n_samples, 10, replace=False)
        missing_indices_score = np.random.choice(n_samples, 8, replace=False)
        
        ages[missing_indices_age] = np.nan
        incomes[missing_indices_income] = np.nan
        scores[missing_indices_score] = np.nan
        
        self.test_data = pd.DataFrame({
            'age': ages,
            'income': incomes,
            'score': scores,
            'category': np.random.choice(['A', 'B', 'C'], n_samples),
            'target': np.random.choice([0, 1], n_samples)
        })
        
        # 记录原始缺失值统计
        self.original_missing_stats = {
            'age': self.test_data['age'].isnull().sum(),
            'income': self.test_data['income'].isnull().sum(),
            'score': self.test_data['score'].isnull().sum(),
            'total': self.test_data.isnull().sum().sum()
        }
    
    def test_missing_value_execution(self):
        """测试缺失值处理执行"""
        # 验证原始数据确实包含缺失值
        assert self.original_missing_stats['total'] > 0, "原始数据应该包含缺失值"
        
        print(f"原始缺失值统计: {self.original_missing_stats}")
        
        # 执行 (Act): 执行缺失值处理操作
        processed_data = self.preprocessor.handle_missing_values(
            self.test_data.copy(), strategy='mean'
        )
        
        # 断言 (Assert): 验证处理后的数据是否正确填充了缺失值，并显示处理结果统计
        
        # 1. 验证数据结构保持不变
        assert isinstance(processed_data, pd.DataFrame), "处理后应该返回DataFrame"
        assert len(processed_data) == len(self.test_data), "数据行数应该保持不变"
        assert len(processed_data.columns) == len(self.test_data.columns), "数据列数应该保持不变"
        
        # 2. 验证数值列的缺失值被正确填充
        numeric_columns = self.test_data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col != 'target':  # target列通常不需要填充
                original_missing = self.test_data[col].isnull().sum()
                processed_missing = processed_data[col].isnull().sum()
                
                if original_missing > 0:
                    assert processed_missing == 0, f"{col}列的缺失值应该被完全填充"
                    
                    # 验证填充值是合理的（接近均值）
                    original_mean = self.test_data[col].mean()
                    filled_values = processed_data.loc[self.test_data[col].isnull(), col]
                    
                    # 填充值应该等于或接近原始数据的均值
                    for filled_val in filled_values:
                        assert abs(filled_val - original_mean) < 1e-10, f"{col}列填充值应该等于均值"
        
        # 3. 显示处理结果统计
        processed_missing_stats = {
            'age': processed_data['age'].isnull().sum(),
            'income': processed_data['income'].isnull().sum(), 
            'score': processed_data['score'].isnull().sum(),
            'total': processed_data.isnull().sum().sum()
        }
        
        print(f"处理后缺失值统计: {processed_missing_stats}")
        
        # 4. 验证缺失值数量显著减少
        assert processed_missing_stats['total'] < self.original_missing_stats['total'], "总缺失值数量应该减少"
        
        # 5. 计算并显示处理效果
        filled_count = self.original_missing_stats['total'] - processed_missing_stats['total']
        fill_rate = (filled_count / self.original_missing_stats['total']) * 100 if self.original_missing_stats['total'] > 0 else 0
        
        print(f"填充统计: 原始缺失{self.original_missing_stats['total']}个, 填充{filled_count}个, 填充率{fill_rate:.1f}%")
        
        # 6. 验证处理效果符合预期
        assert fill_rate >= 80, f"数值列的填充率应该至少80%，实际{fill_rate:.1f}%"
        
        print("缺失值处理执行测试通过：处理后的数据正确填充了缺失值，处理结果统计符合预期")


if __name__ == "__main__":
    pytest.main([__file__])