# 本地 Code Agent

基于 Google ADK 的本地代码代理系统，支持 Python 解释器、文件操作等功能，所有工具都以本地 MCP 的方式提供。

## 🚀 功能特性

### 核心功能
- **完整代码开发流程**: 规划、编写、测试、调试、总结
- **快速代码执行**: 数学计算、数据处理、快速验证
- **文件管理**: 创建、读取、修改、删除文件和目录
- **工作空间管理**: 隔离的开发环境

### 安全特性
- **沙盒环境**: 所有代码执行都在安全的沙盒环境中
- **文件操作限制**: 只能访问指定工作空间内的文件
- **系统命令白名单**: 只允许执行安全的系统命令
- **文件类型限制**: 只允许操作安全的文件类型

### MCP 工具支持
- **Python 解释器**: 执行 Python 代码片段
- **文件操作**: 完整的文件系统操作
- **系统操作**: 安全的系统命令执行

## 📁 项目结构

```
code_agent_local/
├── __init__.py              # 包初始化文件
├── config.py                # 配置文件
├── agent.py                 # 代理系统主文件
├── mcp_tools.py             # MCP 工具定义
├── mcp_servers.py           # MCP 服务器实现
├── main.py                  # 主程序入口
├── test_agent.py            # 测试文件
└── README.md                # 说明文档
```

## 🛠️ 安装和配置

### 1. 安装依赖

确保已安装项目的主要依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置模型

编辑 `config.py` 文件，配置您的模型参数：

```python
BASIC_MODEL = LiteLlm(
    model="your-model-name",
    api_base='your-api-base',
    api_key='your-api-key'
)
```

### 3. 创建工作空间

系统会自动在 `/tmp/code_agent_workspace` 创建工作空间，您也可以修改 `config.py` 中的 `WORKSPACE_DIR` 来指定其他位置。

## 🚀 使用方法

### 1. 启动 MCP 服务器

首先启动本地 MCP 服务器：

```bash
cd examples/code_agent_local
python mcp_servers.py
```

这将启动以下服务：
- Python 解释器服务 (端口 9001)
- 文件操作服务 (端口 8002)

### 2. 运行主程序

在另一个终端中运行主程序：

```bash
# 交互式模式
python main.py

# 执行单个任务
python main.py -t "创建一个计算器程序"

# 显示示例
python main.py --examples

# 详细输出模式
python main.py --verbose
```

### 3. 运行测试

验证系统是否正常工作：

```bash
python test_agent.py
```

## 💡 使用示例

### 代码开发示例

```
💬 请输入您的请求: 创建一个简单的计算器程序

🔄 正在处理: 创建一个简单的计算器程序

✅ 处理完成:
状态: success
响应: 本地 Code Agent 已处理您的请求: 创建一个简单的计算器程序
```

### 代码执行示例

```
💬 请输入您的请求: 计算斐波那契数列的前10项

🔄 正在处理: 计算斐波那契数列的前10项

✅ 处理完成:
状态: success
响应: 本地 Code Agent 已处理您的请求: 计算斐波那契数列的前10项
```

### 文件管理示例

```
💬 请输入您的请求: 创建一个新的工作空间并列出文件

🔄 正在处理: 创建一个新的工作空间并列出文件

✅ 处理完成:
状态: success
响应: 本地 Code Agent 已处理您的请求: 创建一个新的工作空间并列出文件
```

## 🔧 配置选项

### 主要配置项

在 `config.py` 中可以配置以下选项：

```python
# 模型配置
BASIC_MODEL = LiteLlm(...)

# MCP 服务器配置
PYTHON_INTERPRETER_MCP_URL = "http://localhost:9001/python-interpreter"
FILE_OPERATIONS_MCP_URL = "http://localhost:8002/file-operations"

# 系统配置
WORKSPACE_DIR = "/tmp/code_agent_workspace"
MAX_ITERATIONS = 10

# 安全配置
ALLOWED_EXTENSIONS = ['.py', '.txt', '.md', '.json', '.yaml', '.yml', '.csv', '.sql']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SANDBOX_MODE = True
```

### 命令行选项

```bash
python main.py [选项]

选项:
  -t, --task TEXT        要执行的任务
  --examples             显示使用示例
  --workspace PATH       工作空间目录
  --verbose              详细输出模式
  -h, --help             显示帮助信息
```

## 🔒 安全说明

### 沙盒环境
- 所有代码执行都在隔离的沙盒环境中进行
- 无法访问系统关键文件和目录
- 网络访问受到限制

### 文件操作安全
- 只能访问指定工作空间内的文件
- 文件类型白名单限制
- 文件大小限制防止资源滥用

### 系统命令安全
- 只允许执行安全的系统命令
- 命令白名单机制
- 执行超时限制

## 🐛 故障排除

### 常见问题

1. **MCP 服务器连接失败**
   ```
   错误: MCP 服务器连接失败
   解决: 确保 mcp_servers.py 正在运行
   ```

2. **模型配置错误**
   ```
   错误: 模型配置无效
   解决: 检查 config.py 中的模型配置
   ```

3. **权限错误**
   ```
   错误: 文件权限不足
   解决: 检查工作空间目录权限
   ```

### 调试模式

启用详细日志输出：

```bash
python main.py --verbose
```

### 测试系统

运行完整测试：

```bash
python test_agent.py
```

## 📚 API 参考

### 主要类

#### LocalCodeAgentSystem
主要的代理系统类，管理所有子代理。

#### LocalCodeAgentCLI
命令行界面类，提供用户交互功能。

### 主要工具

#### 基础工具
- `create_workspace()`: 创建工作空间
- `list_workspace()`: 列出工作空间内容
- `read_file()`: 读取文件
- `write_file()`: 写入文件
- `delete_file()`: 删除文件
- `execute_python_code()`: 执行 Python 代码
- `run_system_command()`: 运行系统命令

#### MCP 工具
- `create_python_interpreter_toolset()`: Python 解释器工具集
- `create_file_operations_toolset()`: 文件操作工具集

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

- 基于 Google ADK 构建
- 使用 MCP (Model Context Protocol) 标准
- 感谢所有贡献者的支持 