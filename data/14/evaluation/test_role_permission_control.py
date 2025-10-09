#!/usr/bin/env python3
"""
权限控制测试脚本
测试 [2.3.3a 权限控制 (角色)] 功能
"""

import subprocess
import os
import sys
from pathlib import Path

def test_role_permission_control():
    """测试权限控制功能"""
    print("🧪 开始测试权限控制功能...")
    
    # 测试步骤1: 检查--role选项是否存在
    print("\n📋 步骤1: 检查--role选项是否存在")
    cmd1 = ["python", "-m", "src.main", "--help"]
    
    try:
        result1 = subprocess.run(cmd1, capture_output=True, text=True, encoding='utf-8')
        
        if result1.returncode != 0:
            print(f"❌ 帮助命令执行失败，退出码: {result1.returncode}")
            return False
        
        # 检查是否包含--role选项说明
        if "--role" in result1.stdout and "用户角色" in result1.stdout:
            print("✅ --role选项存在且说明正确")
            print(f"   找到选项说明: {[line.strip() for line in result1.stdout.split('\\n') if '--role' in line][0]}")
        else:
            print("❌ --role选项不存在或说明不正确")
            return False
            
    except Exception as e:
        print(f"❌ 步骤1执行异常: {e}")
        return False
    
    # 测试步骤2: 普通用户权限测试（应该失败）
    print("\n📋 步骤2: 测试普通用户权限（应该被拒绝）")
    cmd2 = [
        "python", "-m", "src.main", "--role", "普通用户", 
        "analyze", "stats", 
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]
    
    try:
        result2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8')
        
        if result2.returncode == 1:
            print("✅ 普通用户权限正确被拒绝（退出码1）")
        else:
            print(f"❌ 普通用户权限检查失败，退出码: {result2.returncode}")
            return False
        
        # 检查错误信息
        expected_messages = [
            "权限错误：'普通用户'角色无权执行此操作",
            "此操作需要'分析员'或更高权限"
        ]
        
        for msg in expected_messages:
            if msg in result2.stdout:
                print(f"✅ 包含期望的错误信息: {msg}")
            else:
                print(f"❌ 缺少期望的错误信息: {msg}")
                print(f"实际输出: {result2.stdout}")
                return False
                
    except Exception as e:
        print(f"❌ 步骤2执行异常: {e}")
        return False
    
    # 测试步骤3: 分析员权限测试（应该成功）
    print("\n📋 步骤3: 测试分析员权限（应该成功）")
    cmd3 = [
        "python", "-m", "src.main", "--role", "分析员", 
        "analyze", "stats", 
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]
    
    try:
        result3 = subprocess.run(cmd3, capture_output=True, text=True, encoding='utf-8')
        
        if result3.returncode == 0:
            print("✅ 分析员权限正确通过（退出码0）")
        else:
            print(f"❌ 分析员权限检查失败，退出码: {result3.returncode}")
            print(f"错误输出: {result3.stderr}")
            return False
        
        # 检查成功信息
        expected_success_messages = [
            "成功读取数据文件: evaluation/sample_data.csv",
            "描述性统计分析完成，报告已保存至 evaluation/reports/descriptive"
        ]
        
        for msg in expected_success_messages:
            if msg in result3.stdout:
                print(f"✅ 包含期望的成功信息: {msg}")
            else:
                print(f"❌ 缺少期望的成功信息: {msg}")
                print(f"实际输出: {result3.stdout}")
                return False
                
    except Exception as e:
        print(f"❌ 步骤3执行异常: {e}")
        return False
    
    # 验证输出文件是否生成
    print("\n📋 验证输出文件")
    expected_files = [
        "evaluation/reports/descriptive/descriptive_stats.md",
        "evaluation/reports/descriptive/gender_distribution.png",
        "evaluation/reports/descriptive/venue_type_distribution.png"
    ]
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ 输出文件存在: {file_path}")
        else:
            print(f"⚠️  输出文件不存在: {file_path}")
    
    print("\n🎉 所有权限控制测试通过！")
    return True

def test_additional_roles():
    """测试其他角色"""
    print("\n🔍 测试其他角色...")
    
    # 测试管理员角色（应该成功）
    print("\n📋 测试管理员权限（应该成功）")
    cmd = [
        "python", "-m", "src.main", "--role", "管理员", 
        "analyze", "stats", 
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 管理员权限正确通过")
        else:
            print(f"❌ 管理员权限检查失败，退出码: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ 管理员权限测试异常: {e}")
        return False
    
    # 测试默认角色（应该成功）
    print("\n📋 测试默认角色（应该成功）")
    cmd_default = [
        "python", "-m", "src.main",
        "analyze", "stats", 
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]
    
    try:
        result_default = subprocess.run(cmd_default, capture_output=True, text=True, encoding='utf-8')
        
        if result_default.returncode == 0:
            print("✅ 默认角色（分析员）正确通过")
        else:
            print(f"❌ 默认角色检查失败，退出码: {result_default.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ 默认角色测试异常: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_role_permission_control()
    
    if success:
        additional_success = test_additional_roles()
        success = success and additional_success
    
    sys.exit(0 if success else 1)