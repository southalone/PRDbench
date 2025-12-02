#!/usr/bin/env python3
"""
运行测试覆盖度检查的完整流程
这个脚本演示了如何执行"2.1b 自动化单元测试 - 测试覆盖度"测试
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(command, description):
    """运行命令并返回结果"""
    print(f"\n{'='*50}")
    print(f"执行: {description}")
    print(f"命令: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(f"退出码: {result.returncode}")
        if result.stdout:
            print("标准输出:")
            print(result.stdout)
        if result.stderr:
            print("标准错误:")
            print(result.stderr)
        
        return result.returncode == 0, result
    except Exception as e:
        print(f"执行错误: {e}")
        return False, None

def main():
    """主函数 - 执行完整的测试覆盖度检查流程"""
    print("开始执行测试覆盖度检查...")
    
    # 步骤1: 生成实际的测试覆盖度报告
    success1, result1 = run_command(
        "python evaluation/test_coverage_analyzer.py src/tests evaluation/actual_test_coverage_report.json",
        "生成实际测试覆盖度报告"
    )
    
    if not success1:
        print("[ERROR] 生成测试覆盖度报告失败")
        return False
    
    # 步骤2: 验证生成的文件存在
    actual_report_path = Path("evaluation/actual_test_coverage_report.json")
    expected_report_path = Path("evaluation/expected_test_coverage_report.json")
    
    if not actual_report_path.exists():
        print(f"[ERROR] 实际报告文件不存在: {actual_report_path}")
        return False
    
    if not expected_report_path.exists():
        print(f"[ERROR] 期望报告文件不存在: {expected_report_path}")
        return False
    
    print("[OK] 报告文件都存在")
    
    # 步骤3: 比较文件内容
    success2, result2 = run_command(
        f"python evaluation/file_comparator.py {expected_report_path} {actual_report_path}",
        "比较期望报告和实际报告"
    )
    
    if not success2:
        print("[ERROR] 文件比较失败")
        return False
    
    # 步骤4: 解析比较结果
    try:
        comparison_result = json.loads(result2.stdout)
        if comparison_result.get('files_match', False):
            print("[SUCCESS] 文件内容匹配！测试覆盖度检查通过")
            
            # 显示覆盖度详情
            with open(actual_report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            print(f"\n[STATS] 测试覆盖度统计:")
            stats = report_data.get('overall_stats', {})
            print(f"  总功能数: {stats.get('total_functions', 'N/A')}")
            print(f"  完全覆盖功能数: {stats.get('fully_covered_functions', 'N/A')}")
            print(f"  覆盖度百分比: {stats.get('coverage_percentage', 'N/A')}%")
            print(f"  测试文件数: {stats.get('total_test_files', 'N/A')}")
            print(f"  测试方法数: {stats.get('total_test_methods', 'N/A')}")
            
            return True
        else:
            print("[ERROR] 文件内容不匹配！测试覆盖度检查失败")
            return False
            
    except json.JSONDecodeError as e:
        print(f"[ERROR] 解析比较结果失败: {e}")
        return False

if __name__ == '__main__':
    success = main()
    
    print(f"\n{'='*50}")
    if success:
        print("[SUCCESS] 测试覆盖度检查完成 - 全部通过!")
    else:
        print("[FAILED] 测试覆盖度检查完成 - 存在问题!")
    print(f"{'='*50}")
    
    sys.exit(0 if success else 1)