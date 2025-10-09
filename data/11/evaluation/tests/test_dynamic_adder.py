import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import create_adder


def test_dynamic_adder_generator():
    """测试动态参数函数生成器功能"""
    # 准备 (Arrange): 准备一个基础加数
    base_add = 10
    
    # 执行 (Act): 调用 dynamic_adder_generator(base_add) 生成一个新的加法函数
    adder_func = create_adder(base_add)
    result = adder_func(5)
    
    # 断言 (Assert): 验证 adder_func(5) 的返回值是否为 15
    expected = 15
    assert result == expected, f"动态生成的加法函数应该返回 {expected}，但返回了 {result}"
    
    # 额外测试：验证函数确实是可复用的
    assert adder_func(0) == 10, "adder_func(0) 应该返回 10"
    assert adder_func(-5) == 5, "adder_func(-5) 应该返回 5"