# -*- coding: utf-8 -*-
"""库存检查测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from services.borrow_service import borrow_service
from services.auth_service import auth_service
from services.user_service import user_service

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

def test_stock_check():
    """测试库存检查功能"""
    db_manager = setup_database()
    book_id = "TESTZEROSTOCK"
    user_id = "TESTUSERSTOCK"
    
    try:
        # 清理测试数据
        db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_id,))
        db_manager.execute_update("DELETE FROM user WHERE StudentId = ?", (user_id,))
        
        # 创建测试用户
        db_manager.execute_update("""
            INSERT INTO user (StudentId, Name, Password, IsAdmin, tel)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, "测试用户", "hashedpwd", 0, "test@test.com"))
        
        # 创建库存为0的测试图书
        db_manager.execute_update("""
            INSERT INTO book (BookName, BookId, Auth, NumStorage, NumCanBorrow)
            VALUES (?, ?, ?, ?, ?)
        """, ("测试图书", book_id, "测试作者", 1, 0))
        
        # 模拟用户登录
        user = user_service.get_user_by_id(user_id)
        if user:
            auth_service.current_user = user
            
            success, result = borrow_service.borrow_book(user_id, book_id)
            assert not success, "应该阻止借阅库存为0的图书"
            assert "库存" in result or "不足" in result, f"应提示库存不足: {result}"
        
        print("测试通过：正确阻止借阅库存为0的图书")
    finally:
        try:
            db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_id,))
            db_manager.execute_update("DELETE FROM user WHERE StudentId = ?", (user_id,))
        except:
            pass
