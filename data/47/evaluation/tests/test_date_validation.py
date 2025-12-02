# -*- coding: utf-8 -*-
"""日期格式验证测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from utils.validators import validator

def test_date_format_validation():
    """测试日期格式验证功能"""
    
    # 测试无效格式1
    valid, error = validator.validate_date("2023/13/01")
    assert not valid, "无效日期格式应该验证失败"
    assert "格式" in error
    
    # 测试无效格式2
    valid, error = validator.validate_date("2023-02-30")
    assert not valid, "不存在的日期应该验证失败"
    assert "格式" in error
    
    # 测试无效格式3
    valid, error = validator.validate_date("abcd-ef-gh")
    assert not valid, "字母日期应该验证失败"
    assert "格式" in error
    
    print("测试通过：日期格式验证功能正常")
    return True
