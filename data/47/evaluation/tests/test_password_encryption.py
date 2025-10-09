# -*- coding: utf-8 -*-
"""密码加密存储验证测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from services.user_service import user_service
from utils.encrypt import encryptor

def setup_database():
    """设置测试数据库"""
    try:
        from config.database_mode import db_mode_manager
        # 强制切换到SQLite模式
        db_mode_manager.switch_to_sqlite()
        
        # 使用统一的数据库管理器
        from utils.database import db_manager
        
        return db_manager
    except Exception as e:
        pytest.skip(f"数据库设置失败: {str(e)}")

def test_password_encryption():
    """测试密码加密存储功能"""
    db_manager = setup_database()
    student_id = "TESTPWD001"  # 只包含字母和数字
    password = "password123"
    
    try:
        # 清理测试数据
        db_manager.execute_update("DELETE FROM user WHERE StudentId = ?", (student_id,))
        
        success, result = user_service.register_user(student_id, "测试用户", password)
        assert success, f"用户注册失败: {result}"
        
        # 查询密码
        results = db_manager.execute_query("SELECT Password FROM user WHERE StudentId = ?", (student_id,))
        assert results, "用户未保存到数据库"
        stored_password = results[0]['Password']
        
        assert len(stored_password) == 32, f"密码长度不正确，应为32位"
        assert stored_password != password, "密码未加密"
        assert stored_password == encryptor.md5_hash(password), "MD5加密结果不正确"
        
        print("测试通过：密码正确加密为32位MD5哈希值")
    finally:
        try:
            db_manager.execute_update("DELETE FROM user WHERE StudentId = ?", (student_id,))
        except:
            pass
