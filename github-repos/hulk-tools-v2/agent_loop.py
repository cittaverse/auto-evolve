#!/usr/bin/env python3
"""
Agent 循环重构 — 参考 Claude Code ReAct 模式

核心思想:
1. ReAct 循环 — Reason → Act → Observe → Iterate
2. 迭代限制 — 防止无限循环
3. 工具调用闭环 — 模型决定调用什么工具

深度实现:
- 完整 ReAct 循环
- 工具调用验证
- 错误恢复机制
- 状态追踪
"""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, AsyncIterator
from datetime import datetime
from enum import Enum

try:
    from .tool_system import Tool, ToolRegistry
    from .context_manager import ContextManager, MessageRole
    from .streaming import StreamGenerator, ChunkType
    from .hook_system import HulkHookEngine
except ImportError:
    from tool_system import Tool, ToolRegistry
    from context_manager import ContextManager, MessageRole
    from streaming import StreamGenerator, ChunkType
    from hook_system import HulkHookEngine


# === Agent 状态 ===

class AgentState(str, Enum):
    """Agent 状态"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    ERROR = "error"
    DONE = "done"


@dataclass
class AgentConfig:
    """Agent 配置"""
    model: str = "qwen3.5-plus"
    max_iterations: int = 20
    max_tokens: int = 8192
    temperature: float = 0.7
    timeout_seconds: int = 300


@dataclass
class ToolCall:
    """工具调用"""
    id: str
    name: str
    args: Dict[str, Any]
    result: Any = None
    error: Optional[str] = None


# === Agent 循环实现 ===

class AgentLoop:
    """
    Agent 循环 — ReAct 模式实现
    
    循环流程:
    1. Reason: 调用模型，获取下一步行动
    2. Act: 执行工具调用 (如果有)
    3. Observe: 记录工具结果到上下文
    4. Iterate: 重复直到任务完成或达到最大迭代
    """
    
    def __init__(
        self,
        tool_registry: ToolRegistry,
        context: ContextManager,
        config: Optional[AgentConfig] = None,
        hooks_enabled: bool = True
    ):
        self.tools = tool_registry
        self.context = context
        self.config = config or AgentConfig()
        self.state = AgentState.IDLE
        self.current_iteration = 0
        self.tool_calls: List[ToolCall] = []
        
        # Hook 系统
        self.hooks_enabled = hooks_enabled
        self.hooks = HulkHookEngine() if hooks_enabled else None
    
    async def run(
        self,
        prompt: str,
        stream: Optional[StreamGenerator] = None
    ) -> Any:
        """
        运行 Agent 循环
        
        Args:
            prompt: 用户输入
            stream: 流式生成器 (可选)
            
        Returns:
            最终结果
        """
        # 1. 初始化
        self.state = AgentState.THINKING
        self.current_iteration = 0
        self.tool_calls = []
        
        # 添加用户输入到上下文
        self.context.add_message(MessageRole.USER, prompt)
        
        if stream:
            await stream.status(f"Starting agent loop (max {self.config.max_iterations} iterations)...")
        
        # 2. 进入循环
        while self.current_iteration < self.config.max_iterations:
            self.current_iteration += 1
            
            if stream:
                await stream.progress(
                    self.current_iteration,
                    self.config.max_iterations,
                    f"Iteration {self.current_iteration}"
                )
            
            # 3. Reason: 调用模型
            self.state = AgentState.THINKING
            if stream:
                await stream.status("Thinking...")
            
            response = await self._call_model()
            
            # 4. 检查响应
            if self._has_tool_calls(response):
                # 4a. 有工具调用 → Act
                self.state = AgentState.ACTING
                tool_calls = self._parse_tool_calls(response)
                
                for tool_call in tool_calls:
                    result = await self._execute_tool(tool_call, stream)
                    tool_call.result = result
                    
                    # 4b. Observe: 记录结果
                    self.state = AgentState.OBSERVING
                    self._add_tool_result(tool_call)
                    
                    if stream:
                        await stream.tool_result(tool_call.name, result)
                
            elif self._has_content(response):
                # 4c. 有文本内容 → 完成
                self.state = AgentState.DONE
                content = self._get_content(response)
                
                if stream:
                    await stream.text(content)
                    await stream.done(content)
                
                return content
            
            else:
                # 4d. 空响应 → 错误
                self.state = AgentState.ERROR
                if stream:
                    await stream.error("Empty response from model")
                raise ValueError("Empty response from model")
        
        # 5. 达到最大迭代
        self.state = AgentState.ERROR
        if stream:
            await stream.error(f"Max iterations ({self.config.max_iterations}) reached")
        raise RuntimeError(f"Max iterations ({self.config.max_iterations}) reached")
    
    async def _call_model(self) -> Any:
        """调用模型"""
        # 获取上下文消息
        messages = self.context.get_messages()
        
        # 调用模型 (这里用伪代码，实际调用 web_search 或其他 API)
        # response = await call_llm_api(
        #     model=self.config.model,
        #     messages=messages,
        #     max_tokens=self.config.max_tokens,
        #     temperature=self.config.temperature,
        #     tools=self.tools.list_tools()
        # )
        
        # 模拟响应
        await asyncio.sleep(0.5)
        return {
            "content": f"Task completed after {self.current_iteration} iterations.",
            "tool_calls": []
        }
    
    def _has_tool_calls(self, response: Any) -> bool:
        """检查是否包含工具调用"""
        if isinstance(response, dict):
            return bool(response.get("tool_calls"))
        return False
    
    def _parse_tool_calls(self, response: Any) -> List[ToolCall]:
        """解析工具调用"""
        tool_calls = []
        for i, tc in enumerate(response.get("tool_calls", [])):
            tool_call = ToolCall(
                id=f"call_{i}",
                name=tc.get("name", "unknown"),
                args=tc.get("args", {})
            )
            tool_calls.append(tool_call)
        return tool_calls
    
    def _has_content(self, response: Any) -> bool:
        """检查是否包含文本内容"""
        if isinstance(response, dict):
            return bool(response.get("content"))
        return False
    
    def _get_content(self, response: Any) -> str:
        """获取文本内容"""
        if isinstance(response, dict):
            return response.get("content", "")
        return str(response)
    
    async def _execute_tool(
        self,
        tool_call: ToolCall,
        stream: Optional[StreamGenerator] = None
    ) -> Any:
        """执行工具 (带 Hook 检查)"""
        if stream:
            await stream.tool_call(tool_call.name, tool_call.args)
        
        # 1. PreToolUse Hook
        if self.hooks_enabled and self.hooks:
            hook_input = {
                "hook_event": f"pre_{tool_call.name}",
                "tool_name": tool_call.name,
                "args": tool_call.args
            }
            hook_result = self.hooks.evaluate("pre_tool_use", hook_input)
            
            if hook_result.get("decision") == "block":
                reason = hook_result.get("reason", "Blocked by hook")
                if stream:
                    await stream.error(f"Hook blocked: {reason}")
                return {"error": reason, "blocked_by_hook": True}
            
            # 显示警告
            if hook_result.get("systemMessage"):
                if stream:
                    await stream.text(f"⚠️ {hook_result['systemMessage']}")
        
        # 2. 执行工具
        try:
            result = await self.tools.execute(tool_call.name, tool_call.args)
            
            # 3. PostToolUse Hook
            if self.hooks_enabled and self.hooks:
                hook_input["result"] = result
                self.hooks.evaluate("post_tool_use", hook_input)
            
            return result
        except Exception as e:
            tool_call.error = str(e)
            return {"error": str(e)}
    
    def _add_tool_result(self, tool_call: ToolCall):
        """添加工具结果到上下文"""
        self.context.add_message(
            role=MessageRole.TOOL,
            content={
                "tool_call_id": tool_call.id,
                "tool_name": tool_call.name,
                "result": tool_call.result,
                "error": tool_call.error
            },
            priority=3  # 工具结果优先级较低
        )
    
    def get_state(self) -> Dict:
        """获取当前状态"""
        return {
            "state": self.state.value,
            "iteration": self.current_iteration,
            "max_iterations": self.config.max_iterations,
            "tool_calls": len(self.tool_calls),
            "context_tokens": self.context.get_token_count()
        }


# === 使用示例 ===

async def example_usage():
    """使用示例"""
    print("=" * 60)
    print("Agent 循环演示 — ReAct 模式")
    print("=" * 60)
    print()
    
    # 1. 创建工具注册表
    from .tool_system import ToolRegistry, WebSearchTool, ExecTool
    registry = ToolRegistry()
    registry.register(WebSearchTool())
    registry.register(ExecTool())
    
    # 2. 创建上下文管理器
    context = ContextManager(max_tokens=128000)
    context.add_system_message("You are a helpful AI research assistant.")
    
    # 3. 创建 Agent 循环
    config = AgentConfig(max_iterations=10)
    agent = AgentLoop(registry, context, config)
    
    # 4. 运行
    from .streaming import StreamGenerator, TerminalStreamHandler, StreamExecutor
    
    async def task(stream: StreamGenerator) -> AsyncIterator:
        result = await agent.run("Search for recent AI news and summarize.", stream)
        for chunk in stream.get_chunks():
            yield chunk
    
    executor = StreamExecutor(TerminalStreamHandler(show_timestamp=True))
    result = await executor.execute(task)
    
    print()
    print(f"最终结果：{result}")
    print()
    print(f"Agent 状态：{agent.get_state()}")


async def main():
    try:
        await example_usage()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
