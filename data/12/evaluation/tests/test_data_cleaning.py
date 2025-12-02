"""
数据清洗功能单元测试
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


class TestDataCleaning:
    
    def setup_method(self):
        """设置测试数据"""
        self.processor = DataProcessor()
        
        # 创建包含各种数据问题的测试数据
        self.dirty_data = pd.DataFrame({
            'biz_id': ['B001', 'B002', 'B003', 'B004', 'B005', 'B006'],
            'trans_date': pd.to_datetime([
                '2023-06-15', '2023-06-16', '2023-05-10',  # 正常日期
                '2023-03-01', '2023-06-17', '2023-06-15'   # 早于开业日期, 正常, 重复
            ]),
            'store_id': ['S001', 'S002', 'S003', 'S004', 'S005', 'S001'],
            'brand_name': ['品牌A', None, '品牌C', '品牌D', '', '品牌A'],  # 包含空值
            'amount': [1000, 1500, None, -500, 2000, 1000],  # 包含空值和负值
            'opening_date': pd.to_datetime([
                '2023-05-01', '2023-05-01', '2023-05-01', 
                '2023-05-01', '2023-05-01', '2023-05-01'
            ])
        })
    
    def test_missing_value_handling(self):
        """测试缺失值处理"""
        cleaned_data = self.processor.data_cleaning(self.dirty_data.copy())
        
        # 验证brand_name缺失值被填充
        assert cleaned_data['brand_name'].notna().all()
        assert '未知品牌' in cleaned_data['brand_name'].values
        
        # 验证amount为空的记录被移除
        assert cleaned_data['amount'].notna().all()
        
        # 验证数据清洗后记录数合理（会移除空值、负值、早期交易等）
        assert len(cleaned_data) <= len(self.dirty_data)
        assert len(cleaned_data) > 0  # 确保还有有效数据
    
    def test_anomaly_filtering(self):
        """测试异常值过滤"""
        cleaned_data = self.processor.data_cleaning(self.dirty_data.copy())
        
        # 验证负金额被过滤
        assert (cleaned_data['amount'] > 0).all()
        
        # 验证早于开业日期的交易被过滤
        assert (cleaned_data['trans_date'] >= cleaned_data['opening_date']).all()
    
    def test_duplicate_removal(self):
        """测试重复数据去重"""
        # 创建明确的重复数据
        duplicate_data = pd.DataFrame({
            'biz_id': ['B001', 'B001', 'B002'],
            'trans_date': pd.to_datetime(['2023-06-15', '2023-06-15', '2023-06-16']),
            'store_id': ['S001', 'S001', 'S002'],
            'brand_name': ['品牌A', '品牌A', '品牌B'],
            'amount': [1000, 1000, 1500],
            'opening_date': pd.to_datetime(['2023-05-01', '2023-05-01', '2023-05-01'])
        })
        
        cleaned_data = self.processor.data_cleaning(duplicate_data.copy())
        
        # 验证重复记录被去除（基于composite_key）
        # composite_key = biz_id + trans_date + store_id
        composite_keys = cleaned_data['biz_id'] + '_' + cleaned_data['trans_date'].dt.strftime('%Y%m%d') + '_' + cleaned_data['store_id']
        assert len(composite_keys) == len(composite_keys.unique())
    
    def test_data_integrity_after_cleaning(self):
        """测试清洗后数据完整性"""
        cleaned_data = self.processor.data_cleaning(self.dirty_data.copy())
        
        # 验证必要列仍然存在
        required_columns = ['biz_id', 'trans_date', 'store_id', 'brand_name', 'amount']
        for col in required_columns:
            assert col in cleaned_data.columns
        
        # 验证数据类型正确
        assert pd.api.types.is_datetime64_any_dtype(cleaned_data['trans_date'])
        assert pd.api.types.is_numeric_dtype(cleaned_data['amount'])
        
        # 验证清洗后数据记录数合理
        assert len(cleaned_data) > 0
        assert len(cleaned_data) <= len(self.dirty_data)
    
    def test_empty_dataset_handling(self):
        """测试空数据集处理"""
        empty_data = pd.DataFrame(columns=['biz_id', 'trans_date', 'store_id', 'brand_name', 'amount', 'opening_date'])
        
        # 应该能够处理空数据集而不报错
        cleaned_data = self.processor.data_cleaning(empty_data.copy())
        assert len(cleaned_data) == 0
        assert list(cleaned_data.columns) == list(empty_data.columns)


if __name__ == "__main__":
    pytest.main([__file__])