#!/usr/bin/env python
# coding: utf-8

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import BasicInfo as info
import TreeBuild as tb
import pytest

def test_function():
    """测试父子关系建立与索引查找"""
    # 保存原始文件名
    original_filename = info.cur_filename
    test_filename = "test_data_018.csv"
    info.cur_filename = test_filename
    
    # 清理之前的数据
    info.alist = []
    tb.family = []
    
    # 创建测试数据
    test_data = [
        {"姓名": "王五", "出生地": "广州", "出生日期": "19800808", "死亡日期": "0", "身高": "172.0", 
         "学历": "本科", "职业": "教师", "最高职务": "校长", "亲属": "", "关系": "0", "性别": "男"},
        {"姓名": "孙七", "出生地": "杭州", "出生日期": "20100101", "死亡日期": "0", "身高": "120.0", 
         "学历": "小学", "职业": "学生", "最高职务": "", "亲属": "王五", "关系": "1", "性别": "男"}
    ]
    
    # 创建测试CSV文件
    df = pd.DataFrame(test_data)
    df.to_csv(test_filename, index=False)
    
    # 读取文件并构建树
    info.read_file()
    tb.buildTree(info.alist)
    
    # 检查family列表包含所有成员
    assert len(tb.family) >= 2, "family列表应该包含至少2个成员"
    
    # 找到王五和孙七的索引
    wang_idx = None
    sun_idx = None
    for i, member in enumerate(tb.family):
        if info.alist[member.idx]['姓名'] == '王五':
            wang_idx = i
        elif info.alist[member.idx]['姓名'] == '孙七':
            sun_idx = i
    
    assert wang_idx is not None, "应该找到王五"
    assert sun_idx is not None, "应该找到孙七"
    
    # 检查父子关系建立
    assert sun_idx in tb.family[wang_idx].kids, "父代成员的kids列表应该包含子代索引"
    
    # 测试通过姓名查找成员
    found_wang_idx = tb.find_rela("王五")
    found_sun_idx = tb.find_rela("孙七")
    
    assert found_wang_idx == wang_idx, "系统应该能通过姓名正确查找到王五在family列表中的位置"
    assert found_sun_idx == sun_idx, "系统应该能通过姓名正确查找到孙七在family列表中的位置"
    
    # 清理测试数据
    info.alist = []
    tb.family = []
    info.cur_filename = original_filename
    
    # 删除测试文件
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    print("✅ 父代成员的kids列表包含子代索引，且系统能通过姓名正确查找到成员在family列表中的位置")

if __name__ == "__main__":
    test_function()