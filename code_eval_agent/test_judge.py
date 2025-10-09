#!/usr/bin/env python3
"""
测试Judge工具
验证自动化测试评判功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 在导入任何其他模块之前设置环境变量
os.environ['CODE_AGENT_WORKSPACE_DIR'] = os.getcwd()

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 直接从当前目录导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 尝试导入judge工具
try:
    from examples.code_agent_local.mcp_tools import judge
except ImportError:
    # 如果上面失败，尝试直接导入
    import importlib.util
    spec = importlib.util.spec_from_file_location("mcp_tools", "mcp_tools.py")
    mcp_tools = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcp_tools)
    judge = mcp_tools.judge

class MockToolContext:
    """模拟工具上下文"""
    class Actions:
        def __init__(self):
            self.escalate = False
    
    def __init__(self):
        self.actions = self.Actions()

# 创建全局context实例
mock_context = MockToolContext()

async def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试基本功能 ===")
    
    # 测试简单的Hello World程序
    print("1. 测试Hello World程序...")
    result = judge(
        mock_context,
        context="程序应该输出Hello World和用户姓名",
        entry_command="python test_data/hello_world.py",
        input_file="test_data/input_name.txt"
    )
    print(result)
    output = result.get('log', '')
    if "你好, 张三!" in output and "你好, lisa!" in output:
        print("✅ 输出包含你好, 张三!和你好, lisa!")
    else:
        print("❌ 输出不包含你好, 张三!和你好, lisa!")
        return False
    if 'success' in result:
        print("✅ 程序执行成功")
    else:
        print("❌ 程序执行失败")
        return False
    
    return True

async def test_calculator_program():
    """测试计算器程序"""
    print("\n=== 测试计算器程序 ===")
    
    # 测试正常的计算器功能
    print("1. 测试正常计算...")
    result = judge(
        mock_context,
        context="程序应该输出15+3=18和15×3=45的计算结果",
        entry_command="python test_data/calculator.py",
        input_file="test_data/input_normal.txt"
    )
    
    print(result)
    if 'error' in result and result['error']:
        print(f"错误: {result['error']}")
        return False
    
    print(result['log'])

    output=result.get('log', '')
    if "15 + 3 = 18" in output and "15 × 3 = 45" in output:
        print("✅ 输出包含15+3=18和15*3=45")
    else:
        print("❌ 输出不包含15+3=18和15*3=45")
        return False

    # 检查程序是否执行成功
    if result.get('success'):
        print("✅ 程序执行成功")
    else:
        print("❌ 程序执行失败")
        return False

    return True

async def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    # 测试无效输入
    print("1. 测试无效输入...")
    result = judge(
        mock_context,
        context="程序应该处理无效输入并输出错误信息",
        entry_command="python test_data/calculator.py",
        input_file="test_data/input_invalid.txt"
    )
    
    print(result)
    # 对于这种情况，程序应该退出非零状态
    if result.get('error'):
        print("✅ 程序正确处理了无效输入，报错：",result.get('error'))
    else:
        print("⚠️  程序可能没有正确处理无效输入")
    
    # 测试不存在的程序
    print("\n2. 测试不存在的程序...")
    result = judge(
        mock_context,
        context="程序不存在应该报错",
        entry_command="python test_data/nonexistent_program.py",
        input_file="test_data/input_normal.txt"
    )
    
    if 'error' in result or not result.get('success'):
        print("✅ 正确处理了不存在的程序,报错：",result.get('error'))
    
    else:
        print("❌ 没有正确处理不存在的程序")
        return False
    
    # 测试程序崩溃
    print("\n3. 测试程序崩溃...")
    result = judge(
        mock_context,
        context="程序会崩溃并抛出异常",
        entry_command="python test_data/error_program.py"
    )
    print(result)

    if 'error' in result or not result.get('success'):
        print("✅ 正确捕获了程序崩溃，报错：",result.get('error'))
    else:
        print("⚠️  程序崩溃处理可能有问题")
        return False
    
    
    return True

async def test_input_file_variations():
    """测试不同的输入文件情况"""
    print("\n=== 测试输入文件变化 ===")
    
    # 测试没有输入文件的情况
    print("1. 测试无输入文件的程序...")
    result = judge(
        mock_context,
        context="程序应该输出Hello World",
        entry_command="python -c 'print(\"Hello World without input\")'"
    )
    
    
    print(f"程序输出: {result.get('log', '')}")
    

    if "Hello World without input" not in result.get('log', ''):
        print("❌ 程序输出不符合预期")
        return False
        
    print("✅ 无输入文件的程序测试通过")
    
    # 测试不存在的输入文件
    print("\n2. 测试不存在的输入文件...")
    result = judge(
        mock_context,
        context="应该报告输入文件不存在",
        entry_command="python test_data/hello_world.py",
        input_file="test_data/nonexistent_input.txt"
    )
    
    if 'error' in result and not result['success']:
        print("✅ 正确处理了不存在的输入文件，报错：", result.get('error'))
    else:
        print("❌ 没有正确处理不存在的输入文件")
        return False
    
    return True


def main():
    """主测试函数"""
    print("🚀 开始测试Judge工具...")
    print("=" * 60)
    
    # 检查测试数据文件是否存在
    test_files = [
        "test_data/hello_world.py",
        "test_data/calculator.py", 
        "test_data/error_program.py",
        "test_data/input_normal.txt",
        "test_data/input_name.txt",
        "test_data/input_invalid.txt"
    ]
    
    missing_files = []
    for file_path in test_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少测试文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("请先运行测试数据创建脚本")
        return
    
    print("✅ 测试数据文件检查完成")
    print()
    
    # 运行所有测试
    tests = [
        test_basic_functionality,
        test_calculator_program,
        test_error_handling,
        test_input_file_variations
    ]
    
    success_count = 0
    for test in tests:
        try:
            if asyncio.run(test()):
                success_count += 1
                print(f"✅ {test.__name__} 通过")
            else:
                print(f"❌ {test.__name__} 失败")
        except Exception as e:
            print(f"❌ {test.__name__} 异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"测试完成: {success_count}/{len(tests)} 通过")
    
    if success_count == len(tests):
        print("🎉 所有测试通过！Judge工具工作正常。")
    else:
        print("⚠️  部分测试失败，请检查配置和依赖。")
        print("\n💡 可能的问题:")
        print("   - pexpect模块未安装")
        print("   - 测试程序文件权限问题") 
        print("   - Python路径问题")

if __name__ == "__main__":
    main() 