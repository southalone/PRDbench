#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import TreeBuild as tb
import BasicInfo as info

class TestTreeStructure:
    
    def test_member_class_definition(self):
        """测试Member类定义与根节点设置"""
        # 创建一个member实例
        member = tb.member(idx=0, kids=[], spouse=-1)
        
        # 验证属性存在
        assert hasattr(member, 'idx')
        assert hasattr(member, 'kids')
        assert hasattr(member, 'spouse')
        
        # 验证初始值
        assert member.idx == 0
        assert member.kids == []
        assert member.spouse == -1
        
    def test_spouse_relationship(self):
        """测试配偶关系双向建立与子女共有"""
        # 准备测试数据
        test_data = [
            ['张三', '北京', '19700101', '0', '175', '本科', '工程师', '经理', '', '0', '1', '男'],
            ['李四', '上海', '19720101', '0', '165', '本科', '教师', '主任', '张三', '1', '1', '女'],
            ['张小明', '北京', '20000101', '0', '160', '高中', '学生', '学生', '张三', '2', '1', '男']
        ]
        
        # 构建家族树
        family = tb.buildTree(test_data)
        
        # 验证配偶关系
        assert len(family) >= 2
        if len(family) >= 2:
            # 验证配偶关系双向建立
            zhang_san_idx = 0
            li_si_idx = 1
            
            assert family[zhang_san_idx].spouse == li_si_idx
            assert family[li_si_idx].spouse == zhang_san_idx
            
            # 验证子女共有
            assert family[zhang_san_idx].kids == family[li_si_idx].kids
            
    def test_parent_child_relationship(self):
        """测试父子关系建立与索引查找"""
        # 准备测试数据
        test_data = [
            ['张三', '北京', '19700101', '0', '175', '本科', '工程师', '经理', '', '0', '1', '男'],
            ['张小明', '北京', '20000101', '0', '160', '高中', '学生', '学生', '张三', '2', '1', '男']
        ]
        
        # 构建家族树
        family = tb.buildTree(test_data)
        
        # 验证父子关系
        assert len(family) >= 2
        if len(family) >= 2:
            parent_idx = 0
            child_idx = 1
            
            # 验证父代的kids列表包含子代索引
            assert child_idx in family[parent_idx].kids
            
            # 验证索引查找功能
            found_idx = tb.find_rela('张三')
            assert found_idx == parent_idx
            
    def test_index_rebuild_consistency(self):
        """测试索引重建与结构一致性"""
        # 准备测试数据
        test_data = [
            ['张三', '北京', '19700101', '0', '175', '本科', '工程师', '经理', '', '0', '1', '男'],
            ['李四', '上海', '19720101', '0', '165', '本科', '教师', '主任', '', '0', '1', '女'],
            ['张小明', '北京', '20000101', '0', '160', '高中', '学生', '学生', '张三', '2', '1', '男']
        ]
        
        # 构建家族树
        family = tb.buildTree(test_data)
        original_length = len(family)
        
        # 验证索引一致性
        for i, member in enumerate(family):
            assert member.idx == i
            
        # 验证结构完整性
        assert len(family) == original_length
        assert all(isinstance(member, tb.member) for member in family)

if __name__ == '__main__':
    pytest.main([__file__])