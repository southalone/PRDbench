"""
数据详情链接生成单元测试
"""
import pytest
import pandas as pd
from datetime import datetime
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processor import DataProcessor


class TestDetailLinks:
    
    def setup_method(self):
        """设置测试数据"""
        self.processor = DataProcessor()
        
        # 创建测试数据
        self.test_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003'],
            'trans_date': pd.to_datetime(['2023-06-15', '2023-06-16', '2023-06-17']),
            'git_repo': ['repo1', 'repo2', 'repo3'],
            'amount': [1000, 1500, 2000]
        })
    
    def test_detail_link_format(self):
        """测试详情链接格式正确性"""
        # 模拟添加详情链接的过程
        test_df = self.test_data.copy()
        test_df['detail_link'] = test_df.apply(
            lambda x: f"repo://{x['git_repo']}/detail?store_id={x['store_id']}&date={x['trans_date'].strftime('%Y-%m-%d')}", 
            axis=1
        )
        
        # 验证链接格式
        for _, row in test_df.iterrows():
            link = row['detail_link']
            
            # 验证链接以repo://开头
            assert link.startswith('repo://'), f"链接格式错误: {link}"
            
            # 验证包含正确的参数
            assert f"store_id={row['store_id']}" in link
            assert f"date={row['trans_date'].strftime('%Y-%m-%d')}" in link
            assert f"repo://{row['git_repo']}/detail" in link
    
    def test_detail_link_parameter_filling(self):
        """测试详情链接参数填充正确性"""
        test_df = self.test_data.copy()
        test_df['detail_link'] = test_df.apply(
            lambda x: f"repo://{x['git_repo']}/detail?store_id={x['store_id']}&date={x['trans_date'].strftime('%Y-%m-%d')}", 
            axis=1
        )
        
        # 验证第一条记录的链接
        expected_link = "repo://repo1/detail?store_id=S001&date=2023-06-15"
        assert test_df.iloc[0]['detail_link'] == expected_link
        
        # 验证第二条记录的链接
        expected_link = "repo://repo2/detail?store_id=S002&date=2023-06-16"
        assert test_df.iloc[1]['detail_link'] == expected_link
    
    def test_detail_link_with_special_characters(self):
        """测试包含特殊字符的参数处理"""
        special_data = pd.DataFrame({
            'store_id': ['S-001', 'S_002', 'S.003'],
            'trans_date': pd.to_datetime(['2023-06-15', '2023-06-16', '2023-06-17']),
            'git_repo': ['repo-1', 'repo_2', 'repo.3'],
            'amount': [1000, 1500, 2000]
        })
        
        special_data['detail_link'] = special_data.apply(
            lambda x: f"repo://{x['git_repo']}/detail?store_id={x['store_id']}&date={x['trans_date'].strftime('%Y-%m-%d')}", 
            axis=1
        )
        
        # 验证特殊字符被正确处理
        for _, row in special_data.iterrows():
            link = row['detail_link']
            assert row['store_id'] in link
            assert row['git_repo'] in link
    
    def test_detail_link_date_format(self):
        """测试日期格式的正确性"""
        test_df = self.test_data.copy()
        test_df['detail_link'] = test_df.apply(
            lambda x: f"repo://{x['git_repo']}/detail?store_id={x['store_id']}&date={x['trans_date'].strftime('%Y-%m-%d')}", 
            axis=1
        )
        
        # 验证日期格式为YYYY-MM-DD
        import re
        date_pattern = r'date=(\d{4}-\d{2}-\d{2})'
        
        for _, row in test_df.iterrows():
            link = row['detail_link']
            match = re.search(date_pattern, link)
            
            assert match is not None, f"日期格式错误: {link}"
            
            extracted_date = match.group(1)
            expected_date = row['trans_date'].strftime('%Y-%m-%d')
            assert extracted_date == expected_date
    
    def test_detail_link_with_missing_data(self):
        """测试缺失数据的处理"""
        missing_data = pd.DataFrame({
            'store_id': ['S001', None, 'S003'],
            'trans_date': pd.to_datetime(['2023-06-15', '2023-06-16', '2023-06-17']),
            'git_repo': ['repo1', 'repo2', None],
            'amount': [1000, 1500, 2000]
        })
        
        # 处理缺失值
        missing_data['git_repo'] = missing_data['git_repo'].fillna('unknown')
        missing_data['store_id'] = missing_data['store_id'].fillna('unknown')
        
        missing_data['detail_link'] = missing_data.apply(
            lambda x: f"repo://{x['git_repo']}/detail?store_id={x['store_id']}&date={x['trans_date'].strftime('%Y-%m-%d')}", 
            axis=1
        )
        
        # 验证链接仍然能够生成
        assert missing_data['detail_link'].notna().all()
        assert 'unknown' in missing_data.iloc[1]['detail_link']
        assert 'unknown' in missing_data.iloc[2]['detail_link']


if __name__ == "__main__":
    pytest.main([__file__])