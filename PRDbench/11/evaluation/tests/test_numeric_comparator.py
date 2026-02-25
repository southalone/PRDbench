import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import compare_numbers


def test_numeric_comparator():
    """测试数值比较器功能"""
    # 准备 (Arrange): 准备三组输入数据：(a=5, b=10), (a=10, b=5), (a=5, b=5)
    test_cases = [
        (5, 10, -1),  # a < b 应该返回 -1
        (10, 5, 1),   # a > b 应该返回 1
        (5, 5, 0)     # a == b 应该返回 0
    ]
    
    # 执行 (Act) 和 断言 (Assert)
    for a, b, expected in test_cases:
        result = compare_numbers(a, b)
        assert result == expected, f"compare_numbers({a}, {b}) 应该返回 {expected}，但返回了 {result}"