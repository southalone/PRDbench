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
    """测试配偶关系双向建立与子女共有"""
    # 保存原始文件名
    original_filename = info.cur_filename
    test_filename = "test_data_017.csv"
    info.cur_filename = test_filename
    
    # 清理之前的数据
    info.alist = []
    tb.family = []
    
    # 创建测试数据
    test_data = [
        {"姓名": "王五", "出生地": "广州", "出生日期": "19800808", "死亡日期": "0", "身高": "172.0",
         "学历": "本科", "职业": "教师", "最高职务": "校长", "亲属": "", "关系": "0", "性别": "男"},
        {"姓名": "赵六", "出生地": "深圳", "出生日期": "19750315", "死亡日期": "0", "身高": "165.0",
         "学历": "高中", "职业": "销售员", "最高职务": "销售经理", "亲属": "王五", "关系": "0", "性别": "女"},
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
    assert len(tb.family) >= 3, "family列表应该包含至少3个成员"
    
    # 找到王五和赵六的索引
    wang_idx = None
    zhao_idx = None
    for i, member in enumerate(tb.family):
        if info.alist[member.idx]['姓名'] == '王五':
            wang_idx = i
        elif info.alist[member.idx]['姓名'] == '赵六':
            zhao_idx = i
    
    assert wang_idx is not None, "应该找到王五"
    assert zhao_idx is not None, "应该找到赵六"
    
    # 检查配偶关系双向建立
    assert tb.family[wang_idx].spouse == zhao_idx, "王五的配偶应该指向赵六"
    assert tb.family[zhao_idx].spouse == wang_idx, "赵六的配偶应该指向王五"
    
    # 检查子女共有
    assert tb.family[wang_idx].kids == tb.family[zhao_idx].kids, "配偶双方的kids列表应该一致"
    assert len(tb.family[wang_idx].kids) > 0, "配偶双方应该有子女"
    
    # 清理测试数据
    info.alist = []
    tb.family = []
    info.cur_filename = original_filename
    
    # 删除测试文件
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    print("✅ 配偶双方的spouse属性正确指向对方，且他们的kids列表一致并包含子女索引")

if __name__ == "__main__":
    test_function()