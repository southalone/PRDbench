import asyncio
from typing import AsyncGenerator, Dict, Optional
from pydantic import Field
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
import tiktoken
from datetime import datetime
import threading
import hashlib
import time

current_time = lambda: int(time.time())


class EarlyStopException(Exception):
    """自定义异常，用于强制停止agent执行"""
    def __init__(self, reason: str = "Early stop triggered"):
        self.reason = reason
        super().__init__(reason)

class LiteLlmWithSleep(LiteLlm):
    """
    Wrapper around LiteLlm that adds configurable sleep between responses.
    
    This allows you to control the rate of LLM responses without modifying
    the original library code.
    """
    
    sleep_duration: float = Field(default=2.0, description="Time to sleep between responses in seconds")
    enable_compression: bool = Field(default=False, description="是否启用压缩")
    max_tokens_threshold: int = Field(default=None, description="Token threshold to trigger compression")
    tokenizer: object = Field(default=None, description="Tokenizer for token counting")
    max_total_tokens: int = Field(default=5_000_000, description="Max total tokens for truncate")
    warning_threshold: float = Field(default=0.8, description="Warning threshold for total tokens")
    max_session_time: int = Field(default=3600, description="Max session time in seconds")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化session级别的token管理
        self._session_tokens: Dict[str, int] = {}
        self._session_times: Dict[str, int] = {}
        self._session_early_stop: Dict[str, bool] = {}
        self._session_early_stop_reason: Dict[str, str] = {}
        self._lock = threading.Lock()
        
        # 初始化tokenizer
        if self.tokenizer is None:
            try:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            except:
                self.tokenizer = None
    
    def _get_session_id(self, llm_request: LlmRequest) -> str:
        """获取或生成session ID"""
        # 从请求的custom_metadata中获取session_id，如果没有则生成一个
        # ADK不支持获取session ID，这里暂且用第一轮的prompt来代替
        # TODO后续更新为ADK支持的session ID
        first_prompt = str(llm_request.contents[0].parts[0].text)
        session_id = hashlib.md5(first_prompt.encode()).hexdigest()[:8]
        return session_id
    
    def _get_session_tokens(self, session_id: str) -> int:
        """获取指定session的token计数"""
        with self._lock:
            return self._session_tokens.get(session_id, 0)
    
    def _set_session_tokens(self, session_id: str, tokens: int):
        """设置指定session的token计数"""
        with self._lock:
            self._session_tokens[session_id] = tokens
    
    def _add_session_tokens(self, session_id: str, tokens: int):
        """为指定session添加token计数"""
        with self._lock:
            current = self._session_tokens.get(session_id, 0)
            self._session_tokens[session_id] = current + tokens


    def _get_session_times(self, session_id: str) -> int:
        """获取指定session的起始时间计数"""
        with self._lock:
            s_time = self._session_times.get(session_id, current_time())
            self._session_times[session_id] = s_time 
            return s_time
    
    def _set_session_times(self, session_id: str, times: int):
        """设置指定session的起始时间计数"""
        with self._lock:
            self._session_times[session_id] = times
    

    
    def _get_session_early_stop(self, session_id: str) -> bool:
        """获取指定session的early stop状态"""
        with self._lock:
            return self._session_early_stop.get(session_id, False)
    
    def _set_session_early_stop(self, session_id: str, triggered: bool, reason: str = None):
        """设置指定session的early stop状态"""
        with self._lock:
            self._session_early_stop[session_id] = triggered
            self._session_early_stop_reason[session_id] = str(reason)
    
    def reset_session_tokens(self, session_id: str):
        """重置指定session的token计数"""
        with self._lock:
            self._session_tokens[session_id] = 0
            self._session_early_stop[session_id] = False

    def get_session_token_info(self, session_id: str) -> dict:
        """获取指定session的token使用信息"""
        current_tokens = self._get_session_tokens(session_id)
        start_time = self._get_session_times(session_id)
        return {
            "session_id": session_id,
            "current_tokens": current_tokens,
            "start_time": start_time,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": current_tokens / self.max_total_tokens if self.max_total_tokens else 0,
            "early_stop_triggered": self._get_session_early_stop(session_id),
        }

    def set_new_response_info(self, old_request, new_request):
        # 把老的会话的token计数和起始时间设置到新的会话中
        old_session_id = self._get_session_id(old_request)
        new_session_id = self._get_session_id(new_request)
        old_token_count = self._get_session_tokens(old_session_id)
        self._set_session_tokens(new_session_id, old_token_count)
        old_start_time = self._get_session_times(old_session_id)
        self._set_session_times(new_session_id, old_start_time)

    def count_tokens_with_tiktoken(self, text: str) -> int:
        """使用 tiktoken 计算 token 数量"""
        return len(self.tokenizer.encode(text))


 
    
    def _update_token_count(self, llm_request: LlmRequest, response: LlmResponse, session_id: str):
        """更新指定session的token计数"""
        import logging
        logger = logging.getLogger(__name__)
        request_tokens = response.usage_metadata.prompt_token_count
        response_tokens = response.usage_metadata.candidates_token_count
        total_tokens = request_tokens + response_tokens
        logger.info(f"Session {session_id}: 请求token数: {request_tokens}, 响应token数: {response_tokens}, 总token数: {total_tokens}")


        self._add_session_tokens(session_id, total_tokens)
        
        
        # 检查是否超过限制
        current_total = self._get_session_tokens(session_id)
        
        if self.max_total_tokens and current_total >= self.max_total_tokens:
            self._set_session_early_stop(session_id, True, reason=f"Token使用量已达到上限 ({current_total}/{self.max_total_tokens})")
            logger.warning(f"Session {session_id}: Token使用量已达到上限 ({current_total}/{self.max_total_tokens})")
        else:
            logger.info(f"Session {session_id}: 当前token数: {current_total}, 最大token数: {self.max_total_tokens}")
        if current_time() >= self._get_session_times(session_id) + self.max_session_time:
            self._set_session_early_stop(session_id, True, reason=f"会话时间已达到上限 ({ current_time() - self._get_session_times(session_id)}s/{self.max_session_time}s)")
            logger.warning(f"Session {session_id}: 会话时间已达到上限 ({ current_time() - self._get_session_times(session_id)}s/{self.max_session_time}s)")
        else:
            logger.info(f"Session {session_id}: 会话时间: {current_time() - self._get_session_times(session_id)}s, 最大会话时间: {self.max_session_time}s")
    
    def _create_exit_loop_response(self, session_id: str = None, reason=None) -> LlmResponse:
        """创建包含exit_loop工具调用的响应"""
        # 标记已触发early stop
        if session_id:
            self._set_session_early_stop(session_id, True, reason=reason)
        if reason:
            reason = f"reason: {reason}"
        
        # 获取当前session的token信息
        current_tokens = self._get_session_tokens(session_id) if session_id else 0
        
        # 创建一个更明确的停止响应
        return LlmResponse(
            content=types.Content(
                role="assistant",
                parts=[
                    types.Part(text=f"{reason}，正在退出...")
                ]
            ),
            partial=False,  # 表示这是完整响应
            turn_complete=True,  # 表示对话轮次完成
            error_code="TOKEN_LIMIT_EXCEEDED" if reason is None else reason,  # 使用错误代码
            error_message=f"reason: {reason}",
            interrupted=True,  # 标记为被中断
            custom_metadata={
                "early_stop": True,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "force_stop": True,
                "stop_immediately": True,
                "no_more_responses": True,  # 标记不再生成响应
                "session_should_end": True,  # 明确标记会话应该结束
                "session_id": session_id  # 添加session_id
            }
        )
    
    def _force_early_stop(self, reason: str = "Token limit exceeded"):
        """强制触发early stop并抛出异常"""
        self.early_stop_triggered = True
        raise EarlyStopException(reason)

    def reset_token_count(self):
        """重置token计数（保持向后兼容）"""
        # 这个方法现在重置所有session的token计数
        with self._lock:
            self._session_tokens.clear()
            self._session_early_stop.clear()
    
    def force_reset_early_stop(self):
        """强制重置early stop状态（保持向后兼容）"""
        # 这个方法现在重置所有session的early stop状态
        with self._lock:
            self._session_early_stop.clear()
        import logging
        logger = logging.getLogger(__name__)
        logger.info("所有session的Early stop状态已重置")
    
    def is_early_stop_triggered(self) -> bool:
        """检查是否已触发early stop（保持向后兼容）"""
        # 这个方法现在检查是否有任何session触发了early stop
        with self._lock:
            return any(self._session_early_stop.values())
    
    def get_token_usage_info(self) -> dict:
        """获取token使用信息（保持向后兼容）"""
        # 这个方法现在返回所有session的总token使用信息
        with self._lock:
            total_tokens = sum(self._session_tokens.values())
            total_early_stop = sum(self._session_early_stop.values())
        
        return {
            "total_sessions": len(self._session_tokens),
            "total_tokens": total_tokens,
            "max_tokens": self.max_total_tokens,
            "usage_ratio": total_tokens / self.max_total_tokens if self.max_total_tokens else 0,
            "early_stop_sessions": total_early_stop,
            "session_details": {
                session_id: self.get_session_token_info(session_id)
                for session_id in self._session_tokens.keys()
            }
        }
    
    def _add_token_warning_to_request(self, llm_request: LlmRequest, session_id: str) -> LlmRequest:
        """在请求中添加token警告信息"""
        current_tokens = self._get_session_tokens(session_id)
        
        if self.max_total_tokens and self.warning_threshold:
            usage_ratio = current_tokens / self.max_total_tokens
            if usage_ratio >= self.warning_threshold:
                warning_message = f"\n⚠️ 警告: 当前token使用率已达到 {usage_ratio:.1%} ({current_tokens}/{self.max_total_tokens})，请控制回复长度。"
                
                # 在第一个content的parts开头添加警告
                if llm_request.contents and llm_request.contents[0].parts:
                    # 创建新的parts列表，在开头添加警告
                    new_parts = [types.Part(text=warning_message)]
                    new_parts.extend(llm_request.contents[0].parts)
                    
                    # 创建新的content
                    new_content = types.Content(
                        role=llm_request.contents[0].role,
                        parts=new_parts
                    )
                    
                    # 创建新的request
                    new_request = LlmRequest(
                        contents=[new_content] + llm_request.contents[1:],
                        config=llm_request.config
                    )

                    # 压缩后的request需要继承之前的token计数
                    self.set_new_response_info(llm_request, new_request)


                    return new_request
        
        return llm_request
    
    def string_to_contents(self, compressed_string: str) -> list[types.Content]:
        """将压缩后的字符串转换回 Content 列表"""
        # 压缩后的内容使用 "summary" 角色，更准确地表示这是摘要内容
        
        return [types.Content(
            role="summary",  # 使用 "summary" 而不是 "user"
            parts=[types.Part.from_text(text=compressed_string)]
        )]
        
    def content_to_string(self, content: types.Content) -> str:
        """将单个 Content 转换为字符串"""
        if not content.parts:
            return ""
        
        parts_text = []
        for part in content.parts:
            if part.text:
                parts_text.append(f"[{content.role}]: {part.text}")
            elif part.function_call:
                parts_text.append(f"[{content.role} function_call]: {part.function_call}")
            elif part.function_response:
                parts_text.append(f"[{content.role} function_response]: {part.function_response}")
        
        return "\n".join(parts_text)

    def contents_to_string(self, contents: list[types.Content]) -> str:
        """将 contents 列表转换为字符串"""
        return "\n\n".join(self.content_to_string(content) for content in contents)
    
    def should_compress(self, llm_request: LlmRequest) -> bool:
        """判断是否需要压缩"""
        if not self.enable_compression:
            return False
        
        # 计算 contents 的 token 数量
        content_string = self.contents_to_string(llm_request.contents)
        content_tokens = self.count_tokens_with_tiktoken(content_string)
        import logging
        logger = logging.getLogger(__name__)
        if content_tokens > self.max_tokens_threshold:
            logger.info(f"content_tokens: {content_tokens}, max_tokens_threshold: {self.max_tokens_threshold}")
            # logger.info(f"开启压缩token")
        return content_tokens > self.max_tokens_threshold
    
    async def compress_with_llm_async(self, llm_request: LlmRequest) -> LlmRequest:
        """异步使用 LLM 压缩 LlmRequest 中的 contents"""
        # not in use
        # 分离历史内容和当前用户提问
        if len(llm_request.contents) <= 2:
            # 如果只有两个content，不需要压缩
            return llm_request
        
        # 保留第一个和最后一个content（通常是当前用户提问）
        first_content = llm_request.contents[0]
        historical_contents = llm_request.contents[1:]
    
        # 1. 将 contents 转换为字符串
        content_string = self.contents_to_string(historical_contents)
        compression_prompt = f"""You are the component that summarizes internal chat history into a given structure.
When the conversation history grows too large, you will be invoked to distill the entire history into a concise, structured XML snapshot. This snapshot is CRITICAL, as it will become the agent's *only* memory of the past. The agent will resume its work based solely on this snapshot. All crucial details, plans, errors, and user directives MUST be preserved.

First, you will think through the entire history in a private <scratchpad>. Review the user's overall goal, the agent's actions, tool outputs, file modifications, and any unresolved questions. Identify every piece of information that is essential for future actions.

After your reasoning is complete, generate the final <state_snapshot> XML object. Be incredibly dense with information. Omit any irrelevant conversational filler.

The structure MUST be as follows:
<state_snapshot>
    <overall_goal>
        <!-- A single, concise sentence describing the user's high-level objective. -->
    </overall_goal>
    <key_knowledge>
        <!-- Crucial facts, conventions, and constraints the agent must remember based on the conversation history and interaction with the user. Use bullet points. -->
    </key_knowledge>
    <file_system_state>
        <!-- List files that have been created, read, modified, or deleted. Note their status and critical learnings. -->
    </file_system_state>
    <recent_actions>
        <!-- A summary of the last few significant agent actions and their outcomes. Focus on facts. -->
    </recent_actions>
    <current_plan>
        <!-- The agent's step-by-step plan. Mark completed steps. -->
    </current_plan>
</state_snapshot>
"""
        
        # 2. 创建压缩请求，将压缩指令作为 system prompt
        compression_request = LlmRequest(
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=content_string)]
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=compression_prompt,
                temperature=0.1,
                max_output_tokens=2000
            )
        )


        import logging
        logger = logging.getLogger(__name__)
        # logger.info(f"压缩前，first prompt: {llm_request.contents[0].parts[0].text}")
        logger.info(f"压缩前，first prompt length: {len(llm_request.contents[0].parts[0].text.strip())}")
        if len(llm_request.contents[0].parts[0].text.strip()) < 5:
            logger.info(f"压缩前，first prompt长度异常")
        
        
        # 3. 临时禁用压缩以避免递归
        original_enable_compression = self.enable_compression
        try:
            self.enable_compression = False
            
            # 4. 调用 LLM 进行压缩
            compressed_content = ""
            async for response in super().generate_content_async(compression_request, stream=False):
                if response.content and response.content.parts:
                    for part in response.content.parts:
                        if part.text:
                            compressed_content += part.text
            

            llm_request.contents = [
                first_content,
                types.Content(
                    role="summary",
                    parts=[types.Part.from_text(text=compressed_content)]
                )
            ]
            # self.set_new_response_info(llm_request, compressed_request)

            logger.info(f"压缩后, content长度: {len(compressed_content)}")

            
        finally:
            self.enable_compression = original_enable_compression
    
    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False, retry_count: int = 0, max_retries: int = 4
    ) -> AsyncGenerator[LlmResponse, None]:
        """
        Generates content asynchronously with sleep between responses.
        
        Args:
            llm_request: The request to send to the model
            stream: Whether to stream the response
            retry_count: 当前重试次数
            max_retries: 最大重试次数
            
        Yields:
            LlmResponse: The model response with sleep between yields
        """
        session_id = self._get_session_id(llm_request)
        # 检查是否已经触发early stop
        if self._get_session_early_stop(session_id):
            yield self._create_exit_loop_response(session_id, reason=self._session_early_stop_reason.get(session_id))
            return
            
        # 检查token限制
        if self.max_total_tokens and self._get_session_tokens(session_id) >= self.max_total_tokens:
            yield self._create_exit_loop_response(session_id, f"Token使用量已达到上限: {self.max_total_tokens}")
            return 
        
        # 检查时间限制
        if current_time() >= self._get_session_times(session_id) + self.max_session_time:
            yield self._create_exit_loop_response(session_id, f"会话时间已达到上限: {self.max_session_time}s")
            return

            
        
        # 在请求中添加token警告信息（如果超过警告阈值）
        llm_request = self._add_token_warning_to_request(llm_request, session_id)
        if self.should_compress(llm_request):
            # 2. 提示模型进行压缩，
            llm_request.contents.append(types.Content(
                role="warning",
                parts=[types.Part.from_text(text="Your conversation history token usage has reached limit. In subsequent interactions, earlier parts of the conversation may be truncated. It is recommended that you summarize your conversation history and save it to a file for future reference.")]
            ))
            # assert len(llm_request.contents) == 3
        # Get the original generator from the parent class
        try:
            import logging
            logger = logging.getLogger(__name__)
            # logger.info('--------------------------------')
            # logger.info(f"prompt now:{llm_request}")
            async for response in super().generate_content_async(llm_request, stream):
                # 更新token计数
                self._update_token_count(llm_request, response, session_id)
                # Yield the response
                yield response
                
                # Add sleep after each response (except the last one if needed)
                if self.sleep_duration > 0:
                    await asyncio.sleep(self.sleep_duration)
                    
        except Exception as e:
            # 如果发生异常，检查是否可以重试
            import logging
            logger = logging.getLogger(__name__)
            
            if retry_count < max_retries:
                # 可以重试，增加重试计数
                retry_count += 1
                logger.warning(f"生成内容时发生异常: {e}，正在进行第 {retry_count} 次重试...")
        
                # 短暂等待后重试
                await asyncio.sleep(1)

                # 递归调用自身进行重试
                async for response in self.generate_content_async(llm_request, stream, retry_count, max_retries):
                    yield response
                return
            else:
                # 达到最大重试次数，触发early stop
                logger.error(f"生成内容时发生异常: {e}，已达到最大重试次数 {max_retries}")
                self._set_session_early_stop(session_id, True, reason=f"生成内容时发生异常: {e}，已重试 {max_retries} 次")
                yield self._create_exit_loop_response(session_id, reason=f"生成内容时发生异常: {e}，已重试 {max_retries} 次")
                return

        # 最后检查一次，确保没有遗漏
        if self._get_session_early_stop(session_id):
            yield self._create_exit_loop_response(session_id, reason=self._session_early_stop_reason.get(session_id))
            return
