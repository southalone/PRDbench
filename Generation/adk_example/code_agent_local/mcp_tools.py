"""
本地 Code Agent MCP 工具定义
提供 Python 解释器、文件操作和系统操作功能
"""

# JSON错误修复补丁
import json
import logging

logger_patch = logging.getLogger(__name__)

def _safe_json_loads(json_str: str, fallback_value: dict = None) -> dict:
    """安全的JSON解析，自动修复常见格式错误"""
    if fallback_value is None:
        fallback_value = {}
    
    if not json_str or json_str.strip() == "":
        return fallback_value
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger_patch.warning(f"JSON解析错误，尝试修复: {e}")
        
        # 尝试修复常见问题
        fixed_attempts = [
            _fix_unterminated_string(json_str),
            _fix_trailing_comma(json_str),
            _extract_partial_json(json_str),
        ]
        
        for fixed_json in fixed_attempts:
            if fixed_json:
                try:
                    result = json.loads(fixed_json)
                    logger_patch.info(f"JSON修复成功")
                    return result
                except json.JSONDecodeError:
                    continue
        
        logger_patch.error(f"JSON修复失败，使用默认值")
        return fallback_value

def _fix_unterminated_string(json_str: str) -> str:
    """修复未闭合的字符串"""
    try:
        if json_str.count('"') % 2 == 1:  # 奇数个引号
            return json_str + '"}'
    except Exception:
        pass
    return None

def _fix_trailing_comma(json_str: str) -> str:
    """修复尾随逗号"""
    try:
        import re
        fixed = re.sub(r',\s*}', '}', json_str)
        fixed = re.sub(r',\s*]', ']', fixed)
        return fixed
    except Exception:
        pass
    return None

def _extract_partial_json(json_str: str) -> str:
    """提取部分有效的JSON"""
    try:
        start = json_str.find('{')
        if start == -1:
            return None
        
        brace_count = 0
        for i, char in enumerate(json_str[start:], start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return json_str[start:i+1]
        
        if brace_count > 0:
            return json_str[start:] + '}' * brace_count
    except Exception:
        pass
    return None

# 应用JSON修复补丁
def apply_json_fix():
    """应用JSON错误修复补丁到LiteLLM"""
    try:
        import google.adk.models.lite_llm as lite_llm_module
        
        # 保存原始函数
        original_function = lite_llm_module._message_to_generate_content_response
        
        # NOTE:
        # - LiteLLM/ADK 在不同版本里可能会给该函数新增关键字参数（例如 model_version）。
        # - 新版本里 original_function 可能只接受 1 个位置参数（message），其余参数为 keyword-only。
        #   因此这里必须用关键字方式透传 is_partial，避免 “takes 1 positional argument but 2 ... were given”。
        def patched_function(message, is_partial: bool = False, *args, **kwargs):
            try:
                # 保持最大兼容：忽略额外位置参数，仅透传关键字参数
                if "is_partial" in kwargs:
                    is_partial = kwargs.pop("is_partial")
                return original_function(message, is_partial=is_partial, **kwargs)
            except json.JSONDecodeError as e:
                logger_patch.warning(f"检测到JSON错误，使用修复版本: {e}")
                
                # 修复版本的响应生成
                from google.genai import types
                from google.adk.models.llm_response import LlmResponse
                
                parts = []
                if message.get("content", None):
                    parts.append(types.Part.from_text(text=message.get("content")))

                if message.get("tool_calls", None):
                    for tool_call in message.get("tool_calls"):
                        if tool_call.type == "function":
                            try:
                                # 使用安全的JSON解析
                                args = _safe_json_loads(tool_call.function.arguments or "{}")
                                part = types.Part.from_function_call(
                                    name=tool_call.function.name,
                                    args=args,
                                )
                                part.function_call.id = tool_call.id
                                parts.append(part)
                            except Exception as func_error:
                                logger_patch.error(f"函数调用创建失败: {func_error}")
                                # 添加错误信息作为文本
                                error_text = f"[函数调用错误: {tool_call.function.name}]"
                                parts.append(types.Part.from_text(text=error_text))

                return LlmResponse(
                    content=types.Content(role="model", parts=parts), 
                    partial=is_partial
                )
        
        # 应用补丁
        lite_llm_module._message_to_generate_content_response = patched_function
        logger_patch.info("✅ JSON错误修复补丁已应用")
        
    except Exception as e:
        logger_patch.warning(f"JSON修复补丁应用失败: {e}")

# 启动时应用补丁
apply_json_fix()

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

logger = logging.getLogger(__name__)
safe_commands = ['ls', 'pwd', 'echo', 'cat', 'head', 'tail', 'grep', 'find', 'python', 'python3', 'chmod', 'cd', 'lsof', 'mkdir']

from .config import (
    PYTHON_INTERPRETER_MCP_URL, 
    FILE_OPERATIONS_MCP_URL, 
    SYSTEM_OPERATIONS_MCP_URL,
    MCP_SSE_TIMEOUT,
    WORKSPACE_DIR,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    SANDBOX_MODE,
    CURRENT_EXECUTION_ID
)

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
    列出工作空间内容
    
    Args:
        tool_context: 工具上下文
        workspace_name: 工作空间名称，如果为None则使用当前执行ID
    
    Returns:
        dict: 包含工作空间文件列表的字典
    """
    if workspace_name is None:
        workspace_name = CURRENT_EXECUTION_ID
    
    workspace_path = Path(WORKSPACE_DIR) / workspace_name
    
    if not workspace_path.exists():
        return {"error": "工作空间不存在"}
    
    files = []
    for item in workspace_path.rglob("*"):
        try:
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
        except (PermissionError, OSError) as e:
            # 跳过无法访问的文件/目录（如 /proc 下的某些文件）
            logger_patch.debug(f"跳过无法访问的路径: {item}, 错误: {e}")
            continue
    
    return {
        "workspace_path": str(workspace_path),
        "workspace_name": workspace_name,
        "files": files
    }

def validate_file_path(file_path: str) -> bool:
    """验证文件路径是否安全"""
    # tmp 目录不进行安全检查
    return True 
    if file_path.startswith("/tmp"):
        return True
    if SANDBOX_MODE:
        # 在沙盒模式下，只允许访问工作空间内的文件
        workspace_path = Path(WORKSPACE_DIR).resolve()
        file_path = Path(file_path).resolve()
        
        if not str(file_path).startswith(str(workspace_path)) or not str(file_path).startswith("/tmp"):
            return False
    # # 检查文件扩展名
    # if Path(file_path).suffix not in ALLOWED_EXTENSIONS:
    #     return False
    
    return True

def read_file(tool_context: ToolContext, file_path: str):
    """
    读取文件内容
    
    Args:
        tool_context: 工具上下文
        file_path: 文件路径
    
    Returns:
        dict: 包含文件内容的字典
    """
    if not validate_file_path(file_path):
        return {"error": "文件路径不安全或文件类型不被允许"}
    
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
    写入文件内容
    
    Args:
        tool_context: 工具上下文
        file_path: 文件路径 (必需，可以是相对路径或绝对路径)
        content: 要写入的内容 (必需)
    
    Returns:
        dict: 包含操作结果的字典
    """
    try:
        file_path_obj = Path(file_path)
        file_path_str = str(file_path_obj)
        
        # 如果路径不是以 /work 开头，需要补全
        if not file_path_str.startswith('/work'):
            # 获取基础工作空间路径
            # 优先使用环境变量 CODE_AGENT_WORKSPACE_DIR
            env_workspace = os.getenv('CODE_AGENT_WORKSPACE_DIR', '')
            if env_workspace:
                base_workspace = Path(env_workspace)
            else:
                base_workspace = Path(WORKSPACE_DIR)
            
            # 解析基础工作空间路径（可能是相对路径）
            base_workspace_resolved = base_workspace.resolve()
            
            # 尝试找到包含 session ID 的项目目录
            # 格式应该是：workspace/${MODEL_NAME}_Dev_inference/${i}
            # 或者：/work/workspace/${MODEL_NAME}_Dev_inference/${i}
            base_project_path = None
            
            # 方法1：检查环境变量路径是否已经包含 session ID（数字目录）
            if env_workspace:
                parts = base_workspace_resolved.parts
                if len(parts) >= 1 and parts[-1].isdigit():
                    # 找到了包含 session ID 的路径
                    base_project_path = base_workspace_resolved
            
            # 方法2：从当前工作目录推断
            if base_project_path is None:
                cwd = Path.cwd()
                cwd_parts = cwd.parts
                # 查找 workspace 目录
                if 'workspace' in cwd_parts:
                    workspace_idx = cwd_parts.index('workspace')
                    # 检查 workspace 后是否有 MODEL_NAME 和 session ID
                    if workspace_idx + 2 < len(cwd_parts) and cwd_parts[workspace_idx + 2].isdigit():
                        # 找到了：workspace/${MODEL_NAME}_Dev_inference/${i}
                        workspace_path_parts = cwd_parts[workspace_idx:]
                        base_project_path = Path('/work') / Path(*workspace_path_parts[:3])
            
            # 方法3：如果还是找不到，使用基础工作空间路径，补全为 /work 开头
            if base_project_path is None:
                # 确保路径以 /work 开头
                workspace_parts = base_workspace_resolved.parts
                if 'workspace' in workspace_parts:
                    workspace_idx = workspace_parts.index('workspace')
                    base_project_path = Path('/work') / Path(*workspace_parts[workspace_idx:])
                else:
                    # 如果没有 workspace，直接补全
                    base_project_path = Path('/work') / base_workspace_resolved
            
            # 如果是相对路径，补全到项目路径下
            if not file_path_obj.is_absolute():
                file_path_obj = base_project_path / file_path
            else:
                # 绝对路径但不是 /work 开头，尝试转换为 /work 开头
                # 如果路径包含 workspace，提取 workspace 之后的部分
                abs_parts = file_path_obj.resolve().parts
                if 'workspace' in abs_parts:
                    workspace_idx = abs_parts.index('workspace')
                    file_path_obj = Path('/work') / Path(*abs_parts[workspace_idx:])
                else:
                    # 无法转换，使用原路径
                    file_path_obj = file_path_obj.resolve()
        else:
            # 已经是 /work 开头的路径，直接使用
            if not file_path_obj.is_absolute():
                # 相对路径，需要找到基础路径
                env_workspace = os.getenv('CODE_AGENT_WORKSPACE_DIR', '')
                if env_workspace:
                    base_path = Path(env_workspace).resolve()
                else:
                    base_path = Path(WORKSPACE_DIR).resolve()
                
                # 检查基础路径是否包含 session ID
                if base_path.parts[-1].isdigit():
                    file_path_obj = base_path / file_path
                else:
                    # 尝试从当前目录推断
                    cwd = Path.cwd()
                    if 'workspace' in cwd.parts:
                        workspace_idx = cwd.parts.index('workspace')
                        if workspace_idx + 2 < len(cwd.parts) and cwd.parts[workspace_idx + 2].isdigit():
                            base_project_path = Path('/work') / Path(*cwd.parts[workspace_idx:workspace_idx+3])
                            file_path_obj = base_project_path / file_path
                        else:
                            file_path_obj = Path('/work') / base_path / file_path
                    else:
                        file_path_obj = Path('/work') / base_path / file_path
            else:
                file_path_obj = file_path_obj.resolve()
        
        file_path_str = str(file_path_obj.resolve())
        
        if not validate_file_path(file_path_str):
            return {"error": "文件路径不安全或文件类型不被允许"}
        
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path_obj, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "file_path": file_path_str,
            "status": "written",
            "size": len(content)
        }
    except Exception as e:
        return {"error": f"写入文件失败: {str(e)}"}

def delete_file(tool_context: ToolContext, file_path: str):
    """
    删除文件
    
    Args:
        tool_context: 工具上下文
        file_path: 文件路径
    
    Returns:
        dict: 包含操作结果的字典
    """
    if not validate_file_path(file_path):
        return {"error": "文件路径不安全或文件类型不被允许"}
    
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
    激活工作空间的虚拟环境
    
    Args:
        tool_context: 工具上下文
        workspace_name: 工作空间名称，如果为None则使用当前执行ID
    
    Returns:
        dict: 包含激活结果的字典
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
    执行Python代码
    
    Args:
        tool_context: 工具上下文
        code: 要执行的Python代码 (必需)
        timeout: 执行超时时间（秒），默认30秒
        use_venv: 是否使用虚拟环境，默认True
    
    Returns:
        dict: 包含执行结果的字典
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

def run_system_command(tool_context: ToolContext, command: str, timeout: int = 15):
    """
    运行系统命令
    
    Args:
        tool_context: 工具上下文
        command: 要执行的系统命令
        timeout: 执行超时时间（秒），默认30秒
    
    Returns:
        dict: 包含执行结果的字典
    """
    # 开放限制
    SANDBOX_MODE = False

    if SANDBOX_MODE:
        # 在沙盒模式下，只允许安全的命令
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
    交互式运行系统命令，支持输入输出交互

    Args:
        tool_context: 工具上下文
        command: 要执行的系统命令
        inputs: 需要输入给命令的内容（字符串列表，每个元素回车一次）
        timeout: 超时时间（秒）

    Returns:
        dict: 包含执行结果的字典
    """
    if SANDBOX_MODE:
        safe_commands = ['ls', 'pwd', 'echo', 'cat', 'head', 'tail', 'grep', 'find', 'python', 'python3', 'lsof']
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
    运行一个交互式Python代码会话。
    
    第一次调用时需要提供code参数来启动新会话，后续调用需要提供session_id来继续之前的会话。
    如果需要向Python代码输入内容，提供user_input参数。
    
    Args:
        tool_context: 工具上下文
        cmd: 要执行的Python代码
        session_id: 会话ID，用于继续之前的会话
        timeout: 超时时间（秒）
    Returns:
        dict: 包含执行结果的字典
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
    启动一个交互式shell会话。
    
    Args:
        tool_context: 工具上下文
        cmd: 要执行的shell命令
    Returns:
        dict: 包含执行结果的字典
    """
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
    
    # 如果检测到 conda 环境，在命令前添加 source activate
    if conda_env_path and conda_env_path.strip():
        cmd = f"source activate {conda_env_path} && {cmd}"
    
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
    运行一个交互式shell会话。
    
    第一次调用时需要提供cmd参数来启动新会话，后续调用需要提供session_id来继续之前的会话。
    如果需要向shell输入内容，提供user_input参数。
    
    参数:
        session_id (str, optional): 会话ID，用于继续之前的会话
        user_input (str, optional): 要发送到shell的输入内容
        
    返回:
        Dict[str, Any]: 包含以下字段的字典：
            - session_id: str, 会话ID
            - output: str, shell输出内容
            - waiting: bool, 是否在等待输入
            - finished: bool, 会话是否结束
    """
    # 获取当前会话的状态
    session_state = getattr(tool_context, 'python_env_state', {})
    if session_id not in session_state:
        session_state[session_id] = False
    is_in_python = session_state[session_id]
    
    SANDBOX_MODE = False

    # 检查命令安全性
    if SANDBOX_MODE and is_in_python and user_input:
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
    终止一个shell会话。
    
    参数:
        session_id (str): 要终止的会话ID
        
    返回:
        Dict[str, Any]: 操作结果
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

'''
def create_meituan_search_toolset():
    return MCPToolset(
            connection_params=SseServerParams(
                url='http://mcphub-server.sankuai.com/mcphub-api/6025f6404b9640',
                sse_read_timeout=30
            )
        )
'''
'''
def create_meituan_browse_toolset():    
    return MCPToolset(
            connection_params=SseServerParams(
                url='http://mcphub-server.sankuai.com/mcphub-api/913526fb42f543',
                sse_read_timeout=30
            )
        )
'''

#meituan_search = create_meituan_search_toolset()
#meituan_browse = create_meituan_browse_toolset()

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
    #meituan_search,
    #meituan_browse,
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

