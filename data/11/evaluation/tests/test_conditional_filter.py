import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import filter_data


def test_conditional_filter():
    """测试条件过滤器功能"""
    # 准备 (Arrange): 准备一个数据列表和一个自定义条件函数
    data = [1, 2, 3, 4, 5, 6]
    
    def is_even(n):
        """判断是否为偶数的条件函数"""
        return n % 2 == 0
    
    # 执行 (Act): 调用 conditional_filter(data, is_even)
    result = filter_data(data, is_even)
    
    # 断言 (Assert): 验证返回的列表是否为 [2, 4, 6]
    expected = [2, 4, 6]
    assert result == expected, f"filter_data({data}, is_even) 应该返回 {expected}，但返回了 {result}"