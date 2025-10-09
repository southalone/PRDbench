#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isolated pytest runner to solve buffer detached issue
"""
import os
import sys
import subprocess
import tempfile


def run_isolated_pytest(test_file, test_method=None):
    """Run pytest in completely isolated process"""
    print(f"=== 在完全隔离的环境中运行pytest ===")
    print(f"测试文件: {test_file}")
    
    # 创建一个启动脚本
    script_content = f'''
import sys
import os
sys.path.insert(0, '{os.path.abspath("../src")}')

# 完全重置stdout/stderr
import io
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

# 设置环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUNBUFFERED"] = "1"

# 运行pytest
import pytest
'''
    
    if test_method:
        script_content += f'''
pytest.main(["{test_file}::{test_method}", "-v", "-s", "--tb=short"])
'''
    else:
        script_content += f'''
pytest.main(["{test_file}", "-v", "-s", "--tb=short"])
'''
    
    # 写入临时脚本
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        script_path = f.name
    
    try:
        # 在新的Python进程中运行
        result = subprocess.run([
            sys.executable, script_path
        ], 
        cwd=os.getcwd(),
        capture_output=True, 
        text=True,
        encoding='utf-8',
        timeout=120
        )
        
        print("=== 输出结果 ===")
        print(result.stdout)
        if result.stderr:
            print("=== 错误输出 ===") 
            print(result.stderr)
        print(f"=== 退出代码: {result.returncode} ===")
        
        return result.returncode == 0
        
    finally:
        # 清理临时文件
        if os.path.exists(script_path):
            os.unlink(script_path)


if __name__ == "__main__":
    # 测试缺失值检测
    success = run_isolated_pytest(
        "tests/test_missing_values_detection.py",
        "TestMissingValuesDetection::test_missing_values_detection"
    )
    
    if success:
        print("\n✅ 隔离pytest测试成功!")
    else:
        print("\n❌ 隔离pytest测试仍然失败")