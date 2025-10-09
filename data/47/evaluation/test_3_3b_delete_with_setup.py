#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def test_3_3b_book_delete():
    """测试3.3b图书删除功能 - 包含数据准备和删除验证"""
    print("=== 3.3b 图书删除功能测试 ===\n")
    
    try:
        # 1. 数据准备
        print("1. 准备测试数据...")
        from utils.database import db_manager
        
        # 添加一本专门用于删除测试的图书
        delete_test_book = {
            'book_id': 'DELETE-TEST-001',
            'book_name': '待删除测试图书',
            'auth': '测试作者',
            'category': '测试',
            'publisher': '测试出版社',
            'publish_time': '2023-01-01',
            'num_storage': 1
        }
        
        # 清理可能存在的记录
        db_manager.execute_update('DELETE FROM user_book WHERE BookId = ?', (delete_test_book['book_id'],))
        db_manager.execute_update('DELETE FROM book WHERE BookId = ?', (delete_test_book['book_id'],))
        
        # 添加测试图书
        db_manager.execute_update('''
            INSERT INTO book 
            (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged, CreateTime, UpdateTime) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', (
            delete_test_book['book_id'], delete_test_book['book_name'], delete_test_book['auth'],
            delete_test_book['category'], delete_test_book['publisher'], delete_test_book['publish_time'],
            delete_test_book['num_storage'], delete_test_book['num_storage'], 0
        ))
        
        print(f"+ 已添加测试图书: {delete_test_book['book_name']} ({delete_test_book['book_id']})")
        
        # 2. 创建删除测试输入文件
        print("\n2. 创建删除测试输入...")
        delete_input = '''1
admin
123456

2
5
DELETE-TEST-001
y

0
0
0
'''
        
        with open('evaluation/test_3_3b_temp_input.in', 'w', encoding='utf-8') as f:
            f.write(delete_input)
        
        print("+ 创建临时输入文件")
        
        # 3. 执行删除测试
        print("\n3. 执行删除测试...")
        result = subprocess.run(
            'chcp 65001 && type evaluation\\test_3_3b_temp_input.in | python src\\run.py',
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd='.'
        )
        
        output = result.stdout
        print("+ 测试执行完成")
        
        # 4. 验证删除结果
        print("\n4. 验证删除结果...")
        remaining_books = db_manager.execute_query(
            'SELECT COUNT(*) as count FROM book WHERE BookId = ?', 
            (delete_test_book['book_id'],)
        )
        
        remaining_count = remaining_books[0]['count'] if remaining_books else 0
        
        # 分析输出
        has_confirm_prompt = "确认删除此图书吗" in output
        has_success_msg = "删除成功" in output or remaining_count == 0
        
        print(f"验证结果:")
        print(f"  显示确认提示: {'✓' if has_confirm_prompt else '✗'}")
        print(f"  图书成功删除: {'✓' if remaining_count == 0 else '✗'}")
        print(f"  剩余记录数: {remaining_count}")
        
        # 5. 清理临时文件
        if os.path.exists('evaluation/test_3_3b_temp_input.in'):
            os.remove('evaluation/test_3_3b_temp_input.in')
        
        success = has_confirm_prompt and remaining_count == 0
        
        if success:
            print("\n✓ 3.3b图书删除功能测试通过")
            print("  - 管理员能访问图书删除功能")
            print("  - 显示确认提示") 
            print("  - 确认后成功删除图书记录")
        else:
            print("\n✗ 3.3b图书删除功能测试失败")
            
        return success
        
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_3_3b_book_delete()
    sys.exit(0 if success else 1)