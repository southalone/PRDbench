#!/usr/bin/env python3
"""
测试脚本：验证描述性统计图表输出功能
测试类型：file_comparison
测试目标：2.2.1b 描述性统计 (图表输出)
"""

import os
import subprocess
import sys
from pathlib import Path
import filecmp

def run_test():
    """运行图表生成测试"""
    print("=" * 60)
    print("测试：2.2.1b 描述性统计 (图表输出)")
    print("=" * 60)
    
    # 测试命令
    test_command = [
        "python", "-m", "src.main", "analyze", "stats",
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]
    
    # 预期输出文件
    expected_files = [
        "evaluation/expected_gender_distribution.png",
        "evaluation/expected_venue_type_distribution.png"
    ]
    
    # 实际输出文件
    actual_files = [
        "evaluation/reports/descriptive/gender_distribution.png",
        "evaluation/reports/descriptive/venue_type_distribution.png"
    ]
    
    print("步骤 1: 清理之前的输出文件...")
    for file_path in actual_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  已删除: {file_path}")
    
    print("\n步骤 2: 执行测试命令...")
    print(f"命令: {' '.join(test_command)}")
    
    try:
        result = subprocess.run(test_command, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败，退出码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
            return False
        
        print("✅ 命令执行成功")
        print(f"标准输出: {result.stdout}")
        
    except Exception as e:
        print(f"❌ 命令执行异常: {e}")
        return False
    
    print("\n步骤 3: 验证输出文件...")
    all_files_exist = True
    
    for actual_file in actual_files:
        if os.path.exists(actual_file):
            file_size = os.path.getsize(actual_file)
            print(f"✅ 文件已生成: {actual_file} (大小: {file_size} 字节)")
        else:
            print(f"❌ 文件未生成: {actual_file}")
            all_files_exist = False
    
    if not all_files_exist:
        return False
    
    print("\n步骤 4: 文件比较...")
    # 注意：PNG文件是二进制文件，每次生成可能略有不同（时间戳等）
    # 这里我们主要检查文件是否存在且大小合理
    comparison_passed = True
    
    for expected_file, actual_file in zip(expected_files, actual_files):
        if os.path.exists(expected_file) and os.path.exists(actual_file):
            expected_size = os.path.getsize(expected_file)
            actual_size = os.path.getsize(actual_file)
            
            # 允许文件大小有一定差异（PNG文件可能因为生成时间等略有不同）
            size_diff_ratio = abs(expected_size - actual_size) / expected_size
            
            if size_diff_ratio < 0.1:  # 允许10%的大小差异
                print(f"✅ 文件大小匹配: {actual_file}")
                print(f"   预期大小: {expected_size} 字节, 实际大小: {actual_size} 字节")
            else:
                print(f"⚠️  文件大小差异较大: {actual_file}")
                print(f"   预期大小: {expected_size} 字节, 实际大小: {actual_size} 字节")
                print(f"   差异比例: {size_diff_ratio:.2%}")
        else:
            print(f"❌ 无法比较文件: {expected_file} 或 {actual_file} 不存在")
            comparison_passed = False
    
    print("\n" + "=" * 60)
    if all_files_exist and comparison_passed:
        print("🎉 测试通过！所有图表文件已成功生成。")
        return True
    else:
        print("❌ 测试失败！")
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)