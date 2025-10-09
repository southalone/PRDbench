#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def add_low_stock_books():
    """添加库存不足的测试图书"""
    print("=== 添加库存不足测试图书 ===")
    
    try:
        from services.book_service import book_service
        
        # 库存不足的测试图书
        low_stock_books = [
            {
                'book_id': 'WARNING-001',
                'book_name': '库存预警图书1',
                'auth': '测试作者',
                'category': '测试',
                'publisher': '测试出版社',
                'publish_time': '2023-01-01',
                'num_storage': 1
            },
            {
                'book_id': 'WARNING-002', 
                'book_name': '库存预警图书2',
                'auth': '测试作者',
                'category': '测试',
                'publisher': '测试出版社',
                'publish_time': '2023-01-01',
                'num_storage': 2
            }
        ]
        
        print("开始添加库存不足图书...")
        
        for book_info in low_stock_books:
            # 先删除可能存在的同名图书
            try:
                book_service.delete_book(book_info['book_id'])
                print(f"- 删除已存在的 {book_info['book_id']}")
            except:
                pass
            
            # 添加新图书
            success, result = book_service.add_book(
                book_name=book_info['book_name'],
                book_id=book_info['book_id'],
                auth=book_info['auth'],
                category=book_info['category'],
                publisher=book_info['publisher'],
                publish_time=book_info['publish_time'],
                num_storage=book_info['num_storage']
            )
            
            if success:
                print(f"+ 成功添加: {book_info['book_name']} (库存: {book_info['num_storage']})")
            else:
                print(f"- 添加失败: {book_info['book_name']} - {result}")
        
        # 验证添加结果
        print("\n验证库存预警图书:")
        low_stock_list = book_service.get_low_stock_books(threshold=3)
        
        if low_stock_list:
            print(f"发现 {len(low_stock_list)} 本库存不足图书:")
            for book in low_stock_list:
                print(f"  - {book['BookName']}: 库存 {book['NumStorage']} 本")
        else:
            print("未发现库存不足图书")
        
        print("\n库存不足测试图书添加完成!")
        return True
        
    except Exception as e:
        print(f"添加图书异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_low_stock_books()
    sys.exit(0 if success else 1)