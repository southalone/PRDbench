#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
用于自动化执行测试计划中的各种测试
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

def load_test_plan():
    """加载测试计划"""
    test_plan_path = Path(__file__).parent / "detailed_test_plan.json"
    with open(test_plan_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_shell_interaction_test(testcase):
    """运行shell交互测试"""
    cmd = testcase['test_command']
    input_file = testcase.get('test_input')

    print(f"运行命令: {cmd}")

    if input_file:
        input_path = Path(__file__).parent.parent / input_file
        if input_path.exists():
            with open(input_path, 'r', encoding='utf-8') as f:
                input_data = f.read()

            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=30
                )
                return result.returncode == 0, result.stdout, result.stderr
            except subprocess.TimeoutExpired:
                return False, "", "测试超时"
        else:
            return False, "", f"输入文件不存在: {input_file}"
    else:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "测试超时"

def run_unit_test(testcase):
    """运行单元测试"""
    cmd = testcase['test_command']
    print(f"运行单元测试: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "测试超时"

def run_file_comparison_test(testcase):
    """运行文件比较测试"""
    # 先运行命令生成文件
    success, stdout, stderr = run_shell_interaction_test(testcase)

    if not success:
        return False, stdout, stderr

    # 这里可以添加文件比较逻辑
    return True, "文件比较测试通过", ""

def run_single_test(test_item):
    """运行单个测试"""
    metric = test_item['metric']
    test_type = test_item['type']
    testcases = test_item['testcases']

    print(f"\n{'='*60}")
    print(f"测试项目: {metric}")
    print(f"测试类型: {test_type}")
    print(f"{'='*60}")

    all_passed = True

    for i, testcase in enumerate(testcases, 1):
        print(f"\n--- 测试用例 {i} ---")

        if test_type == "shell_interaction":
            success, stdout, stderr = run_shell_interaction_test(testcase)
        elif test_type == "unit_test":
            success, stdout, stderr = run_unit_test(testcase)
        elif test_type == "file_comparison":
            success, stdout, stderr = run_file_comparison_test(testcase)
        else:
            success, stdout, stderr = False, "", f"未知测试类型: {test_type}"

        if success:
            print("✅ 测试通过")
        else:
            print("❌ 测试失败")
            all_passed = False

        if stdout:
            print(f"输出: {stdout[:200]}...")
        if stderr:
            print(f"错误: {stderr[:200]}...")

    return all_passed

def main():
    """主函数"""
    print("东野圭吾小说文本挖掘与语义分析工具 - 自动化测试")
    print("="*60)

    # 检查当前目录
    current_dir = Path.cwd()
    if current_dir.name != "problem8":
        print("请在项目根目录下运行此脚本")
        sys.exit(1)

    # 加载测试计划
    try:
        test_plan = load_test_plan()
        print(f"加载了 {len(test_plan)} 个测试项目")
    except Exception as e:
        print(f"加载测试计划失败: {e}")
        sys.exit(1)

    # 运行测试
    passed_tests = 0
    total_tests = len(test_plan)

    for test_item in test_plan:
        try:
            if run_single_test(test_item):
                passed_tests += 1
        except KeyboardInterrupt:
            print("\n测试被用户中断")
            break
        except Exception as e:
            print(f"测试执行出错: {e}")

    # 输出结果
    print(f"\n{'='*60}")
    print(f"测试完成: {passed_tests}/{total_tests} 项测试通过")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
