# -*- coding: utf-8 -*-
"""数据库连接异常处理测试"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.database import db_manager
    
    def test_database_connection_exception():
        """测试数据库连接异常处理功能"""
        
        # 使用错误的数据库路径测试异常处理
        original_path = db_manager.db_path
        db_manager.db_path = '/nonexistent/path/test.db'
        
        try:
            # 尝试连接错误的数据库路径
            result = db_manager.test_connection()
            if not result:
                print("测试通过：正确处理数据库连接异常")
                db_manager.db_path = original_path
                return True
            else:
                print("测试失败：未正确处理数据库连接异常")
                db_manager.db_path = original_path
                return False
        except Exception as e:
            print(f"测试通过：捕获到异常 - {e}")
            db_manager.db_path = original_path
            return True
    
    if __name__ == "__main__":
        try:
            if test_database_connection_exception():
                print("[PASS] 测试通过：数据库连接异常处理功能正常")
            else:
                print("[FAIL] 测试失败：数据库连接异常处理异常")
                sys.exit(1)
        except Exception as e:
            print(f"[FAIL] 测试失败：{e}")
            sys.exit(1)

except ImportError as e:
    print(f"[FAIL] 导入模块失败：{e}")
    sys.exit(1)