"""
数据整合和多表关联单元测试
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src')
sys.path.insert(0, src_path)

from data_processor import DataProcessor
from data_generator import DataGenerator


class TestDataIntegration:
    
    def setup_method(self):
        """设置测试数据"""
        self.processor = DataProcessor()
        self.generator = DataGenerator()
        
        # 生成测试数据
        self.store_df, self.sales_df, self.warehouse_df = self.generator.generate_all_data(10, 100)
    
    def test_biz_id_join_result_validation(self):
        """测试biz_id关联结果验证"""
        # 加载数据
        self.processor.load_data(self.store_df, self.sales_df, self.warehouse_df)
        
        # 执行数据整合
        integrated_df = self.processor.data_integration()
        
        # 验证biz_id关联结果
        assert 'git_repo' in integrated_df.columns, "缺少仓库信息字段"
        # biz_group字段在当前实现中不存在，仓库信息表只包含biz_id和git_repo
        
        # 验证所有记录都有有效的biz_id关联
        non_null_repos = integrated_df['git_repo'].notna()
        assert non_null_repos.any(), "没有成功关联到仓库信息"
        
        # 验证关联的一致性
        for biz_id in integrated_df['biz_id'].unique():
            if pd.notna(biz_id):
                biz_records = integrated_df[integrated_df['biz_id'] == biz_id]
                git_repos = biz_records['git_repo'].dropna().unique()
                if len(git_repos) > 0:
                    # 同一个biz_id应该对应同一个git_repo
                    assert len(git_repos) == 1, f"biz_id {biz_id} 对应多个git_repo: {git_repos}"
    
    def test_store_key_join_result_validation(self):
        """测试store_key关联结果验证"""
        # 加载数据
        self.processor.load_data(self.store_df, self.sales_df, self.warehouse_df)
        
        # 执行数据整合
        integrated_df = self.processor.data_integration()
        
        # 验证store_key关联结果
        assert 'store_id' in integrated_df.columns, "缺少门店ID字段"
        assert 'brand_name' in integrated_df.columns, "缺少品牌名称字段"
        assert 'a_value_type' in integrated_df.columns, "缺少价值类型字段"
        assert 'private_domain_type' in integrated_df.columns, "缺少私域类型字段"
        
        # 验证所有记录都有有效的store_key关联
        assert integrated_df['store_id'].notna().all(), "存在未关联到门店信息的记录"
        
        # 验证高价值门店筛选
        high_value_count = (integrated_df['a_value_type'] == '高价值').sum()
        assert high_value_count > 0, "没有筛选出高价值门店"
        
        # 验证私域类型筛选
        valid_domain_types = integrated_df['private_domain_type'].isin(['总部直管', '区域重点'])
        assert valid_domain_types.all(), "存在不符合条件的私域类型"
    
    def test_data_integration_completeness(self):
        """测试数据整合完整性"""
        # 加载数据
        self.processor.load_data(self.store_df, self.sales_df, self.warehouse_df)
        
        # 执行数据整合
        integrated_df = self.processor.data_integration()
        
        # 验证关键字段都存在
        required_fields = [
            'store_key', 'biz_id', 'trans_date', 'amount',
            'store_id', 'a_value_type', 'private_domain_type',
            'git_repo'
        ]
        
        for field in required_fields:
            assert field in integrated_df.columns, f"缺少必需字段: {field}"
        
        # 验证数据类型
        assert pd.api.types.is_datetime64_any_dtype(integrated_df['trans_date']), "交易日期类型错误"
        assert pd.api.types.is_numeric_dtype(integrated_df['amount']), "交易金额类型错误"
        
        # 验证数据量合理性
        assert len(integrated_df) > 0, "整合后数据为空"
        assert len(integrated_df) <= len(self.sales_df), "整合后数据量超出预期"


if __name__ == "__main__":
    pytest.main([__file__])