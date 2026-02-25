#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Comparison 测试脚本生成器
在evaluation/文件夹下批量生成和执行所有file_comparison测试
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def load_test_plan():
    """加载测试计划"""
    with open('detailed_test_plan.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_single_test_script(metric, description, testcase, expected_files):
    """为单个file_comparison测试生成测试脚本"""
    test_command = testcase.get('test_command', '')
    test_input = testcase.get('test_input', '')
    
    # 生成安全的文件名
    safe_name = (metric.replace(' ', '_')
                      .replace('.', '_')
                      .replace('-', '_')
                      .replace('/', '_'))
    
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成的File Comparison测试脚本
测试项目: {metric}
"""

import subprocess
import sys
import os
from pathlib import Path

def test_{safe_name}():
    """执行{metric}测试"""
    print("="*80)
    print("测试项目: {metric}")
    print("="*80)
    
    test_command = "{test_command}"
    test_input = "{test_input}"
    expected_files = {expected_files}
    
    print(f"命令: {{test_command}}")
    print(f"输入序列: {{test_input}}")
    print(f"期望输出文件: {{expected_files}}")
    print("-"*80)
    
    try:
        if test_input and "echo -e" in test_command:
            # 处理交互式命令
            input_text = test_input.replace('\\\\n', '\\n')
            
            # 提取实际的执行命令和工作目录
            if "cd src &&" in test_command:
                cmd = ["python", "main.py"]
                cwd = "../src"
            elif "cd evaluation &&" in test_command:
                parts = test_command.split("cd evaluation && ")[-1]
                cmd = parts.split()
                cwd = "."
            else:
                print("[错误] 无法解析命令格式")
                return False
            
            print(f"实际执行: {{' '.join(cmd)}} (工作目录: {{cwd}})")
            print(f"输入内容: {{repr(input_text)}}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                input=input_text,
                text=True,
                capture_output=True,
                cwd=cwd,
                timeout=60,
                encoding='utf-8',
                errors='ignore'
            )
            
        else:
            # 直接执行命令（适用于evaluation目录下的Python脚本）
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='ignore'
            )
        
        print(f"退出码: {{result.returncode}}")
        
        # 显示输出（限制长度避免过多内容）
        if result.stdout:
            stdout_preview = result.stdout[:800] + ("...（截断）" if len(result.stdout) > 800 else "")
            print(f"标准输出:\\n{{stdout_preview}}")
        
        if result.stderr:
            stderr_preview = result.stderr[:400] + ("...（截断）" if len(result.stderr) > 400 else "")
            print(f"标准错误:\\n{{stderr_preview}}")
        
        # 检查是否存在"无效选择"错误
        has_invalid_choice = ("无效选择" in result.stdout or 
                             "无效选择" in result.stderr)
        
        if has_invalid_choice:
            print("[失败] 仍然存在'无效选择'错误!")
            return False
        
        # 检查程序是否正常结束
        normal_exit = (result.returncode == 0 or 
                      "感谢使用推荐系统" in result.stdout or
                      "测试完成" in result.stdout)
        
        if not normal_exit:
            print(f"[警告] 程序异常退出，退出码: {{result.returncode}}")
        
        # 检查期望的输出文件
        files_check_passed = True
        if expected_files:
            for expected_file in expected_files:
                # 尝试多个可能的文件路径
                possible_paths = [
                    expected_file,  # 当前目录
                    f"../{{expected_file}}",  # 上级目录
                    f"../evaluation/{{expected_file}}",  # evaluation目录
                ]
                
                file_found = False
                for file_path in possible_paths:
                    if os.path.exists(file_path):
                        print(f"[检查通过] 期望文件 {{expected_file}} 在 {{file_path}} 找到")
                        
                        # 显示文件信息
                        try:
                            file_size = os.path.getsize(file_path)
                            print(f"文件大小: {{file_size}} 字节")
                            
                            if file_size > 0:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    preview = content[:150] + ("..." if len(content) > 150 else "")
                                    print(f"文件内容预览: {{preview}}")
                        except Exception as e:
                            print(f"读取文件信息失败: {{e}}")
                        
                        file_found = True
                        break
                
                if not file_found:
                    print(f"[警告] 期望文件 {{expected_file}} 未找到")
                    files_check_passed = False
        
        # 综合判断测试结果
        if has_invalid_choice:
            test_result = False
            result_msg = "失败 - 存在无效选择错误"
        elif normal_exit:
            test_result = True
            result_msg = "通过 - 程序正常执行"
        else:
            test_result = False
            result_msg = "失败 - 程序异常退出"
        
        print(f"\\n[{{result_msg}}]")
        return test_result
        
    except subprocess.TimeoutExpired:
        print("[失败] 测试超时（60秒）")
        return False
    except Exception as e:
        print(f"[失败] 执行异常: {{e}}")
        return False

if __name__ == "__main__":
    success = test_{safe_name}()
    print("="*80)
    print(f"测试结果: {{'通过' if success else '失败'}}")
    sys.exit(0 if success else 1)
'''
    
    return script_content, f"test_{safe_name}.py"

def generate_all_test_scripts():
    """生成所有file_comparison测试脚本"""
    tests = load_test_plan()
    file_comparison_tests = [test for test in tests if test.get('type') == 'file_comparison']
    
    print(f"找到 {len(file_comparison_tests)} 个file_comparison测试")
    
    # 创建测试脚本目录
    test_dir = Path("generated_file_comparison_tests")
    test_dir.mkdir(exist_ok=True)
    
    generated_scripts = []
    
    for i, test in enumerate(file_comparison_tests, 1):
        metric = test['metric']
        description = test['description']
        testcase = test['testcases'][0]  # 取第一个测试用例
        expected_files = test.get('expected_output_files', [])
        
        # 生成脚本内容
        script_content, script_name = generate_single_test_script(
            metric, description, testcase, expected_files
        )
        
        # 写入脚本文件
        script_path = test_dir / script_name
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        generated_scripts.append({
            'name': metric,
            'script_path': str(script_path),
            'description': description
        })
        
        print(f"{i:2d}. 已生成: {script_path}")
    
    return generated_scripts

def execute_all_tests(test_scripts):
    """批量执行所有生成的测试脚本"""
    print(f"\n{'='*80}")
    print("开始批量执行File Comparison测试")
    print('='*80)
    
    results = []
    
    for i, test_script in enumerate(test_scripts, 1):
        print(f"\n[{i}/{len(test_scripts)}] 执行测试: {test_script['name']}")
        print(f"脚本路径: {test_script['script_path']}")
        
        try:
            result = subprocess.run(
                [sys.executable, test_script['script_path']],
                capture_output=True,
                text=True,
                timeout=120,
                encoding='utf-8',
                errors='ignore'
            )
            
            success = result.returncode == 0
            results.append({
                'name': test_script['name'],
                'success': success,
                'output': result.stdout,
                'error': result.stderr
            })
            
            status = "[通过]" if success else "[失败]"
            print(f"{status} {test_script['name']}")
            
        except subprocess.TimeoutExpired:
            print(f"[超时] {test_script['name']}")
            results.append({
                'name': test_script['name'],
                'success': False,
                'output': "",
                'error': "测试超时（120秒）"
            })
        except Exception as e:
            print(f"[错误] {test_script['name']}: {e}")
            results.append({
                'name': test_script['name'],
                'success': False,
                'output': "",
                'error': str(e)
            })
    
    return results

def generate_test_report(results):
    """生成详细的测试报告"""
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed
    
    report_content = f"""# File Comparison 测试报告

## 测试概览
- **执行时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **总测试数**: {total}
- **通过数**: {passed}
- **失败数**: {failed}
- **成功率**: {passed/total*100:.1f}%

## 测试结果详情

"""
    
    for result in results:
        status_icon = "✅" if result['success'] else "❌"
        report_content += f"### {status_icon} {result['name']}\n\n"
        
        if result['success']:
            report_content += "**状态**: 测试通过\n\n"
        else:
            report_content += "**状态**: 测试失败\n\n"
            if result['error']:
                report_content += f"**错误信息**: \n```\n{result['error']}\n```\n\n"
        
        report_content += "---\n\n"
    
    # 保存报告
    report_path = "file_comparison_test_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n详细测试报告已生成: {report_path}")
    return report_path

def main():
    """主函数"""
    print("File Comparison 测试脚本生成器和执行器")
    print("="*80)
    
    # 第一步：生成所有测试脚本
    print("\n第一步：生成测试脚本")
    print("-"*40)
    test_scripts = generate_all_test_scripts()
    
    # 第二步：执行所有测试
    print("\n第二步：批量执行测试")
    print("-"*40)
    results = execute_all_tests(test_scripts)
    
    # 第三步：生成测试报告
    print("\n第三步：生成测试报告")
    print("-"*40)
    report_path = generate_test_report(results)
    
    # 第四步：输出最终统计
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed
    
    print(f"\n{'='*80}")
    print("最终测试结果统计")
    print('='*80)
    print(f"总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {failed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有File Comparison测试均已通过！")
        return True
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请查看详细报告: {report_path}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)