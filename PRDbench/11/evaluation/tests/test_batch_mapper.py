import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import batch_map_replace


def test_batch_mapper_replacer():
    """测试批量映射替换器功能"""
    # 准备 (Arrange): 准备一个数据列表和一个映射字典
    data = ['A', 'B', 'C']
    mapping = {'A': 'Apple', 'B': 'Banana'}
    
    # 执行 (Act): 调用 batch_mapper(data, mapping)
    result = batch_map_replace(data, mapping)
    
    # 断言 (Assert): 验证返回的列表是否为 ['Apple', 'Banana', 'C']
    expected = ['Apple', 'Banana', 'C']
    assert result == expected, f"batch_map_replace({data}, {mapping}) 应该返回 {expected}，但返回了 {result}"
    
    # 额外测试：测试字典数据
    dict_data = {'x': 'A', 'y': 'B', 'z': 'D'}
    dict_result = batch_map_replace(dict_data, mapping)
    dict_expected = {'x': 'Apple', 'y': 'Banana', 'z': 'D'}
    assert dict_result == dict_expected, f"字典批量映射失败"
    
    # 额外测试：测试单个值
    single_result = batch_map_replace('A', mapping)
    assert single_result == 'Apple', "单个值映射失败"
    
    # 测试不存在的映射
    single_result2 = batch_map_replace('D', mapping)
    assert single_result2 == 'D', "不存在的映射应该保持原值"