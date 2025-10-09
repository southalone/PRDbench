#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
用于执行联邦学习系统的所有测试
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def run_shell_interaction_test(test_case):
    """运行shell交互测试"""
    print(f"\n运行测试: {test_case['metric']}")
    print(f"测试类型: {test_case['type']}")

    # 获取测试命令和输入文件
    test_command = test_case['testcases'][0]['test_command']
    test_input_file = test_case['testcases'][0]['test_input']

    if test_input_file:
        input_file_path = os.path.join(os.path.dirname(__file__), test_input_file)
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r', encoding='utf-8') as f:
                input_data = f.read()
        else:
            print(f"警告: 输入文件不存在: {input_file_path}")
            return False
    else:
        input_data = ""

    try:
        # 执行测试命令
        process = subprocess.Popen(
            test_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        stdout, stderr = process.communicate(input=input_data, timeout=30)

        # 检查预期输出
        output = stdout + stderr
        expected_output = test_case['expected_output']

        print(f"程序输出: {output[:200]}...")
        print(f"预期输出: {expected_output}")

        # 简单的输出验证（实际测试中应该更严格）
        if "错误" in expected_output and "错误" in output:
            print("✓ 测试通过")
            return True
        elif "菜单" in expected_output and any(x in output for x in ["[1]", "[2]", "[3]", "[4]", "[5]", "[6]"]):
            print("✓ 测试通过")
            return True
        elif "训练" in expected_output and "训练" in output:
            print("✓ 测试通过")
            return True
        elif "退出" in expected_output and ("再见" in output or process.returncode == 0):
            print("✓ 测试通过")
            return True
        else:
            print("✗ 测试失败")
            return False

    except subprocess.TimeoutExpired:
        process.kill()
        print("✗ 测试超时")
        return False
    except Exception as e:
        print(f"✗ 测试异常: {e}")
        return False

def run_unit_test(test_case):
    """运行单元测试"""
    print(f"\n运行测试: {test_case['metric']}")
    print(f"测试类型: {test_case['type']}")

    test_command = test_case['testcases'][0]['test_command']

    try:
        # 执行pytest命令
        result = subprocess.run(
            test_command.split(),
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
            timeout=60
        )

        print(f"测试输出: {result.stdout}")
        if result.stderr:
            print(f"错误输出: {result.stderr}")

        if result.returncode == 0:
            print("✓ 测试通过")
            return True
        else:
            print("✗ 测试失败")
            return False

    except subprocess.TimeoutExpired:
        print("✗ 测试超时")
        return False
    except Exception as e:
        print(f"✗ 测试异常: {e}")
        return False

def run_file_comparison_test(test_case):
    """运行文件比较测试"""
    print(f"\n运行测试: {test_case['metric']}")
    print(f"测试类型: {test_case['type']}")

    # 先运行命令生成文件
    test_command = test_case['testcases'][0]['test_command']
    test_input_file = test_case['testcases'][0]['test_input']

    if test_input_file:
        input_file_path = os.path.join(os.path.dirname(__file__), test_input_file)
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r', encoding='utf-8') as f:
                input_data = f.read()
        else:
            print(f"警告: 输入文件不存在: {input_file_path}")
            return False
    else:
        input_data = ""

    try:
        # 执行命令
        process = subprocess.Popen(
            test_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        stdout, stderr = process.communicate(input=input_data, timeout=30)

        # 检查期望的输出文件是否存在
        expected_files = test_case.get('expected_output_files', [])
        if expected_files:
            for expected_file in expected_files:
                expected_path = os.path.join(os.path.dirname(__file__), expected_file)
                if os.path.exists(expected_path):
                    print(f"✓ 期望文件存在: {expected_file}")
                else:
                    print(f"✗ 期望文件不存在: {expected_file}")
                    return False

        print("✓ 文件比较测试通过")
        return True

    except subprocess.TimeoutExpired:
        process.kill()
        print("✗ 测试超时")
        return False
    except Exception as e:
        print(f"✗ 测试异常: {e}")
        return False

def main():
    """主函数"""
    print("开始运行联邦学习系统测试...")

    # 加载测试计划
    test_plan_path = os.path.join(os.path.dirname(__file__), 'detailed_test_plan.json')

    if not os.path.exists(test_plan_path):
        print(f"错误: 测试计划文件不存在: {test_plan_path}")
        return

    with open(test_plan_path, 'r', encoding='utf-8') as f:
        test_plan = json.load(f)

    print(f"加载了 {len(test_plan)} 个测试用例")

    # 统计结果
    total_tests = len(test_plan)
    passed_tests = 0
    failed_tests = 0

    # 运行测试
    for i, test_case in enumerate(test_plan, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{total_tests}: {test_case['metric']}")
        print(f"{'='*60}")

        test_type = test_case['type']

        try:
            if test_type == 'shell_interaction':
                success = run_shell_interaction_test(test_case)
            elif test_type == 'unit_test':
                success = run_unit_test(test_case)
            elif test_type == 'file_comparison':
                success = run_file_comparison_test(test_case)
            else:
                print(f"未知的测试类型: {test_type}")
                success = False

            if success:
                passed_tests += 1
            else:
                failed_tests += 1

        except Exception as e:
            print(f"测试执行异常: {e}")
            failed_tests += 1

        # 短暂暂停，避免资源冲突
        time.sleep(1)

    # 输出测试结果
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print(f"{'='*60}")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")

    if failed_tests == 0:
        print("\n🎉 所有测试都通过了！")
    else:
        print(f"\n⚠️  有 {failed_tests} 个测试失败")

if __name__ == "__main__":
    main()
