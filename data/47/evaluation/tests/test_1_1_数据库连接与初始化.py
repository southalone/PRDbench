#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def main():
    """测试数据库连接与初始化"""
    print("测试数据库连接...")
    
    try:
        # 导入并切换到SQLite模式
        from config.database_mode import db_mode_manager
        
        # 检测并选择数据库模式
        db_mode = db_mode_manager.select_database_mode(prefer_mysql=False)
        
        if db_mode == 'sqlite':
            print("+ 数据库连接成功（SQLite模式）")
            
            # 检查SQLite数据库表结构
            from utils.database import db_manager
            
            tables = ['user', 'book', 'user_book']
            table_count = 0
            for table in tables:
                try:
                    result = db_manager.execute_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if result:
                        print(f"+ {table}表存在且可访问")
                        table_count += 1
                    else:
                        print(f"- {table}表不存在")
                except Exception as e:
                    print(f"- {table}表检查失败: {e}")
            
            if table_count == 3:
                print("数据库初始化验证完成")
                return True
            else:
                print(f"数据库表结构不完整：{table_count}/3")
                return False
        else:
            print("- 数据库连接失败")
            return False
    except Exception as e:
        print(f"- 测试异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("[PASS] 测试通过")
    else:
        print("[FAIL] 测试失败")
    sys.exit(0 if success else 1)
