# -*- coding: utf-8 -*-
"""重复借阅检查测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.database import db_manager
    from services.borrow_service import borrow_service
    from config.database_mode import db_mode_manager
    
    # 设置SQLite模式
    db_mode_manager.select_database_mode(prefer_sqlite=True)
    db_mode_manager.switch_to_sqlite()
    
    def test_duplicate_borrow_check():
        """测试重复借阅检查功能"""
        
        # 创建测试用户
        db_manager.execute_query(
            "INSERT OR REPLACE INTO user (StudentId, Name, Password, IsAdmin) VALUES (?, ?, ?, ?)",
            ('TEST001', '测试用户', 'e10adc3949ba59abbe56e057f20f883e', 0)
        )
        
        # 创建测试图书
        db_manager.execute_query(
            "INSERT OR REPLACE INTO book (BookId, BookName, Auth, Category, NumStorage, NumCanBorrow) VALUES (?, ?, ?, ?, ?, ?)",
            ('ISBN001', 'Python编程', '张三', '计算机', 5, 4)
        )
        
        # 模拟用户已借阅该图书
        from datetime import datetime
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db_manager.execute_query(
            "INSERT INTO user_book (StudentId, BookId, BorrowState, BorrowTime) VALUES (?, ?, ?, ?)",
            ('TEST001', 'ISBN001', 1, current_time)
        )
        
        # 尝试重复借阅同一本书
        try:
            result = borrow_service.borrow_book('TEST001', 'ISBN001')
            if not result['success'] and '已借阅' in result['message']:
                print("测试通过：正确阻止重复借阅")
                return True
            else:
                print("测试失败：未阻止重复借阅")
                return False
        except Exception as e:
            print(f"测试异常：{e}")
            return False
    
    if __name__ == "__main__":
        try:
            if test_duplicate_borrow_check():
                print("[PASS] 测试通过：重复借阅检查功能正常")
            else:
                print("[FAIL] 测试失败：重复借阅检查异常")
                sys.exit(1)
        except Exception as e:
            print(f"[FAIL] 测试失败：{e}")
            sys.exit(1)

except ImportError as e:
    print(f"[FAIL] 导入模块失败：{e}")
    sys.exit(1)