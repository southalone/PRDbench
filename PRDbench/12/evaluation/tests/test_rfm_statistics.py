"""
RFM细分结果统计单元测试
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
from display import DataDisplay


class TestRFMStatistics:
    
    def setup_method(self):
        """设置测试数据"""
        self.processor = DataProcessor()
        self.display = DataDisplay()
        
        # 创建完整的测试数据包含RFM和金额信息
        self.test_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003', 'S004', 'S005', 'S006', 'S007', 'S008'],
            'recency': [5, 10, 60, 15, 45, 8, 30, 90],
            'frequency': [15, 12, 3, 10, 5, 18, 7, 2], 
            'monetary': [8000, 6000, 1000, 5000, 2000, 9000, 3000, 800],
            'amount': [120000, 72000, 3000, 50000, 10000, 162000, 21000, 1600],  # 总交易金额
            'segment': ['重要价值客户', '重要价值客户', '一般新客户', '重要保持客户', 
                       '一般发展客户', '重要价值客户', '一般保持客户', '一般新客户']
        })
    
    def test_segment_count_percentage_calculation(self):
        """测试细分结果统计数量占比计算"""
        # 计算细分统计
        segment_stats = self.test_data.groupby('segment').agg({
            'store_id': 'count',
            'amount': 'sum'
        }).reset_index()
        segment_stats.columns = ['segment', 'store_count', 'total_amount']
        
        # 计算占比
        total_stores = len(self.test_data)
        segment_stats['percentage'] = (segment_stats['store_count'] / total_stores * 100).round(1)
        
        # 验证占比计算正确性
        assert abs(segment_stats['percentage'].sum() - 100.0) < 0.1, "占比总和应该等于100%"
        
        # 验证每个细分类型的占比
        for _, row in segment_stats.iterrows():
            expected_percentage = (row['store_count'] / total_stores) * 100
            assert abs(row['percentage'] - expected_percentage) < 0.1, f"细分类型 {row['segment']} 占比计算错误"
        
        # 验证重要价值客户占比（有3个门店，应该是37.5%）
        important_customers = segment_stats[segment_stats['segment'] == '重要价值客户']
        if len(important_customers) > 0:
            expected_percentage = 3 / 8 * 100  # 37.5%
            actual_percentage = important_customers.iloc[0]['percentage']
            assert abs(actual_percentage - expected_percentage) < 0.1, "重要价值客户占比计算错误"
    
    def test_transaction_amount_contribution_percentage(self):
        """测试细分结果统计交易金额贡献占比"""
        # 计算金额贡献占比
        segment_stats = self.test_data.groupby('segment').agg({
            'store_id': 'count',
            'amount': 'sum'
        }).reset_index()
        segment_stats.columns = ['segment', 'store_count', 'total_amount']
        
        # 计算金额贡献占比
        total_amount = segment_stats['total_amount'].sum()
        segment_stats['amount_percentage'] = (segment_stats['total_amount'] / total_amount * 100).round(1)
        
        # 验证金额占比总和为100%
        assert abs(segment_stats['amount_percentage'].sum() - 100.0) < 0.1, "金额占比总和应该等于100%"
        
        # 验证重要价值客户的金额贡献应该最高
        important_customers = segment_stats[segment_stats['segment'] == '重要价值客户']
        if len(important_customers) > 0:
            important_amount_pct = important_customers.iloc[0]['amount_percentage']
            max_amount_pct = segment_stats['amount_percentage'].max()
            assert important_amount_pct == max_amount_pct, "重要价值客户应该有最高的金额贡献占比"
        
        # 验证各细分类型金额贡献占比计算正确性
        for _, row in segment_stats.iterrows():
            expected_percentage = (row['total_amount'] / total_amount) * 100
            assert abs(row['amount_percentage'] - expected_percentage) < 0.1, f"细分类型 {row['segment']} 金额占比计算错误"
    
    def test_segment_filtering_by_type(self):
        """测试按细分类型筛选功能"""
        # 测试筛选重要价值客户
        important_customers = self.test_data[self.test_data['segment'] == '重要价值客户']
        assert len(important_customers) == 3, "重要价值客户数量不正确"
        
        # 验证筛选结果的数据完整性
        assert important_customers['store_id'].notna().all(), "筛选结果包含空的门店ID"
        assert important_customers['monetary'].notna().all(), "筛选结果包含空的月均金额"
        
        # 验证重要价值客户的特征
        avg_monetary = important_customers['monetary'].mean()
        overall_avg_monetary = self.test_data['monetary'].mean()
        assert avg_monetary > overall_avg_monetary, "重要价值客户的平均月均金额应该高于总体平均"
        
        # 测试筛选一般新客户
        new_customers = self.test_data[self.test_data['segment'] == '一般新客户']
        assert len(new_customers) == 2, "一般新客户数量不正确"
        
        # 验证一般新客户的特征
        avg_monetary_new = new_customers['monetary'].mean()
        assert avg_monetary_new < overall_avg_monetary, "一般新客户的平均月均金额应该低于总体平均"
    
    def test_comprehensive_segment_statistics(self):
        """测试综合细分统计信息"""
        # 创建完整的统计信息
        segment_stats = self.test_data.groupby('segment').agg({
            'store_id': 'count',
            'amount': ['sum', 'mean'],
            'monetary': 'mean',
            'frequency': 'mean',
            'recency': 'mean'
        }).round(2)
        
        # 展平列名
        segment_stats.columns = ['store_count', 'total_amount', 'avg_amount', 'avg_monetary', 'avg_frequency', 'avg_recency']
        segment_stats = segment_stats.reset_index()
        
        # 计算占比
        total_stores = len(self.test_data)
        total_amount = segment_stats['total_amount'].sum()
        segment_stats['store_percentage'] = (segment_stats['store_count'] / total_stores * 100).round(1)
        segment_stats['amount_percentage'] = (segment_stats['total_amount'] / total_amount * 100).round(1)
        
        # 验证统计信息完整性
        assert len(segment_stats) > 0, "统计结果为空"
        assert segment_stats['store_count'].sum() == total_stores, "门店数量统计错误"
        assert abs(segment_stats['store_percentage'].sum() - 100.0) < 0.1, "门店占比总和错误"
        assert abs(segment_stats['amount_percentage'].sum() - 100.0) < 0.1, "金额占比总和错误"
        
        # 验证平均值计算合理性
        assert (segment_stats['avg_monetary'] > 0).all(), "月均金额应该为正数"
        assert (segment_stats['avg_frequency'] > 0).all(), "平均频次应该为正数"
        assert (segment_stats['avg_recency'] >= 0).all(), "平均最近购买天数应该非负"
    
    def test_segment_business_insights(self):
        """测试细分结果的业务洞察"""
        # 验证RFM细分的业务逻辑合理性
        segment_insights = self.test_data.groupby('segment').agg({
            'monetary': 'mean',
            'frequency': 'mean', 
            'recency': 'mean'
        }).round(2)
        
        # 重要价值客户应该有最好的RFM指标
        if '重要价值客户' in segment_insights.index:
            important_customers = segment_insights.loc['重要价值客户']
            
            # 与一般新客户比较
            if '一般新客户' in segment_insights.index:
                new_customers = segment_insights.loc['一般新客户']
                
                # 重要价值客户应该有更高的月均金额和频次，更低的最近购买天数
                assert important_customers['monetary'] > new_customers['monetary'], "重要价值客户月均金额应该更高"
                assert important_customers['frequency'] > new_customers['frequency'], "重要价值客户交易频次应该更高"
                assert important_customers['recency'] < new_customers['recency'], "重要价值客户最近购买天数应该更少"


if __name__ == "__main__":
    pytest.main([__file__])