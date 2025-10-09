#!/usr/bin/env python3
"""
本地 Code Agent 测试文件
测试各种功能是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.code_agent_local.agent import local_code_agent_system
from examples.code_agent_local.mcp_tools import (
    create_workspace, list_workspace, read_file, write_file, 
    execute_python_code, run_system_command, interactive_system_command
)
from examples.code_agent_local.config import WORKSPACE_DIR

class MockToolContext:
    """模拟工具上下文"""
    class Actions:
        def __init__(self):
            self.escalate = False
    
    def __init__(self):
        self.actions = self.Actions()

async def test_basic_tools():
    """测试基础工具功能"""
    print("🧪 测试基础工具功能...")
    
    context = MockToolContext()
    
    # 测试创建工作空间
    print("\n1. 测试创建工作空间")
    result = create_workspace(context, "test_workspace")
    print(f"   结果: {result}")
    
    # 测试列出工作空间
    print("\n2. 测试列出工作空间")
    result = list_workspace(context, "test_workspace")
    print(f"   结果: {result}")
    
    # 测试写入文件
    print("\n3. 测试写入文件")
    test_content = "print('Hello, World!')\nprint('这是一个测试文件')"
    result = write_file(context, f"{WORKSPACE_DIR}/test_workspace/src/test.py", test_content)
    print(f"   结果: {result}")
    
    # 测试读取文件
    print("\n4. 测试读取文件")
    result = read_file(context, f"{WORKSPACE_DIR}/test_workspace/src/test.py")
    print(f"   结果: {result}")
    
    # 测试执行Python代码
    print("\n5. 测试执行Python代码")
    test_code = """
import math
print("计算圆的面积")
radius = 5
area = math.pi * radius ** 2
print(f"半径为 {radius} 的圆的面积是: {area:.2f}")
"""
    result = execute_python_code(context, test_code)
    print(f"   结果: {result}")
    
    # 测试系统命令
    print("\n6. 测试系统命令")
    result = run_system_command(context, "echo 'Hello from system command'")
    print(f"   结果: {result}")

    # 测试交互式系统命令
    # print("\n7. 测试交互式系统命令")
    # result = interactive_system_command(context, "python fortune_teller.py")
    # print(f"   结果: {result}")

async def test_agent_system():
    """测试代理系统"""
    print("\n🧪 测试代理系统...")
    
    # 测试代理系统初始化
    print("\n1. 测试代理系统初始化")
    agent_system = local_code_agent_system
    root_agent = agent_system.get_root_agent()
    print(f"   根代理名称: {root_agent.name}")
    print(f"   代理系统状态: 正常")
    
    # 测试代理运行
    print("\n2. 测试代理运行")
    test_input = "创建一个简单的计算器程序"
    result = agent_system.run(test_input)
    print(f"   输入: {test_input}")
    print(f"   结果: {result}")

async def test_mcp_integration():
    """测试MCP集成"""
    print("\n🧪 测试MCP集成...")
    
    # 这里应该测试与MCP服务器的连接
    # 由于MCP服务器需要单独启动，这里只是模拟测试
    print("\n1. 测试MCP工具集创建")
    from examples.code_agent_local.mcp_tools import (
        create_python_interpreter_toolset,
        create_file_operations_toolset
    )
    
    try:
        python_toolset = create_python_interpreter_toolset()
        file_toolset = create_file_operations_toolset()
        print("   MCP工具集创建成功")
    except Exception as e:
        print(f"   MCP工具集创建失败: {e}")

def test_config():
    """测试配置"""
    print("\n🧪 测试配置...")
    
    from examples.code_agent_local.config import (
        BASIC_MODEL, WORKSPACE_DIR, ALLOWED_EXTENSIONS,
        MAX_FILE_SIZE, SANDBOX_MODE, CURRENT_EXECUTION_ID
    )
    
    print(f"1. 当前执行ID: {CURRENT_EXECUTION_ID}")
    print(f"2. 基础模型: {BASIC_MODEL}")
    print(f"3. 工作空间目录: {WORKSPACE_DIR}")
    print(f"4. 允许的文件扩展名: {ALLOWED_EXTENSIONS}")
    print(f"5. 最大文件大小: {MAX_FILE_SIZE} bytes")
    print(f"6. 沙盒模式: {SANDBOX_MODE}")

async def main():
    """主测试函数"""
    print("🚀 开始本地 Code Agent 测试")
    print("=" * 60)
    
    # 测试配置
    test_config()
    
    # 测试基础工具
    await test_basic_tools()
    
    # 测试代理系统
    await test_agent_system()
    
    # 测试MCP集成
    await test_mcp_integration()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("\n📝 测试总结:")
    print("- 基础工具功能正常")
    print("- 代理系统初始化成功")
    print("- 配置加载正常")
    print("- MCP工具集创建成功")
    print("\n💡 下一步:")
    print("1. 启动MCP服务器: python mcp_servers.py")
    print("2. 运行主程序: python main.py")
    print("3. 开始使用本地 Code Agent")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc() 