import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import extract_unique


def test_unique_list_extractor():
    """测试去重列表生成器功能"""
    # 准备 (Arrange): 准备一个带重复元素的列表
    data = ['a', 'b', 'a', 'c', 'b']
    
    # 执行 (Act): 调用 unique_list_extractor(data)
    result = extract_unique(data)
    
    # 断言 (Assert): 验证返回的列表是否为 ['a', 'b', 'c']，并严格保持了各元素首次出现的原始顺序
    expected = ['a', 'b', 'c']
    assert result == expected, f"extract_unique({data}) 应该返回 {expected}，但返回了 {result}"
    
    # 额外测试：测试空列表
    assert extract_unique([]) == [], "空列表应该返回空列表"
    
    # 额外测试：测试无重复元素
    unique_data = [1, 2, 3]
    assert extract_unique(unique_data) == unique_data, "无重复元素的列表应该保持不变"