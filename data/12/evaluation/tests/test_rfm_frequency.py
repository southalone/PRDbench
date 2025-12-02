"""
RFM指标计算 - Frequency计算功能单元测试
测试数据处理器中的Frequency（月均交易次数）计算逻辑
"""

import pytest
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processor import DataProcessor


class TestRFMFrequencyCalculation:
    """RFM Frequency计算功能测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.processor = DataProcessor()
    
    def test_frequency_calculation_basic(self):
        """测试基础的Frequency计算功能"""
        # 准备测试数据
        current_date = datetime.now()
        
        # 创建包含不同交易频率的测试数据
        test_data = {
            'store_id': ['S001', 'S001', 'S001', 'S002', 'S002', 'S003'],
            'trans_date': [
                current_date - timedelta(days=90),  # S001: 3个月前
                current_date - timedelta(days=60),  # S001: 2个月前
                current_date - timedelta(days=30),  # S001: 1个月前 (3次交易在3个月内)
                current_date - timedelta(days=60),  # S002: 2个月前
                current_date - timedelta(days=30),  # S002: 1个月前 (2次交易在2个月内)
                current_date - timedelta(days=15),  # S003: 15天前 (1次交易)
            ],
            'amount': [100.0, 200.0, 150.0, 120.0, 180.0, 300.0]
        }
        
        df = pd.DataFrame(test_data)
        
        # 执行RFM计算
        rfm_result = self.processor.calculate_rfm_metrics(df)
        
        # 验证计算结果
        assert rfm_result is not None
        assert len(rfm_result) == 3  # 3个门店
        assert 'frequency' in rfm_result.columns
        
        # 验证具体的Frequency值
        store_s001_freq = rfm_result[rfm_result['store_id'] == 'S001']['frequency'].iloc[0]
        store_s002_freq = rfm_result[rfm_result['store_id'] == 'S002']['frequency'].iloc[0]
        store_s003_freq = rfm_result[rfm_result['store_id'] == 'S003']['frequency'].iloc[0]
        
        # S001: 3次交易，时间跨度90-30=60天=2个月，频率=3/2=1.5次/月
        assert 1.4 <= store_s001_freq <= 1.6  # 允许合理误差
        
        # S002: 2次交易，时间跨度60-30=30天=1个月，频率=2/1=2次/月
        assert 1.8 <= store_s002_freq <= 2.2
        
        # S003: 1次交易，最少按1个月计算，频率=1/1=1次/月
        assert 0.9 <= store_s003_freq <= 1.1
        
        print(f"[OK] Frequency计算测试通过")
        print(f"  - S001门店Frequency: {store_s001_freq:.2f}次/月")
        print(f"  - S002门店Frequency: {store_s002_freq:.2f}次/月")
        print(f"  - S003门店Frequency: {store_s003_freq:.2f}次/月")
    
    def test_frequency_calculation_single_transaction(self):
        """测试单次交易的Frequency计算"""
        current_date = datetime.now()
        
        # 只有一次交易的门店
        test_data = {
            'store_id': ['S001'],
            'trans_date': [current_date - timedelta(days=15)],
            'amount': [100.0]
        }
        
        df = pd.DataFrame(test_data)
        rfm_result = self.processor.calculate_rfm_metrics(df)
        
        # 单次交易的门店，frequency应该为1.0（按最少1个月计算）
        frequency_value = rfm_result[rfm_result['store_id'] == 'S001']['frequency'].iloc[0]
        assert frequency_value == 1.0
        
        print(f"[OK] 单次交易测试通过")
        print(f"  - 单次交易Frequency: {frequency_value}次/月")
    
    def test_frequency_calculation_high_frequency(self):
        """测试高频交易的Frequency计算"""
        current_date = datetime.now()
        
        # 创建高频交易数据（10次交易在2个月内）
        test_data = {
            'store_id': ['S001'] * 10,
            'trans_date': [
                current_date - timedelta(days=60),
                current_date - timedelta(days=55),
                current_date - timedelta(days=50),
                current_date - timedelta(days=45),
                current_date - timedelta(days=40),
                current_date - timedelta(days=35),
                current_date - timedelta(days=30),
                current_date - timedelta(days=25),
                current_date - timedelta(days=20),
                current_date - timedelta(days=15),
            ],
            'amount': [100.0] * 10
        }
        
        df = pd.DataFrame(test_data)
        rfm_result = self.processor.calculate_rfm_metrics(df)
        
        frequency_value = rfm_result[rfm_result['store_id'] == 'S001']['frequency'].iloc[0]
        
        # 10次交易在约1.5个月内，月均交易次数应该约为6-7次
        assert 4.0 <= frequency_value <= 8.0
        
        print(f"[OK] 高频交易测试通过")
        print(f"  - 高频交易Frequency: {frequency_value:.2f}次/月")
    
    def test_frequency_data_types(self):
        """测试Frequency计算结果的数据类型"""
        current_date = datetime.now()
        
        test_data = {
            'store_id': ['S001', 'S001'],
            'trans_date': [
                current_date - timedelta(days=30),
                current_date - timedelta(days=15)
            ],
            'amount': [100.0, 200.0]
        }
        
        df = pd.DataFrame(test_data)
        rfm_result = self.processor.calculate_rfm_metrics(df)
        
        # 验证返回结果的数据类型
        assert isinstance(rfm_result, pd.DataFrame)
        assert 'frequency' in rfm_result.columns
        assert pd.api.types.is_numeric_dtype(rfm_result['frequency'])
        
        frequency_value = rfm_result['frequency'].iloc[0]
        # 检查是否为数值类型
        assert pd.api.types.is_numeric_dtype(type(frequency_value)) or isinstance(frequency_value, (int, float))
        assert float(frequency_value) > 0  # Frequency应该是正数
        
        print(f"[OK] 数据类型测试通过")
        print(f"  - Frequency值类型: {type(frequency_value)}")
        print(f"  - Frequency值: {frequency_value:.2f}")


if __name__ == "__main__":
    # 可以直接运行此文件进行测试
    test_instance = TestRFMFrequencyCalculation()
    test_instance.setup_method()
    
    try:
        test_instance.test_frequency_calculation_basic()
        test_instance.test_frequency_calculation_single_transaction()
        test_instance.test_frequency_calculation_high_frequency()
        test_instance.test_frequency_data_types()
        print("\n[SUCCESS] 所有RFM Frequency计算测试通过!")
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {str(e)}")
        raise