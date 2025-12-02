#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def fix_mysql_syntax_in_file(filepath):
    """修复文件中的MySQL语法为SQLite语法"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换 %s 为 ?
        content = re.sub(r'%s', '?', content)
        
        # 替换 NOW() 为 datetime('now')
        content = re.sub(r'NOW\(\)', "datetime('now')", content)
        
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
    """批量修复evaluation/tests目录下的MySQL语法"""
    tests_dir = 'evaluation/tests'
    fixed_count = 0
    
    print("开始批量修复evaluation/tests中的MySQL语法...")
    
    for filename in os.listdir(tests_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(tests_dir, filename)
            if fix_mysql_syntax_in_file(filepath):
                fixed_count += 1
    
    print(f"修复完成！共修复 {fixed_count} 个测试文件")

if __name__ == "__main__":
    main()