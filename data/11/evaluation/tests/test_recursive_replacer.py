import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import recursive_replace


def test_recursive_replacer():
    """测试递归替换器功能"""
    # 准备 (Arrange): 准备一个嵌套列表，以及替换目标和替换值
    data = [1, [2, 1, [3, 1]]]
    target = 1
    replacement = 'X'
    
    # 执行 (Act): 调用 recursive_replacer(data, target, replacement)
    result = recursive_replace(data, target, replacement)
    
    # 断言 (Assert): 验证返回的列表是否为 ['X', [2, 'X', [3, 'X']]]
    expected = ['X', [2, 'X', [3, 'X']]]
    assert result == expected, f"recursive_replace({data}, {target}, {replacement}) 应该返回 {expected}，但返回了 {result}"
    
    # 额外测试：测试字典结构
    dict_data = {'a': 1, 'b': {'c': 1, 'd': 2}}
    dict_result = recursive_replace(dict_data, 1, 'X')
    dict_expected = {'a': 'X', 'b': {'c': 'X', 'd': 2}}
    assert dict_result == dict_expected, f"字典递归替换失败"
    
    # 额外测试：测试单个值
    single_result = recursive_replace(1, 1, 'X')
    assert single_result == 'X', "单个值替换失败"