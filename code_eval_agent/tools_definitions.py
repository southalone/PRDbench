"""
工具定义文件
定义了Agent可以使用的所有工具及其使用方法
"""

# 交互式Shell工具定义
INTERACTIVE_SHELL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_interactive_shell",
            "description": """
运行一个交互式shell会话。这个工具允许你与shell进行交互式对话。

使用方法：
1. 首次使用时，提供cmd参数来启动新的shell会话
2. 获取返回的session_id，用于后续交互
3. 如果shell在等待输入(waiting=True)，可以通过提供user_input来发送输入
4. 使用返回的session_id继续与同一个shell会话交互
5. 当finished=True时，会话结束

示例工作流程：
- 启动Python: run_interactive_shell(cmd="python")
- 继续交互: run_interactive_shell(session_id="xxx", user_input="print('hello')")
- 启动bash: run_interactive_shell(cmd="bash")
- 执行命令: run_interactive_shell(session_id="yyy", user_input="ls -la")

注意：
- 每个会话都是独立的，有自己的环境和状态
- 会话会保持所有的历史状态（变量、目录等）
- 如果会话异常，可以使用kill_shell_session强制终止
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {
                        "type": "string",
                        "description": "要执行的shell命令，仅在首次调用时需要。例如：'python', 'bash', 'node', 'mysql -u root -p'等"
                    },
                    "session_id": {
                        "type": "string", 
                        "description": "会话ID，用于继续之前的会话。首次调用时不需要提供"
                    },
                    "user_input": {
                        "type": "string",
                        "description": "要发送到shell的输入内容。当shell等待输入时使用"
                    }
                }
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "kill_shell_session",
            "description": "强制终止一个正在运行的shell会话。当会话出现问题或不再需要时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "要终止的会话ID"
                    }
                },
                "required": ["session_id"]
            }
        }
    }
]

# 所有工具定义
ALL_TOOLS = INTERACTIVE_SHELL_TOOLS

# 工具使用说明
TOOL_USAGE_GUIDE = """
# 交互式Shell工具使用指南

## 基本概念
- 每个shell会话都有一个唯一的session_id
- 会话保持状态：变量、当前目录、环境等
- 支持任何可以在命令行运行的程序

## 常见使用场景

### 1. Python交互式编程
```
# 启动Python
result = run_interactive_shell(cmd="python")
session_id = result["session_id"]

# 执行Python代码
run_interactive_shell(session_id=session_id, user_input="x = 10")
run_interactive_shell(session_id=session_id, user_input="print(x * 2)")
```

### 2. 系统管理
```
# 启动bash
result = run_interactive_shell(cmd="bash")
session_id = result["session_id"]

# 执行系统命令
run_interactive_shell(session_id=session_id, user_input="cd /tmp")
run_interactive_shell(session_id=session_id, user_input="ls -la")
run_interactive_shell(session_id=session_id, user_input="pwd")
```

### 3. 数据库操作
```
# 连接MySQL
result = run_interactive_shell(cmd="mysql -u root -p")
session_id = result["session_id"]

# 输入密码
run_interactive_shell(session_id=session_id, user_input="password123")
# 执行SQL
run_interactive_shell(session_id=session_id, user_input="SHOW DATABASES;")
```

## 返回值说明
```json
{
    "session_id": "会话ID",
    "output": "程序输出内容", 
    "waiting": true/false,  // 是否在等待输入
    "finished": true/false  // 会话是否结束
}
```

## 最佳实践
1. 总是检查waiting状态，决定是否需要提供输入
2. 保存session_id用于后续交互
3. 会话结束后(finished=True)不要再使用该session_id
4. 出现问题时使用kill_shell_session强制终止
5. 对于长时间运行的命令，要有耐心等待输出
""" 