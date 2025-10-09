#!/usr/bin/env python3
"""
测试虚拟环境功能
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 修复导入问题
import config
from mcp_tools import create_workspace, activate_venv, execute_python_code, list_workspace

def test_venv_functionality():
    """测试虚拟环境功能"""
    print("🧪 开始测试虚拟环境功能...")
    
    # 1. 创建工作空间（包含虚拟环境）
    print("\n1. 创建工作空间...")
    result = create_workspace(None, "test_venv_workspace", create_venv=True)
    print(f"工作空间创建结果: {result}")
    
    # 2. 激活虚拟环境
    print("\n2. 激活虚拟环境...")
    venv_result = activate_venv(None, "test_venv_workspace")
    print(f"虚拟环境激活结果: {venv_result}")
    
    # 3. 在虚拟环境中执行代码
    print("\n3. 在虚拟环境中执行代码...")
    code = """
import sys
import os
print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")
print(f"当前工作目录: {os.getcwd()}")
print(f"已安装的包:")
os.system("pip list")
"""
    
    exec_result = execute_python_code(None, code, use_venv=True)
    print(f"代码执行结果: {exec_result}")
    
    # 4. 列出工作空间内容
    print("\n4. 列出工作空间内容...")
    list_result = list_workspace(None, "test_venv_workspace")
    print(f"工作空间内容: {list_result}")
    
    print("\n✅ 虚拟环境功能测试完成！")

if __name__ == "__main__":
    test_venv_functionality() 