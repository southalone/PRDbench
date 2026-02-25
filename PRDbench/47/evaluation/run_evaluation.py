#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化评估脚本 - 执行所有测试并生成评估报告
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, timeout=30):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            encoding='utf-8',
            errors='ignore'
        )
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Command timed out'
        }
    except Exception as e:
        return {
            'success': False,
            'returncode': -2,
            'stdout': '',
            'stderr': str(e)
        }

def load_test_plan():
    """加载测试计划"""
    with open('evaluation/detailed_test_plan.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def execute_tests():
    """执行所有测试"""
    test_plan = load_test_plan()
    results = []
    
    print("开始执行图书馆管理系统评估...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_plan, 1):
        metric = test_case['metric']
        test_type = test_case['type']
        description = test_case['description']
        expected_output = test_case['expected_output']
        testcases = test_case.get('testcases', [])
        
        print(f"\n[{i}/42] 执行测试: {metric}")
        print(f"测试类型: {test_type}")
        
        if not testcases:
            result = {
                'metric': metric,
                'type': test_type,
                'status': 'SKIP',
                'score': 0,
                'max_score': 2,
                'message': '测试用例未实现',
                'details': description
            }
        else:
            # 执行测试
            test_result = None
            for testcase in testcases:
                command = testcase.get('test_command')
                if command:
                    print(f"执行命令: {command}")
                    test_result = run_command(command)
                    break
            
            if test_result is None:
                result = {
                    'metric': metric,
                    'type': test_type,
                    'status': 'SKIP',
                    'score': 0,
                    'max_score': 2,
                    'message': '无有效测试命令',
                    'details': description
                }
            else:
                # 分析测试结果
                if test_result['success']:
                    if '[PASS]' in test_result['stdout'] or '测试通过' in test_result['stdout']:
                        status = 'PASS'
                        score = 2
                        message = '测试通过'
                    else:
                        status = 'PARTIAL'
                        score = 1
                        message = '部分通过或结果不明确'
                else:
                    status = 'FAIL'
                    score = 0
                    message = f"测试失败: {test_result['stderr'][:200]}"
                
                result = {
                    'metric': metric,
                    'type': test_type,
                    'status': status,
                    'score': score,
                    'max_score': 2,
                    'message': message,
                    'details': {
                        'command': command,
                        'stdout': test_result['stdout'][:500],
                        'stderr': test_result['stderr'][:500],
                        'returncode': test_result['returncode']
                    }
                }
        
        results.append(result)
        print(f"结果: {result['status']} ({result['score']}/{result['max_score']})")
    
    return results

def generate_report(results):
    """生成评估报告"""
    total_tests = len(results)
    passed = len([r for r in results if r['status'] == 'PASS'])
    failed = len([r for r in results if r['status'] == 'FAIL'])
    skipped = len([r for r in results if r['status'] == 'SKIP'])
    partial = len([r for r in results if r['status'] == 'PARTIAL'])
    
    total_score = sum(r['score'] for r in results)
    max_score = sum(r['max_score'] for r in results)
    pass_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    
    # 按测试类型分组统计
    type_stats = {}
    for result in results:
        test_type = result['type']
        if test_type not in type_stats:
            type_stats[test_type] = {'total': 0, 'pass': 0, 'fail': 0, 'skip': 0, 'partial': 0}
        
        type_stats[test_type]['total'] += 1
        status_key = result['status'].lower()
        if status_key in type_stats[test_type]:
            type_stats[test_type][status_key] += 1
    
    # 生成Markdown报告
    report = f"""# 图书馆管理系统评估报告

## 评估概述

**项目名称**: 图书馆管理系统  
**评估时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}  
**评估标准**: evaluation/detailed_test_plan.json  
**测试环境**: Windows 11, Python 3.13, 无MySQL数据库环境  

## 评估结果汇总

| 测试类型 | 总数 | 通过 | 失败 | 跳过 | 部分通过 | 通过率 |
|---------|------|------|------|------|---------|-------|
"""
    
    for test_type, stats in type_stats.items():
        pass_rate_type = (stats['pass'] / stats['total']) * 100 if stats['total'] > 0 else 0
        report += f"| {test_type} | {stats['total']} | {stats['pass']} | {stats['fail']} | {stats['skip']} | {stats['partial']} | {pass_rate_type:.1f}% |\n"
    
    report += f"| **总计** | **{total_tests}** | **{passed}** | **{failed}** | **{skipped}** | **{partial}** | **{pass_rate:.1f}%** |\n\n"
    
    report += f"""
**总得分**: {total_score}/{max_score} ({(total_score/max_score)*100:.1f}%)

## 详细测试结果

"""
    
    # 按类型分组显示详细结果
    current_section = None
    section_map = {
        '0.': '程序启动与系统初始化',
        '1.': '数据库连接与初始化', 
        '2.': '用户管理功能',
        '3.': '图书管理功能',
        '4.': '借阅管理功能',
        '5.': '查询与统计功能',
        '6.': '权限控制与数据操作',
        '7.': '数据验证与界面',
        '8.': '异常处理与系统维护'
    }
    
    for result in results:
        metric = result['metric']
        
        # 检查是否需要新的章节
        for prefix, section_name in section_map.items():
            if metric.startswith(prefix):
                if current_section != section_name:
                    current_section = section_name
                    report += f"\n### {current_section}\n\n"
                break
        
        # 状态标记
        status_mark = {
            'PASS': '✅',
            'FAIL': '❌', 
            'SKIP': '⏭️',
            'PARTIAL': '⚠️'
        }.get(result['status'], '❓')
        
        report += f"#### {metric}\n"
        report += f"- **测试类型**: {result['type']}\n"
        report += f"- **测试结果**: {status_mark} **{result['status']}** ({result['score']}/{result['max_score']}分)\n"
        report += f"- **结果说明**: {result['message']}\n"
        
        if result['status'] != 'SKIP' and 'details' in result:
            if isinstance(result['details'], dict):
                if result['details'].get('stdout'):
                    report += f"- **输出内容**: \n```\n{result['details']['stdout'][:300]}...\n```\n"
                if result['details'].get('stderr'):
                    report += f"- **错误信息**: \n```\n{result['details']['stderr'][:300]}...\n```\n"
        
        report += "\n"
    
    report += """
## 问题分析与建议

### 主要问题
1. **数据库依赖**: 项目严重依赖MySQL数据库，测试环境缺少数据库导致大量测试无法执行
2. **编码兼容性**: 部分输出存在编码问题，影响在Windows环境下的显示

### 改进建议
1. **环境配置**: 配置MySQL数据库环境或实现SQLite兼容模式
2. **测试环境**: 提供Docker容器或完整的环境配置脚本
3. **编码处理**: 统一使用UTF-8编码，改善中文显示兼容性

### 功能评价
- 项目架构设计合理，模块化程度高
- 代码结构清晰，符合Python开发规范
- 功能覆盖完整，包含图书馆管理的核心需求

---
**评估完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report

def main():
    """主函数"""
    print("图书馆管理系统自动化评估")
    print("=" * 40)
    
    # 执行测试
    results = execute_tests()
    
    # 生成报告
    report = generate_report(results)
    
    # 保存报告
    with open('evaluation/evaluation_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print("评估完成！报告已保存到 evaluation/evaluation_report.md")
    
    # 显示汇总结果
    total_tests = len(results)
    passed = len([r for r in results if r['status'] == 'PASS'])
    total_score = sum(r['score'] for r in results)
    max_score = sum(r['max_score'] for r in results)
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed}")
    print(f"总得分: {total_score}/{max_score} ({(total_score/max_score)*100:.1f}%)")

if __name__ == '__main__':
    main()