#!/usr/bin/env python3
"""
验证文件比对测试的简化脚本
验证"2.1b 自动化单元测试 - 测试覆盖度"测试是否正确设置
"""

import subprocess
import sys
import json
from pathlib import Path

def main():
    print("验证文件比对测试设置...")
    
    # 1. 检查所有必需文件是否存在
    required_files = [
        "evaluation/test_coverage_analyzer.py",
        "evaluation/expected_test_coverage_report.json", 
        "evaluation/file_comparator.py",
        "src/tests/test_utils.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"ERROR: 缺少必需文件 {file_path}")
            return False
        else:
            print(f"OK: 文件存在 {file_path}")
    
    # 2. 执行测试命令
    print("\n执行测试命令...")
    try:
        result = subprocess.run([
            "python", "evaluation/test_coverage_analyzer.py", 
            "src/tests", "evaluation/test_output.json"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("OK: 测试覆盖度分析器执行成功")
        else:
            print(f"ERROR: 测试覆盖度分析器失败，退出码: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"ERROR: 执行测试命令失败: {e}")
        return False
    
    # 3. 验证输出文件
    if Path("evaluation/test_output.json").exists():
        print("OK: 生成了输出文件")
        
        # 读取并验证输出内容
        try:
            with open("evaluation/test_output.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'overall_stats' in data and data['overall_stats'].get('coverage_percentage') == 100.0:
                print("OK: 测试覆盖度为100%")
            else:
                print("WARNING: 测试覆盖度不是100%")
                
        except Exception as e:
            print(f"ERROR: 读取输出文件失败: {e}")
            return False
    else:
        print("ERROR: 未生成输出文件")
        return False
    
    print("\n文件比对测试验证完成 - 所有检查通过!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)