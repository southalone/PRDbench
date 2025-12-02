"""
本地 Code Agent MCP 工具定义
提供 Python 解释器、文件操作和系统操作功能
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from google.adk.tools import ToolContext
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from pydantic import BaseModel
import logging
import pexpect
import asyncio
from aiohttp import web
from typing import Dict, Any, Optional
from code_agent_local.interative_shell import step, terminate
from datetime import datetime
import time

logger = logging.getLogger(__name__)

# 修复相对导入
try:
    from .config import (
        PYTHON_INTERPRETER_MCP_URL, 
        FILE_OPERATIONS_MCP_URL, 
        SYSTEM_OPERATIONS_MCP_URL,
        MCP_SSE_TIMEOUT,
        WORKSPACE_DIR,
        ALLOWED_EXTENSIONS,
        MAX_FILE_SIZE,
        SANDBOX_MODE,
        CURRENT_EXECUTION_ID,
        ENABLE_PATH_RESTRICTION
    )
except ImportError:
    # 如果相对导入失败，使用绝对导入
    from config import (
        PYTHON_INTERPRETER_MCP_URL, 
        FILE_OPERATIONS_MCP_URL, 
        SYSTEM_OPERATIONS_MCP_URL,
        MCP_SSE_TIMEOUT,
        WORKSPACE_DIR,
        ALLOWED_EXTENSIONS,
        MAX_FILE_SIZE,
        SANDBOX_MODE,
        CURRENT_EXECUTION_ID,
        ENABLE_PATH_RESTRICTION
    )
SAFE_COMMANDS = ['ls', 'pwd', 'echo', 'cat', 'head', 'tail', 'grep', 'find', 'python', 'python3', 'chmod', 'cd', 'pytest']
        
# 数据模型定义
class PythonCode(BaseModel):
    """Python代码执行请求"""
    code: str
    timeout: int = 30
    capture_output: bool = True

class FileOperation(BaseModel):
    """文件操作请求"""
    operation: str  # read, write, delete, list, copy, move
    path: str
    content: Optional[str] = None
    destination: Optional[str] = None

class SystemCommand(BaseModel):
    """系统命令执行请求"""
    command: str
    timeout: int = 30
    capture_output: bool = True
    working_directory: Optional[str] = None

# 基础工具函数
def exit_loop(tool_context: ToolContext):
    """当任务完成时退出循环"""
    tool_context.actions.escalate = True
    return {"status": "completed"}

def create_workspace(tool_context: ToolContext, workspace_name: Optional[str] = None, create_venv: bool = True):
    """
    创建工作空间
    
    Args:
        tool_context: 工具上下文
        workspace_name: 工作空间名称，如果为None则使用当前执行ID
        create_venv: 是否创建虚拟环境，默认True
    
    Returns:
        dict: 包含工作空间信息的字典
    """
    if workspace_name is None:
        workspace_name = CURRENT_EXECUTION_ID
    
    workspace_path = Path(WORKSPACE_DIR) / workspace_name
    workspace_path.mkdir(parents=True, exist_ok=True)
    
    # 创建基础目录结构
    (workspace_path / "src").mkdir(exist_ok=True)
    (workspace_path / "tests").mkdir(exist_ok=True)
    (workspace_path / "data").mkdir(exist_ok=True)
    (workspace_path / "docs").mkdir(exist_ok=True)
    
    result = {
        "workspace_path": str(workspace_path),
        "workspace_name": workspace_name,
        "status": "created",
        "directories": ["src", "tests", "data", "docs"]
    }
    
    # 创建虚拟环境
    if create_venv:
        try:
            venv_path = workspace_path / "venv"
            
            # 创建虚拟环境
            subprocess.run(
                ['python', '-m', 'venv', str(venv_path)],
                check=True,
                capture_output=True,
                text=True
            )
            
            # 生成激活脚本
            activate_script = workspace_path / "activate_venv.sh"
            with open(activate_script, 'w', encoding='utf-8') as f:
                f.write(f"""#!/bin/bash
# 激活虚拟环境脚本
echo "激活虚拟环境: {venv_path}"
source "{venv_path}/bin/activate"
echo "虚拟环境已激活，Python路径: $(which python)"
echo "当前工作目录: $(pwd)"
""")
            
            # 设置脚本可执行权限
            os.chmod(activate_script, 0o755)
            
            # 创建 requirements.txt 模板
            requirements_file = workspace_path / "requirements.txt"
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write("# 项目依赖包\n# 示例：\n# requests==2.31.0\n# pandas==2.0.3\n")
            
            # 创建 .gitignore 文件
            gitignore_file = workspace_path / ".gitignore"
            with open(gitignore_file, 'w', encoding='utf-8') as f:
                f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Data files
data/*.csv
data/*.json
""")
            
            result.update({
                "venv_created": True,
                "venv_path": str(venv_path),
                "activate_script": str(activate_script),
                "requirements_file": str(requirements_file),
                "gitignore_file": str(gitignore_file)
            })
            
            logger.info(f"虚拟环境创建成功: {venv_path}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"创建虚拟环境失败: {e}")
            result.update({
                "venv_created": False,
                "venv_error": str(e)
            })
        except Exception as e:
            logger.error(f"创建虚拟环境时发生错误: {e}")
            result.update({
                "venv_created": False,
                "venv_error": str(e)
            })
    else:
        result["venv_created"] = False
    
    return result

def list_workspace(tool_context: ToolContext, workspace_name: Optional[str] = None):
    """
    List the files and directories in the workspace.
    
    Args:
        tool_context: Tool context
        workspace_name: The name of the workspace, if None, use the current execution ID.
    
    Returns:
        dict: A dictionary containing the list of files and directories in the workspace.
    """
    if workspace_name is None:
        workspace_name = CURRENT_EXECUTION_ID
    
    workspace_path = Path(WORKSPACE_DIR) / workspace_name
    
    if not workspace_path.exists():
        return {"error": "The workspace does not exist！"}
    
    files = []
    for item in workspace_path.rglob("*"):
        if item.is_file():
            files.append({
                "path": str(item.relative_to(workspace_path)),
                "size": item.stat().st_size,
                "type": "file"
            })
        elif item.is_dir():
            files.append({
                "path": str(item.relative_to(workspace_path)),
                "type": "directory"
            })
    
    return {
        "workspace_path": str(workspace_path),
        "workspace_name": workspace_name,
        "files": files
    }

def validate_write_path(file_path: str) -> bool:
    """验证文件路径是否安全"""
    
    if ENABLE_PATH_RESTRICTION:
        # allowed_paths是根目录，允许的path列表为： {WORKSPACE_DIR}/{数字}/reports
        allowed_paths = [os.path.join(WORKSPACE_DIR, str(i), 'reports') for i in range(1, 51)]
        logger.warning(f"checking write path: {file_path}, allowed_paths: {WORKSPACE_DIR}/*/reports")
        if any(os.path.commonpath([file_path, allowed_path]) == allowed_path for allowed_path in allowed_paths):
            return True
        else:
            return False
    else:
        return True


def validate_read_file_path(file_path: str) -> bool:
    """验证文件路径是否安全"""
    logger.warning(f"checking read path: {file_path}, allowed_paths: {WORKSPACE_DIR}")
    # tmp 目录不进行安全检查
    if file_path.startswith("/tmp"):
        return True
    
    # 允许当前目录及其子目录的相对路径
    if not file_path.startswith("/"):
        return True
    
    if SANDBOX_MODE:
        # 在沙盒模式下，只允许访问工作空间内的文件
        workspace_path = Path(WORKSPACE_DIR).resolve()
        file_path_resolved = Path(file_path).resolve()
        
        # 检查是否在工作空间内或tmp目录内
        if (str(file_path_resolved).startswith(str(workspace_path)) or 
            str(file_path_resolved).startswith("/tmp")):
            return True
        else:
            return False
    
    return True

def read_file(tool_context: ToolContext, file_path: str):
    """
    Read the content of the file.
    
    Args:
        tool_context: Tool context
        file_path: The path of the file.
    
    Returns:
        dict: A dictionary containing the content of the file.
    """
    if not validate_read_file_path(file_path):
        return {"error": "The file path is not allowed to be read! Please concentrate on the file path in the project directory!"}
    
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return {"error": "文件不存在"}
        
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return {"error": "文件过大"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "file_path": str(file_path),
            "content": content,
            "size": len(content)
        }
    except Exception as e:
        return {"error": f"读取文件失败: {str(e)}"}

def write_file(tool_context: ToolContext, file_path: str, content: str):
    """
    Write the content to the file.
    
    Args:
        tool_context: Tool context
        file_path: The path of the file (required)
        content: The content to be written (required)
    
    Returns:
        dict: A dictionary containing the result of the operation.
    """
    if not validate_write_path(file_path):
        logger.warning(f"file_path: {file_path} is not allowed to be modified")
        return {"error": "This file is not allowed to be modified! If the src code could not handle the case, you can give 0 as the result. You can not modify the code file and metric files."}
    
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "file_path": str(file_path),
            "status": "written",
            "size": len(content)
        }
    except Exception as e:
        return {"error": f"写入文件失败: {str(e)}"}

def delete_file(tool_context: ToolContext, file_path: str):
    """
    Delete the file.
    
    Args:
        tool_context: Tool context
        file_path: The path of the file.
    
    Returns:
        dict: A dictionary containing the result of the operation.
    """
    if not validate_write_path(file_path):
        return {"error": "This file is not allowed to be deleted! You can not delete the code file and metric files."}
    
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return {"error": "文件不存在"}
        
        file_path.unlink()
        return {
            "file_path": str(file_path),
            "status": "deleted"
        }
    except Exception as e:
        return {"error": f"删除文件失败: {str(e)}"}

def activate_venv(tool_context: ToolContext, workspace_name: Optional[str] = None):
    """
    Activate the virtual environment of the workspace.
    
    Args:
        tool_context: Tool context
        workspace_name: The name of the workspace, if None, use the current execution ID.
    
    Returns:
        dict: A dictionary containing the result of the activation.
    """
    if workspace_name is None:
        workspace_name = CURRENT_EXECUTION_ID
    
    workspace_path = Path(WORKSPACE_DIR) / workspace_name
    venv_path = workspace_path / "venv"
    
    if not venv_path.exists():
        return {"error": "虚拟环境不存在，请先创建虚拟环境"}
    
    try:
        # 获取虚拟环境的 Python 解释器路径
        if os.name == 'nt':  # Windows
            python_path = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            python_path = venv_path / "bin" / "python"
        
        if not python_path.exists():
            return {"error": "虚拟环境 Python 解释器不存在"}
        
        # 检查虚拟环境中的包
        result = subprocess.run(
            [str(python_path), '-m', 'pip', 'list'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "workspace_name": workspace_name,
            "venv_path": str(venv_path),
            "python_path": str(python_path),
            "status": "activated",
            "installed_packages": result.stdout if result.returncode == 0 else "无法获取包列表"
        }
        
    except Exception as e:
        return {"error": f"激活虚拟环境失败: {str(e)}"}

def execute_python_code(tool_context: ToolContext, code: str, timeout: int = 30, use_venv: bool = True):
    """
    Execute the Python code.
    
    Args:
        tool_context: Tool context
        code: The Python code to be executed (required)
        timeout: The timeout for the execution (seconds), default 30 seconds
        use_venv: Whether to use the virtual environment, default True
    
    Returns:
        dict: A dictionary containing the result of the execution.
    """
    try:
        # 确定使用的 Python 解释器
        if use_venv:
            workspace_path = Path(WORKSPACE_DIR) / CURRENT_EXECUTION_ID
            venv_path = workspace_path / "venv"
            
            if venv_path.exists():
                if os.name == 'nt':  # Windows
                    python_executable = str(venv_path / "Scripts" / "python.exe")
                else:  # Unix/Linux/macOS
                    python_executable = str(venv_path / "bin" / "python")
                
                if not Path(python_executable).exists():
                    python_executable = 'python'  # 回退到系统 Python
            else:
                python_executable = 'python'  # 回退到系统 Python
        else:
            python_executable = 'python'
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # 执行代码
        result = subprocess.run(
            [python_executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=WORKSPACE_DIR
        )
        
        # 清理临时文件
        os.unlink(temp_file)
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "execution_time": "completed",
            "python_executable": python_executable,
            "used_venv": use_venv and venv_path.exists() if use_venv else False
        }
    except subprocess.TimeoutExpired:
        return {"error": "代码执行超时"}
    except Exception as e:
        return {"error": f"代码执行失败: {str(e)}"}

def run_system_command(tool_context: ToolContext, command: str, timeout: int = 30):
    """
    Run the system command.
    
    Args:
        tool_context: Tool context
        command: The system command to be executed
        timeout: The timeout for the execution (seconds), default 30 seconds
    
    Returns:
        dict: A dictionary containing the result of the execution.
    """
    if SANDBOX_MODE:
        # 在沙盒模式下，只允许安全的命令
        safe_commands = SAFE_COMMANDS
        if not any(cmd in command for cmd in safe_commands):
            return {"error": "你执行的命令在沙盒模式下不被允许; 安全命令列表: " + str(safe_commands)}
    try:
        logger.info(f"执行系统命令: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=WORKSPACE_DIR
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "命令执行超时"}
    except Exception as e:
        return {"error": f"命令执行失败: {str(e)}"}

def interactive_system_command(
    tool_context: ToolContext,
    command: str,
    inputs: Optional[List[str]] = None,
    timeout: int = 15
):
    """
    Run the system command interactively, support input and output interaction.

    Args:
        tool_context: Tool context
        command: The system command to be executed
        inputs: The content to be input to the command (string list, each element enter once)
        timeout: The timeout for the execution (seconds)

    Returns:
        dict: A dictionary containing the result of the execution.
    """
    if SANDBOX_MODE:
        safe_commands = SAFE_COMMANDS
        if not any(cmd in command for cmd in safe_commands):
            return {"error": "命令在沙盒模式下不被允许"}

    try:
        logger.info(f"交互式执行系统命令: {command}")
        child = pexpect.spawn(command, cwd=WORKSPACE_DIR, timeout=timeout, encoding='utf-8')
        output = ""
        if inputs:
            for inp in inputs:
                child.expect([pexpect.TIMEOUT, pexpect.EOF], timeout=1)
                child.sendline(inp)
        child.expect(pexpect.EOF)
        output = child.before
        return_code = child.exitstatus
        return {
            "stdout": output,
            "stderr": "",  # pexpect不直接区分stderr
            "return_code": return_code
        }
    except pexpect.TIMEOUT:
        return {"error": "命令执行超时"}
    except Exception as e:
        return {"error": f"交互式命令执行失败: {str(e)}"}

def run_interactive_python_code(tool_context: ToolContext, cmd: str, session_id: Optional[str] = None, timeout: int = 30):
    """
    Run a interactive Python code session.
    
    The first time to call, you need to provide the code parameter to start a new session, and then provide the session_id to continue the previous session.
    If you need to input content to the Python code, provide the user_input parameter.
    
    Args:
        tool_context: Tool context
        cmd: The Python code to be executed
        session_id: The session ID, for continuing the previous session.
        timeout: The timeout for the execution (seconds)
    Returns:
        dict: A dictionary containing the result of the execution.
    """
    session_id = None
    try:
        result = step(
            cmd=cmd,
            session_id=session_id,
            user_input=user_input
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "session_id": session_id,
            "output": "",
            "waiting": False,
            "finished": True
        }

def start_interative_shell(tool_context: ToolContext, cmd: str = "bash") -> Dict[str, Any]:
    """
    Start a interactive shell session.
    
    Args:
        tool_context: Tool context
        cmd: The shell command to be executed
    Returns:
        dict: A dictionary containing the result of the execution.
    """
    session_id = None
    try:
        result = step(
            cmd=cmd,
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "session_id": session_id,
            "output": session_id,
            "waiting": False,
            "finished": True
        }

IS_IN_PYTHON_ENV = False

def run_interactive_shell(tool_context: ToolContext, session_id: Optional[str] = None, user_input: Optional[str] = None) -> Dict[str, Any]:
    """
    Run a interactive shell session.
    
    The first time to call, you need to provide the cmd parameter to start a new session, and then provide the session_id to continue the previous session.
    If you need to input content to the shell, provide the user_input parameter.
    
    参数:
        session_id (str, optional): The session ID, for continuing the previous session.
        user_input (str, optional): The content to be input to the shell.
        
    Returns:
        Dict[str, Any]: A dictionary containing the result of the execution.
            - session_id: str, The session ID
            - output: str, The output of the shell
            - waiting: bool, Whether to wait for input
            - finished: bool, Whether the session is finished
    """
    # 获取当前会话的状态
    session_state = getattr(tool_context, 'python_env_state', {})
    if session_id not in session_state:
        session_state[session_id] = False
    is_in_python = session_state[session_id]
    
    # 检查命令安全性
    if is_in_python and user_input:
        safe_commands = SAFE_COMMANDS
        current_command = user_input.split()[0] if user_input else ''
        if not any(cmd in current_command for cmd in safe_commands):
            return {"error": "你执行的命令在沙盒模式下不被允许; 安全命令列表: " + str(safe_commands)}
    
    # 更新Python环境状态
    if user_input and user_input.startswith("python"):
        session_state[session_id] = True
    elif user_input == "exit":
        session_state[session_id] = False
    
    # 保存状态回上下文
    setattr(tool_context, 'python_env_state', session_state)
    
    try:
        result = step(
            session_id=session_id,
            user_input=user_input
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "session_id": session_id,
            "output": "",
            "waiting": False,
            "finished": True
        }

def kill_shell_session(tool_context: ToolContext, session_id: str) -> Dict[str, Any]:
    """
    Terminate a shell session.
    
    参数:
        session_id (str): The session ID to be terminated
        
    返回:
        Dict[str, Any]: The result of the operation
    """
    try:
        terminate(session_id)
        return {
            "message": f"Session {session_id} has been terminated",
            "output": f"Session {session_id} has been terminated"
        }
    except Exception as e:
        return {
            "error": str(e),
            "output": "",
        }

def deal_graph(tool_context: ToolContext, graph_path_list: list, prompt: str):
    """
    Interact with the multi-modal LLM and get the reply.
    
    Args:
        graph_path_list(list): The list of image file paths
        prompt(str): The prompt of the user, need to describe the requirement in detail, and describe the pictures in the order of the image file path list (for example, whether the first picture is consistent with the type of the second picture)
    
    Returns:
        dict: The reply content of the model
    """
    for graph_path in graph_path_list:
        if not validate_read_file_path(graph_path):
            return {"error": "该文件不允许被读取！"}
    try:
        import base64
        import requests
        import json
        import os
        
        # API配置
        api_key = '1873999896563486807'
        api_base = 'https://aigc.sankuai.com/v1/openai/native'
        model_name = "gpt-4o-2024-11-20"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        url = f'{api_base}/chat/completions'
        
        def encode_image(image_path):
            """将图像文件编码为base64字符串"""
            try:
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
            except Exception as e:
                return {"error": f"编码图像失败 {image_path}: {e}"}

        
        # 构建消息内容
        content = [{"type": "text", "text": prompt}]
        
        # 处理图像列表
        for graph_path in graph_path_list:
            if not os.path.exists(graph_path):
                return {"error": f"图像文件不存在: {graph_path}"}

                
            # 编码图像
            base64_image = encode_image(graph_path)
            if base64_image is None:
                continue
                
            # 获取文件扩展名来确定MIME类型
            file_ext = os.path.splitext(graph_path)[1].lower()
            mime_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg', 
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_type_map.get(file_ext, 'image/jpeg')
            
            # 添加图像到内容中
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}"
                }
            })
        
        # 构建请求数据
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.1
        }
        
        try:

            # 发送请求
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    reply_content = result['choices'][0]['message']['content']
                    return {"MLLM_reply_content": reply_content}
                else:
                    return {"error": "API response format exception"}
            else:
                error_info = response.text
                return {"error": f"API请求失败: {response.status_code} - {error_info}"}
                
        except requests.exceptions.Timeout:
            return {"error": "请求超时"}
        except requests.exceptions.RequestException as e:
            return {"error": f"请求异常: {e}"}
        except Exception as e:
            return {"error": f"未知错误: {e}"}
    except Exception as e:
        return {"error": "图片解析失败"}
   
def judge(tool_context, context: str, entry_command: str, input_file: Optional[str] = None):
    """
    Run the program and simulate the user interaction, record the interaction process and output result.
    If the program does not exit automatically after the input ends, send Ctrl+C to force interrupt.
    When KeyboardInterrupt is captured, it is also considered successful.

    Args:
        tool_context: Tool context
        context: The expected output description and test requirements (only used for information transmission, not for judgment)
        entry_command: The entry command of the program (e.g. "python main.py")
        input_file: The path of the file containing the simulated user input (e.g. "a.in")

    Returns:
        dict: A dictionary containing the test result and interaction record
    """
    import os
    import time
    import pexpect
    from typing import Optional

    class CustomLogger:
        def __init__(self, file):
            self.file = file

        def write(self, data):
            for line in data.splitlines(True):
                self.file.write("program: " + line)
            self.file.flush()

        def flush(self):
            self.file.flush()

    log_file_path = 'pexpect_interact.log'
    result = {
        "success": False,
        "log": '',
        "error": None
    }
    work_dir = WORKSPACE_DIR

    if input_file and not os.path.exists(input_file):
        result["error"] = f"输入文件{input_file}不存在，请检查路径后重新调用。"
        return result

    input_lines = []
    if input_file and os.path.exists(input_file):
        with open(input_file, 'r', encoding='utf-8') as infile:
            input_lines = [line.rstrip('\n') for line in infile]

    child = pexpect.spawn(entry_command, cwd=work_dir, timeout=30, encoding='utf-8')

    with open(log_file_path, 'w', encoding='utf-8') as logfile:
        logger = CustomLogger(logfile)
        child.logfile_read = logger

        def send_user_line(line):
            logfile.write('user: ' + line + '\n')
            logfile.flush()
            child.sendline(line)

        try:
            logfile.flush()
            time.sleep(0.2)
            for line in input_lines:
                send_user_line(line.rstrip('\n'))
                time.sleep(0.2)

            try:
                child.expect(pexpect.EOF, timeout=10)
            except pexpect.TIMEOUT:
                logfile.write('user: <Ctrl+C>\n')
                logfile.flush()
                child.sendcontrol('c')
                try:
                    child.expect(pexpect.EOF, timeout=3)
                except pexpect.TIMEOUT:
                    child.close(force=True)
                    result["error"] = "程序未正常结束，已发送 Ctrl+C 强制中断。"

            child.close()

            if child.exitstatus == 0 or child.exitstatus==130 or 'keyboardInterrupt' in last_output:
                result["success"] = True
            else:
                last_output = child.before if hasattr(child, 'before') else ''
                if not result["error"]:
                    result["error"] = f"程序退出状态码: {child.exitstatus}\n最后输出: {last_output}"

        except pexpect.TIMEOUT:
            result["error"] = f"程序执行超时"
        except Exception as e:
            import traceback
            print(Exception)
            tb_lines = traceback.format_exc()
            if isinstance(e, KeyboardInterrupt):
                result["success"] = True
                result["error"] = None
            #result["error"] = tb_lines

    with open(log_file_path, 'r', encoding='utf-8') as logfile:
        result["log"] = logfile.read()
    return result



# 工具定义
TOOL_DEFINITIONS = {
    "run_interactive_shell": {
        "name": "run_interactive_shell",
        "description": """
        运行一个交互式shell会话。这个工具允许模型与shell进行交互式对话。
        
        使用方法：
        1. 首次使用时，提供cmd参数来启动新的shell会话
        2. 获取返回的session_id，用于后续交互
        3. 如果shell在等待输入(waiting=True)，可以通过提供user_input来发送输入
        4. 使用返回的session_id继续与同一个shell会话交互
        5. 当finished=True时，会话结束
        
        示例：
        - 启动新会话：run_interactive_shell(cmd="python")
        - 继续会话：run_interactive_shell(session_id="xxx", user_input="print('hello')")
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "cmd": {
                    "type": "string",
                    "description": "要执行的shell命令，仅在首次调用时需要"
                },
                "session_id": {
                    "type": "string",
                    "description": "会话ID，用于继续之前的会话"
                },
                "user_input": {
                    "type": "string",
                    "description": "要发送到shell的输入内容"
                }
            }
        }
    },
    "kill_shell_session": {
        "name": "kill_shell_session",
        "description": "强制终止一个正在运行的shell会话",
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
    },
    'judge': {
        'name': 'judge',
        'description': '运行程序并模拟用户交互，记录交互过程和输出结果',
        'parameters': {
            'type': 'object',
            'properties': {
                'context': {
                    'type': 'string',
                    'description': '预期输出描述和测试要求'
                },
                'entry_command': {
                    'type': 'string',
                    'description': '程序入口命令'
                },
                'input_file': {
                    'type': 'string',
                    'description': '包含模拟用户输入的文件路径'
                }
            },
            'required': ['context', 'entry_command']
        }
    }
}

# 创建MCP工具集
def create_python_interpreter_toolset():
    """创建Python解释器MCP工具集"""
    return MCPToolset(
        connection_params=SseServerParams(
            url=PYTHON_INTERPRETER_MCP_URL,
            sse_read_timeout=MCP_SSE_TIMEOUT
        )
    )

def create_file_operations_toolset():
    """创建文件操作MCP工具集"""
    return MCPToolset(
        connection_params=SseServerParams(
            url=FILE_OPERATIONS_MCP_URL,
            sse_read_timeout=MCP_SSE_TIMEOUT
        )
    )

def create_system_operations_toolset():
    """创建系统操作MCP工具集"""
    return MCPToolset(
        connection_params=SseServerParams(
            url=SYSTEM_OPERATIONS_MCP_URL,
            sse_read_timeout=MCP_SSE_TIMEOUT
        )
    )


# def create_meituan_search_toolset():
#     return MCPToolset(
#             connection_params=SseServerParams(
#                 url='http://mcphub-server.sankuai.com/mcphub-api/6025f6404b9640',
#                 sse_read_timeout=30
#             )
#         )

# def create_meituan_browse_toolset():    
#     return MCPToolset(
#             connection_params=SseServerParams(
#                 url='http://mcphub-server.sankuai.com/mcphub-api/913526fb42f543',
#                 sse_read_timeout=30
#             )
#         )


# meituan_search = create_meituan_search_toolset()
# meituan_browse = create_meituan_browse_toolset()

# 基础工具列表 - 移除重复，确保每个工具只出现一次
BASIC_TOOLS = [
    exit_loop,
    create_workspace,
    list_workspace,
    read_file,
    write_file,
    delete_file,
    activate_venv,
    execute_python_code,
    run_system_command,
    interactive_system_command,
    run_interactive_shell,
    # meituan_search,
    # meituan_browse,
    judge,  # 添加Judge工具
    deal_graph
    # interactive_python_code,
]

# MCP工具集 - 暂时注释掉，避免工具重复问题
# MCP_TOOLS = [
#     create_python_interpreter_toolset(),
#     create_file_operations_toolset(),
#     create_system_operations_toolset()
# ]

# 所有工具 - 暂时只使用基础工具
ALL_TOOLS = BASIC_TOOLS 

