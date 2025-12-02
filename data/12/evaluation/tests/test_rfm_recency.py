"""
RFM指标计算 - Recency计算功能单元测试
测试数据处理器中的Recency（最近购买时间间隔）计算逻辑
"""

import pytest
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processor import DataProcessor


class TestRFMRecencyCalculation:
    """RFM Recency计算功能测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.processor = DataProcessor()
    
    def test_recency_calculation_basic(self):
        """测试基础的Recency计算功能"""
        # 准备测试数据
        current_date = datetime.now()
        
        # 创建包含不同交易日期的测试数据
        test_data = {
            'store_id': ['S001', 'S001', 'S002', 'S002', 'S003'],
            'trans_date': [
                current_date - timedelta(days=30),  # 30天前
                current_date - timedelta(days=10),  # 10天前（最近）
                current_date - timedelta(days=45),  # 45天前（最近）
                current_date - timedelta(days=60),  # 60天前
                current_date - timedelta(days=5),   # 5天前（最近）
            ],
            'amount': [100.0, 200.0, 150.0, 80.0, 300.0]
        }
        
        df = pd.DataFrame(test_data)
        
        # 执行RFM计算
        rfm_result = self.processor.calculate_rfm_metrics(df)
        
        # 验证计算结果
        assert rfm_result is not None
        assert len(rfm_result) == 3  # 3个门店
        assert 'recency' in rfm_result.columns
        
        # 验证具体的Recency值
        store_s001_recency = rfm_result[rfm_result['store_id'] == 'S001']['recency'].iloc[0]
        store_s002_recency = rfm_result[rfm_result['store_id'] == 'S002']['recency'].iloc[0]
        store_s003_recency = rfm_result[rfm_result['store_id'] == 'S003']['recency'].iloc[0]
        
        # S001的最近交易是10天前
        assert abs(store_s001_recency - 10) <= 1  # 允许1天误差
        
        # S002的最近交易是45天前
        assert abs(store_s002_recency - 45) <= 1
        
        # S003的最近交易是5天前
        assert abs(store_s003_recency - 5) <= 1
        
        print(f"[OK] Recency计算测试通过")
        print(f"  - S001门店Recency: {store_s001_recency}天")
        print(f"  - S002门店Recency: {store_s002_recency}天")
        print(f"  - S003门店Recency: {store_s003_recency}天")
    
    def test_recency_calculation_edge_cases(self):
        """测试Recency计算的边界情况"""
        current_date = datetime.now()
        
        # 测试只有今天交易的情况
        test_data_today = {
            'store_id': ['S001', 'S001'],
            'trans_date': [current_date, current_date - timedelta(hours=2)],
            'amount': [100.0, 50.0]
        }
        
        df_today = pd.DataFrame(test_data_today)
        rfm_result_today = self.processor.calculate_rfm_metrics(df_today)
        
        # 今天的交易，Recency应该是0或接近0
        today_recency = rfm_result_today[rfm_result_today['store_id'] == 'S001']['recency'].iloc[0]
        assert today_recency <= 1  # 最多1天
        
        print(f"[OK] 边界情况测试通过")
        print(f"  - 当天交易Recency: {today_recency}天")
    
    def test_recency_data_types(self):
        """测试Recency计算结果的数据类型"""
        current_date = datetime.now()
        
        test_data = {
            'store_id': ['S001'],
            'trans_date': [current_date - timedelta(days=15)],
            'amount': [100.0]
        }
        
        df = pd.DataFrame(test_data)
        rfm_result = self.processor.calculate_rfm_metrics(df)
        
        # 验证返回结果的数据类型
        assert isinstance(rfm_result, pd.DataFrame)
        assert 'recency' in rfm_result.columns
        assert pd.api.types.is_numeric_dtype(rfm_result['recency'])
        
        recency_value = rfm_result['recency'].iloc[0]
        # 检查是否为数值类型（包括numpy类型）
        assert pd.api.types.is_numeric_dtype(type(recency_value)) or isinstance(recency_value, (int, float))
        assert float(recency_value) >= 0  # Recency不应该是负数
        
        print(f"[OK] 数据类型测试通过")
        print(f"  - Recency值类型: {type(recency_value)}")
        print(f"  - Recency值: {recency_value}")


if __name__ == "__main__":
    # 可以直接运行此文件进行测试
    test_instance = TestRFMRecencyCalculation()
    test_instance.setup_method()
    
    try:
        test_instance.test_recency_calculation_basic()
        test_instance.test_recency_calculation_edge_cases()
        test_instance.test_recency_data_types()
        print("\n[SUCCESS] 所有RFM Recency计算测试通过!")
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {str(e)}")
        raise