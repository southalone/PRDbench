#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def main():
    """测试图书添加功能"""
    print("测试图书添加功能...")
    
    try:
        # 设置SQLite模式
        from config.database_mode import db_mode_manager
        db_mode_manager.select_database_mode(prefer_sqlite=True)
        db_mode_manager.switch_to_sqlite()
        
        from services.book_service import book_service
        from utils.database import db_manager
        
        # 准备测试数据
        book_data = {
            "book_name": "测试图书添加",
            "book_id": "9787111234567",
            "auth": "测试作者",
            "category": "测试分类",
            "publisher": "测试出版社",
            "publish_time": "2023-01-01",
            "num_storage": 5
        }
        
        # 1. 检查图书是否已存在，如果存在则删除
        try:
            existing_books = db_manager.execute_query(
                "SELECT COUNT(*) as count FROM book WHERE BookId = ?", (book_data["book_id"],)
            )
            
            if existing_books and len(existing_books) > 0:
                count = existing_books[0].get('count', 0)
                if count > 0:
                    print(f"+ 检测到图书{book_data['book_id']}已存在，先删除...")
                    db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_data["book_id"],))
                    db_manager.execute_update("DELETE FROM user_book WHERE BookId = ?", (book_data["book_id"],))
                    print(f"+ 已清理图书{book_data['book_id']}的所有数据")
                    
                    # 再次验证删除成功
                    check_books = db_manager.execute_query(
                        "SELECT COUNT(*) as count FROM book WHERE BookId = ?", (book_data["book_id"],)
                    )
                    if check_books[0]['count'] == 0:
                        print(f"+ 确认图书{book_data['book_id']}已成功删除")
                    else:
                        print(f"- 图书{book_data['book_id']}删除失败")
                        return False
                else:
                    print(f"+ 图书{book_data['book_id']}不存在，可以直接添加")
            else:
                print(f"+ 图书{book_data['book_id']}不存在，可以直接添加")
                
        except Exception as e:
            print(f"- 检查图书存在性时发生异常: {e}")
            return False
        
        # 在添加前再次确保清理数据
        db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_data["book_id"],))
        db_manager.execute_update("DELETE FROM user_book WHERE BookId = ?", (book_data["book_id"],))
        
        # 2. 测试添加图书
        success, result = book_service.add_book(**book_data)
        
        if success:
            print("+ 图书添加成功")
            print("+ 显示添加成功信息")
            
            # 3. 验证数据库中的数据
            import time
            time.sleep(0.5)  # 等待事务提交
            
            book_results = db_manager.execute_query(
                "SELECT BookName, BookId, Auth, Category, Publisher, PublishTime, NumStorage FROM book WHERE BookId = ?", (book_data["book_id"],)
            )
            
            if book_results:
                book_db_data = book_results[0]
                print("+ 图书信息正确保存到数据库")
                print(f"  书名: {book_db_data['BookName']}")
                print(f"  书号: {book_db_data['BookId']}")
                print(f"  作者: {book_db_data['Auth']}")
                print(f"  分类: {book_db_data['Category']}")
                print(f"  出版社: {book_db_data['Publisher']}")
                print(f"  出版时间: {book_db_data['PublishTime']}")
                print(f"  库存数量: {book_db_data['NumStorage']}")
                print("+ 包含书名、书号、作者、分类、出版社、出版时间、库存数量等7项信息")
                
                # 清理测试数据
                db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_data["book_id"],))
                return True
            else:
                print("- 图书信息未保存到数据库")
                # 调试信息：显示所有图书
                all_books = db_manager.execute_query("SELECT BookId, BookName FROM book LIMIT 10")
                print(f"数据库中现有图书({len(all_books)}个):")
                for book in all_books:
                    print(f"  {book['BookId']} - {book['BookName']}")
                return False
        else:
            print(f"- 图书添加失败: {result}")
            return False
            
    except Exception as e:
        print(f"- 测试异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
