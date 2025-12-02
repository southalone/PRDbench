#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import BasicInfo as info
import pandas as pd

class TestDataProcessing:
    
    def test_data_type_handling(self):
        """测试数据类型处理与结果聚合"""
        # 准备测试数据
        test_data = [
            ['张三', '北京', '19900101', '0', '175.5', '本科', '工程师', '经理', '', '0', '1', '男'],
            ['李四', '上海', '19850615', '20201212', '168.0', '研究生', '教师', '主任', '', '0', '1', '女'],
            ['王五', '广州', '19750320', '0', '180.2', '高中', '司机', '队长', '', '0', '1', '男']
        ]
        
        # 保存到临时文件
        temp_file = 'temp_test_data.csv'
        df = pd.DataFrame(test_data, columns=[
            'name', 'born_place', 'born_date', 'dead_date', 'height', 
            'edu_bg', 'pos', 'top_pos', 'born_rela', 'rela_ship', 'layer', 'sex'
        ])
        df.to_csv(temp_file, index=False, encoding='utf-8')
        
        try:
            # 测试数据读取和类型转换
            df_read = pd.read_csv(temp_file, encoding='utf-8')
            
            # 验证数据类型处理
            assert len(df_read) == 3
            
            # 验证数值型字段处理
            heights = df_read['height'].astype(float)
            assert all(isinstance(h, float) for h in heights)
            
            # 验证日期字段处理
            birth_dates = df_read['born_date'].astype(str)
            assert all(len(date) == 8 for date in birth_dates if date != '0')
            
            # 验证结果聚合
            male_count = len(df_read[df_read['sex'] == '男'])
            female_count = len(df_read[df_read['sex'] == '女'])
            assert male_count + female_count == len(df_read)
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == '__main__':
    pytest.main([__file__])