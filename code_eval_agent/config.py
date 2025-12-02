import os
import uuid
from datetime import datetime
from google.adk.models.lite_llm import LiteLlm
from lite_llm_wrapper import LiteLlmWithSleep

# 基础模型配置
BASIC_MODEL =LiteLlmWithSleep(
        model="openai/gemini-2.5-pro",
        api_base='https://aigc.sankuai.com/v1/openai/native',
        api_key='1873925539543834701',
        max_tokens=32768,
        temperature=0.1
    )

friday_model_dict = {
    "claude_3_7_sonnet": LiteLlmWithSleep(
        # model="openai/anthropic.claude-3.7-sonnet",
        # api_base='https://aigc.sankuai.com/v1/openai/native',
        # api_key='1873925539543834701',
        model="openai/claude-3-7-sonnet-20250219",
        api_base='https://api.toiotech.com/v1',
        api_key='sk-nw5G71pE0RgR4ew85fdYUDWTYxdFma0M4aQoUTuxNrXNXFqP',
        # max_completion_tokens=32000,
        max_tokens_threshold=131072-32000-1000,
        enable_compression=True,
        temperature=0.1
    ),
    "gemini": LiteLlmWithSleep(
        model="openai/gemini-2.5-pro",
        api_base='https://aigc.sankuai.com/v1/openai/native',
        api_key='1873925539543834701',
        max_tokens=32768,
        temperature=0.1
    ),
    'gpt_5':LiteLlmWithSleep(
    model="openai/gpt-5",
    api_base='https://api.toiotech.com/v1',
    api_key='sk-LfUBAupPQCgffAEkCb61278d4c734225A7533778B123CbBa',
    # max_completion_tokens=32000,
    max_tokens_threshold=256_000-32000,
    enable_compression=True
),
"qwen3_coder": LiteLlmWithSleep(
    model="openai/qwen3-coder-480b-a35b-instruct",
    api_base='https://api.toiotech.com/v1',
    api_key='sk-nw5G71pE0RgR4ew85fdYUDWTYxdFma0M4aQoUTuxNrXNXFqP',
    # max_completio[n_tokens=32000,
    max_tokens_threshold=256_000-32000,
    enable_compression=True,
    temperature=0.1,
    presence_penalty=1.2
)
}



# 生成随机执行ID
def generate_execution_id():
    """生成唯一的执行ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"exec_{timestamp}_{unique_id}"

# 当前执行ID
CURRENT_EXECUTION_ID = generate_execution_id()

# 本地MCP服务器配置
# PYTHON_INTERPRETER_MCP_URL = "http://localhost:9001/python-interpreter"
# FILE_OPERATIONS_MCP_URL = "http://localhost:8002/file-operations"
# SYSTEM_OPERATIONS_MCP_URL = "http://localhost:8003/system-operations"

import os

# 端口环境变量名称
PYTHON_INTERPRETER_PORT = os.getenv("PYTHON_INTERPRETER_PORT", "9001")
FILE_OPERATIONS_PORT = os.getenv("FILE_OPERATIONS_PORT", "8002")
SYSTEM_OPERATIONS_PORT = os.getenv("SYSTEM_OPERATIONS_PORT", "8003")

PYTHON_INTERPRETER_MCP_URL = f"http://localhost:{PYTHON_INTERPRETER_PORT}/python-interpreter"
FILE_OPERATIONS_MCP_URL = f"http://localhost:{FILE_OPERATIONS_PORT}/file-operations"
SYSTEM_OPERATIONS_MCP_URL = f"http://localhost:{SYSTEM_OPERATIONS_PORT}/system-operations"


# MCP连接配置
MCP_SSE_TIMEOUT = 30
MAX_ITERATIONS = 10

# 系统配置
SYSTEM_NAME = "LocalCodeAgent"
BASE_WORKSPACE_DIR = "/tmp/code_agent_workspace"

# 支持环境变量覆盖工作目录，方便本地测试
# 使用方法：export CODE_AGENT_WORKSPACE_DIR=/path/to/your/workspace
WORKSPACE_DIR = os.getenv('CODE_AGENT_WORKSPACE_DIR', BASE_WORKSPACE_DIR)

# 如果是相对路径，转换为绝对路径
if not os.path.isabs(WORKSPACE_DIR):
    WORKSPACE_DIR = os.path.abspath(WORKSPACE_DIR)

# 安全配置
ALLOWED_EXTENSIONS = ['.py', '.txt', '.md', '.json', '.yaml', '.yml', '.csv', '.sql', '.in', '.jsonl']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SANDBOX_MODE = True


# 是否启用路径限制
ENABLE_PATH_RESTRICTION = os.getenv('ENABLE_PATH_RESTRICTION', 'true').lower() == 'true'

print(f"🚀 当前执行ID: {CURRENT_EXECUTION_ID}")
print(f"📁 工作空间路径: {WORKSPACE_DIR}") 