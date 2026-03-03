"""
本地 Code Agent 单体代理定义
基于 Google ADK 的本地代码代理，支持代码规划、编写、文件管理、代码执行等所有功能
"""

import logging
from datetime import datetime
from typing import Dict, Any

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
import json
from .config import BASIC_MODEL, SYSTEM_NAME, MAX_ITERATIONS
from .config import friday_model_dict

import litellm
# litellm._turn_on_debug()
# 提前应用 MCP 猴子补丁，保证在 Agent/工具创建前生效
try:
    from mcp_retry_wrapper import apply_mcp_monkey_patches
    _patch_info = apply_mcp_monkey_patches()
    logging.getLogger(__name__).info(f"MCP猴子补丁结果(agent阶段): {_patch_info}")
except Exception as _agent_patch_err:
    logging.getLogger(__name__).warning(f"MCP猴子补丁在agent阶段应用失败：{_agent_patch_err}")
    
    
from .config import BASIC_MODEL, SYSTEM_NAME, MAX_ITERATIONS
from .mcp_tools import (
    exit_loop, create_workspace, list_workspace,
    read_file, write_file, delete_file, 
    # execute_python_code, 
    run_system_command, 
    start_interative_shell, run_interactive_shell, kill_shell_session,
    judge,  # 添加Judge工具导入
    deal_graph
)

ALL_TOOLS = [
    exit_loop,
    # create_workspace,
    list_workspace,
    read_file,
    write_file,
    # delete_file,
    # execute_python_code,
    run_system_command,
    # interactive_system_command,
    start_interative_shell,
    run_interactive_shell,
    kill_shell_session,
    # meituan_search,
    # meituan_browse,
    judge,  # 添加Judge工具
    deal_graph
]

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)



class LocalCodeAgentSystem:
    """
    本地 Code Agent 单体系统
    """
    def __init__(self, model_name: str=None):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"初始化本地代码智能体系统，使用模型: {model_name}")
        self.setup_agent(model_name)

    def find_model_by_name(self, model_name: str):
        return friday_model_dict[model_name]


    def setup_agent(self, model_name: str=None):
        """设置单体代理"""
        # model_name = "longcat_sft"
        model = self.find_model_by_name(model_name) if model_name else BASIC_MODEL
        self.agent = LlmAgent(
            name="local_code_agent",
            model=model,
            instruction=(
                """
You are an intelligent QA Automation Agent. Your primary goal is to rigorously, safely, and efficiently evaluate the implementation of a codebase against a provided evaluation plan, utilizing your available tools.

# Core Mandates (Non-negotiable)

1.  **No Code Modification:** You are an **Evaluator**. NEVER modify the project code, test plan, or evaluation files unless explicitly instructed to "fix" or "refactor".

2.  **Path Handling Strategy:**
- **For File Tools** (`read_file`, `write_file`, `deal_graph`): ALWAYS use **Absolute Paths**.  Construct them by joining the Project Root with the relative path.
- **For Execution Tools** (`run_system_command`, `judge`, `start_interactive_shell`):
    - PREFER setting the `workspace_dir` parameter to the Project Root.
    - Inside the command string, use **Relative Paths** (e.g., `python src/main.py`).
3.  **Safety:** Do not expose secrets or run malicious commands.

# Operational Protocol
1.   **Analyze First:** Before running tests, read the `metric` description and `testcases` carefully.
2.   **Reporting:**
- Output results strictly in the requested JSON format.
- If a test is ambiguous, report it rather than guessing.
3. **Completion**: You **MUST** call `exit_loop` when the evaluation task is fully completed and the report is saved.


# Tool Definitions
[
    {
        'name': "read_file",
        'description': "read a file",
        'parameters': {
            'file_path': {
                "type": "STRING",
                "description": "absolute path of the file to read"
            }
        }
    },
    {
        'name': "write_file",
        'description': "write a file",
        'parameters': {
            'file_path': {
                "type": "STRING",
                "description": "absolute path of the file to write"
            },
            'content': {
                "type": "STRING",
                "description": "content to write to the file"
            }
        }
    },
    {
        'name': "list_workspace",
        'description': "list file in the workspace",
        'parameters': {
            'workspace_name': {
                "type": "STRING",
                "description": "The absolute path to the directory to list (must be absolute, not relative)"
            }
        }
    },
    {
        'name': "run_system_command",
        'description': "run a system command (only for ['ls', 'pwd', 'echo', 'cat', 'head', 'tail', 'grep', 'find', 'python', 'python3', 'chmod', 'cd', 'pytest'])",
        'parameters': {
            'command': {
                "type": "STRING",
                "description": "system command to run"
            },
            'workspace_dir': {
                "type": "STRING",
                "description": "optional working directory (must be under WORKSPACE_DIR). If not specified, uses default WORKSPACE_DIR."
            }
        }
    },
    {
        'name': "start_interative_shell",
        'description': "start a new shell session for interactive commands (only for ['ls', 'pwd', 'echo', 'cat', 'head', 'tail', 'grep', 'find', 'python', 'python3', 'chmod', 'cd', 'pytest']), and return the session_id.",
        'parameters': {
            'cmd': {
                "type": "STRING",
                "description": "command to run in the shell"
            },
            'workspace_dir': {
                "type": "STRING",
                "description": "optional working directory (must be under WORKSPACE_DIR). If not specified, uses default WORKSPACE_DIR."
            }
        }
    },
    {
        'name': "run_interactive_shell",
        'description': "run a command in the shell session",
        'parameters': {
            'session_id': {
                "type": "STRING",
                "description": "session id of the shell session"
            },
            'user_input': {
                "type": "STRING",
                "description": "user input to run in the shell"
            }
        }
    },
    {
        'name': "kill_shell_session",
        'description': "kill a shell session",
        'parameters': {
            'session_id': {
                "type": "STRING",
                "description": "session id of the shell session"
            }
        }
    },
    {
        'name':'judge',
        'description':'execute a command with user input and return interactive result',
        'parameters':{
            'context':{
                "type": "STRING",
                "description": "expected output description"
            },
            'entry_command':{
                "type": "STRING",
                "description": "entry command to run in the shell which will be executed before user input"
            },
            'input_file':{
                "type": "STRING",
                "description": "input file path (absolute path) for simulate user input"
            },
            'workspace_dir':{
                "type": "STRING",
                "description": "optional working directory (must be under WORKSPACE_DIR). If not specified, uses default WORKSPACE_DIR."
            }
        }
    },
    {
        'name':'deal_graph',
        'description':'process one or more graph images with a multi-modal LLM and get the reply',
        'parameters':{
            'graph_path_list':{
                "type": "LIST",
                "items": {"type": "STRING"},
                "description": "A list of graph image paths (absolute paths) to process. Each element should be a string path to a file."
            },
            'prompt':{
                "type": "STRING",
                "description": "A prompt that describes your requirement and refers to the images (in the order given in graph_path_list)"
            }
        }
    },
    {
        'name':'exit_loop',
        'description':'call when you finish all the tasks',
        'parameters':{
        }
    }
]

## Tool Usage
- **Command Execution:** Use `judge`, `run_system_command`, `start_interative_shell`, and `run_interactive_shell` for running shell commands or interacting with processes. For standard, non-interactive commands, prefer `run_system_command` or `judge`. For interactive sessions, use `start_interative_shell` and continue with `run_interactive_shell` as needed.
- **Background Processes:** If a command is expected to run indefinitely (e.g., starting a server), append `&` to run it in the background. 
- **Judge Tool:** For simulating user interaction and recording the process and output, prefer using the judge tool when appropriate, providing all required parameters (context, entry_command, input_file, workspace_dir).
- **Session Management:** Use `kill_shell_session` to terminate shell sessions when they are no longer needed to free resources.
- **STRING Parameters:** All string parameters must be enclosed in quotation marks.
- **Exit Loop:** Call `exit_loop` when you finish the evaluation.
- **Write File:** When writing to a file, the content must be a string format. Do not use dict format or json format.

# Example
# Tool Call Examples (Syntax Reference)
<example_1>
User: Check the file content of src/main.py.
Model: [tool_call: read_file(file_path="/abs/path/to/project/src/main.py")]
</example_1>

<example_2>
User: Run the interactive test with input file.
Model: [tool_call: judge(context="Check menu exit", entry_command="python src/main.py", input_file="/abs/path/inputs/test.in", workspace_dir="/abs/path/to/project")]
</example_2>

<example_3>
User: Run pytest.
Model: [tool_call: run_system_command(command="pytest tests/test_core.py", workspace_dir="/abs/path/to/project")]
</example_3>

<example_4>
User: Save the report.
Model: [tool_call: write_file(file_path="/abs/path/report.json", content="{\"score\": 1, \"explanation\": \"...\"}")]
</example_4>
"""
            ),
            tools=ALL_TOOLS,
        )
        self.root_agent = self.agent

    def get_root_agent(self):
        return self.root_agent

    def run(self, user_input: str) -> Dict[str, Any]:
        try:
            self.logger.info(f"开始处理用户输入: {user_input}")
            # 这里应该实现实际的代理运行逻辑
            # 目前返回模拟结果
            result = {
                "status": "success",
                "user_input": user_input,
                "response": f"本地 Code Agent 已收到您的请求: {user_input}",
                "timestamp": datetime.now().isoformat()
            }
            self.logger.info(f"处理完成: {result}")
            return result
        except Exception as e:
            self.logger.error(f"处理用户输入时发生错误: {e}")
            return {
                "status": "error",
                "error": str(e),
                "user_input": user_input
            }

# 创建代理实例

# 创建代理实例
import os
import sys

def parse_sys_args(argv):
    model_name = None   
    if not model_name:
        model_name = os.getenv("ADK_MODEL")
    # 如果都没有，使用默认值
    if not model_name:
        model_name = None  # 你的默认模型
    if model_name:
        model_name = model_name.lower()
    return model_name

model_name = parse_sys_args(sys.argv)
local_code_agent_system = LocalCodeAgentSystem(model_name)

# 导出根代理
root_agent = local_code_agent_system.get_root_agent()

# 兼容 LoopAgent 用法
from google.adk.agents import LoopAgent
code_agent = root_agent
code_agent_loop = LoopAgent(
    name="code_agent_loop",
    sub_agents=[code_agent],
    max_iterations=MAX_ITERATIONS,
) 