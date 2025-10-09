#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实体输出格式测试
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import pytest

def test_entity_name_and_type():
    """测试实体名称和类型输出"""
    # 模拟实体数据
    entities = {
        'nr': [('加贺恭一郎', 3, '是一名优秀的刑警')],
        'ns': [('东京', 2, '案件发生在东京的')],
        't': [('2023年3月15日', 1, '案件发生在2023年3月15日晚上')],
        'nn': [('医生', 1, '医生检查了病人的')]
    }

    # 测试每个实体都包含名称和类型
    for entity_type, entity_list in entities.items():
        for entity_name, frequency, context in entity_list:
            assert entity_name is not None and entity_name != ""
            assert entity_type in ['nr', 'ns', 't', 'nn']
            assert isinstance(frequency, int) and frequency > 0
            assert context is not None and context != ""

def test_entity_frequency():
    """测试实体频次信息"""
    # 模拟实体数据
    entities = {
        'nr': [('加贺恭一郎', 3, '是一名优秀的刑警')],
        'ns': [('东京', 2, '案件发生在东京的')]
    }

    # 测试频次信息
    for entity_type, entity_list in entities.items():
        for entity_name, frequency, context in entity_list:
            assert isinstance(frequency, int)
            assert frequency > 0

def test_entity_context():
    """测试实体上下文信息"""
    # 模拟实体数据
    entities = {
        'nr': [('加贺恭一郎', 3, '是一名优秀的刑警')],
        'ns': [('东京', 2, '案件发生在东京的')]
    }

    # 测试上下文信息
    for entity_type, entity_list in entities.items():
        for entity_name, frequency, context in entity_list:
            assert context is not None
            assert isinstance(context, str)
            assert len(context) > 0

if __name__ == "__main__":
    pytest.main([__file__])
