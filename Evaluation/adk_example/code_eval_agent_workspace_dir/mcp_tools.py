"""
本地 Code Agent MCP 工具定义
提供 Python 解释器、文件操作和系统操作功能
"""

import os
import sys
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
from code_eval_agent_workspace_dir.interative_shell import step, terminate
from datetime import datetime
import time
import json

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
SAFE_COMMANDS = ['rm', 'ls', 'pwd', 'echo', 'cat', 'head', 'tail', 'grep', 'find', 'python', 'python3', 'chmod', 'cd', 'pytest', 'kill']


def validate_workspace_dir(workspace_dir: str, base_dir: str = None) -> bool:
    """
    验证 workspace_dir 是否在 base_dir 下
    
    Args:
        workspace_dir: 要验证的工作目录路径
        base_dir: 基础目录路径，默认使用 WORKSPACE_DIR
        
    Returns:
        bool: 如果路径在 base_dir 下返回 True，否则返回 False
    """
    if base_dir is None:
        base_dir = WORKSPACE_DIR
    
    try:
        workspace_dir_resolved = Path(workspace_dir).resolve()
        base_dir_resolved = Path(base_dir).resolve()
        return str(workspace_dir_resolved).startswith(str(base_dir_resolved))
    except Exception as e:
        logger.warning(f"验证工作目录时出错: {e}")
        return False


def _get_venv_env(workspace_dir: str) -> Dict[str, str]:
    """
    获取包含虚拟环境配置的环境变量字典
    
    依次检查以下位置的虚拟环境：
    1. workspace_dir/venv (如果workspace_dir已经是项目目录)
    2. workspace_dir/CURRENT_EXECUTION_ID/venv (如果workspace_dir是基础工作目录)
    
    如果找到虚拟环境，将其 bin 目录添加到 PATH 前面
    
    Args:
        workspace_dir: 工作目录路径
        
    Returns:
        dict: 包含虚拟环境配置的环境变量字典
    """
    # 复制当前环境变量
    env = os.environ.copy()
    
    # 候选虚拟环境路径列表
    venv_candidates = [
        Path(workspace_dir) / "venv",  # 直接在工作目录下
        Path(workspace_dir) / CURRENT_EXECUTION_ID / "venv"  # 在子目录下
    ]
    
    logger.info(f"查找虚拟环境，workspace_dir: {workspace_dir}, CURRENT_EXECUTION_ID: {CURRENT_EXECUTION_ID}")
    
    # 依次检查每个候选路径
    for venv_path in venv_candidates:
        logger.info(f"检查虚拟环境路径: {venv_path}, 存在: {venv_path.exists()}")
        if venv_path.exists():
            venv_bin = venv_path / "bin"
            if venv_bin.exists():
                # 将虚拟环境的 bin 目录添加到 PATH 最前面
                current_path = env.get('PATH', '')
                env['PATH'] = f"{venv_bin}:{current_path}"
                env['VIRTUAL_ENV'] = str(venv_path)
                # 取消 PYTHONHOME（如果设置了），避免冲突
                env.pop('PYTHONHOME', None)
                logger.info(f"✅ 使用虚拟环境: {venv_path}")
                logger.info(f"   Python路径: {venv_bin / 'python'}")
                return env
    
    logger.warning(f"⚠️  未找到虚拟环境，将使用系统Python")
    return env


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
        # allowed_paths是根目录，允许的path列表为： {WORKSPACE_DIR}/*/reports
        # 允许 {WORKSPACE_DIR}/{任意文件夹}/reports 路径下写入
        # 只要file_path在WORKSPACE_DIR下，且目录中包含'reports'作为文件夹名就返回True
        try:
            file_path_resolved = Path(file_path).resolve()
            workspace_dir_resolved = Path(WORKSPACE_DIR).resolve()

            if str(file_path_resolved).startswith(str(workspace_dir_resolved)):
                # 判断路径中是否有"reports"这个目录名
                for parent in file_path_resolved.parents:
                    if parent.name == "reports" and str(parent).startswith(str(workspace_dir_resolved)):
                        return True
            return False
        except Exception as e:
            logger.warning(f"Error in validate_write_path: {e}")
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

def write_file(tool_context: ToolContext, file_path: str, content: Any):
    """
    Write the content to the file.
    
    Args:
        tool_context: Tool context
        file_path: The path of the file (required)
        content: The content (string to be written (required)
    
    Returns:
        dict: A dictionary containing the result of the operation.
    """
    if not (isinstance(content, str) or isinstance(content, dict)):
        logger.warning(f"The content must be a string or a dict! content: {content}")
        return {"error": f"The content must be a string or a dict! Now type: {type(content)}"}
    
    if not validate_write_path(file_path):
        logger.warning(f"file_path: {file_path} is not allowed to be modified")
        return {"error": "This file is not allowed to be modified! If the src code could not handle the case, you can give 0 as the result. You can not modify the code file and metric files."}
    
    try:
        if isinstance(content, dict):
            content = json.dumps(content)
         
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

def execute_python_code(tool_context: ToolContext, code: str, timeout: int = 30, use_venv: bool = True, workspace_dir: Optional[str] = None, use_current_env: bool = True):
    """
    Execute the Python code.
    
    Args:
        tool_context: Tool context
        code: The Python code to be executed (required)
        timeout: The timeout for the execution (seconds), default 30 seconds
        use_venv: Whether to try using virtual environment when use_current_env=False
        use_current_env: Whether to use current process's python/env (default True)
        workspace_dir: Optional working directory (must be under WORKSPACE_DIR). If not provided, uses default WORKSPACE_DIR.
    
    Returns:
        dict: A dictionary containing the result of the execution.
    """
    # 确定工作目录
    if workspace_dir:
        # 验证路径安全性
        if not validate_workspace_dir(workspace_dir):
            return {"error": f"工作目录 '{workspace_dir}' 不在允许的基础目录 '{WORKSPACE_DIR}' 下"}
        work_dir = workspace_dir
    else:
        work_dir = WORKSPACE_DIR
    
    try:
        # 确定使用的 Python 解释器
        if use_current_env:
            python_executable = sys.executable
            logger.info(f"execute_python_code 使用当前进程解释器: {python_executable}")
        elif use_venv:
            # 候选虚拟环境路径列表
            venv_candidates = [
                Path(work_dir) / "venv",  # 直接在工作目录下
                Path(work_dir) / CURRENT_EXECUTION_ID / "venv"  # 在子目录下
            ]
            
            python_executable = 'python'  # 默认使用系统 Python
            
            # 依次检查每个候选路径
            for venv_path in venv_candidates:
                if venv_path.exists():
                    if os.name == 'nt':  # Windows
                        python_exec = venv_path / "Scripts" / "python.exe"
                    else:  # Unix/Linux/macOS
                        python_exec = venv_path / "bin" / "python"
                    
                    if python_exec.exists():
                        python_executable = str(python_exec)
                        logger.info(f"execute_python_code 使用虚拟环境: {venv_path}")
                        break
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
            cwd=work_dir
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

def run_system_command(tool_context: ToolContext, command: str, timeout: int = 30, workspace_dir: Optional[str] = None):
    """
    Run the system command.
    
    Args:
        tool_context: Tool context
        command: The system command to be executed
        timeout: The timeout for the execution (seconds), default 30 seconds
        workspace_dir: Optional working directory (must be under WORKSPACE_DIR). If not provided, uses default WORKSPACE_DIR.
    
    Returns:
        dict: A dictionary containing the result of the execution.
    """
    # 确定工作目录
    if workspace_dir:
        # 验证路径安全性
        if not validate_workspace_dir(workspace_dir):
            return {"error": f"工作目录 '{workspace_dir}' 不在允许的基础目录 '{WORKSPACE_DIR}' 下"}
        session_workdir = workspace_dir
    else:
        session_workdir = WORKSPACE_DIR
    
    if SANDBOX_MODE:
        # 在沙盒模式下，只允许安全的命令
        safe_commands = SAFE_COMMANDS
        if not any(cmd in command for cmd in safe_commands):
            return {"error": "你执行的命令在沙盒模式下不被允许; 安全命令列表: " + str(safe_commands)}
        
    try:
        logger.info(f"执行系统命令: {command}, 工作目录: {session_workdir}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=session_workdir,  # 使用 session 工作目录
            env=os.environ.copy()  # 保持与启动时一致的环境
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "working_directory": session_workdir  # 返回使用的工作目录
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
        child = pexpect.spawn('bash', ['-c', command], cwd=WORKSPACE_DIR, timeout=timeout, encoding='utf-8', env=os.environ.copy())

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

def start_interative_shell(tool_context: ToolContext, cmd: Optional[str] = None, workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Start a interactive shell session.
    
    此工具仅用于启动新的交互式shell会话，不能执行命令。
    如果需要执行命令，请使用 run_interactive_shell 工具。
    
    Args:
        tool_context: Tool context
        cmd: 此参数不应提供。如果提供了cmd参数，将返回错误。
        workspace_dir: Optional working directory (must be under WORKSPACE_DIR). If not provided, uses default WORKSPACE_DIR.
    Returns:
        dict: A dictionary containing the result of the execution.
    """
    # 检查是否提供了cmd参数，如果提供了就报错
    if cmd is not None and cmd.strip() != "" and cmd.strip() != "bash":
        return {
            "error": f"start_interative_shell 工具只能启动新的shell会话，不能执行命令。检测到cmd参数: '{cmd}'。如需执行命令，请使用 run_interactive_shell 工具。",
            "session_id": None,
            "output": "",
            "waiting": False,
            "finished": True
        }
    
    # 确定工作目录
    if workspace_dir:
        # 验证路径安全性
        if not validate_workspace_dir(workspace_dir):
            return {
                "error": f"工作目录 '{workspace_dir}' 不在允许的基础目录 '{WORKSPACE_DIR}' 下",
                "session_id": None,
                "output": "",
                "waiting": False,
                "finished": True
            }
        session_workdir = workspace_dir
    else:
        session_workdir = WORKSPACE_DIR
    
    # 继承当前进程的环境，不做 PATH/VIRTUAL_ENV 改写
    env = os.environ.copy()
    
    session_id = None
    try:
        # 只启动bash shell，不执行任何命令
        result = step(
            cmd="bash",
            cwd=session_workdir,  # 传递工作目录到 shell
            env=env,  # 传递环境变量（与启动时一致）
            read_timeout=2.0  # 初始读取超时时间
        )
        
        session_id = result.get("session_id")
        
        # 返回session信息，不等待命令输出（因为只是启动shell，不执行命令）
        return {
            "session_id": session_id,
            "output": result.get("output", ""),
            "waiting": result.get("waiting", False),
            "finished": result.get("finished", False)
        }
    except Exception as e:
        return {
            "error": str(e),
            "session_id": session_id,
            "output": "",
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
        api_key = '2003426909183381528'
        api_base = 'https://aigc.sankuai.com/v1/openai/native'
        model_name = "gpt-4o-2024-11-20"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'uid': "Yi4TygCohR3TpCx7/PRhCQ=="
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
   
def judge(tool_context, context: str, entry_command: str, input_file: Optional[str] = None, workspace_dir: Optional[str] = None):
    """
    Run the program and simulate the user interaction, record the interaction process and output result.
    If the program does not exit automatically after the input ends, send Ctrl+C to force interrupt.
    When KeyboardInterrupt is captured, it is also considered successful.

    Args:
        tool_context: Tool context
        context: The expected output description and test requirements (only used for information transmission, not for judgment)
        entry_command: The entry command of the program (e.g. "python main.py")
        input_file: The path of the file containing the simulated user input (e.g. "a.in")
        workspace_dir: Optional working directory (must be under WORKSPACE_DIR). If not provided, uses default WORKSPACE_DIR.

    Returns:
        dict: A dictionary containing the test result, interaction record, and user inputs
            - success: bool, whether the program executed successfully
            - log: str, raw terminal output (program output + user input echo)
            - user_input: str, all user inputs separated by newlines
            - error: str or None, error message if any
    """
    import os
    import time
    import pexpect
    from typing import Optional

    class CustomLogger:
        """自定义日志记录器，直接写入原始内容，不添加前缀"""
        def __init__(self, file):
            self.file = file

        def write(self, data):
            # 直接写入原始数据，不添加 "program:" 前缀
            self.file.write(data)
            self.file.flush()

        def flush(self):
            self.file.flush()

    # 确定工作目录
    if workspace_dir:
        # 验证路径安全性
        if not validate_workspace_dir(workspace_dir):
            return {
                "success": False,
                "log": '',
                "user_input": '',
                "error": f"工作目录 '{workspace_dir}' 不在允许的基础目录 '{WORKSPACE_DIR}' 下"
            }
        work_dir = workspace_dir
    else:
        work_dir = WORKSPACE_DIR
    
    # 继承当前进程的环境，不改写 PATH/VIRTUAL_ENV
    env = os.environ.copy()
    
    log_file_path = 'pexpect_interact.log'
    result = {
        "success": False,
        "log": '',
        "user_input": '',
        "error": None
    }
    
    # 记录所有用户输入
    user_inputs = []

    if input_file and not os.path.exists(input_file):
        result["error"] = f"输入文件{input_file}不存在，请检查路径后重新调用。"
        return result

    input_lines = []
    if input_file and os.path.exists(input_file):
        with open(input_file, 'r', encoding='utf-8') as infile:
            input_lines = [line.rstrip('\n') for line in infile]
    
    # 检查并获取 conda 环境路径
    conda_env_path = None
    # 方法1: 优先使用启动脚本设置的 CONDA_ENV_PATH 环境变量
    if 'CONDA_ENV_PATH' in os.environ and os.environ['CONDA_ENV_PATH'].strip():
        conda_env_path = os.environ['CONDA_ENV_PATH'].strip()
    # 方法2: 检查 CONDA_PREFIX 环境变量（当前激活的 conda 环境）
    elif 'CONDA_PREFIX' in os.environ:
        conda_env_path = os.environ['CONDA_PREFIX']
    # 方法3: 检查 CONDA_DEFAULT_ENV 并尝试获取完整路径
    elif 'CONDA_DEFAULT_ENV' in os.environ:
        try:
            # 尝试通过 conda info 获取环境路径
            result = subprocess.run(
                ['conda', 'info', '--envs'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # 解析输出，查找当前环境
                env_name = os.environ['CONDA_DEFAULT_ENV']
                for line in result.stdout.split('\n'):
                    if line.strip().startswith(env_name) or f'/{env_name}' in line:
                        # 提取路径（通常在环境名之后）
                        parts = line.split()
                        if len(parts) >= 2:
                            conda_env_path = parts[-1]
                            break
        except Exception as e:
            logger.warning(f"获取 conda 环境信息时出错: {e}")
    
    # 如果检测不到 conda 环境，返回错误
    if not conda_env_path or conda_env_path.strip() == '':
        result["error"] = "无法检测到 conda 环境。请确保已激活 conda 环境或设置了 CONDA_ENV_PATH 环境变量。"
        return result
    
    entry_command = f"source activate {conda_env_path} && {entry_command}"

    child = pexpect.spawn('/bin/bash', ['-c', entry_command], cwd=work_dir, timeout=30, encoding='utf-8')
    with open(log_file_path, 'w', encoding='utf-8') as logfile:
        # 使用 logfile_read 只记录程序输出，用户输入由bash回显自动记录
        logger = CustomLogger(logfile)
        child.logfile_read = logger

        def wait_for_output(timeout=10, idle_threshold=1.0):
            """等待程序输出，确保输出被记录到日志中
            
            使用短超时循环非阻塞读取，快速响应有输出的情况，
            同时也能等待慢速输出（最多等待timeout秒）
            
            Args:
                timeout: 最大等待时间（秒）
                idle_threshold: 空闲多久后认为程序暂时停止输出（秒）
            """
            start_time = time.time()
            idle_time = 0
            while time.time() - start_time < timeout:
                try:
                    # 尝试非阻塞读取
                    data = child.read_nonblocking(size=1024, timeout=0.1)
                    print(f"data: {data}")
                    if data:
                        # 有数据，重置空闲时间
                        idle_time = 0
                        # 数据已经被logfile_read自动记录了
                    else:
                        # 没有数据，增加空闲时间
                        idle_time += 0.1
                        
                    # 如果空闲时间达到阈值，认为程序暂时不会再输出，提前返回
                    if idle_time >= idle_threshold:
                        break
                        
                except pexpect.TIMEOUT:
                    # 没有数据可读，增加空闲时间
                    idle_time += 0.1
                    if idle_time >= idle_threshold:
                        break
                    time.sleep(0.1)
                    
                except pexpect.EOF:
                    # 程序结束了
                    raise

        def send_user_line(line):
            # 先等待并读取程序的输出（等待提示符显示）
            # 使用较短的空闲超时（0.8秒），因为交互过程中响应较快
            try:
                wait_for_output(timeout=10, idle_threshold=0.8)
            except pexpect.EOF:
                # 程序意外结束
                raise
            
            # 记录用户输入（追加到user_inputs列表）
            user_inputs.append(line)
            
            # 发送用户输入
            child.sendline(line)
            
            # 立即短暂等待，读取输入的回显+程序的即时响应
            # 回显通常很快，使用0.5秒空闲超时
            time.sleep(0.05)  # 给一点时间让回显出现
            try:
                wait_for_output(timeout=2, idle_threshold=0.5)
            except pexpect.EOF:
                # 程序意外结束
                raise

        try:
            logfile.flush()
            
            # 在开始输入之前，先等待程序的初始输出
            # 程序启动时输出较慢，使用更长的空闲超时（2秒）
            try:
                wait_for_output(timeout=15, idle_threshold=10.0)
            except pexpect.EOF:
                # 程序在接收输入之前就结束了
                last_output = child.before if hasattr(child, 'before') else ''
                exit_status = child.exitstatus if hasattr(child, 'exitstatus') else None
                child.close()
                # 如果用户没有提供 input_file，这种情况可能只是“程序无需交互，直接执行结束”
                # 这时不应提示“但提供了输入文件”，并且应按退出码决定是否算成功
                if input_file:
                    result["success"] = False
                    result["error"] = (
                        "The program terminated before receiving any input, but an input file was provided. Please check whether the output contains the contents of the corresponding .in file. If not, assign a score of 0; if it does, score according to the output."
                        f"\n退出状态码: {exit_status}\n最后输出: {last_output}"
                    )
                else:
                    # 不提供输入文件时，程序提前结束不一定是失败（例如：无交互程序）
                    if exit_status == 0 or exit_status == 130 or 'keyboardInterrupt' in (last_output or ''):
                        result["success"] = True
                        result["error"] = None
                    else:
                        result["success"] = False
                        result["error"] = (
                            "程序在接收输入之前就已经结束。程序可能不需要输入或运行失败，请你根据输出做出打分。"
                            f"\n退出状态码: {exit_status}\n最后输出: {last_output}"
                        )
                with open(log_file_path, 'r', encoding='utf-8') as logfile_read:
                    result["log"] = logfile_read.read()
                result["user_input"] = '\n'.join(user_inputs)
                return result
            
            # 依次发送每一行输入
            for line in input_lines:
                send_user_line(line.rstrip('\n'))
                # send_user_line内部已经包含等待，不需要额外sleep

            # 所有输入发送完毕后，等待程序的最终输出和结束
            try:
                # 先等待最后的输出（限时10秒，空闲超时1秒）
                wait_for_output(timeout=10, idle_threshold=1.0)
                # 然后等待程序结束
                child.expect(pexpect.EOF, timeout=10)
            except pexpect.TIMEOUT:
                # 程序在输入结束后仍然没有结束，发送Ctrl+C
                # 先再等待一下输出
                try:
                    wait_for_output(timeout=0.5, idle_threshold=0.5)
                except:
                    pass
                
                # 记录Ctrl+C到user_inputs
                user_inputs.append('<Ctrl+C>')
                
                # 发送Ctrl+C（terminal会自动显示^C，不需要手动写入）
                child.sendcontrol('c')
                
                # 等待Ctrl+C后的输出
                try:
                    wait_for_output(timeout=1, idle_threshold=0.5)
                except:
                    pass
                
                try:
                    child.expect(pexpect.EOF, timeout=3)
                except pexpect.TIMEOUT:
                    child.close(force=True)
                    result["error"] = "程序未正常结束，已发送 Ctrl+C 强制中断。这不代表程序运行成功/失败，请根据日志做额外的打分判断。"
            child.close()

            last_output = child.before if hasattr(child, 'before') else ''
            if child.exitstatus == 0 or child.exitstatus==130 or 'keyboardInterrupt' in last_output:
                result["success"] = True
            else:
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

    with open(log_file_path, 'r', encoding='utf-8') as logfile:
        result["log"] = logfile.read()
    
    # 将用户输入列表转换为字符串，每行一个输入
    result["user_input"] = '\n'.join(user_inputs)
    
    return result



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

