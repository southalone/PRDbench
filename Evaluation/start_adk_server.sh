# ==================== ADK服务器启动脚本 ====================
# 功能：启动Claude 3.7 Sonnet ADK服务器，并运行代码生成脚本
# 用法: ./start_adk_server.sh <test_type> <root_path> <port> <python_port> <file_port> <system_port>

# 请首先开启文件MCP服务（参考adk_example/readme.md）

# 检查参数数量
if [ $# -ne 6 ]; then
    echo "用法: $0 <test_type> <root_path> <port> <python_port> <file_port> <system_port>"
    exit 1
fi

# 接收脚本参数
TEST_TYPE=$1
ROOT_PATH=$2
PORT=$3
export PYTHON_INTERPRETER_PORT=$4
export FILE_OPERATIONS_PORT=$5
export SYSTEM_OPERATIONS_PORT=$6

echo "参数设置："
echo "  test_type: $TEST_TYPE"
echo "  root_path: $ROOT_PATH"
echo "  port: $PORT"

MODEL_NAME="qwen3_coder_480b_a35b_local"
SESSION_NAME="adk_server_${MODEL_NAME}_2_$TEST_TYPE"
FILE_SERVER_NAME="file_server_${MODEL_NAME}_2_$TEST_TYPE"


# 清理现有的ADK服务器和文件服务tmux会话（避免端口冲突）
echo "SESSION NAME $SESSION_NAME"
echo "FILE SERVER NAME $FILE_SERVER_NAME"
echo "清理现有的ADK服务器tmux会话..."
tmux kill-session -t $SESSION_NAME 2>/dev/null || true
echo "清理现有的文件服务tmux会话..."
tmux kill-session -t $FILE_SERVER_NAME 2>/dev/null || true

# 设置ADK服务器的工作目录为root_path
export CODE_AGENT_WORKSPACE_DIR="$ROOT_PATH"
echo "设置ADK工作目录: $CODE_AGENT_WORKSPACE_DIR"

# 启动文件服务（每次都重新启动以确保使用正确的端口配置）
echo "启动文件服务... $FILE_SERVER_NAME"
tmux new-session -d -s $FILE_SERVER_NAME -n $FILE_SERVER_NAME
tmux send-keys -t $FILE_SERVER_NAME "export PYTHON_INTERPRETER_PORT=${PYTHON_INTERPRETER_PORT} ; export FILE_OPERATIONS_PORT=${FILE_OPERATIONS_PORT} ; export SYSTEM_OPERATIONS_PORT=${SYSTEM_OPERATIONS_PORT} ; export CODE_AGENT_WORKSPACE_DIR=${ROOT_PATH} ; cd Evaluation/adk_example/code_eval_agent_workspace_dir ; ./start.sh" C-m

# 等待文件服务启动
echo "等待文件服务启动..."
sleep 5

# 启动一个共用的ADK服务器（只启动一次，工作目录设置为root_path）
echo "启动共用的${MODEL_NAME} ADK服务器..."

# 创建ADK服务器会话
tmux new-session -d -s $SESSION_NAME -n $SESSION_NAME

# 设置环境变量
tmux send-keys -t $SESSION_NAME "export CONDA_ENV_PATH=${CONDA_ENV_PATH}" C-m
tmux send-keys -t $SESSION_NAME "export ADK_MODEL=${MODEL_NAME}" C-m
tmux send-keys -t $SESSION_NAME "export CODE_AGENT_WORKSPACE_DIR=${ROOT_PATH}" C-m
tmux send-keys -t $SESSION_NAME "export PYTHON_INTERPRETER_PORT=${PYTHON_INTERPRETER_PORT}" C-m
tmux send-keys -t $SESSION_NAME "export FILE_OPERATIONS_PORT=${FILE_OPERATIONS_PORT}" C-m
tmux send-keys -t $SESSION_NAME "export SYSTEM_OPERATIONS_PORT=${SYSTEM_OPERATIONS_PORT}" C-m
tmux send-keys -t $SESSION_NAME "cd Evaluation/adk_example" C-m

# 等待环境设置完成
sleep 2

# 启动ADK服务器
tmux send-keys -t $SESSION_NAME "adk api_server --port ${PORT}" C-m

# 等待ADK服务器启动
echo "等待ADK服务器启动..."
sleep 15

# 检查服务器是否启动成功
# echo "检查ADK服务器状态..."
# if curl -s "http://localhost:${PORT}/health" > /dev/null 2>&1; then
#     echo "ADK服务器启动成功！"
# else
#     echo "警告: ADK服务器可能未完全启动，继续执行..."
# fi
