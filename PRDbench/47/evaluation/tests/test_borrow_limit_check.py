# -*- coding: utf-8 -*-
"""借阅数量限制检查测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.database import db_manager
    from services.borrow_service import BorrowService
    
    def test_borrow_limit_check():
        """测试借阅数量限制检查功能"""
        
        # 创建普通用户
        db_manager.execute_update(
            "INSERT OR REPLACE INTO user (StudentId, Name, Password, IsAdmin) VALUES (?, ?, ?, ?)",
            ('USER001', '普通用户', 'e10adc3949ba59abbe56e057f20f883e', 0)
        )
        
        # 创建管理员用户
        db_manager.execute_update(
            "INSERT OR REPLACE INTO user (StudentId, Name, Password, IsAdmin) VALUES (?, ?, ?, ?)",
            ('ADMIN001', '管理员用户', 'e10adc3949ba59abbe56e057f20f883e', 1)
        )
        
        # 创建多本测试图书
        for i in range(15):
            db_manager.execute_update(
                "INSERT OR REPLACE INTO book (BookId, BookName, Auth, Category, NumStorage, NumCanBorrow) VALUES (?, ?, ?, ?, ?, ?)",
                (f'ISBN{i:03d}', f'测试图书{i}', '测试作者', '计算机', 5, 5)
            )
        
        borrow_service = BorrowService()
        
        # 测试普通用户借阅5本书（达到上限）
        for i in range(5):
            db_manager.execute_update(
                "INSERT INTO user_book (StudentId, BookId, BorrowState, BorrowTime, CreateTime, UpdateTime) VALUES (?, ?, ?, datetime('now'), datetime('now'), datetime('now'))",
                ('USER001', f'ISBN{i:03d}', 1)
            )
        
        # 尝试借阅第6本书
        try:
            result = borrow_service.borrow_book('USER001', 'ISBN005')
            if not result['success'] and ('上限' in result['message'] or '超过' in result['message']):
                print("测试通过：正确限制普通用户借阅数量")
                return True
            else:
                print("测试失败：未正确限制普通用户借阅数量")
                return False
        except Exception as e:
            print(f"测试异常：{e}")
            return False
    
    if __name__ == "__main__":
        try:
            if test_borrow_limit_check():
                print("[PASS] 测试通过：借阅数量限制检查功能正常")
            else:
                print("[FAIL] 测试失败：借阅数量限制检查异常")
                sys.exit(1)
        except Exception as e:
            print(f"[FAIL] 测试失败：{e}")
            sys.exit(1)

except ImportError as e:
    print(f"[FAIL] 导入模块失败：{e}")
    sys.exit(1)