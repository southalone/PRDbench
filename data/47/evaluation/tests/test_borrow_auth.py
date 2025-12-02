# -*- coding: utf-8 -*-
"""借阅身份验证检查测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from services.borrow_service import borrow_service
from services.auth_service import auth_service

def test_borrow_authentication_check():
    """测试借阅身份验证检查功能"""
    auth_service.logout()
    
    try:
        success, result = borrow_service.borrow_book("TESTUSER", "TESTBOOK001")
        assert not success, "未登录用户应该被阻止借阅"
        assert "登录" in result or "身份" in result, f"应提示身份验证错误: {result}"
        
        print("测试通过：正确阻止未登录用户借阅")
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")
