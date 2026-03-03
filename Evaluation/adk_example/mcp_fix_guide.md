# MCP连接问题修复指南

## 问题症状
```
asyncio.exceptions.CancelledError: Cancelled by cancel scope
```
在Agent初始化时MCP连接失败。

## 解决方案

### 1. 立即修复 - 猴子补丁方式

在你的Agent初始化代码前添加：

```python
import asyncio
import logging
from mcp_retry_wrapper import RetryConfig, RobustMcpSessionManager

# 设置日志以便观察重试过程
logging.basicConfig(level=logging.INFO)

# 全局补丁MCP会话管理器
def patch_mcp_session_manager():
    """全局替换MCP会话管理器为重试版本"""
    import google.adk.tools.mcp_tool.mcp_session_manager as mcp_module
    
    # 保存原始类
    original_manager = mcp_module.McpSessionManager
    
    # 创建重试配置
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=2.0,
        max_delay=15.0,
        timeout=30.0,
        exponential_backoff=True
    )
    
    # 替换为健壮版本
    class PatchedMcpSessionManager(RobustMcpSessionManager):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, retry_config=retry_config, **kwargs)
        
        async def create_session(self):
            # 使用带重试的版本
            return await self.create_session_with_retry()
    
    # 应用补丁
    mcp_module.McpSessionManager = PatchedMcpSessionManager
    print("✅ MCP重试补丁已应用")

# 在Agent创建前调用
patch_mcp_session_manager()

# 然后正常创建你的Agent
# agent = Agent(...)
```

### 2. 配置优化方式

修改你的Agent配置：

```python
from mcp_retry_wrapper import MCP_PRODUCTION_CONFIG, RetryConfig

# 1. 增加MCP连接超时时间
mcp_config = {
    "connection_timeout": 45.0,  # 增加到45秒
    "read_timeout": 60.0,        # 读取超时60秒
    "max_retries": 3,            # 最多重试3次
}

# 2. 设置更宽松的asyncio超时
asyncio_config = {
    "default_timeout": 120.0,    # 默认超时2分钟
    "mcp_timeout": 60.0,         # MCP专用超时1分钟
}

# 3. 在创建Agent时应用配置
agent = Agent(
    model=your_model,
    tools=your_tools,
    # 添加MCP相关配置
    **mcp_config
)
```

### 3. 环境变量配置

设置环境变量来控制重试行为：

```bash
# 在启动脚本或.env文件中
export MCP_MAX_RETRIES=5
export MCP_CONNECTION_TIMEOUT=45
export MCP_BASE_DELAY=2.0
export MCP_MAX_DELAY=30.0
export MCP_ENABLE_FALLBACK=true
```

然后在代码中读取：

```python
import os

retry_config = RetryConfig(
    max_retries=int(os.getenv("MCP_MAX_RETRIES", 3)),
    timeout=float(os.getenv("MCP_CONNECTION_TIMEOUT", 30.0)),
    base_delay=float(os.getenv("MCP_BASE_DELAY", 1.0)),
    max_delay=float(os.getenv("MCP_MAX_DELAY", 15.0)),
)
```

### 4. 完整的Agent包装器

创建一个健壮的Agent包装器：

```python
from mcp_retry_wrapper import RobustMcpSessionManager, RetryConfig
import asyncio
import logging

class RobustAgent:
    """带MCP重试机制的Agent包装器"""
    
    def __init__(self, original_agent, retry_config=None):
        self.agent = original_agent
        self.retry_config = retry_config or RetryConfig(
            max_retries=3,
            timeout=30.0,
            base_delay=2.0
        )
        self._setup_mcp_retry()
    
    def _setup_mcp_retry(self):
        """设置MCP重试机制"""
        # 这里可以添加更多的重试逻辑
        pass
    
    async def run_with_retry(self, *args, **kwargs):
        """带重试的Agent运行"""
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                return await self.agent.run(*args, **kwargs)
            except asyncio.CancelledError as e:
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.base_delay * (2 ** attempt)
                    logging.warning(f"Agent运行失败，{delay}秒后重试...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise e
            except Exception as e:
                logging.error(f"Agent运行出错: {e}")
                raise e

# 使用方式
# original_agent = Agent(...)
# robust_agent = RobustAgent(original_agent)
# result = await robust_agent.run_with_retry(your_request)
```

## 诊断工具

### 1. MCP连接测试脚本

```python
import asyncio
import httpx
from mcp_retry_wrapper import McpHealthChecker

async def diagnose_mcp_connection(mcp_url: str):
    """诊断MCP连接问题"""
    
    print(f"🔍 诊断MCP连接: {mcp_url}")
    
    # 1. 基本网络连通性测试
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(mcp_url)
            print(f"✅ HTTP连接正常: {response.status_code}")
    except Exception as e:
        print(f"❌ HTTP连接失败: {e}")
        return False
    
    # 2. MCP健康检查
    health_checker = McpHealthChecker(mcp_url)
    is_healthy = await health_checker.is_healthy()
    print(f"{'✅' if is_healthy else '❌'} MCP服务健康状态: {is_healthy}")
    
    # 3. 延迟测试
    try:
        import time
        start_time = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(mcp_url)
        latency = (time.time() - start_time) * 1000
        print(f"📊 连接延迟: {latency:.2f}ms")
    except Exception as e:
        print(f"❌ 延迟测试失败: {e}")
    
    return True

# 使用方式
# asyncio.run(diagnose_mcp_connection("http://your-mcp-server:port"))
```

### 2. 日志监控

```python
import logging

# 设置详细的MCP日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 专门监控MCP相关日志
mcp_logger = logging.getLogger('mcp_retry_wrapper')
mcp_logger.setLevel(logging.INFO)

# 添加文件日志
file_handler = logging.FileHandler('mcp_connections.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
mcp_logger.addHandler(file_handler)
```

## 常见问题和解决方案

### Q: 重试次数应该设置多少？
**A:** 
- 开发环境：1-2次重试即可
- 生产环境：3-5次重试
- 网络不稳定环境：可以增加到10次

### Q: 超时时间如何设置？
**A:**
- 本地MCP服务：10-15秒
- 远程MCP服务：30-45秒
- 公网MCP服务：60秒以上

### Q: 如何处理完全无法连接的情况？
**A:** 使用降级模式：
```python
# 设置备用工具或跳过MCP工具
if not mcp_available:
    agent.tools = [basic_tool1, basic_tool2]  # 使用基础工具
    logger.warning("MCP不可用，使用基础工具集")
```

### Q: 如何判断是临时故障还是配置问题？
**A:** 
- 查看错误类型：`CancelledError`通常是临时的
- 查看重试模式：如果所有重试都在同一位置失败，可能是配置问题
- 检查网络：使用诊断脚本测试基本连通性

## 推荐配置

**生产环境**：
```python
RetryConfig(
    max_retries=3,
    base_delay=2.0,
    max_delay=15.0,
    exponential_backoff=True,
    timeout=45.0
)
```

**开发环境**：
```python
RetryConfig(
    max_retries=1,
    base_delay=1.0,
    max_delay=5.0,
    exponential_backoff=False,
    timeout=15.0
)
``` 