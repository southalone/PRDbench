"""
MCP连接重试和错误处理包装器
解决MCP服务连接失败、超时和取消错误的问题
"""

import asyncio
import logging
import time
from typing import Optional, Any, Dict, List
from contextlib import asynccontextmanager
import httpx
# 兼容导入不同命名的 SessionManager 类
try:
    from google.adk.tools.mcp_tool.mcp_session_manager import MCPSessionManager as _BaseSessionManager
except Exception:  # pragma: no cover - 环境差异容错
    from google.adk.tools.mcp_tool.mcp_session_manager import McpSessionManager as _BaseSessionManager

# 兼容导入不同命名的 MCPToolset 类
try:
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset as _BaseMCPToolset
except Exception:  # pragma: no cover - 环境差异容错
    from google.adk.tools.mcp_tool.mcp_toolset import McpToolset as _BaseMCPToolset

logger = logging.getLogger(__name__)


class RetryConfig:
    """重试配置类"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_backoff: bool = True,
        timeout: float = 30.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_backoff = exponential_backoff
        self.timeout = timeout


class RobustMcpSessionManager(_BaseSessionManager):
    """带重试机制的MCP会话管理器"""
    
    def __init__(self, *args, retry_config: Optional[RetryConfig] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry_config = retry_config or RetryConfig()
        self._connection_cache = {}
        
    async def create_session_with_retry(self, headers: Optional[Dict[str, str]] = None):
        """带重试机制的会话创建（兼容 headers）"""
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                logger.info(f"MCP连接尝试 {attempt + 1}/{self.retry_config.max_retries + 1}")
                
                # 设置超时
                async with asyncio.timeout(self.retry_config.timeout):
                    # 调用基类真正的创建方法，避免递归
                    session = await super().create_session(headers=headers)
                    logger.info("MCP连接成功建立")
                    return session
                    
            except asyncio.CancelledError as e:
                logger.warning(f"MCP连接被取消 (尝试 {attempt + 1}): {e}")
                last_exception = e
                
            except asyncio.TimeoutError as e:
                logger.warning(f"MCP连接超时 (尝试 {attempt + 1}): {e}")
                last_exception = e
                
            except httpx.ConnectError as e:
                logger.warning(f"MCP网络连接错误 (尝试 {attempt + 1}): {e}")
                last_exception = e
                
            except Exception as e:
                logger.warning(f"MCP连接未知错误 (尝试 {attempt + 1}): {e}")
                last_exception = e
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.retry_config.max_retries:
                delay = self._calculate_delay(attempt)
                logger.info(f"等待 {delay:.2f} 秒后重试...")
                await asyncio.sleep(delay)
        
        # 所有重试都失败
        logger.error(f"MCP连接失败，已重试 {self.retry_config.max_retries} 次")
        raise last_exception

    async def create_session(self, headers: Optional[Dict[str, str]] = None):
        """覆盖基类的 create_session，默认使用带重试版本。"""
        return await self.create_session_with_retry(headers=headers)
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算重试延迟时间"""
        if self.retry_config.exponential_backoff:
            delay = self.retry_config.base_delay * (2 ** attempt)
        else:
            delay = self.retry_config.base_delay
        
        return min(delay, self.retry_config.max_delay)


class RobustMcpToolset(_BaseMCPToolset):
    """带重试和容错机制的MCP工具集"""
    
    def __init__(self, *args, retry_config: Optional[RetryConfig] = None, **kwargs):
        # 先按基类正常初始化，获取 _connection_params / _errlog
        super().__init__(*args, **kwargs)
        self.retry_config = retry_config or RetryConfig()
        self._fallback_tools = []
        self._last_error: Optional[str] = None
        # 使用相同的 connection_params/errlog 构建健壮会话管理器，替换基类的
        try:
            self._mcp_session_manager = RobustMcpSessionManager(
                connection_params=self._connection_params,
                errlog=self._errlog,
                retry_config=self.retry_config,
            )
        except Exception as e:
            logger.warning(f"构建RobustMcpSessionManager失败，回退原管理器: {e}")
    
    async def get_tools(self, readonly_context=None):
        """覆盖原有方法，确保即使MCP失败也不抛异常，返回可降级结果。
        这样上层 FastAPI 不会 500，客户端可以正常拿到 JSON。
        """
        try:
            return await super().get_tools(readonly_context)
        except BaseException as e:
            logger.error(f"获取MCP工具失败(get_tools): {e}")
            self._last_error = str(e)
            # 返回降级工具或空列表，避免抛出导致 500
            if self._fallback_tools:
                logger.info("使用降级工具列表")
                return self._fallback_tools
            logger.warning("返回空工具列表")
            return []
    
    async def get_tools_with_retry(self, ctx):
        """带重试和降级的工具获取"""
        try:
            # 尝试正常获取MCP工具
            return await self.get_tools(ctx)
            
        except Exception as e:
            logger.error(f"获取MCP工具失败: {e}")
            
            # 返回降级工具或空列表
            if self._fallback_tools:
                logger.info("使用降级工具列表")
                return self._fallback_tools
            else:
                logger.warning("返回空工具列表")
                return []
    
    def set_fallback_tools(self, tools: List[Any]):
        """设置降级工具列表"""
        self._fallback_tools = tools


def apply_mcp_monkey_patches(retry_config: Optional[RetryConfig] = None):
    """将 ADK 的 MCP 类替换为健壮版本，避免抛出异常导致 /run 返回 500。
    - 替换 McpSessionManager 为 RobustMcpSessionManager，create_session 带重试
    - 替换 McpToolset 为 RobustMcpToolset，get_tools 捕获异常并返回降级结果
    """
    try:
        import google.adk.tools.mcp_tool.mcp_session_manager as mcp_session_module
        import google.adk.tools.mcp_tool.mcp_toolset as mcp_toolset_module

        # 补丁 SessionManager：确保 create_session 使用带重试的版本
        original_manager_lower = getattr(mcp_session_module, 'McpSessionManager', None)
        original_manager_upper = getattr(mcp_session_module, 'MCPSessionManager', None)

        class PatchedMcpSessionManager(RobustMcpSessionManager):
            def __init__(self, *args, **kwargs):
                # 透传必须参数 connection_params, errlog；retry_config 可选
                super().__init__(*args, retry_config=retry_config or RetryConfig(), **kwargs)
            async def create_session(self):
                return await self.create_session_with_retry()

        # 应用 SessionManager 补丁
        if original_manager_lower is not None:
            mcp_session_module.McpSessionManager = PatchedMcpSessionManager  # type: ignore[attr-defined]
        if original_manager_upper is not None:
            mcp_session_module.MCPSessionManager = PatchedMcpSessionManager  # type: ignore[attr-defined]

        # 补丁 Toolset：把原始 McpToolset 指向健壮版本
        original_toolset_lower = getattr(mcp_toolset_module, 'McpToolset', None)
        original_toolset_upper = getattr(mcp_toolset_module, 'MCPToolset', None)

        class PatchedMcpToolset(RobustMcpToolset):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, retry_config=retry_config or RetryConfig(), **kwargs)

        # 如果存在小写类名则覆盖
        if original_toolset_lower is not None:
            mcp_toolset_module.McpToolset = PatchedMcpToolset  # type: ignore[attr-defined]
        # 如果存在大写类名则覆盖
        if original_toolset_upper is not None:
            mcp_toolset_module.MCPToolset = PatchedMcpToolset  # type: ignore[attr-defined]

        logger.info("✅ MCP猴子补丁已应用：McpSessionManager 与 McpToolset 使用健壮版本")
        return {
            "patched": True,
            "original_manager_lower": str(original_manager_lower),
            "original_manager_upper": str(original_manager_upper),
            "original_toolset_lower": str(original_toolset_lower),
            "original_toolset_upper": str(original_toolset_upper)
        }
    except Exception as e:
        logger.error(f"应用 MCP 猴子补丁失败: {e}")
        return {"patched": False, "error": str(e)}


@asynccontextmanager
async def robust_mcp_connection(
    mcp_config: Dict[str, Any],
    retry_config: Optional[RetryConfig] = None
):
    """
    健壮的MCP连接上下文管理器
    
    Args:
        mcp_config: MCP配置字典
        retry_config: 重试配置
    """
    session_manager = None
    session = None
    
    try:
        # 创建带重试的session manager
        session_manager = RobustMcpSessionManager(
            retry_config=retry_config or RetryConfig()
        )
        
        # 尝试创建会话
        session = await session_manager.create_session_with_retry()
        
        yield session
        
    except Exception as e:
        logger.error(f"MCP连接完全失败: {e}")
        # 可以在这里实现降级逻辑
        yield None
        
    finally:
        # 清理资源
        if session:
            try:
                await session.close()
            except Exception as e:
                logger.warning(f"关闭MCP会话时出错: {e}")


class McpHealthChecker:
    """MCP服务健康检查器"""
    
    def __init__(self, mcp_url: str, check_interval: float = 60.0):
        self.mcp_url = mcp_url
        self.check_interval = check_interval
        self._is_healthy = False
        self._last_check = 0
    
    async def is_healthy(self) -> bool:
        """检查MCP服务是否健康"""
        current_time = time.time()
        
        # 如果距离上次检查不到check_interval秒，返回缓存结果
        if current_time - self._last_check < self.check_interval:
            return self._is_healthy
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.mcp_url)
                self._is_healthy = response.status_code == 200
                
        except Exception as e:
            logger.warning(f"MCP健康检查失败: {e}")
            self._is_healthy = False
        
        self._last_check = current_time
        return self._is_healthy


# Agent配置助手
class AgentConfigHelper:
    """Agent配置助手，处理MCP工具配置"""
    
    @staticmethod
    def create_robust_mcp_config(
        mcp_url: str,
        max_retries: int = 3,
        timeout: float = 30.0,
        enable_fallback: bool = True
    ) -> Dict[str, Any]:
        """创建健壮的MCP配置"""
        
        retry_config = RetryConfig(
            max_retries=max_retries,
            timeout=timeout,
            base_delay=1.0,
            max_delay=10.0,
            exponential_backoff=True
        )
        
        return {
            "mcp_url": mcp_url,
            "retry_config": retry_config,
            "enable_fallback": enable_fallback,
            "health_check_interval": 60.0
        }
    
    @staticmethod
    async def setup_robust_agent_tools(agent, mcp_configs: List[Dict[str, Any]]):
        """为Agent设置健壮的MCP工具"""
        robust_tools = []
        
        for config in mcp_configs:
            try:
                # 创建健壮的MCP工具集
                mcp_toolset = RobustMcpToolset(
                    retry_config=config.get("retry_config")
                )
                
                # 设置降级工具（如果需要）
                if config.get("enable_fallback"):
                    fallback_tools = []  # 这里可以添加备用工具
                    mcp_toolset.set_fallback_tools(fallback_tools)
                
                robust_tools.append(mcp_toolset)
                
            except Exception as e:
                logger.error(f"设置MCP工具失败: {e}")
                continue
        
        # 将工具添加到agent
        if robust_tools:
            agent.tools.extend(robust_tools)
        
        return robust_tools


# 使用示例和配置
async def example_robust_mcp_usage():
    """健壮MCP使用示例"""
    
    # 1. 基本重试配置
    retry_config = RetryConfig(
        max_retries=5,          # 最多重试5次
        base_delay=2.0,         # 基础延迟2秒
        max_delay=30.0,         # 最大延迟30秒
        exponential_backoff=True, # 使用指数退避
        timeout=45.0            # 单次连接超时45秒
    )
    
    # 2. 使用健壮的连接管理器
    mcp_config = {
        "url": "http://your-mcp-server:port",
        "headers": {"Authorization": "Bearer your-token"}
    }
    
    async with robust_mcp_connection(mcp_config, retry_config) as mcp_session:
        if mcp_session:
            logger.info("MCP连接成功，可以正常使用")
            # 使用MCP会话
        else:
            logger.warning("MCP连接失败，使用降级模式")
            # 降级逻辑
    
    # 3. 健康检查
    health_checker = McpHealthChecker("http://your-mcp-server:port/health")
    if await health_checker.is_healthy():
        logger.info("MCP服务健康")
    else:
        logger.warning("MCP服务不健康，建议检查")


# 实际应用的配置建议
MCP_PRODUCTION_CONFIG = {
    "retry_config": RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=15.0,
        exponential_backoff=True,
        timeout=30.0
    ),
    "enable_health_check": True,
    "health_check_interval": 60.0,
    "enable_fallback": True,
    "log_level": "INFO"
}

MCP_DEVELOPMENT_CONFIG = {
    "retry_config": RetryConfig(
        max_retries=1,
        base_delay=0.5,
        max_delay=5.0,
        exponential_backoff=False,
        timeout=10.0
    ),
    "enable_health_check": False,
    "enable_fallback": False,
    "log_level": "DEBUG"
} 