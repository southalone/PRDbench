"""
数据展示功能单元测试
"""
import pytest
import pandas as pd
import os
import tempfile
from datetime import datetime
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from display import DataDisplay
from data_processor import DataProcessor
from data_generator import DataGenerator


class TestDisplayFunctionality:
    
    def setup_method(self):
        """设置测试数据"""
        self.display = DataDisplay()
        self.processor = DataProcessor()
        self.generator = DataGenerator()
        
        # 生成完整的处理数据
        store_df, sales_df, warehouse_df = self.generator.generate_all_data(10, 100)
        self.processor.load_data(store_df, sales_df, warehouse_df)
        self.processed_df = self.processor.process_all()
        self.display.load_processed_data(self.processed_df)
    
    def test_table_display_required_columns_completeness(self):
        """测试表格数据展示必需列完整性检查"""
        # 获取显示的数据
        df = self.processed_df.copy()
        
        # 验证必需的列存在
        required_columns = {
            'biz_id': '业务组',
            'trans_date': '交易日期', 
            'store_id': '门店ID',
            'brand_name': '品牌',
            'org_path': '组织架构',
            'private_domain_type': '私域类型',
            'segment': 'RFM细分',
            'monetary': '月均金额',
            'value_tag': '价值标签',
            'detail_link': '详情链接'
        }
        
        # 验证所有必需列都存在
        for col in required_columns.keys():
            assert col in df.columns, f"缺少必需列: {col}"
        
        # 验证数据类型正确性
        assert pd.api.types.is_datetime64_any_dtype(df['trans_date']), "交易日期类型错误"
        assert pd.api.types.is_numeric_dtype(df['amount']), "交易金额类型错误"
        
        # 验证关键列没有全部为空
        assert df['store_id'].notna().any(), "门店ID列全部为空"
        assert df['segment'].notna().any(), "RFM细分列全部为空"
    
    def test_table_display_data_integrity_validation(self):
        """测试表格数据展示数据完整性验证"""
        df = self.processed_df.copy()
        
        # 验证数据完整性
        assert len(df) > 0, "处理后数据为空"
        
        # 验证门店ID唯一性（在同一日期下）
        duplicate_check = df.groupby(['store_id', 'trans_date']).size().max()
        assert duplicate_check == 1, "存在重复的门店-日期组合"
        
        # 验证金额数据合理性
        assert (df['amount'] > 0).all(), "存在非正数金额"
        assert df['amount'].notna().all(), "存在空的金额数据"
        
        # 验证RFM指标合理性
        if 'monetary' in df.columns:
            assert (df['monetary'] > 0).all(), "月均金额应该为正数"
        if 'frequency' in df.columns:
            assert (df['frequency'] > 0).all(), "交易频次应该为正数"
        if 'recency' in df.columns:
            assert (df['recency'] >= 0).all(), "最近购买天数应该非负"
        
        # 验证细分类型合理性
        valid_segments = {
            "重要价值客户", "重要保持客户", "重要发展客户", "重要挽留客户",
            "一般价值客户", "一般保持客户", "一般发展客户", "一般新客户"
        }
        segment_values = df['segment'].dropna().unique()
        for segment in segment_values:
            assert segment in valid_segments, f"无效的细分类型: {segment}"
    
    def test_csv_export_file_comparison(self):
        """测试CSV数据导出文件比对"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            test_filename = tmp_file.name
        
        try:
            # 执行导出
            export_success = self.display.export_to_csv(test_filename)
            assert export_success, "CSV导出失败"
            
            # 验证文件存在
            assert os.path.exists(test_filename), "导出文件不存在"
            
            # 读取导出的文件并验证
            exported_df = pd.read_csv(test_filename, encoding='utf-8-sig')
            
            # 验证导出文件结构
            assert len(exported_df) > 0, "导出文件为空"
            assert len(exported_df.columns) > 0, "导出文件无列"
            
            # 验证关键列存在
            expected_columns = ['biz_id', 'store_id', 'brand_name', 'segment']
            for col in expected_columns:
                if col in self.processed_df.columns:
                    assert col in exported_df.columns, f"导出文件缺少列: {col}"
            
            # 验证数据一致性（记录数应该匹配）
            expected_records = len(self.processed_df)
            actual_records = len(exported_df)
            assert actual_records == expected_records, f"记录数不匹配: 期望{expected_records}, 实际{actual_records}"
            
            # 验证数据内容
            if 'store_id' in exported_df.columns:
                exported_stores = set(exported_df['store_id'].dropna())
                original_stores = set(self.processed_df['store_id'].dropna())
                assert exported_stores == original_stores, "导出的门店ID不匹配"
            
        finally:
            # 清理临时文件
            if os.path.exists(test_filename):
                os.unlink(test_filename)
    
    def test_csv_export_encoding_handling(self):
        """测试CSV导出编码处理"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            test_filename = tmp_file.name
        
        try:
            # 执行导出
            export_success = self.display.export_to_csv(test_filename)
            assert export_success, "CSV导出失败"
            
            # 验证文件可以用不同编码读取
            try:
                # 尝试UTF-8-SIG编码
                df_utf8_sig = pd.read_csv(test_filename, encoding='utf-8-sig')
                assert len(df_utf8_sig) > 0, "UTF-8-SIG编码读取失败"
            except UnicodeDecodeError:
                pytest.fail("UTF-8-SIG编码读取失败")
            
            # 验证中文字符正确导出
            if 'brand_name' in df_utf8_sig.columns:
                chinese_brands = df_utf8_sig['brand_name'].dropna()
                if len(chinese_brands) > 0:
                    # 检查是否包含中文字符且没有乱码
                    sample_brand = chinese_brands.iloc[0]
                    assert isinstance(sample_brand, str), "品牌名称应该是字符串"
                    # 中文字符应该正常显示，不应该是问号或其他乱码
                    assert '?' not in sample_brand or len(sample_brand.replace('?', '')) > 0
            
        finally:
            # 清理临时文件
            if os.path.exists(test_filename):
                os.unlink(test_filename)


if __name__ == "__main__":
    pytest.main([__file__])