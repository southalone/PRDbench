import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data.preprocessor import DataPreprocessor


class TestMissingValueHandling:
    """缺失值处理单元测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.preprocessor = DataPreprocessor()
        
    def create_data_with_missing_values(self):
        """创建包含缺失值的测试数据"""
        np.random.seed(42)
        
        # 创建基础数据
        data = {
            'user_id': range(1, 101),
            'age': np.random.normal(30, 10, 100),
            'income': np.random.normal(50000, 15000, 100),
            'rating': np.random.uniform(1, 5, 100),
            'category': ['电子产品', '服装', '食品', '图书', '家居'] * 20,
            'description': ['商品描述' + str(i) for i in range(100)]
        }
        
        df = pd.DataFrame(data)
        
        # 插入不同比例的缺失值
        # 10%缺失率
        missing_10_indices = np.random.choice(df.index, size=10, replace=False)
        df.loc[missing_10_indices, 'age'] = np.nan
        
        # 30%缺失率
        missing_30_indices = np.random.choice(df.index, size=30, replace=False)
        df.loc[missing_30_indices, 'income'] = np.nan
        
        # 50%缺失率
        missing_50_indices = np.random.choice(df.index, size=50, replace=False)
        df.loc[missing_50_indices, 'category'] = np.nan
        
        # 少量缺失值
        df.loc[0:4, 'rating'] = np.nan
        df.loc[95:99, 'description'] = np.nan
        
        return df
    
    def test_missing_value_handling(self):
        """测试缺失值处理功能"""
        # 准备测试数据
        df = self.create_data_with_missing_values()
        
        # 记录处理前的缺失值统计
        missing_before = df.isnull().sum()
        
        # 执行数据清洗（包含缺失值处理）
        cleaned_df = self.preprocessor.clean_data(df.copy())
        
        # 记录处理后的缺失值统计
        missing_after = cleaned_df.isnull().sum()
        
        # 断言：所有缺失值都应该被处理
        assert missing_after.sum() == 0, "处理后不应该有缺失值"
        
        # 验证数值型列使用均值填充
        original_age_mean = df['age'].mean()
        filled_age_values = cleaned_df.loc[df['age'].isnull(), 'age']
        assert all(abs(val - original_age_mean) < 0.001 for val in filled_age_values), "数值型缺失值应该用均值填充"
        
        # 验证分类型列使用众数填充
        original_category_mode = df['category'].mode()[0]
        filled_category_values = cleaned_df.loc[df['category'].isnull(), 'category']
        assert all(val == original_category_mode for val in filled_category_values), "分类型缺失值应该用众数填充"
        
        # 验证数据完整性
        assert len(cleaned_df) == len(df), "缺失值处理不应该删除数据行"
        assert cleaned_df.columns.equals(df.columns), "缺失值处理不应该改变列结构"
    
    def test_missing_value_strategies(self):
        """测试不同的缺失值处理策略"""
        # 创建测试数据
        df = pd.DataFrame({
            'numeric_col': [1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10],
            'categorical_col': ['A', 'B', np.nan, 'A', 'A', np.nan, 'C', 'A', 'B', 'A']
        })
        
        # 处理缺失值
        result_df = self.preprocessor.clean_data(df.copy())
        
        # 验证数值列：均值填充
        expected_mean = df['numeric_col'].mean()  # (1+2+4+5+7+8+9+10)/8 = 5.75
        filled_values = result_df.loc[df['numeric_col'].isnull(), 'numeric_col']
        assert all(abs(val - expected_mean) < 0.001 for val in filled_values), f"数值列应该用均值{expected_mean}填充"
        
        # 验证分类列：众数填充（'A'出现最多）
        expected_mode = 'A'
        filled_values = result_df.loc[df['categorical_col'].isnull(), 'categorical_col']
        assert all(val == expected_mode for val in filled_values), f"分类列应该用众数{expected_mode}填充"
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试空数据框
        empty_df = pd.DataFrame()
        result = self.preprocessor.clean_data(empty_df)
        assert len(result) == 0, "空数据框应该返回空结果"
        
        # 测试全为缺失值的列
        all_missing_df = pd.DataFrame({
            'user_id': [1, 2, 3],
            'all_missing': [np.nan, np.nan, np.nan]
        })
        result = self.preprocessor.clean_data(all_missing_df)
        # 分类型全缺失列应该填充为'未知'
        assert all(result['all_missing'] == '未知'), "全缺失的分类列应该填充为'未知'"
        
        # 测试无缺失值的数据
        no_missing_df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['A', 'B', 'C', 'D', 'E']
        })
        result = self.preprocessor.clean_data(no_missing_df)
        pd.testing.assert_frame_equal(result, no_missing_df, check_dtype=False), "无缺失值的数据不应该被修改"
    
    def test_missing_value_statistics(self):
        """测试缺失值统计信息"""
        df = self.create_data_with_missing_values()
        
        # 统计处理前的缺失值情况
        missing_stats_before = {
            'age': df['age'].isnull().sum(),
            'income': df['income'].isnull().sum(), 
            'category': df['category'].isnull().sum(),
            'rating': df['rating'].isnull().sum(),
            'description': df['description'].isnull().sum()
        }
        
        # 验证我们创建的缺失值比例是否正确
        assert missing_stats_before['age'] == 10, "age列应该有10个缺失值(10%)"
        assert missing_stats_before['income'] == 30, "income列应该有30个缺失值(30%)"
        assert missing_stats_before['category'] == 50, "category列应该有50个缺失值(50%)"
        assert missing_stats_before['rating'] == 5, "rating列应该有5个缺失值"
        assert missing_stats_before['description'] == 5, "description列应该有5个缺失值"
        
        # 处理缺失值
        cleaned_df = self.preprocessor.clean_data(df)
        
        # 验证所有缺失值都被处理
        missing_stats_after = cleaned_df.isnull().sum()
        assert missing_stats_after.sum() == 0, "处理后所有列都不应该有缺失值"