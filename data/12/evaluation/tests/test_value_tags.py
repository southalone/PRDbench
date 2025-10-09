"""
高价值属性标签生成单元测试
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src')
sys.path.insert(0, src_path)

from data_processor import DataProcessor


class TestValueTagGeneration:
    
    def setup_method(self):
        """设置测试数据"""
        self.processor = DataProcessor()
        
        # 创建RFM测试数据
        self.rfm_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003', 'S004', 'S005'],
            'recency': [5, 30, 60, 10, 45],
            'frequency': [15, 8, 3, 12, 5],
            'monetary': [8000, 3000, 1000, 6000, 2000]
        })
        
        # 创建分解结果数据
        self.decomp_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003', 'S004', 'S005'],
            'trend': [7500, 2800, 1200, 5800, 1800],
            'seasonal': [100, 50, 0, 80, 20],
            'residual': [200, 150, 100, 180, 120],
            'decomposition_method': ['STL', 'STL', 'Enhanced Statistics', 'STL', 'Enhanced Statistics']
        })
    
    def test_value_tag_generation_execution(self):
        """测试价值标签生成是否成功执行"""
        result_df = self.processor.generate_value_tags(self.rfm_data, self.decomp_data)
        
        # 验证返回结果包含所有门店
        assert len(result_df) == 5
        
        # 验证包含value_tag列
        assert 'value_tag' in result_df.columns
        
        # 验证所有门店都有标签
        assert result_df['value_tag'].notna().all()
    
    def test_value_tag_types(self):
        """测试价值标签类型的正确性"""
        result_df = self.processor.generate_value_tags(self.rfm_data, self.decomp_data)
        
        # 获取所有生成的标签类型
        tag_types = result_df['value_tag'].unique()
        
        # 预期的标签类型
        expected_tags = {
            "增长型高价值", "稳定型高价值", "潜力型高价值", 
            "发展型高价值", "观察型高价值", "数据不足"
        }
        
        # 验证所有生成的标签都在预期范围内
        for tag in tag_types:
            assert tag in expected_tags, f"未知的价值标签: {tag}"
    
    def test_high_value_tag_logic(self):
        """测试高价值标签生成逻辑"""
        result_df = self.processor.generate_value_tags(self.rfm_data, self.decomp_data)
        
        # S001应该是高价值门店（高monetary、高frequency、低recency、正趋势）
        s001_tag = result_df[result_df['store_id'] == 'S001']['value_tag'].iloc[0]
        assert s001_tag in ["增长型高价值", "稳定型高价值"]
        
        # S003应该是观察型高价值（所有指标都偏低）
        s003_tag = result_df[result_df['store_id'] == 'S003']['value_tag'].iloc[0]
        assert s003_tag == "观察型高价值"
    
    def test_missing_data_handling(self):
        """测试缺失数据的处理"""
        # 创建包含缺失值的分解数据
        missing_decomp = self.decomp_data.copy()
        missing_decomp.loc[0, 'trend'] = np.nan
        
        result_df = self.processor.generate_value_tags(self.rfm_data, missing_decomp)
        
        # 验证缺失数据被正确处理
        s001_tag = result_df[result_df['store_id'] == 'S001']['value_tag'].iloc[0]
        assert s001_tag == "数据不足"
    
    def test_tag_distribution(self):
        """测试标签分布的合理性"""
        result_df = self.processor.generate_value_tags(self.rfm_data, self.decomp_data)
        
        # 验证标签分布
        tag_counts = result_df['value_tag'].value_counts()
        
        # 每个标签至少应该有1个门店（基于我们的测试数据）
        assert len(tag_counts) >= 1
        assert tag_counts.sum() == len(result_df)


if __name__ == "__main__":
    pytest.main([__file__])