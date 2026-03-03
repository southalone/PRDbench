#!/bin/bash

# 本地 Code Agent 启动脚本
# 一键启动 MCP 服务器和主程序

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Python 是否安装
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装，请先安装 Python 3"
        exit 1
    fi
    print_success "Python 3 已安装"
}

# 检查依赖是否安装
check_dependencies() {
    print_info "检查依赖..."
    
    # 检查必要的 Python 包
    python3 -c "import aiohttp" 2>/dev/null || {
        print_warning "aiohttp 未安装，正在安装..."
        pip3 install aiohttp
    }
    
    python3 -c "import google.adk" 2>/dev/null || {
        print_error "mt-llm-adk 未安装，请运行: pip install mt-llm-adk==1.2.1.3"
        exit 1
    }
    
    print_success "依赖检查完成"
}

# 创建工作空间目录
create_workspace() {
    print_info "创建工作空间目录..."
    mkdir -p /tmp/code_agent_workspace
    print_success "工作空间目录已创建: /tmp/code_agent_workspace"
}

# 启动 MCP 服务器
start_mcp_servers() {
    print_info "启动 MCP 服务器..."

    # 读取端口，优先环境变量，默认9001/8002
    PYTHON_INTERPRETER_PORT="${PYTHON_INTERPRETER_PORT:-9001}"
    FILE_OPERATIONS_PORT="${FILE_OPERATIONS_PORT:-8002}"

    # 检查端口是否被占用
    if lsof -Pi :"$PYTHON_INTERPRETER_PORT" -sTCP:LISTEN -t >/dev/null ; then
        print_warning "端口 $PYTHON_INTERPRETER_PORT 已被占用，可能 MCP 服务器已在运行"
    fi

    if lsof -Pi :"$FILE_OPERATIONS_PORT" -sTCP:LISTEN -t >/dev/null ; then
        print_warning "端口 $FILE_OPERATIONS_PORT 已被占用，可能 MCP 服务器已在运行"
    fi

    # 启动 MCP 服务器（后台运行）
    python3 mcp_servers.py &
    MCP_PID=$!

    # 等待服务器启动
    sleep 3

    # 检查服务器是否启动成功
    if curl -s "http://localhost:${PYTHON_INTERPRETER_PORT}/python-interpreter/health" > /dev/null; then
        print_success "Python 解释器 MCP 服务器启动成功 (端口 $PYTHON_INTERPRETER_PORT)"
    else
        print_error "Python 解释器 MCP 服务器启动失败(端口 $PYTHON_INTERPRETER_PORT)"
        exit 1
    fi

    if curl -s "http://localhost:${FILE_OPERATIONS_PORT}/file-operations/health" > /dev/null; then
        print_success "文件操作 MCP 服务器启动成功 (端口 $FILE_OPERATIONS_PORT)"
    else
        print_error "文件操作 MCP 服务器启动失败"
        exit 1
    fi

    print_success "所有 MCP 服务器启动完成"
}



# 清理函数
cleanup() {
    print_info "正在清理..."
    
    # 停止 MCP 服务器
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null || true
        print_info "MCP 服务器已停止"
    fi
    
    # 停止所有相关的 Python 进程
    pkill -f "mcp_servers.py" 2>/dev/null || true
    
    print_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "本地 Code Agent 启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --test-only     只运行测试，不启动主程序"
    echo "  --mcp-only      只启动 MCP 服务器"
    echo "  --help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                    # 完整启动（推荐）"
    echo "  $0 --test-only        # 只运行测试"
    echo "  $0 --mcp-only         # 只启动 MCP 服务器"
    echo "  $0 -t '计算 2+2'      # 执行特定任务"
}

# 主函数
main() {
    # 设置信号处理
    trap cleanup EXIT INT TERM
    
    print_info "🚀 启动本地 Code Agent 系统"
    echo ""
    
    # 解析命令行参数
    TEST_ONLY=false
    MCP_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --test-only)
                TEST_ONLY=true
                shift
                ;;
            --mcp-only)
                MCP_ONLY=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
    
    # 检查环境
    check_python
    check_dependencies
    # create_workspace
    
    # 启动 MCP 服务器
    start_mcp_servers
    print_info "MCP 服务器已启动，按 Ctrl+C 停止"
    wait
}

# 运行主函数
main "$@" 