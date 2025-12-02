import os

# 端口环境变量名称
PYTHON_INTERPRETER_PORT = os.getenv("PYTHON_INTERPRETER_PORT", "9001")
FILE_OPERATIONS_PORT = os.getenv("FILE_OPERATIONS_PORT", "8002")
SYSTEM_OPERATIONS_PORT = os.getenv("SYSTEM_OPERATIONS_PORT", "8003")

PYTHON_INTERPRETER_MCP_URL = f"http://localhost:{PYTHON_INTERPRETER_PORT}/python-interpreter"
FILE_OPERATIONS_MCP_URL = f"http://localhost:{FILE_OPERATIONS_PORT}/file-operations"
SYSTEM_OPERATIONS_MCP_URL = f"http://localhost:{SYSTEM_OPERATIONS_PORT}/system-operations"

BASE_WORKSPACE_DIR = "/tmp/code_agent_workspace"

# 支持环境变量覆盖工作目录，方便本地测试
# 使用方法：export CODE_AGENT_WORKSPACE_DIR=/path/to/your/workspace
WORKSPACE_DIR = os.getenv('CODE_AGENT_WORKSPACE_DIR', BASE_WORKSPACE_DIR)