#!/usr/bin/env python3
"""
测试执行脚本 - 运行所有测试用例
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """打印测试横幅"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧪 企业管理人才培训与技能分析系统 - 测试套件            ║
║                                                              ║
║        Enterprise Management Training & Skills Analysis       ║
║                    Test Suite Runner                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

def load_test_plan():
    """加载测试计划"""
    try:
        with open('evaluation/detailed_test_plan.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载测试计划失败: {e}")
        return []

def run_shell_interaction_test(test_case):
    """运行shell交互测试"""
    print(f"🔧 执行Shell交互测试...")
    
    for i, testcase in enumerate(test_case['testcases']):
        print(f"   步骤 {i+1}: {testcase['test_command']}")
        
        try:
            # 准备输入
            input_data = None
            if testcase['test_input']:
                input_file = testcase['test_input']
                if os.path.exists(input_file):
                    with open(input_file, 'r', encoding='utf-8') as f:
                        input_data = f.read()
            
            # 执行命令
            result = subprocess.run(
                testcase['test_command'],
                shell=True,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"   ✅ 命令执行成功")
                if result.stdout:
                    print(f"   输出: {result.stdout[:200]}...")
            else:
                print(f"   ❌ 命令执行失败 (退出码: {result.returncode})")
                if result.stderr:
                    print(f"   错误: {result.stderr[:200]}...")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ 命令执行超时")
            return False
        except Exception as e:
            print(f"   ❌ 执行异常: {e}")
            return False
    
    return True

def run_unit_test(test_case):
    """运行单元测试"""
    print(f"🧪 执行单元测试...")
    
    for testcase in test_case['testcases']:
        print(f"   命令: {testcase['test_command']}")
        
        try:
            result = subprocess.run(
                testcase['test_command'],
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"   ✅ 测试通过")
                if "PASSED" in result.stdout:
                    print(f"   详情: 测试用例执行成功")
            else:
                print(f"   ❌ 测试失败 (退出码: {result.returncode})")
                if result.stderr:
                    print(f"   错误: {result.stderr[:300]}...")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ 测试执行超时")
            return False
        except Exception as e:
            print(f"   ❌ 执行异常: {e}")
            return False
    
    return True

def run_file_comparison_test(test_case):
    """运行文件比较测试"""
    print(f"📄 执行文件比较测试...")
    
    for testcase in test_case['testcases']:
        print(f"   命令: {testcase['test_command']}")
        
        try:
            # 执行生成文件的命令
            result = subprocess.run(
                testcase['test_command'],
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"   ✅ 文件生成命令执行成功")
                
                # 检查期望输出文件是否存在
                if test_case['expected_output_files']:
                    for expected_file in test_case['expected_output_files']:
                        if os.path.exists(expected_file):
                            file_size = os.path.getsize(expected_file)
                            print(f"   ✅ 期望文件存在: {expected_file} ({file_size} bytes)")
                        else:
                            print(f"   ❌ 期望文件不存在: {expected_file}")
                            return False
                
            else:
                print(f"   ❌ 文件生成失败 (退出码: {result.returncode})")
                if result.stderr:
                    print(f"   错误: {result.stderr[:200]}...")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ 命令执行超时")
            return False
        except Exception as e:
            print(f"   ❌ 执行异常: {e}")
            return False
    
    return True

def run_single_test(test_case):
    """运行单个测试用例"""
    print(f"\n{'='*60}")
    print(f"测试: {test_case['metric']}")
    print(f"类型: {test_case['type']}")
    print('='*60)
    
    if test_case['type'] == 'shell_interaction':
        return run_shell_interaction_test(test_case)
    elif test_case['type'] == 'unit_test':
        return run_unit_test(test_case)
    elif test_case['type'] == 'file_comparison':
        return run_file_comparison_test(test_case)
    else:
        print(f"❌ 未知测试类型: {test_case['type']}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 加载测试计划
    test_plan = load_test_plan()
    if not test_plan:
        print("❌ 无法加载测试计划")
        return
    
    print(f"📋 加载了 {len(test_plan)} 个测试用例")
    
    # 统计信息
    passed_tests = 0
    failed_tests = 0
    
    # 执行所有测试
    for i, test_case in enumerate(test_plan, 1):
        print(f"\n🔍 执行测试 {i}/{len(test_plan)}")
        
        try:
            if run_single_test(test_case):
                passed_tests += 1
                print(f"✅ 测试通过")
            else:
                failed_tests += 1
                print(f"❌ 测试失败")
        except Exception as e:
            failed_tests += 1
            print(f"❌ 测试异常: {e}")
    
    # 输出测试结果统计
    print(f"\n{'='*60}")
    print(f"📊 测试结果统计")
    print('='*60)
    print(f"总测试数: {len(test_plan)}")
    print(f"通过: {passed_tests}")
    print(f"失败: {failed_tests}")
    print(f"成功率: {passed_tests/len(test_plan)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {failed_tests} 个测试失败，请检查相关功能")

if __name__ == "__main__":
    main()