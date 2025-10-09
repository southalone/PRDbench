# -*- coding: utf-8 -*-
"""学号格式验证测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from utils.validators import validator

def test_student_id_validation():
    """测试学号格式验证功能"""
    
    # 测试空字符串
    valid, error = validator.validate_student_id("")
    assert not valid, "空字符串应该验证失败"
    assert "不能为空" in error
    
    # 测试超长字符串（21字符）
    valid, error = validator.validate_student_id("a" * 21)
    assert not valid, "超长学号应该验证失败"
    assert "长度" in error
    
    # 测试特殊字符
    valid, error = validator.validate_student_id("test@#$")
    assert not valid, "包含特殊字符应该验证失败"
    assert "字母和数字" in error
    
    print("测试通过：学号格式验证功能正常")
    return True

if __name__ == "__main__":
    try:
        test_student_id_validation()
        print("[PASS] 测试通过：学号格式验证功能正常")
    except Exception as e:
        print(f"[FAIL] 测试失败：{e}")
        sys.exit(1)
