# -*- coding: utf-8 -*-
"""密码强度验证测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from utils.validators import validator

def test_password_strength_validation():
    """测试密码强度验证功能"""
    
    # 测试空密码
    valid, error = validator.validate_password("")
    assert not valid, "空密码应该验证失败"
    assert "不能为空" in error
    
    # 测试短密码（5字符）
    valid, error = validator.validate_password("12345")
    assert not valid, "短密码应该验证失败"
    assert "长度" in error
    
    # 测试超长密码（33字符）
    valid, error = validator.validate_password("a" * 33)
    assert not valid, "超长密码应该验证失败"
    assert "长度" in error
    
    print("测试通过：密码强度验证功能正常")
    return True
