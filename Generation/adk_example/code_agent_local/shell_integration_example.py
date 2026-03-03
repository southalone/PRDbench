"""
交互式Shell工具集成示例
展示如何在Agent中使用run_interactive_shell工具
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

class InteractiveShellClient:
    """交互式Shell客户端，用于与MCP服务器通信"""
    
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url
        
    async def run_shell(self, cmd: str = None, session_id: str = None, user_input: str = None) -> Dict[str, Any]:
        """调用交互式shell工具"""
        async with aiohttp.ClientSession() as session:
            data = {}
            if cmd:
                data['cmd'] = cmd
            if session_id:
                data['session_id'] = session_id  
            if user_input:
                data['user_input'] = user_input
                
            async with session.post(f"{self.base_url}/interactive-shell/run", json=data) as resp:
                result = await resp.json()
                return result
                
    async def kill_session(self, session_id: str) -> Dict[str, Any]:
        """终止shell会话"""
        async with aiohttp.ClientSession() as session:
            data = {'session_id': session_id}
            async with session.post(f"{self.base_url}/interactive-shell/kill", json=data) as resp:
                result = await resp.json()
                return result

# Agent工具函数定义
async def run_interactive_shell(cmd: str = None, session_id: str = None, user_input: str = None) -> Dict[str, Any]:
    """
    Agent使用的交互式shell工具函数
    
    参数:
        cmd: 启动新会话时的命令
        session_id: 继续现有会话的ID
        user_input: 发送给shell的输入
        
    返回:
        包含session_id, output, waiting, finished的字典
    """
    client = InteractiveShellClient()
    result = await client.run_shell(cmd=cmd, session_id=session_id, user_input=user_input)
    
    if result.get('status') == 'success':
        return {
            'session_id': result.get('session_id'),
            'output': result.get('output', ''),
            'waiting': result.get('waiting', False),
            'finished': result.get('finished', False)
        }
    else:
        return {
            'error': result.get('error', 'Unknown error'),
            'session_id': session_id,
            'output': '',
            'waiting': False,
            'finished': True
        }

async def kill_shell_session(session_id: str) -> Dict[str, Any]:
    """
    Agent使用的会话终止工具函数
    """
    client = InteractiveShellClient()
    result = await client.kill_session(session_id)
    return result

# 使用示例
async def example_python_session():
    """示例：Python交互式会话"""
    print("=== Python交互式会话示例 ===")
    
    # 启动Python
    result = await run_interactive_shell(cmd="python")
    session_id = result['session_id']
    print(f"启动Python，会话ID: {session_id}")
    print(f"输出: {result['output']}")
    
    # 执行Python代码
    result = await run_interactive_shell(session_id=session_id, user_input="x = 10")
    print(f"设置变量x=10")
    print(f"输出: {result['output']}")
    
    result = await run_interactive_shell(session_id=session_id, user_input="print(f'x的值是: {x}')")
    print(f"打印变量x")
    print(f"输出: {result['output']}")
    
    result = await run_interactive_shell(session_id=session_id, user_input="import math")
    print(f"导入math模块")
    print(f"输出: {result['output']}")
    
    result = await run_interactive_shell(session_id=session_id, user_input="print(f'π的值是: {math.pi}')")
    print(f"使用math模块")
    print(f"输出: {result['output']}")
    
    # 退出Python
    result = await run_interactive_shell(session_id=session_id, user_input="exit()")
    print(f"退出Python")
    print(f"会话结束: {result['finished']}")

async def example_bash_session():
    """示例：Bash交互式会话"""
    print("\n=== Bash交互式会话示例 ===")
    
    # 启动bash
    result = await run_interactive_shell(cmd="bash")
    session_id = result['session_id']
    print(f"启动Bash，会话ID: {session_id}")
    
    # 查看当前目录
    result = await run_interactive_shell(session_id=session_id, user_input="pwd")
    print(f"当前目录: {result['output'].strip()}")
    
    # 列出文件
    result = await run_interactive_shell(session_id=session_id, user_input="ls -la")
    print(f"文件列表:\n{result['output']}")
    
    # 创建临时目录
    result = await run_interactive_shell(session_id=session_id, user_input="mkdir -p /tmp/test_dir")
    print("创建临时目录")
    
    # 切换目录
    result = await run_interactive_shell(session_id=session_id, user_input="cd /tmp/test_dir")
    print("切换到临时目录")
    
    # 确认目录切换
    result = await run_interactive_shell(session_id=session_id, user_input="pwd")
    print(f"新的当前目录: {result['output'].strip()}")
    
    # 退出bash
    result = await run_interactive_shell(session_id=session_id, user_input="exit")
    print(f"退出Bash，会话结束: {result['finished']}")

# Agent集成指南
AGENT_INTEGRATION_GUIDE = """
# Agent集成交互式Shell工具指南

## 1. 在Agent配置中添加工具定义

```python
from tools_definitions import INTERACTIVE_SHELL_TOOLS

# 将工具添加到Agent的工具列表中
agent_tools = INTERACTIVE_SHELL_TOOLS + other_tools
```

## 2. 在Agent中实现工具调用函数

```python
import asyncio
from shell_integration_example import run_interactive_shell, kill_shell_session

class MyAgent:
    def __init__(self):
        self.active_sessions = {}  # 跟踪活跃的shell会话
        
    async def call_tool(self, tool_name: str, parameters: dict):
        if tool_name == "run_interactive_shell":
            return await run_interactive_shell(**parameters)
        elif tool_name == "kill_shell_session":
            return await kill_shell_session(**parameters)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
```

## 3. Agent使用模式

### 模式1: 一次性命令执行
```python
# 执行单个命令
result = await agent.call_tool("run_interactive_shell", {"cmd": "ls -la"})
```

### 模式2: 交互式会话
```python
# 启动会话
result = await agent.call_tool("run_interactive_shell", {"cmd": "python"})
session_id = result["session_id"]

# 持续交互
while not result["finished"]:
    if result["waiting"]:
        # 根据上下文决定输入什么
        user_input = decide_input_based_on_context(result["output"])
        result = await agent.call_tool("run_interactive_shell", {
            "session_id": session_id,
            "user_input": user_input
        })
    else:
        # 等待更多输出
        result = await agent.call_tool("run_interactive_shell", {
            "session_id": session_id
        })
```

## 4. 最佳实践

1. **会话管理**: 跟踪活跃的session_id，避免混淆
2. **错误处理**: 检查返回的error字段，适当处理异常
3. **状态检查**: 根据waiting和finished状态决定下一步操作
4. **资源清理**: 不再需要的会话要及时终止
5. **超时处理**: 为长时间运行的命令设置合理的超时

## 5. 常见使用场景

- **代码执行**: Python/Node.js/等解释器
- **系统管理**: bash/zsh命令执行
- **数据库操作**: mysql/psql客户端
- **开发工具**: git/npm/pip等命令行工具
"""

if __name__ == "__main__":
    # 运行示例
    async def main():
        await example_python_session()
        await example_bash_session()
        print(AGENT_INTEGRATION_GUIDE)
    
    asyncio.run(main()) 