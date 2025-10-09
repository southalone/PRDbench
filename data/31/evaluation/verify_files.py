#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用文件验证脚本
"""
import os
import sys

def verify_file(path, file_type="file"):
    """验证单个文件"""
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    
    if exists and size > 0:
        print(f'{file_type} file generated: True {size} bytes')
        return True
    else:
        print(f'{file_type} file missing or empty: {exists} {size} bytes')
        return False

def verify_svg_content(path):
    """验证SVG文件内容"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()[:500]
            if '<svg' in content:
                print('SVG content check: Valid SVG')
                return True
            else:
                print('SVG content check: Invalid SVG')
                return False
    except Exception as e:
        print(f'SVG content check: Error - {e}')
        return False

def verify_csv_files(files):
    """验证多个CSV文件"""
    results = []
    for f in files:
        exists = os.path.exists(f)
        size = os.path.getsize(f) if exists else 0
        print(f'{f}: exists={exists}, size={size} bytes')
        results.append(exists and size > 0)
    
    status = 'PASSED' if all(results) else 'FAILED'
    print(f'CSV export test: {status}')
    return all(results)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python verify_files.py <type> <file_or_files...>')
        print('Types: pdf, svg, csv')
        sys.exit(1)
    
    file_type = sys.argv[1]
    files = sys.argv[2:]
    
    if file_type == 'pdf':
        verify_file(files[0], 'PDF')
    elif file_type == 'svg':
        verify_file(files[0], 'SVG')
        verify_svg_content(files[0])
    elif file_type == 'csv':
        verify_csv_files(files)
    else:
        print(f'Unknown file type: {file_type}')
        sys.exit(1)