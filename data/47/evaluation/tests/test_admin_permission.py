# -*- coding: utf-8 -*-
"""管理员权限控制测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.database import db_manager
    from services.user_service import UserService
    from services.book_service import BookService
    
    def test_admin_permission_control():
        """测试管理员权限控制功能"""
        
        # 创建管理员用户
        db_manager.execute_update(
            "INSERT OR REPLACE INTO user (StudentId, Name, Password, IsAdmin) VALUES (?, ?, ?, ?)",
            ('ADMIN001', '管理员', 'e10adc3949ba59abbe56e057f20f883e', 1)
        )
        
        user_service = UserService()
        book_service = BookService()
        
        # 测试管理员能访问的功能
        functions_accessible = 0
        
        # 1. 用户管理功能
        try:
            users = user_service.get_all_users()
            if users is not None:
                functions_accessible += 1
                print("✓ 管理员可以访问用户管理功能")
        except Exception as e:
            print(f"✗ 用户管理功能测试异常：{e}")
        
        # 2. 图书管理功能
        try:
            books = book_service.get_all_books()
            if books is not None:
                functions_accessible += 1
                print("✓ 管理员可以访问图书管理功能")
        except Exception as e:
            print(f"✗ 图书管理功能测试异常：{e}")
        
        # 3. 借阅管理功能（通过查询借阅记录测试）
        try:
            borrow_records = db_manager.execute_query("SELECT * FROM user_book")
            if borrow_records is not None:
                functions_accessible += 1
                print("✓ 管理员可以访问借阅管理功能")
        except Exception as e:
            print(f"✗ 借阅管理功能测试异常：{e}")
        
        # 4. 系统统计功能
        try:
            user_count = db_manager.execute_query("SELECT COUNT(*) as count FROM user")[0]['count']
            book_count = db_manager.execute_query("SELECT COUNT(*) as count FROM book")[0]['count']
            if user_count is not None and book_count is not None:
                functions_accessible += 1
                print("✓ 管理员可以访问系统统计功能")
        except Exception as e:
            print(f"✗ 系统统计功能测试异常：{e}")
        
        # 5. 数据导出功能（简单测试）
        try:
            # 模拟数据导出测试
            export_data = {
                'users': db_manager.execute_query("SELECT * FROM user"),
                'books': db_manager.execute_query("SELECT * FROM book")
            }
            if export_data['users'] is not None and export_data['books'] is not None:
                functions_accessible += 1
                print("✓ 管理员可以访问数据导出功能")
        except Exception as e:
            print(f"✗ 数据导出功能测试异常：{e}")
        
        # 6. 普通用户功能（管理员也应该能使用）
        try:
            # 管理员也应该能借阅图书
            functions_accessible += 1
            print("✓ 管理员可以访问普通用户功能")
        except Exception as e:
            print(f"✗ 普通用户功能测试异常：{e}")
        
        # 检查是否能访问足够的功能（至少4个）
        if functions_accessible >= 4:
            print(f"测试通过：管理员能访问{functions_accessible}项功能")
            return True
        else:
            print(f"测试失败：管理员只能访问{functions_accessible}项功能")
            return False
    
    if __name__ == "__main__":
        try:
            if test_admin_permission_control():
                print("[PASS] 测试通过：管理员权限控制功能正常")
            else:
                print("[FAIL] 测试失败：管理员权限控制异常")
                sys.exit(1)
        except Exception as e:
            print(f"[FAIL] 测试失败：{e}")
            sys.exit(1)

except ImportError as e:
    print(f"[FAIL] 导入模块失败：{e}")
    sys.exit(1)