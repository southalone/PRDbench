#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用SQLite数据库以替代MySQL进行评估
"""

import sqlite3
import os
import sys

def create_test_database():
    """创建测试数据库和表结构"""
    db_path = 'evaluation/test_library.db'
    
    # 删除已存在的数据库
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 创建用户表
        cursor.execute('''
        CREATE TABLE user (
            StudentId VARCHAR(20) PRIMARY KEY,
            Name VARCHAR(20) NOT NULL,
            Password VARCHAR(32) NOT NULL,
            IsAdmin TINYINT DEFAULT 0,
            tel VARCHAR(30),
            CreateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建图书表
        cursor.execute('''
        CREATE TABLE book (
            BookId VARCHAR(30) PRIMARY KEY,
            BookName VARCHAR(30) NOT NULL,
            Auth VARCHAR(20) NOT NULL,
            Category VARCHAR(10),
            Publisher VARCHAR(30),
            PublishTime DATE,
            NumStorage INT DEFAULT 0,
            NumCanBorrow INT DEFAULT 0,
            NumBookinged INT DEFAULT 0
        )
        ''')
        
        # 创建借阅表
        cursor.execute('''
        CREATE TABLE user_book (
            StudentId VARCHAR(20),
            BookId VARCHAR(30),
            BorrowTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ReturnTime TIMESTAMP NULL,
            BorrowState TINYINT DEFAULT 1,
            BookingState TINYINT DEFAULT 0,
            FOREIGN KEY (StudentId) REFERENCES user(StudentId),
            FOREIGN KEY (BookId) REFERENCES book(BookId)
        )
        ''')
        
        # 插入测试数据
        # 默认管理员
        cursor.execute('''
        INSERT INTO user (StudentId, Name, Password, IsAdmin, tel) 
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', '系统管理员', 'e10adc3949ba59abbe56e057f20f883e', 1, 'admin@library.com'))
        
        # 测试用户
        cursor.execute('''
        INSERT INTO user (StudentId, Name, Password, IsAdmin, tel) 
        VALUES (?, ?, ?, ?, ?)
        ''', ('TEST001', '测试用户', 'e10adc3949ba59abbe56e057f20f883e', 0, 'test@email.com'))
        
        # 测试图书
        cursor.execute('''
        INSERT INTO book (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('ISBN001', 'Python编程入门', '张三', '计算机', '人民出版社', '2023-01-01', 10, 8, 0))
        
        cursor.execute('''
        INSERT INTO book (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('ISBN002', 'Java程序设计', '李四', '计算机', '清华出版社', '2023-02-01', 5, 0, 2))
        
        conn.commit()
        print("测试数据库创建成功!")
        print(f"数据库位置: {os.path.abspath(db_path)}")
        return True
        
    except Exception as e:
        print(f"创建测试数据库失败: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    success = create_test_database()
    sys.exit(0 if success else 1)