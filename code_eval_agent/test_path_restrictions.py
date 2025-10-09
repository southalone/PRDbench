#!/usr/bin/env python3
"""
测试路径限制功能
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ALLOWED_PATHS, ENABLE_PATH_RESTRICTION
from mcp_tools import validate_file_path

def test_path_restrictions():
    """测试路径限制功能"""
    print("🧪 测试路径限制功能")
    print(f"📁 允许的路径: {ALLOWED_PATHS}")
    print(f"🔒 路径限制启用: {ENABLE_PATH_RESTRICTION}")
    print("-" * 50)
    
    # 测试用例
    test_cases = [
        # (文件路径, 预期结果, 描述)
        ("/tmp/test.txt", True, "tmp目录下的文件"),
        ("/tmp/subdir/test.txt", True, "tmp子目录下的文件"),
        ("test.txt", True, "相对路径文件"),
        ("./test.txt", True, "当前目录相对路径"),
        ("../test.txt", True, "上级目录相对路径"),
    ]
    
    # 添加工作空间目录的测试用例
    if ALLOWED_PATHS:
        workspace_path = ALLOWED_PATHS[0]
        test_cases.extend([
            (f"{workspace_path}/test.txt", True, "工作空间目录下的文件"),
            (f"{workspace_path}/subdir/test.txt", True, "工作空间子目录下的文件"),
        ])
    
    # 添加不允许的路径测试用例
    test_cases.extend([
        ("/home/test.txt", False, "home目录下的文件（通常不允许）"),
        ("/etc/test.txt", False, "etc目录下的文件（通常不允许）"),
        ("/root/test.txt", False, "root目录下的文件（通常不允许）"),
    ])
    
    # 运行测试
    passed = 0
    failed = 0
    
    for file_path, expected, description in test_cases:
        try:
            result = validate_file_path(file_path)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            print(f"{status} {description}: {file_path} -> {result} (预期: {expected})")
            
            if result == expected:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ ERROR {description}: {file_path} -> 异常: {e}")
            failed += 1
    
    print("-" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  有测试失败，请检查配置")
    
    return failed == 0

def test_environment_variables():
    """测试环境变量配置"""
    print("\n🔧 测试环境变量配置")
    print("-" * 30)
    
    # 显示当前环境变量
    allowed_paths_env = os.getenv('ALLOWED_PATHS', '')
    enable_restriction_env = os.getenv('ENABLE_PATH_RESTRICTION', '')
    
    print(f"ALLOWED_PATHS: {allowed_paths_env or '(未设置)'}")
    print(f"ENABLE_PATH_RESTRICTION: {enable_restriction_env or '(未设置)'}")
    print(f"当前配置的允许路径: {ALLOWED_PATHS}")
    print(f"当前路径限制状态: {ENABLE_PATH_RESTRICTION}")

def create_test_files():
    """创建测试文件"""
    print("\n📝 创建测试文件")
    print("-" * 30)
    
    # 在允许的路径中创建测试文件
    for allowed_path in ALLOWED_PATHS:
        test_file = Path(allowed_path) / "test_path_restriction.txt"
        try:
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("这是一个测试文件，用于验证路径限制功能。")
            print(f"✅ 创建测试文件: {test_file}")
        except Exception as e:
            print(f"❌ 创建测试文件失败: {test_file} - {e}")

def cleanup_test_files():
    """清理测试文件"""
    print("\n🧹 清理测试文件")
    print("-" * 30)
    
    for allowed_path in ALLOWED_PATHS:
        test_file = Path(allowed_path) / "test_path_restriction.txt"
        try:
            if test_file.exists():
                test_file.unlink()
                print(f"✅ 删除测试文件: {test_file}")
        except Exception as e:
            print(f"❌ 删除测试文件失败: {test_file} - {e}")

if __name__ == "__main__":
    print("🚀 开始测试路径限制功能")
    print("=" * 60)
    
    # 测试环境变量配置
    test_environment_variables()
    
    # 创建测试文件
    create_test_files()
    
    # 运行路径限制测试
    success = test_path_restrictions()
    
    # 清理测试文件
    cleanup_test_files()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 路径限制功能测试完成，所有测试通过！")
    else:
        print("⚠️  路径限制功能测试完成，但有测试失败！")
    
    sys.exit(0 if success else 1)











