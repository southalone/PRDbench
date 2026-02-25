#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean pytest runner - completely reset Python environment before running pytest
"""
import sys
import os
import subprocess

def run_pytest_clean(test_file, test_method=None):
    """Run pytest in a completely clean subprocess"""
    print(f"=== 在干净环境中运行pytest测试 ===")
    print(f"测试文件: {test_file}")
    
    # 构建pytest命令
    if test_method:
        cmd = [sys.executable, "-m", "pytest", f"{test_file}::{test_method}", "-v"]
    else:
        cmd = [sys.executable, "-m", "pytest", test_file, "-v"]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 在子进程中运行pytest，完全隔离环境
        result = subprocess.run(
            cmd,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60
        )
        
        print("=== STDOUT ===")
        print(result.stdout)
        print("=== STDERR ===")
        print(result.stderr)
        print(f"=== 退出代码: {result.returncode} ===")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("测试超时")
        return False
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False

if __name__ == "__main__":
    # 测试缺失值检测
    success = run_pytest_clean(
        "tests/test_missing_values_detection.py"
    )
    
    if success:
        print("\n✅ pytest测试成功!")
    else:
        print("\n❌ pytest测试失败")