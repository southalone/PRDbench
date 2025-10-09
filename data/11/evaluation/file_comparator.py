#!/usr/bin/env python3
"""
文件比较器
用于比较两个JSON文件的内容是否一致
"""

import json
import sys
from pathlib import Path

def compare_json_files(file1_path, file2_path):
    """比较两个JSON文件的内容"""
    try:
        # 读取文件1
        with open(file1_path, 'r', encoding='utf-8') as f1:
            data1 = json.load(f1)
        
        # 读取文件2
        with open(file2_path, 'r', encoding='utf-8') as f2:
            data2 = json.load(f2)
        
        # 忽略时间戳的比较
        if 'timestamp' in data1:
            del data1['timestamp']
        if 'timestamp' in data2:
            del data2['timestamp']
        
        # 比较内容
        files_match = data1 == data2
        
        return {
            'files_match': files_match,
            'file1': str(file1_path),
            'file2': str(file2_path),
            'details': {
                'file1_keys': list(data1.keys()) if isinstance(data1, dict) else 'not_dict',
                'file2_keys': list(data2.keys()) if isinstance(data2, dict) else 'not_dict'
            }
        }
        
    except FileNotFoundError as e:
        return {
            'files_match': False,
            'error': f'文件未找到: {e}',
            'file1': str(file1_path),
            'file2': str(file2_path)
        }
    except json.JSONDecodeError as e:
        return {
            'files_match': False,
            'error': f'JSON解析错误: {e}',
            'file1': str(file1_path),
            'file2': str(file2_path)
        }
    except Exception as e:
        return {
            'files_match': False,
            'error': f'比较错误: {e}',
            'file1': str(file1_path),
            'file2': str(file2_path)
        }

def main():
    if len(sys.argv) != 3:
        print("Usage: python file_comparator.py <file1> <file2>")
        sys.exit(1)
    
    file1_path = Path(sys.argv[1])
    file2_path = Path(sys.argv[2])
    
    result = compare_json_files(file1_path, file2_path)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 返回适当的退出码
    sys.exit(0 if result['files_match'] else 1)

if __name__ == '__main__':
    main()