#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复测试计划中test_command和test_input重复的问题
当test_command中已经包含输入序列时，应该清空test_input
"""

import json
import re

def load_test_plan():
    """加载测试计划"""
    with open('detailed_test_plan.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_test_plan(tests):
    """保存测试计划"""
    with open('detailed_test_plan.json', 'w', encoding='utf-8') as f:
        json.dump(tests, f, ensure_ascii=False, indent=4)

def extract_input_from_command(command):
    """从命令中提取输入序列"""
    # 匹配 echo -e "输入序列"
    match = re.search(r'echo -e "([^"]+)"', command)
    if match:
        return match.group(1)
    return None

def fix_duplicate_inputs():
    """修复重复输入问题"""
    tests = load_test_plan()
    
    file_comparison_tests = []
    fixed_count = 0
    
    for test in tests:
        if test.get('type') == 'file_comparison':
            file_comparison_tests.append(test)
    
    print(f"找到 {len(file_comparison_tests)} 个file_comparison测试")
    print("\n检查重复输入问题：")
    print("="*80)
    
    for i, test in enumerate(file_comparison_tests, 1):
        metric = test['metric']
        testcase = test['testcases'][0]
        test_command = testcase.get('test_command', '')
        test_input = testcase.get('test_input', '')
        
        print(f"\n{i}. {metric}")
        print(f"   命令: {test_command}")
        print(f"   输入: {test_input}")
        
        # 从命令中提取输入序列
        command_input = extract_input_from_command(test_command)
        
        if command_input and test_input:
            # 检查是否重复
            if command_input == test_input:
                print(f"   [发现重复] 命令中的输入和test_input相同")
                print(f"   [修复] 清空test_input")
                
                # 修复：清空test_input
                for test_item in tests:
                    if test_item.get('metric') == metric:
                        test_item['testcases'][0]['test_input'] = None
                        fixed_count += 1
                        break
            elif command_input:
                print(f"   [检查] 命令输入: {command_input}")
                print(f"   [检查] test_input: {test_input}")
                print(f"   [状态] 输入不同，需要手动检查")
        elif command_input and not test_input:
            print(f"   [正常] 只有命令中有输入")
        elif not command_input and test_input:
            print(f"   [正常] 只有test_input有输入")
        else:
            print(f"   [正常] 都没有输入")
    
    print(f"\n{'='*80}")
    print(f"修复完成！共修复了 {fixed_count} 个重复输入问题")
    
    if fixed_count > 0:
        save_test_plan(tests)
        print("已保存修复后的测试计划")
    
    return fixed_count

def verify_fixes():
    """验证修复结果"""
    tests = load_test_plan()
    
    print(f"\n{'='*80}")
    print("验证修复结果：")
    print('='*80)
    
    file_comparison_tests = [test for test in tests if test.get('type') == 'file_comparison']
    
    for i, test in enumerate(file_comparison_tests, 1):
        metric = test['metric']
        testcase = test['testcases'][0]
        test_command = testcase.get('test_command', '')
        test_input = testcase.get('test_input')
        
        command_input = extract_input_from_command(test_command)
        
        print(f"\n{i}. {metric}")
        
        if command_input and test_input:
            if command_input == test_input:
                print(f"   [警告] 仍然存在重复输入！")
            else:
                print(f"   [正常] 输入不重复")
        elif command_input and not test_input:
            print(f"   [正常] 只有命令输入")
        elif not command_input and test_input:
            print(f"   [正常] 只有test_input")
        else:
            print(f"   [正常] 无输入")

def main():
    """主函数"""
    print("File Comparison 测试用例重复输入修复工具")
    print("="*80)
    
    # 修复重复输入
    fixed_count = fix_duplicate_inputs()
    
    # 验证修复结果
    verify_fixes()
    
    print(f"\n{'='*80}")
    print("修复总结:")
    print(f"- 共修复 {fixed_count} 个重复输入问题")
    print("- 所有file_comparison测试用例已检查完毕")
    
    return fixed_count > 0

if __name__ == "__main__":
    main()