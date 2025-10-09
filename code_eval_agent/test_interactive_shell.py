#!/usr/bin/env python3
"""
测试交互式Shell工具
验证MCP封装和工具集成的功能
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_tools import run_interactive_shell, kill_shell_session

async def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试基本功能 ===")
    
    # 测试启动Python会话
    print("1. 启动Python会话...")
    result = run_interactive_shell(cmd="python")
    print(f"结果: {result}")
    
    if 'error' in result:
        print(f"错误: {result['error']}")
        return False
        
    session_id = result['session_id']
    print(f"会话ID: {session_id}")
    print(f"输出: {result['output']}")
    print(f"等待输入: {result['waiting']}")
    print(f"已结束: {result['finished']}")
    
    # 测试发送命令
    print("\n2. 发送Python命令...")
    result = run_interactive_shell(session_id=session_id, user_input="print('Hello from Python!')")
    print(f"结果: {result}")
    print(f"输出: {result['output']}")
    
    # 测试终止会话
    print("\n3. 终止会话...")
    kill_result = kill_shell_session(session_id)
    print(f"终止结果: {kill_result}")
    
    return True

async def test_bash_session():
    """测试Bash会话"""
    print("\n=== 测试Bash会话 ===")
    
    # 启动bash
    print("1. 启动Bash...")
    result = run_interactive_shell(cmd="bash")
    if 'error' in result:
        print(f"错误: {result['error']}")
        return False
        
    session_id = result['session_id']
    print(f"Bash会话ID: {session_id}")
    
    # 执行几个命令
    commands = ["pwd", "ls -la", "echo 'Hello from Bash!'", "date"]
    
    for cmd in commands:
        print(f"\n执行命令: {cmd}")
        result = run_interactive_shell(session_id=session_id, user_input=cmd)
        print(f"输出: {result['output']}")
        
        if result['finished']:
            print("会话意外结束")
            break
    
    # 退出bash
    print("\n退出Bash...")
    result = run_interactive_shell(session_id=session_id, user_input="exit")
    print(f"退出结果: {result}")
    print(f"会话结束: {result['finished']}")
    
    return True

async def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    # 测试无效的session_id
    print("1. 测试无效session_id...")
    result = run_interactive_shell(session_id="invalid_session", user_input="test")
    print(f"无效session_id结果: {result}")
    
    # 测试无效命令
    print("\n2. 测试无效命令...")
    result = run_interactive_shell(cmd="nonexistent_command_12345")
    print(f"无效命令结果: {result}")
    
    if 'session_id' in result and result['session_id']:
        # 清理会话
        kill_shell_session(result['session_id'])
    
    return True

async def test_interactive_python():
    """测试Python交互式编程"""
    print("\n=== 测试Python交互式编程 ===")
    
    # 启动Python
    result = run_interactive_shell(cmd="python")
    if 'error' in result:
        print(f"启动Python失败: {result['error']}")
        return False
        
    session_id = result['session_id']
    print(f"Python会话ID: {session_id}")
    
    # 定义变量
    print("\n定义变量...")
    result = run_interactive_shell(session_id=session_id, user_input="x = 42")
    print(f"定义变量输出: {result['output']}")
    
    # 使用变量
    print("\n使用变量...")
    result = run_interactive_shell(session_id=session_id, user_input="print(f'x的值是: {x}')")
    print(f"使用变量输出: {result['output']}")
    
    # 导入模块
    print("\n导入模块...")
    result = run_interactive_shell(session_id=session_id, user_input="import math")
    print(f"导入模块输出: {result['output']}")
    
    # 使用模块
    print("\n使用模块...")
    result = run_interactive_shell(session_id=session_id, user_input="print(f'π = {math.pi:.4f}')")
    print(f"使用模块输出: {result['output']}")
    
    # 定义函数
    print("\n定义函数...")
    result = run_interactive_shell(session_id=session_id, user_input="def greet(name): return f'Hello, {name}!'")
    print(f"定义函数输出: {result['output']}")
    
    # 调用函数
    print("\n调用函数...")
    result = run_interactive_shell(session_id=session_id, user_input="print(greet('World'))")
    print(f"调用函数输出: {result['output']}")
    
    # 退出Python
    print("\n退出Python...")
    result = run_interactive_shell(session_id=session_id, user_input="exit()")
    print(f"退出Python结果: {result}")
    
    return True

def main():
    """主测试函数"""
    print("开始测试交互式Shell工具...")
    
    # 运行所有测试
    tests = [
        test_basic_functionality,
        test_bash_session, 
        test_error_handling,
        test_interactive_python
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
    
    print(f"\n测试完成: {success_count}/{len(tests)} 通过")
    
    if success_count == len(tests):
        print("🎉 所有测试通过！交互式Shell工具工作正常。")
    else:
        print("⚠️  部分测试失败，请检查配置和依赖。")

if __name__ == "__main__":
    main() 