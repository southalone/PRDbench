"""
时间序列分解单元测试
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


class TestTimeSeriesDecomposition:
    
    def setup_method(self):
        """设置测试数据"""
        self.processor = DataProcessor()
        
        # 创建足够的时间序列数据用于STL分解
        dates = pd.date_range('2023-01-01', periods=180, freq='D')  # 6个月数据
        
        # 创建包含趋势和季节性的模拟数据
        self.time_series_data = []
        for i, date in enumerate(dates):
            # 模拟3个门店的数据
            for store_id in ['S001', 'S002', 'S003']:
                # 添加趋势（增长）+ 季节性（周期性变化）+ 随机噪声
                trend = 1000 + i * 5  # 增长趋势
                seasonal = 200 * np.sin(2 * np.pi * i / 30)  # 月度季节性
                noise = np.random.normal(0, 50)  # 随机噪声
                amount = max(100, trend + seasonal + noise)  # 确保金额为正
                
                self.time_series_data.append({
                    'store_id': store_id,
                    'trans_date': date,
                    'amount': amount
                })
        
        self.ts_df = pd.DataFrame(self.time_series_data)
    
    def test_stl_decomposition_execution(self):
        """测试STL分解是否成功执行"""
        decomp_result = self.processor.time_series_decomposition(self.ts_df)
        
        # 验证返回结果包含所有门店
        assert len(decomp_result) == 3  # 3个门店
        
        # 验证包含必要的列
        required_columns = ['store_id', 'trend', 'seasonal', 'residual']
        for col in required_columns:
            assert col in decomp_result.columns
        
        # 验证所有门店都有分解结果
        assert set(decomp_result['store_id']) == {'S001', 'S002', 'S003'}
    
    def test_decomposition_components_validity(self):
        """测试分解组件的有效性"""
        decomp_result = self.processor.time_series_decomposition(self.ts_df)
        
        # 验证趋势项、季节项、残差项都是数值
        assert decomp_result['trend'].notna().all()
        assert decomp_result['seasonal'].notna().all()
        assert decomp_result['residual'].notna().all()
        
        # 验证数值类型
        assert pd.api.types.is_numeric_dtype(decomp_result['trend'])
        assert pd.api.types.is_numeric_dtype(decomp_result['seasonal'])
        assert pd.api.types.is_numeric_dtype(decomp_result['residual'])
        
        # 验证趋势项应该为正值（对于我们的测试数据）
        assert (decomp_result['trend'] > 0).all()
    
    def test_insufficient_data_handling(self):
        """测试数据不足时的处理"""
        # 创建数据量不足的时间序列（少于6个月）
        short_dates = pd.date_range('2023-01-01', periods=30, freq='D')  # 1个月数据
        
        short_data = []
        for date in short_dates:
            short_data.append({
                'store_id': 'S001',
                'trans_date': date,
                'amount': 1000 + np.random.normal(0, 100)
            })
        
        short_df = pd.DataFrame(short_data)
        decomp_result = self.processor.time_series_decomposition(short_df)
        
        # 验证即使数据不足也能返回结果
        assert len(decomp_result) == 1
        assert decomp_result.iloc[0]['store_id'] == 'S001'
        
        # 验证使用简单统计代替STL分解
        assert decomp_result.iloc[0]['trend'] > 0
        assert decomp_result.iloc[0]['seasonal'] == 0  # 数据不足时季节项为0
    
    def test_multiple_stores_processing(self):
        """测试多门店并行处理"""
        decomp_result = self.processor.time_series_decomposition(self.ts_df)
        
        # 验证每个门店都有独立的分解结果
        for store_id in ['S001', 'S002', 'S003']:
            store_result = decomp_result[decomp_result['store_id'] == store_id]
            assert len(store_result) == 1
            
            # 验证每个门店的分解结果都不同（由于随机性）
            assert store_result.iloc[0]['trend'] > 0
            assert pd.notna(store_result.iloc[0]['residual'])
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_df = pd.DataFrame(columns=['store_id', 'trans_date', 'amount'])
        decomp_result = self.processor.time_series_decomposition(empty_df)
        
        # 验证能够处理空数据
        assert len(decomp_result) == 0
        assert list(decomp_result.columns) == ['store_id', 'trend', 'seasonal', 'residual']
    
    def test_single_data_point_handling(self):
        """测试单个数据点的处理"""
        single_data = pd.DataFrame({
            'store_id': ['S001'],
            'trans_date': [datetime.now()],
            'amount': [1000]
        })
        
        decomp_result = self.processor.time_series_decomposition(single_data)
        
        # 验证单个数据点也能处理
        assert len(decomp_result) == 1
        assert decomp_result.iloc[0]['trend'] == 1000  # 趋势等于原值
        assert decomp_result.iloc[0]['seasonal'] == 0  # 无季节性
        assert decomp_result.iloc[0]['residual'] == 0  # 无残差


if __name__ == "__main__":
    pytest.main([__file__])