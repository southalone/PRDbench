# -*- coding: utf-8 -*-
"""
批量测试expected_output_files测试用例
快速验证和生成missing的expected文件
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def load_test_plan():
    """加载测试计划"""
    with open('evaluation/detailed_test_plan.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_expected_output_files_tests():
    """获取所有有expected_output_files的测试用例"""
    test_plan = load_test_plan()
    expected_tests = []
    
    for test in test_plan:
        if test.get('expected_output_files') and test['expected_output_files']:
            expected_tests.append({
                'metric': test['metric'],
                'type': test['type'],
                'testcases': test['testcases'],
                'expected_files': test['expected_output_files']
            })
    
    return expected_tests

def run_test_command(test_command):
    """运行测试命令"""
    try:
        print(f"执行: {test_command}")
        result = subprocess.run(test_command, shell=True, capture_output=True, text=True, 
                              cwd='c:/Work/CodeAgent/DZY_19', timeout=120)
        
        if result.returncode == 0:
            print("[OK] 测试命令执行成功")
            return True, result.stdout
        else:
            print(f"[FAIL] 测试命令执行失败: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print("[TIMEOUT] 测试命令执行超时")
        return False, "Timeout"
    except Exception as e:
        print(f"[ERROR] 执行异常: {str(e)}")
        return False, str(e)

def check_expected_file_exists(expected_file):
    """检查expected文件是否存在且为今天生成"""
    if not os.path.exists(expected_file):
        return False, "文件不存在"
    
    # 检查文件修改时间
    mtime = os.path.getmtime(expected_file)
    file_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    if file_date == today:
        return True, f"文件存在且为今天生成 ({file_date})"
    else:
        return False, f"文件存在但为旧文件 ({file_date})"

def batch_test_expected_files():
    """批量测试expected_output_files测试用例"""
    print("=" * 80)
    print("批量测试expected_output_files测试用例")
    print("=" * 80)
    
    expected_tests = get_expected_output_files_tests()
    
    print(f"共发现 {len(expected_tests)} 个expected_output_files测试用例")
    print()
    
    results = []
    
    for i, test in enumerate(expected_tests, 1):
        print(f"[{i}/{len(expected_tests)}] 测试: {test['metric']}")
        print("-" * 60)
        
        # 检查expected文件状态
        expected_file = test['expected_files'][0]
        file_exists, file_status = check_expected_file_exists(expected_file)
        print(f"Expected文件状态: {file_status}")
        
        if file_exists:
            print("[SKIP] Expected文件已存在且为今天生成，跳过")
            results.append({'metric': test['metric'], 'status': 'SKIP', 'reason': '文件已存在'})
        else:
            # 执行测试命令
            if test['testcases']:
                test_command = test['testcases'][0]['test_command']
                
                # 删除旧的expected文件
                if os.path.exists(expected_file):
                    os.remove(expected_file)
                    print(f"已删除旧expected文件: {expected_file}")
                
                # 运行测试
                success, output = run_test_command(test_command)
                
                # 检查是否生成了新的expected文件
                if os.path.exists(expected_file):
                    print(f"[SUCCESS] 成功生成expected文件: {expected_file}")
                    results.append({'metric': test['metric'], 'status': 'SUCCESS', 'reason': '自动生成成功'})
                else:
                    print(f"[FAIL] 未能生成expected文件: {expected_file}")
                    results.append({'metric': test['metric'], 'status': 'FAILED', 'reason': '未能自动生成'})
            else:
                print("[FAIL] 无测试命令")
                results.append({'metric': test['metric'], 'status': 'FAILED', 'reason': '无测试命令'})
        
        print()
    
    # 打印汇总结果
    print("=" * 80)
    print("批量测试结果汇总")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r['status'] in ['SUCCESS', 'SKIP'])
    total_count = len(results)
    
    print(f"总测试用例: {total_count}")
    print(f"成功/跳过: {success_count}")
    print(f"失败: {total_count - success_count}")
    print(f"成功率: {success_count/total_count:.1%}")
    print()
    
    for result in results:
        status_icon = "[OK]" if result['status'] in ['SUCCESS', 'SKIP'] else "[FAIL]"
        print(f"{status_icon} {result['metric']}: {result['status']} - {result['reason']}")

if __name__ == "__main__":
    batch_test_expected_files()