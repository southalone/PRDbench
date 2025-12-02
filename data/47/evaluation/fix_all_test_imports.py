#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def fix_test_imports_in_file(filepath):
    """修复测试文件中的导入问题"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换各种sqlite导入为统一的db_manager导入
        replacements = [
            # 替换 sqlite_database 模块导入
            (r'from sqlite_database import sqlite_manager', 'from utils.database import db_manager'),
            (r'from utils\.sqlite_database import sqlite_db_manager', 'from utils.database import db_manager'),
            
            # 替换对象引用
            (r'sqlite_manager\.', 'db_manager.'),
            (r'sqlite_db_manager\.', 'db_manager.'),
            
            # 移除init_database调用（新的db_manager不需要）
            (r'db_manager\.init_database\(\)\s*\n', ''),
            (r'sqlite_db_manager\.init_database\(\)\s*\n', ''),
            (r'sqlite_manager\.init_database\(\)\s*\n', ''),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'+ 已修复: {filepath}')
            return True
        else:
            print(f'- 无需修复: {filepath}')
            return False
            
    except Exception as e:
        print(f'x 修复失败: {filepath} - {e}')
        return False

def main():
    """批量修复evaluation/tests目录下的导入问题"""
    tests_dir = 'evaluation/tests'
    fixed_count = 0
    
    print("开始批量修复evaluation/tests中的导入问题...")
    
    # 需要修复的文件列表
    files_to_fix = [
        'test_database_exception.py',
        'test_duplicate_borrow_check.py', 
        'test_stock_check.py',
        'test_password_encryption.py',
        'test_book_uniqueness.py',
        'test_database_init.py',
        'test_1_1_数据库连接与初始化.py'
    ]
    
    for filename in files_to_fix:
        filepath = os.path.join(tests_dir, filename)
        if os.path.exists(filepath):
            if fix_test_imports_in_file(filepath):
                fixed_count += 1
        else:
            print(f'- 文件不存在: {filepath}')
    
    print(f"修复完成！共修复 {fixed_count} 个测试文件")

if __name__ == "__main__":
    main()