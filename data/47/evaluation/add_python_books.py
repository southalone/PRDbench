#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def add_python_books():
    """添加3本包含Python的图书，详细打印过程"""
    print("=== 添加Python图书详细过程 ===\n")
    
    try:
        # 1. 导入必要模块
        print("1. 导入模块...")
        from utils.database import db_manager
        from services.book_service import book_service
        print(f"+ db_manager类型: {type(db_manager)}")
        print(f"+ book_service类型: {type(book_service)}")
        
        # 2. 测试数据库连接
        print("\n2. 测试数据库连接...")
        if db_manager.test_connection():
            print("+ 数据库连接成功")
        else:
            print("- 数据库连接失败")
            return False
        
        # 3. 检查当前数据库状态
        print("\n3. 检查当前数据库状态...")
        all_books = db_manager.execute_query("SELECT BookId, BookName FROM book")
        print(f"+ 数据库中当前图书总数: {len(all_books)}")
        
        python_books_current = db_manager.execute_query(
            "SELECT BookName FROM book WHERE BookName LIKE ?", ('%Python%',)
        )
        print(f"+ 当前包含Python的图书: {len(python_books_current)}本")
        
        # 4. 准备要添加的图书数据
        print("\n4. 准备图书数据...")
        python_books = [
            {
                'book_name': 'Python编程：从入门到实践',
                'book_id': '978-7-111-54742-6',
                'auth': '埃里克·马瑟斯',
                'category': '计算机',
                'publisher': '机械工业出版社',
                'publish_time': '2016-07-01',
                'num_storage': 5
            },
            {
                'book_name': '流畅的Python',
                'book_id': '978-7-115-42884-6', 
                'auth': 'Luciano Ramalho',
                'category': '计算机',
                'publisher': '人民邮电出版社',
                'publish_time': '2017-05-01',
                'num_storage': 3
            },
            {
                'book_name': 'Python核心编程',
                'book_id': '978-7-115-28533-4',
                'auth': 'Wesley J. Chun',
                'category': '计算机',
                'publisher': '人民邮电出版社',
                'publish_time': '2012-06-01',
                'num_storage': 4
            }
        ]
        
        # 添加张三的两本小说
        zhangsan_books = [
            {
                'book_name': '春天的故事',
                'book_id': '978-7-5086-5001-0',
                'auth': '张三',
                'category': '文学',
                'publisher': '作家出版社',
                'publish_time': '2020-03-01',
                'num_storage': 6
            },
            {
                'book_name': '夏日回忆录',
                'book_id': '978-7-5086-5002-7',
                'auth': '张三',
                'category': '文学',
                'publisher': '人民文学出版社',
                'publish_time': '2021-07-01',
                'num_storage': 4
            }
        ]
        
        # 添加一本童话（用于书号精确查询测试）
        fairy_tale_books = [
            {
                'book_name': '安徒生童话集',
                'book_id': 'ISBN001',
                'auth': '汉斯·克里斯蒂安·安徒生',
                'category': '儿童文学',
                'publisher': '人民出版社',
                'publish_time': '2019-09-01',
                'num_storage': 8
            }
        ]
        
        all_books = python_books + zhangsan_books + fairy_tale_books
        
        print(f"+ 准备添加 {len(python_books)} 本Python图书")
        print(f"+ 准备添加 {len(zhangsan_books)} 本张三的小说")
        print(f"+ 总计添加 {len(all_books)} 本图书")
        
        # 5. 逐个添加图书
        print("\n5. 开始添加图书...")
        success_count = 0
        
        for i, book_data in enumerate(all_books, 1):
            print(f"\n--- 添加第{i}本图书 ---")
            print(f"书名: {book_data['book_name']}")
            print(f"书号: {book_data['book_id']}")
            print(f"作者: {book_data['auth']}")
            
            # 检查是否已存在
            existing = db_manager.execute_query(
                "SELECT COUNT(*) as count FROM book WHERE BookId = ?", (book_data['book_id'],)
            )
            if existing and existing[0]['count'] > 0:
                print(f"图书{book_data['book_id']}已存在，跳过添加")
                continue
            
            # 尝试添加
            try:
                success, result = book_service.add_book(**book_data)
                if success:
                    print(f"+ 添加成功")
                    success_count += 1
                    
                    # 验证添加结果
                    verify_books = db_manager.execute_query(
                        "SELECT BookName, Auth FROM book WHERE BookId = ?", (book_data['book_id'],)
                    )
                    if verify_books:
                        book = verify_books[0]
                        print(f"+ 验证成功: {book['BookName']} - {book['Auth']}")
                    else:
                        print("- 验证失败: 图书未在数据库中找到")
                        
                else:
                    print(f"- 添加失败: {result}")
                    
            except Exception as e:
                print(f"- 添加异常: {e}")
                import traceback
                traceback.print_exc()
        
        # 6. 最终验证
        print(f"\n6. 最终验证...")
        print(f"成功添加 {success_count}/{len(all_books)} 本图书")
        
        # 查询所有包含Python的图书
        final_python_books = db_manager.execute_query(
            "SELECT BookName, Auth FROM book WHERE BookName LIKE ?", ('%Python%',)
        )
        print(f"\n数据库中包含Python的图书总计: {len(final_python_books)}本")
        for book in final_python_books:
            print(f"  {book['BookName']} - {book['Auth']}")
        
        # 查询张三的图书
        zhangsan_books_final = db_manager.execute_query(
            "SELECT BookName, Auth FROM book WHERE Auth = ?", ('张三',)
        )
        print(f"\n数据库中张三的图书总计: {len(zhangsan_books_final)}本")
        for book in zhangsan_books_final:
            print(f"  {book['BookName']} - {book['Auth']}")
            
        return len(final_python_books) >= 3 and len(zhangsan_books_final) >= 2
        
    except Exception as e:
        print(f"脚本异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_python_books()
    if success:
        print("\n[PASS] Python图书添加完成")
    else:
        print("\n[FAIL] Python图书添加失败")
    sys.exit(0 if success else 1)