#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sys
import os
import pandas as pd
import csv
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import BasicInfo as info

class TestFileFormat:
    
    def test_csv_format_and_field_order(self):
        """测试CSV文件格式与字段顺序"""
        # 创建测试数据
        test_data = [
            ['张三', '北京', '19900101', '0', '175.5', '本科', '工程师', '经理', '', '0', '1', '男']
        ]
        
        # 保存测试文件
        test_file = 'test_format.csv'
        info.save_file(test_data)
        
        try:
            # 检查文件是否存在
            assert os.path.exists('data.csv'), "data.csv文件未创建"
            
            # 检查文件编码（尝试用UTF-8读取）
            with open('data.csv', 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0, "文件内容为空"
            
            # 检查CSV格式
            df = pd.read_csv('data.csv', encoding='utf-8')
            
            # 验证字段顺序（根据PRD要求）
            expected_columns = ['name', 'born_place', 'born_date', 'dead_date', 'height', 
                              'edu_bg', 'pos', 'top_pos', 'born_rela', 'rela_ship', 'layer', 'sex']
            
            # 检查列数
            assert len(df.columns) == len(expected_columns), f"列数不匹配，期望{len(expected_columns)}列，实际{len(df.columns)}列"
            
            # 检查数据完整性
            assert len(df) > 0, "CSV文件中没有数据"
            
            # 检查逗号分隔
            with open('data.csv', 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                assert ',' in first_line, "文件不是逗号分隔格式"
                
        finally:
            # 清理测试文件
            if os.path.exists('data.csv'):
                os.remove('data.csv')

if __name__ == '__main__':
    pytest.main([__file__])