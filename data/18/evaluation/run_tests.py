#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
用于验证所有自动化测试的正确性
"""

import subprocess
import sys
import os

def run_test(test_command):
    """运行单个测试命令"""
    print(f"\n{'='*60}")
    print(f"运行测试: {test_command}")
    print('='*60)
    
    try:
        result = subprocess.run(test_command, shell=True, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        if result.returncode == 0:
            print("✅ 测试通过")
            if result.stdout:
                print("输出:")
                print(result.stdout)
        else:
            print("❌ 测试失败")
            if result.stdout:
                print("标准输出:")
                print(result.stdout)
            if result.stderr:
                print("错误输出:")
                print(result.stderr)
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ 测试执行异常: {e}")
        return False

def main():
    """主函数"""
    print("开始运行MatrixAnalysisFinal项目的自动化测试")
    
    # 定义所有测试命令
    test_commands = [
        # 健壮性测试
        "python src/main.py --help",
        "python src/main.py --unknown-arg",
        "python src/main.py --model INVALIDMODEL --input src/data/LU.txt",
        "python src/main.py --model LU --input non_existent_file.txt",
        
        # 正确性测试
        "python -m pytest evaluation/tests/test_lu_correctness.py::test_lu_factorization_correctness -v",
        "python -m pytest evaluation/tests/test_qr_correctness.py::test_qr_factorization_correctness -v",
        "python -m pytest evaluation/tests/test_hr_correctness.py::test_hr_factorization_correctness -v",
        "python -m pytest evaluation/tests/test_gr_correctness.py::test_gr_factorization_correctness -v",
        "python -m pytest evaluation/tests/test_urv_correctness.py::test_urv_factorization_correctness -v",
        
        # 输出格式测试
        "python -m pytest evaluation/tests/test_output_format.py::test_lu_output_format -v",
        "python -m pytest evaluation/tests/test_output_format.py::test_qr_output_format -v",
        "python -m pytest evaluation/tests/test_output_format.py::test_hr_output_format -v",
        "python -m pytest evaluation/tests/test_output_format.py::test_gr_output_format -v",
        "python -m pytest evaluation/tests/test_output_format.py::test_urv_output_format -v",
        
        # 矩阵秩计算测试
        "python -m pytest evaluation/tests/test_matrix_rank.py::test_lu_matrix_rank -v",
        "python -m pytest evaluation/tests/test_matrix_rank.py::test_qr_matrix_rank -v",
        "python -m pytest evaluation/tests/test_matrix_rank.py::test_hr_matrix_rank -v",
        "python -m pytest evaluation/tests/test_matrix_rank.py::test_gr_matrix_rank -v",
        "python -m pytest evaluation/tests/test_matrix_rank.py::test_urv_matrix_rank -v",
    ]
    
    # 运行所有测试
    passed = 0
    failed = 0
    
    for cmd in test_commands:
        if run_test(cmd):
            passed += 1
        else:
            failed += 1
    
    # 输出总结
    print(f"\n{'='*60}")
    print("测试总结")
    print('='*60)
    print(f"总测试数: {len(test_commands)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed == 0:
        print("🎉 所有测试都通过了！")
        return 0
    else:
        print(f"⚠️  有 {failed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())