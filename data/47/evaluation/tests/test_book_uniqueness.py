# -*- coding: utf-8 -*-
"""书号唯一性验证测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from services.book_service import book_service

def setup_database():
    """设置测试数据库"""
    try:
        from config.database_mode import db_mode_manager
        # 强制切换到SQLite模式
        db_mode_manager.switch_to_sqlite()
        
        # 确保所有模块都使用SQLite管理器
        from utils.database import db_manager
        
        return db_manager
    except Exception as e:
        pytest.skip(f"数据库设置失败: {str(e)}")

def test_book_id_uniqueness():
    """测试书号唯一性检查功能"""
    db_manager = setup_database()
    book_id = "TESTBOOK001"
    
    try:
        # 清理测试数据
        db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_id,))
        
        # 第一次添加
        success1, result1 = book_service.add_book(
            book_name="测试图书", book_id=book_id, auth="测试作者",
            category="测试", publisher="测试出版社",
            publish_time="2023-01-01", num_storage=5
        )
        assert success1, f"第一次添加失败: {result1}"
        
        # 第二次添加相同书号
        success2, result2 = book_service.add_book(
            book_name="测试图书2", book_id=book_id, auth="测试作者2"
        )
        assert not success2, "应该检测到重复书号"
        assert "已存在" in result2 or "重复" in result2, f"错误信息应提示重复: {result2}"
        
        print("测试通过：书号唯一性检查正常")
    finally:
        try:
            db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_id,))
        except:
            pass
