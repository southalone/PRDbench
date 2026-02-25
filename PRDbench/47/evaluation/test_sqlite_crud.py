#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def test_sqlite_crud():
    """测试SQLite原生实现的基础增删改查功能"""
    print("=== SQLite基础功能测试 ===")
    
    try:
        from utils.database import db_manager
        
        print(f"数据库管理器类型: {type(db_manager)}")
        
        # 1. 测试连接
        print("\n1. 测试数据库连接...")
        if db_manager.test_connection():
            print("+ 数据库连接成功")
        else:
            print("- 数据库连接失败")
            return False
        
        # 2. 测试增加 (Create)
        print("\n2. 测试增加数据...")
        test_book_id = "TEST-CRUD-001"
        
        # 先清理可能存在的测试数据
        db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (test_book_id,))
        
        # 添加测试图书
        insert_sql = """
            INSERT INTO book 
            (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged, CreateTime, UpdateTime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """
        result = db_manager.execute_update(insert_sql, (
            test_book_id, "SQLite测试图书", "测试作者", "测试分类", 
            "测试出版社", "2023-01-01", 3, 3, 0
        ))
        
        if result > 0:
            print("+ 添加数据成功")
        else:
            print("- 添加数据失败")
            return False
        
        # 3. 测试查询 (Read)
        print("\n3. 测试查询数据...")
        select_sql = "SELECT BookId, BookName, Auth, NumStorage FROM book WHERE BookId = ?"
        books = db_manager.execute_query(select_sql, (test_book_id,))
        
        if books and len(books) > 0:
            book = books[0]
            print("+ 查询数据成功")
            print(f"  书号: {book['BookId']}")
            print(f"  书名: {book['BookName']}")
            print(f"  作者: {book['Auth']}")
            print(f"  库存: {book['NumStorage']}")
        else:
            print("- 查询数据失败")
            return False
        
        # 4. 测试修改 (Update)
        print("\n4. 测试修改数据...")
        update_sql = "UPDATE book SET BookName = ?, NumStorage = ?, UpdateTime = datetime('now') WHERE BookId = ?"
        result = db_manager.execute_update(update_sql, ("SQLite修改测试图书", 5, test_book_id))
        
        if result > 0:
            print("+ 修改数据成功")
            
            # 验证修改结果
            books = db_manager.execute_query(select_sql, (test_book_id,))
            if books:
                book = books[0]
                print(f"  修改后书名: {book['BookName']}")
                print(f"  修改后库存: {book['NumStorage']}")
        else:
            print("- 修改数据失败")
            return False
        
        # 5. 测试删除 (Delete)
        print("\n5. 测试删除数据...")
        delete_sql = "DELETE FROM book WHERE BookId = ?"
        result = db_manager.execute_update(delete_sql, (test_book_id,))
        
        if result > 0:
            print("+ 删除数据成功")
            
            # 验证删除结果
            books = db_manager.execute_query(select_sql, (test_book_id,))
            if not books or len(books) == 0:
                print("+ 删除验证成功，记录已不存在")
            else:
                print("- 删除验证失败，记录仍然存在")
                return False
        else:
            print("- 删除数据失败")
            return False
        
        print("\n=== SQLite基础功能测试全部通过 ===")
        return True
        
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sqlite_crud()
    if success:
        print("[PASS] SQLite基础功能测试通过")
    else:
        print("[FAIL] SQLite基础功能测试失败")
    sys.exit(0 if success else 1)