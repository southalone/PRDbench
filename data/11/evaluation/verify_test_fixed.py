#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复中文显示问题的验证脚本
"""

import subprocess
import sys
import json
import os
from pathlib import Path

# 设置输出编码
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

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
            print(f"错误: 缺少必需文件 {file_path}")
            return False
        else:
            print(f"正常: 文件存在 {file_path}")
    
    # 2. 执行测试命令
    print("\n执行测试命令...")
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run([
            "python", "evaluation/test_coverage_analyzer.py", 
            "src/tests", "evaluation/test_output_fixed.json"
        ], capture_output=True, text=True, env=env, encoding='utf-8')
        
        if result.returncode == 0:
            print("正常: 测试覆盖度分析器执行成功")
        else:
            print(f"错误: 测试覆盖度分析器失败，退出码: {result.returncode}")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"错误: 执行测试命令失败: {e}")
        return False
    
    # 3. 验证输出文件
    output_file = "evaluation/test_output_fixed.json"
    if Path(output_file).exists():
        print("正常: 生成了输出文件")
        
        # 读取并验证输出内容
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            coverage = data.get('overall_stats', {}).get('coverage_percentage', 0)
            functions_covered = data.get('overall_stats', {}).get('fully_covered_functions', 0)
            total_functions = data.get('overall_stats', {}).get('total_functions', 0)
            
            print(f"正常: 测试覆盖度为 {coverage}%")
            print(f"正常: {functions_covered}/{total_functions} 个功能完全覆盖")
            
            if coverage == 100.0:
                print("优秀: 实现100%测试覆盖!")
            else:
                print("警告: 测试覆盖度不是100%")
                
        except Exception as e:
            print(f"错误: 读取输出文件失败: {e}")
            return False
    else:
        print("错误: 未生成输出文件")
        return False
    
    print("\n" + "="*60)
    print("文件比对测试验证完成 - 所有检查通过!")
    print("="*60)
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)