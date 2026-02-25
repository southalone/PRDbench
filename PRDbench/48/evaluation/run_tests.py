#!/usr/bin/env python3
"""
迷宫问题项目测试执行脚本
运行所有测试并生成测试报告
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🏰 迷宫问题项目测试方案执行")
    print("="*60)

    # 环境检查
    print("\n📋 1. 环境验证测试")
    success1 = run_command("python -c \"import numpy; print(f'✅ NumPy版本: {numpy.__version__}')\"",
                          "检查numpy依赖")

    # 单元测试
    print("\n📋 2. 单元测试 (pytest)")
    success2 = run_command("pytest evaluation/tests/ -v --tb=short",
                          "运行所有单元测试")

    # Shell交互测试示例
    print("\n📋 3. Shell交互测试示例")
    test_cases = [
        ("cd src && python main.py < ../evaluation/inputs/dfs_basic_generate.in",
         "DFS基础生成功能测试"),
        ("cd src && python main.py < ../evaluation/inputs/performance_compare.in",
         "性能比较功能测试"),
        ("cd src && python main.py < ../evaluation/inputs/validate_connectivity.in",
         "连通性验证功能测试")
    ]

    shell_success = True
    for cmd, desc in test_cases:
        success = run_command(cmd, desc)
        shell_success = shell_success and success

    # 测试总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    print(f"环境验证: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"单元测试: {'✅ 通过' if success2 else '❌ 失败'}")
    print(f"Shell交互测试: {'✅ 通过' if shell_success else '❌ 失败'}")

    overall_success = success1 and success2 and shell_success
    print(f"\n整体结果: {'✅ 所有测试通过' if overall_success else '❌ 部分测试失败'}")

    if not overall_success:
        print("\n💡 建议:")
        print("- 检查依赖安装: pip install numpy pytest")
        print("- 检查代码实现是否完整")
        print("- 查看详细错误信息进行调试")
    else:
        print("\n🎉 恭喜！所有测试都通过了，项目功能完整！")

    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
