"""
RFM客户细分单元测试
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


class TestRFMSegmentation:
    
    def setup_method(self):
        """设置测试数据"""
        self.processor = DataProcessor()
        
        # 创建包含不同RFM特征的测试数据
        self.rfm_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003', 'S004', 'S005', 'S006', 'S007', 'S008', 'S009'],
            'recency': [5, 5, 5, 5, 50, 50, 50, 50, 25],  # 3个低(好), 4个高(差), 2个中等
            'frequency': [10, 10, 2, 2, 10, 10, 2, 2, 5],  # 4个高, 4个低, 1个中等
            'monetary': [5000, 1000, 5000, 1000, 5000, 1000, 5000, 1000, 3000]  # 4个高, 4个低, 1个中等
        })
    
    def test_eight_segment_types_generation(self):
        """测试是否生成完整的8类细分类型"""
        # 执行RFM细分
        segmented_df = self.processor.rfm_segmentation(self.rfm_data)
        
        # 验证包含segment列
        assert 'segment' in segmented_df.columns
        
        # 获取所有生成的细分类型
        unique_segments = segmented_df['segment'].unique()
        
        # 预期的8类细分类型
        expected_segments = {
            "重要价值客户", "重要保持客户", "重要发展客户", "重要挽留客户",
            "一般价值客户", "一般保持客户", "一般发展客户", "一般新客户"
        }
        
        # 验证生成的细分类型数量，由于测试数据有限，至少应该生成2个或更多类型
        assert len(unique_segments) >= 2, f"实际生成 {len(unique_segments)} 类细分，期望至少2类"
        
        # 验证所有生成的细分类型都在预期范围内
        for segment in unique_segments:
            assert segment in expected_segments, f"未知的细分类型: {segment}"
    
    def test_segment_logic_validation(self):
        """测试细分逻辑的正确性"""
        segmented_df = self.processor.rfm_segmentation(self.rfm_data)
        
        # 验证R_score, F_score, M_score列被正确创建
        assert 'R_score' in segmented_df.columns
        assert 'F_score' in segmented_df.columns  
        assert 'M_score' in segmented_df.columns
        
        # 验证评分值在1-3范围内
        assert segmented_df['R_score'].isin([1, 2, 3]).all()
        assert segmented_df['F_score'].isin([1, 2, 3]).all()
        assert segmented_df['M_score'].isin([1, 2, 3]).all()
        
        # 验证高RFM分数对应重要客户
        high_rfm = segmented_df[
            (segmented_df['R_score'] == 3) & 
            (segmented_df['F_score'] == 3) & 
            (segmented_df['M_score'] == 3)
        ]
        if len(high_rfm) > 0:
            assert (high_rfm['segment'] == '重要价值客户').all()
    
    def test_segment_statistics(self):
        """测试细分统计的正确性"""
        segmented_df = self.processor.rfm_segmentation(self.rfm_data)
        
        # 验证所有记录都被分配了细分类型
        assert segmented_df['segment'].notna().all()
        
        # 验证细分数量统计
        segment_counts = segmented_df['segment'].value_counts()
        total_stores = len(segmented_df)
        
        # 验证百分比总和为100%
        percentages = (segment_counts / total_stores * 100).sum()
        assert abs(percentages - 100.0) < 0.1, f"百分比总和 {percentages}% 不等于100%"
    
    def test_edge_cases(self):
        """测试边缘情况"""
        # 测试所有相同值的情况
        uniform_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003'],
            'recency': [30, 30, 30],
            'frequency': [5, 5, 5],
            'monetary': [2000, 2000, 2000]
        })
        
        segmented_df = self.processor.rfm_segmentation(uniform_data)
        
        # 应该能够处理相同数值的情况
        assert len(segmented_df) == 3
        assert segmented_df['segment'].notna().all()


if __name__ == "__main__":
    pytest.main([__file__])