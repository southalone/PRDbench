"""
RFM Monetary 指标计算单元测试
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


class TestRFMMonetary:
    
    def setup_method(self):
        """设置测试数据"""
        self.processor = DataProcessor()
        
        # 创建测试数据
        dates = pd.date_range('2023-01-01', periods=30, freq='D')
        self.test_data = pd.DataFrame({
            'store_id': ['S001', 'S001', 'S001', 'S002', 'S002'],
            'trans_date': [dates[0], dates[15], dates[29], dates[5], dates[20]],
            'amount': [1000, 1500, 2000, 800, 1200]
        })
    
    def test_monetary_calculation_logic(self):
        """测试Monetary指标计算逻辑"""
        # 计算RFM指标
        rfm_result = self.processor.calculate_rfm_metrics(self.test_data)
        
        # 验证结果
        assert len(rfm_result) == 2  # 两个门店
        assert 'monetary' in rfm_result.columns
        
        # 验证S001门店的Monetary值
        s001_monetary = rfm_result[rfm_result['store_id'] == 'S001']['monetary'].iloc[0]
        # S001: 总金额4500，时间跨度29天约1个月，月均金额应该约为4500
        assert s001_monetary > 4000
        
        # 验证S002门店的Monetary值
        s002_monetary = rfm_result[rfm_result['store_id'] == 'S002']['monetary'].iloc[0]
        # S002: 总金额2000，时间跨度15天，但代码中months至少为1，所以月均金额为2000
        assert s002_monetary == 2000.0
    
    def test_monetary_with_single_transaction(self):
        """测试单笔交易的Monetary计算"""
        single_data = pd.DataFrame({
            'store_id': ['S003'],
            'trans_date': [datetime.now()],
            'amount': [1500]
        })
        
        rfm_result = self.processor.calculate_rfm_metrics(single_data)
        
        # 单笔交易的月均金额应该等于交易金额
        assert rfm_result.iloc[0]['monetary'] == 1500
    
    def test_monetary_with_zero_amount(self):
        """测试包含零金额交易的处理"""
        zero_data = pd.DataFrame({
            'store_id': ['S004', 'S004'],
            'trans_date': [datetime.now(), datetime.now() - timedelta(days=1)],
            'amount': [0, 1000]
        })
        
        rfm_result = self.processor.calculate_rfm_metrics(zero_data)
        
        # 应该能够处理包含零金额的数据
        assert len(rfm_result) == 1
        assert rfm_result.iloc[0]['monetary'] >= 0


if __name__ == "__main__":
    pytest.main([__file__])