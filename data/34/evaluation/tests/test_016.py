#!/usr/bin/env python
# coding: utf-8

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import BasicInfo as info
import TreeBuild as tb
import pytest

def test_function():
    """测试Member类定义与根节点设置"""
    # 清理之前的数据
    info.alist = []
    tb.family = []
    
    # 添加一个成员
    info.blist = []
    info.add("张三", "北京", "19900101", "0", "175.5", "本科", "软件工程师", "高级工程师", "", "0", "男")
    info.save_file(info.blist)
    
    # 读取文件并构建树
    info.read_file()
    tb.buildTree(info.alist)
    
    # 检查family列表不为空
    assert len(tb.family) > 0, "family列表应该不为空"
    
    # 检查第一个成员（根节点）
    root_member = tb.family[0]
    
    # 检查Member对象包含必要属性
    assert hasattr(root_member, 'idx'), "Member对象应该包含idx属性"
    assert hasattr(root_member, 'kids'), "Member对象应该包含kids属性"
    assert hasattr(root_member, 'spouse'), "Member对象应该包含spouse属性"
    
    # 检查根节点的关系类型为-1（存储在alist中）
    root_info = info.alist[root_member.idx]
    assert root_info['关系'] == -1, "首个成员应该被设为根节点（关系类型为-1）"
    
    # 清理
    info.alist = []
    tb.family = []
    
    print("✅ Member对象包含idx、kids、spouse属性，且首个成员被设为根节点（关系类型为-1）")

if __name__ == "__main__":
    test_function()