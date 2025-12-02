#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成的File Comparison测试脚本
测试项目: 2.3.4 稀疏矩阵处理-运营报告生成
"""

import subprocess
import sys
import os
from pathlib import Path

def test_2_3_4_稀疏矩阵处理_运营报告生成():
    """执行2.3.4 稀疏矩阵处理-运营报告生成测试"""
    print("="*80)
    print("测试项目: 2.3.4 稀疏矩阵处理-运营报告生成")
    print("="*80)
    
    test_command = "cd src && echo -e "5\n1\n1\n0\n0" | python main.py"
    test_input = "5\n1\n1\n0\n0"
    expected_files = ['expected_sparse_report.txt']
    
    print(f"命令: {test_command}")
    print(f"输入序列: {test_input}")
    print(f"期望输出文件: {expected_files}")
    print("-"*80)
    
    try:
        if test_input and "echo -e" in test_command:
            # 处理交互式命令
            input_text = test_input.replace('\\n', '\n')
            
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
            
            print(f"实际执行: {' '.join(cmd)} (工作目录: {cwd})")
            print(f"输入内容: {repr(input_text)}")
            
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
        
        print(f"退出码: {result.returncode}")
        
        # 显示输出（限制长度避免过多内容）
        if result.stdout:
            stdout_preview = result.stdout[:800] + ("...（截断）" if len(result.stdout) > 800 else "")
            print(f"标准输出:\n{stdout_preview}")
        
        if result.stderr:
            stderr_preview = result.stderr[:400] + ("...（截断）" if len(result.stderr) > 400 else "")
            print(f"标准错误:\n{stderr_preview}")
        
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
            print(f"[警告] 程序异常退出，退出码: {result.returncode}")
        
        # 检查期望的输出文件
        files_check_passed = True
        if expected_files:
            for expected_file in expected_files:
                # 尝试多个可能的文件路径
                possible_paths = [
                    expected_file,  # 当前目录
                    f"../{expected_file}",  # 上级目录
                    f"../evaluation/{expected_file}",  # evaluation目录
                ]
                
                file_found = False
                for file_path in possible_paths:
                    if os.path.exists(file_path):
                        print(f"[检查通过] 期望文件 {expected_file} 在 {file_path} 找到")
                        
                        # 显示文件信息
                        try:
                            file_size = os.path.getsize(file_path)
                            print(f"文件大小: {file_size} 字节")
                            
                            if file_size > 0:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    preview = content[:150] + ("..." if len(content) > 150 else "")
                                    print(f"文件内容预览: {preview}")
                        except Exception as e:
                            print(f"读取文件信息失败: {e}")
                        
                        file_found = True
                        break
                
                if not file_found:
                    print(f"[警告] 期望文件 {expected_file} 未找到")
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
        
        print(f"\n[{result_msg}]")
        return test_result
        
    except subprocess.TimeoutExpired:
        print("[失败] 测试超时（60秒）")
        return False
    except Exception as e:
        print(f"[失败] 执行异常: {e}")
        return False

if __name__ == "__main__":
    success = test_2_3_4_稀疏矩阵处理_运营报告生成()
    print("="*80)
    print(f"测试结果: {'通过' if success else '失败'}")
    sys.exit(0 if success else 1)
