#!/usr/bin/env python3
"""
Simple test runner for data anonymization functionality.
This script can be used to quickly test the anonymization feature.
"""

import os
import sys
import subprocess

def main():
    """Run the anonymization test"""
    print("=" * 50)
    print("数据脱敏功能测试")
    print("=" * 50)
    
    # Change to the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    try:
        # Step 1: Setup test data
        print("1. 设置测试数据...")
        result = subprocess.run([sys.executable, "evaluation/setup_test_data.py"], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            print(f"设置测试数据失败: {result.stderr}")
            return False
        print("   ✓ 测试数据设置成功")
        
        # Step 2: Run anonymization export
        print("2. 执行数据脱敏导出...")
        result = subprocess.run([sys.executable, "-m", "src.main", "data", "export", 
                               "--anonymize", "--output-path", "evaluation/anonymized_data.csv"],
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            print(f"数据导出失败: {result.stderr}")
            return False
        print("   ✓ 数据导出成功")
        print(f"   输出: {result.stdout.strip()}")
        
        # Step 3: Verify the output
        print("3. 验证脱敏结果...")
        output_file = "evaluation/anonymized_data.csv"
        if not os.path.exists(output_file):
            print("   ✗ 输出文件不存在")
            return False
        
        # Read and display the anonymized data
        with open(output_file, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        print("   ✓ 脱敏结果:")
        for i, line in enumerate(lines[:6]):  # Show first 6 lines
            print(f"     {line.strip()}")
        if len(lines) > 6:
            print(f"     ... (共 {len(lines)} 行)")
        
        # Check if anonymization worked
        content = ''.join(lines)
        if '张*' in content and '138****5678' in content:
            print("   ✓ 数据脱敏验证成功！")
            return True
        else:
            print("   ✗ 数据脱敏验证失败！")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print("=" * 50)
    if success:
        print("测试结果: 通过 ✓")
    else:
        print("测试结果: 失败 ✗")
    print("=" * 50)
    sys.exit(0 if success else 1)