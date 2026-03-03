import os
import uuid
from datetime import datetime
from google.adk.models.lite_llm import LiteLlm
from lite_llm_wrapper import LiteLlmWithSleep


MAX_TOKENS = int(32768)
MAX_SESSION_TIME = int(3600)
# Firday的模型都是openai开头
# api_key 不要外传
friday_model_dict = {
    "deepseek_v3": LiteLlmWithSleep(
            model="openai/deepseek-v3-friday",
            api_base='MASKED',
            api_key='MASKED',
        max_tokens_threshold=64000-32000,
        enable_compression=True,
        temperature=0.1
    ),
    "deepseek_v3_1": LiteLlmWithSleep(
    # model="openai/deepseek-v3-friday",
    model="openai/deepseek-chat",
    api_base='MASKED',
    api_key='MASKED',
    # model="openai/deepseek-v3-1-250821",
    # api_base='MASKED',
    # api_key='MASKED',
    # max_completion_tokens=32000,
    max_tokens_threshold=128000-32000,
    enable_compression=True,
    temperature=0.1
),
"qwen3_coder": LiteLlmWithSleep(
    model="openai/qwen3-coder-480b-a35b-instruct",
    api_base='MASKED',
    api_key='MASKED',
    # max_completion_tokens=32000,
    max_tokens_threshold=256_000-32000,
    enable_compression=True,
    temperature=0.1
),


"claude-4-5-opus":LiteLlmWithSleep(
    model="openai/claude-opus-4-5-20251101",
    api_base='MASKED',
    api_key='MASKED',
    max_tokens_threshold=256_000-32000,
    enable_compression=True,
    ),

    "gemini-3-pro-preview":LiteLlmWithSleep(
    model="openai/gemini-3-pro-preview",
    api_base='MASKED',
    api_key='MASKED',
    max_tokens_threshold=256_000-32000,
    enable_compression=True,
    ),

"glm-4-7":LiteLlmWithSleep(
    model="openai/glm-4.7",
    api_base='MASKED',
    api_key='MASKED',
    max_tokens_threshold=256_000-32000,
    enable_compression=True,
    ),

    "claude-4-5-opus":LiteLlmWithSleep(
        model="openai/aws.claude-opus-4.5",
        api_base='MASKED',
        api_key='MASKED',
        max_tokens_threshold=256_000-32000,
        enable_compression=True,
        temperature=0.1
    ),

     "gemini-2-5-flash":LiteLlmWithSleep(
    model="openai/gemini-2.5-flash-lite-preview-09-2025",
    api_base='MASKED',
    api_key='MASKED',
    max_tokens_threshold=131072-32000,
    enable_compression=True,
    ),

"kimi-48b":LiteLlmWithSleep(
        model="openai/kimi-48b",
        api_base='MASKED',
        api_key='MASKED',
        custom_llm_provider="openai",
        max_tokens_threshold=131072-32000,
        enable_compression=True,
        temperature=0.7,
        presence_penalty=1.06
    ),

"qwen3-80b":LiteLlmWithSleep(
    model="openai/qwen3-next-80b-a3b-instruct",
    api_base='MASKED',
    api_key='MASKED',
    max_tokens_threshold=256_000-32000,
    enable_compression=True,
    ),

"qwen3-30b":LiteLlmWithSleep(
    model="openai/qwen3-30b-a3b-instruct-2507",
    api_base='MASKED',
    api_key='MASKED',
    max_tokens_threshold=256_000-32000,
    enable_compression=True,
    temperature=0.7
    ),

'doubao-seed-1_6': LiteLlmWithSleep(
        model="openai/Doubao-Seed-1.6",
        api_base='https://aigc.sankuai.com/v1/openai/native',
        api_key='2003426323536850978',
        max_tokens_threshold=256_000-32000,
        enable_compression=True,
        presence_penalty=1.06
    ),

"longcat-3b":LiteLlmWithSleep(
        model="openai/longcat-3b",
        api_base='MASKED',
        api_key='MASKED',
        custom_llm_provider="openai",
        max_tokens_threshold=131072-32000,
        enable_compression=True,
        temperature=0.7,
        presence_penalty=1.06
    ),

'friday_glm': LiteLlmWithSleep(
        model="openai/glm-4.6",
        api_base='MASKED',
        api_key='MASKED',
        max_tokens=32768,
        temperature=0.1
    ),

'kimi_k2': LiteLlmWithSleep(
        model="openai/kimi-k2-0905-preview",
        api_base='MASKED',
        api_key='MASKED',
        max_tokens=32768,
        temperature=0.1
    ),

    "doubao_seed": LiteLlmWithSleep(
    # model="openai/Doubao-Seed-1.6",
    # api_base='MASKED',
    # api_key='MASKED',
    model="openai/doubao-seed-1-6-250615",
    api_base='MASKED',
    api_key='MASKED',
    # max_tokens=256_000-100,
    # max_completion_tokens=32000,    
    max_tokens_threshold=256_000-32000,
    enable_compression=True,
    temperature=0.1
),
    "gemini": LiteLlmWithSleep(
    model="openai/gemini-2.5-pro",
    api_base='MASKED',
    api_key='MASKED',
    # api_base='MASKED',
    # api_key='MASKED',
    # max_completion_tokens=32000,
    max_tokens_threshold=1_048_576-32000,
    enable_compression=True,
    temperature=0.1
),
    "claude_4_sonnet": LiteLlmWithSleep(
    # model="openai/anthropic.claude-sonnet-4",
    # api_base='MASKED',
    # api_key='MASKED',
    model="openai/claude-sonnet-4-20250514",
    api_base='MASKED',
    api_key='MASKED',
    # max_completion_tokens=32000,
    max_tokens_threshold=131072-32000-1000,
    enable_compression=True,
    temperature=0.1
),
    "claude_3_7_sonnet": LiteLlmWithSleep(
    # model="openai/anthropic.claude-3.7-sonnet",
    # api_base='MASKED',
    # api_key='MASKED',
    model="openai/claude-3-7-sonnet-20250219",
    api_base='MASKED',
    api_key='MASKED',
    # max_completion_tokens=32000,
    max_tokens_threshold=131072-32000-1000,
    enable_compression=True,
    temperature=0.1
),
    "gpt_5": LiteLlmWithSleep(
    model="openai/gpt-5",
    api_base='MASKED',
    api_key='MASKED',
    # max_completion_tokens=32000,
    max_tokens_threshold=256_000-32000,
    enable_compression=True
),
    "qwen3_coder": LiteLlmWithSleep(
    model="openai/qwen3-coder-480b-a35b-instruct",
    api_base='MASKED',
    api_key='MASKED',
    # max_completion_tokens=32000,
    max_tokens_threshold=256_000-32000,
    enable_compression=True,
    temperature=0.1
),
}



# 基础模型配置
BASIC_MODEL = LiteLlmWithSleep(
    model="openai/Doubao-Seed-1.6",
    api_base='MASKED',
    api_key='MASKED',
    # 增加输出长度限制，避免部分事件错误
    # max_completion_tokens=8000,
    max_tokens_threshold=300,
    # for debug 
    enable_compression=True,
    max_total_tokens=2000,
    temperature=0.6
)




# 生成随机执行ID
def generate_execution_id():
    """生成唯一的执行ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"exec_{timestamp}_{unique_id}"

# 当前执行ID
CURRENT_EXECUTION_ID = generate_execution_id()

# 本地MCP服务器配置
PYTHON_INTERPRETER_MCP_URL = "http://localhost:8001/python-interpreter"
FILE_OPERATIONS_MCP_URL = "http://localhost:8002/file-operations"
SYSTEM_OPERATIONS_MCP_URL = "http://localhost:8003/system-operations"

# MCP连接配置
MCP_SSE_TIMEOUT = 30
MAX_ITERATIONS = 10

# 系统配置
SYSTEM_NAME = "LocalCodeAgent"
BASE_WORKSPACE_DIR = "work/workspace"
# WORKSPACE_DIR = f"{BASE_WORKSPACE_DIR}/{CURRENT_EXECUTION_ID}"
WORKSPACE_DIR = BASE_WORKSPACE_DIR

# 安全配置
ALLOWED_EXTENSIONS = ['.py', '.txt', '.md', '.json', '.yaml', '.yml', '.csv', '.sql']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SANDBOX_MODE = True

print(f"🚀 当前执行ID: {CURRENT_EXECUTION_ID}")
print(f"📁 工作空间路径: {WORKSPACE_DIR}") 