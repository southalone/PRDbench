#!/usr/bin/env python
# coding: utf-8

import sys
import os
import pandas as pd
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import BasicInfo as info

def test_function():
    """测试数据存储：文件格式与字段顺序"""
    # 保存原始文件名
    original_filename = info.cur_filename
    test_filename = "test_data_054.csv"
    info.cur_filename = test_filename
    
    # 清理之前的数据
    info.alist = []
    info.blist = []
    
    # 添加一个测试成员
    info.add("张三", "北京", "19900101", "0", "175.5", "本科", "软件工程师", "高级工程师", "", "0", "男")
    info.save_file(info.blist)
    
    # 检查文件是否存在
    assert os.path.exists(test_filename), "data.csv文件应该存在"
    
    # 检查文件编码和格式
    try:
        # 尝试用UTF-8编码读取文件
        df = pd.read_csv(test_filename, encoding='utf-8')
        
        # 检查字段顺序是否按照PRD要求
        expected_columns = ["姓名", "出生地", "出生日期", "死亡日期", "身高", "学历", "职业", "最高职务", "亲属", "关系", "性别"]
        actual_columns = df.columns.tolist()
        
        assert actual_columns == expected_columns, f"字段顺序不正确。期望: {expected_columns}, 实际: {actual_columns}"
        
        # 检查是否使用逗号分隔（通过成功读取CSV验证）
        assert len(df) > 0, "文件应该包含数据"
        
        # 检查数据内容
        assert df.iloc[0]['姓名'] == '张三', "数据内容应该正确"
        
    except UnicodeDecodeError:
        pytest.fail("文件编码不是UTF-8")
    except Exception as e:
        pytest.fail(f"文件格式检查失败: {e}")
    
    # 清理测试数据
    info.alist = []
    info.blist = []
    info.cur_filename = original_filename
    
    # 删除测试文件
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    print("✅ data.csv文件使用UTF-8编码，逗号分隔，字段顺序严格按照PRD要求排列")

if __name__ == "__main__":
    test_function()