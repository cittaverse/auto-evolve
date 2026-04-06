#!/usr/bin/env python3
"""
完整测试套件 — 参考 Claude Code 测试策略

测试覆盖:
1. 单元测试 — 工具接口/参数验证/权限控制
2. 集成测试 — Agent 循环/上下文管理
3. 边界测试 — 最大迭代/Token 限制/超时

深度实现:
- Mock 外部依赖
- 异步测试
- 覆盖率报告
- CI 集成
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# 导入被测模块
from tool_system import Tool, ToolRegistry, WebSearchTool, ExecTool
from permission_system import PermissionManager, SafeToolExecutor, SENSITIVE_TOOLS
from resume_system import StateManager, ResumableTask
from streaming import (
    StreamChunk, ChunkType, StreamGenerator,
    TerminalStreamHandler, StreamExecutor
)
from context_manager import (
    ContextManager, Message, MessageRole,
    TokenCounter, TrimmingStrategy
)
from agent_loop import AgentLoop, AgentConfig, AgentState, ToolCall


# ============================================
# P0 测试 — 工具系统
# ============================================

class TestToolSystem:
    """工具系统测试"""
    
    def test_web_search_tool_properties(self):
        """测试 WebSearchTool 属性"""
        tool = WebSearchTool()
        assert tool.name == "web_search"
        assert "search" in tool.description.lower()
        assert "query" in tool.parameters
        assert "count" in tool.parameters
    
    def test_tool_to_dict(self):
        """测试工具序列化"""
        tool = WebSearchTool()
        schema = tool.to_dict()
        assert "name" in schema
        assert "description" in schema
        assert "parameters" in schema
    
    @pytest.mark.asyncio
    async def test_web_search_execute(self):
        """测试 WebSearchTool 执行"""
        tool = WebSearchTool()
        result = await tool.execute({"query": "AI news", "count": 3})
        assert result["status"] == "ok"
        assert result["query"] == "AI news"
        assert result["count"] == 3
    
    @pytest.mark.asyncio
    async def test_web_search_missing_param(self):
        """测试缺少必填参数"""
        tool = WebSearchTool()
        result = await tool.execute({})
        assert "error" in result
        assert "query" in result["error"]


class TestToolRegistry:
    """工具注册表测试"""
    
    def test_register_tool(self):
        """测试注册工具"""
        registry = ToolRegistry()
        tool = WebSearchTool()
        registry.register(tool)
        assert "web_search" in registry.tools
    
    def test_get_tool(self):
        """测试获取工具"""
        registry = ToolRegistry()
        registry.register(WebSearchTool())
        tool = registry.get("web_search")
        assert isinstance(tool, WebSearchTool)
    
    def test_get_unknown_tool(self):
        """测试获取不存在的工具"""
        registry = ToolRegistry()
        with pytest.raises(ValueError, match="Unknown tool"):
            registry.get("nonexistent")
    
    def test_list_tools(self):
        """测试列出工具"""
        registry = ToolRegistry()
        registry.register(WebSearchTool())
        tools = registry.list_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "web_search"
    
    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """测试执行工具"""
        registry = ToolRegistry()
        registry.register(WebSearchTool())
        result = await registry.execute("web_search", {"query": "test"})
        assert result["status"] == "ok"


# ============================================
# P0 测试 — 权限系统
# ============================================

class TestPermissionSystem:
    """权限系统测试"""
    
    def test_sensitive_tools_defined(self):
        """测试敏感工具定义"""
        assert "exec" in SENSITIVE_TOOLS
        assert "write_file" in SENSITIVE_TOOLS
        assert "delete_file" in SENSITIVE_TOOLS
    
    @pytest.mark.asyncio
    async def test_non_sensitive_tool(self):
        """测试非敏感工具无需确认"""
        pm = PermissionManager(auto_confirm=False)
        confirmed = await pm.confirm("web_search", {"query": "test"})
        assert confirmed is True
    
    @pytest.mark.asyncio
    async def test_sensitive_tool_auto_confirm(self):
        """测试自动确认模式"""
        pm = PermissionManager(auto_confirm=True)
        confirmed = await pm.confirm("exec", {"command": "ls"})
        assert confirmed is True
    
    @pytest.mark.asyncio
    async def test_safe_tool_executor_denied(self):
        """测试用户拒绝敏感操作"""
        pm = PermissionManager(auto_confirm=False)
        
        # Mock confirm 返回 False
        original_confirm = pm.confirm
        pm.confirm = AsyncMock(return_value=False)
        
        executor = SafeToolExecutor(pm)
        result = await executor.execute("exec", {"command": "rm -rf"})
        
        assert "error" in result
        assert "User denied" in result["error"]


# ============================================
# P1 测试 — 流式响应
# ============================================

class TestStreaming:
    """流式响应测试"""
    
    def test_stream_chunk_creation(self):
        """测试创建流式块"""
        chunk = StreamChunk(
            type=ChunkType.STATUS,
            content="Testing..."
        )
        assert chunk.type == ChunkType.STATUS
        assert chunk.content == "Testing..."
        assert isinstance(chunk.timestamp, datetime)
    
    def test_stream_chunk_to_dict(self):
        """测试序列化"""
        chunk = StreamChunk(
            type=ChunkType.TEXT,
            content="Hello"
        )
        d = chunk.to_dict()
        assert d["type"] == "text"
        assert d["content"] == "Hello"
        assert "timestamp" in d
    
    @pytest.mark.asyncio
    async def test_stream_generator_status(self):
        """测试状态发出"""
        stream = StreamGenerator()
        result = await stream.status("Starting...")
        assert result is True
        assert len(stream.get_chunks()) == 1
        assert stream.get_chunks()[0].type == ChunkType.STATUS
    
    @pytest.mark.asyncio
    async def test_stream_generator_cancel(self):
        """测试取消流式"""
        stream = StreamGenerator()
        stream.cancel()
        result = await stream.status("After cancel")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_stream_generator_progress(self):
        """测试进度发出"""
        stream = StreamGenerator()
        await stream.progress(5, 10, "Halfway")
        chunk = stream.get_chunks()[-1]
        assert chunk.type == ChunkType.PROGRESS
        assert chunk.content["current"] == 5
        assert chunk.content["total"] == 10


# ============================================
# P1 测试 — 上下文管理器
# ============================================

class TestContextManager:
    """上下文管理器测试"""
    
    def test_token_counter(self):
        """测试 Token 计数"""
        counter = TokenCounter(model="gpt-4")
        tokens = counter.count("Hello, world!")
        assert tokens > 0
    
    def test_message_creation(self):
        """测试消息创建"""
        msg = Message(
            role=MessageRole.USER,
            content="Hello",
            priority=5
        )
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"
        assert msg.priority == 5
    
    def test_context_add_message(self):
        """测试添加消息"""
        ctx = ContextManager(max_tokens=10000)
        ctx.add_message(MessageRole.USER, "Hello")
        assert len(ctx.messages) == 1
    
    def test_context_system_message(self):
        """测试系统消息"""
        ctx = ContextManager()
        ctx.add_system_message("You are helpful.")
        assert len(ctx._system_messages) == 1
    
    def test_context_trim_fifo(self):
        """测试 FIFO 裁剪"""
        ctx = ContextManager(
            max_tokens=500,  # 小窗口
            trimming_strategy=TrimmingStrategy.FIFO
        )
        
        # 添加多条消息直到超出限制
        for i in range(20):
            ctx.add_message(MessageRole.USER, f"Message {i}" * 10)
        
        # 应该自动裁剪
        assert ctx.get_token_count() <= ctx.max_tokens
    
    def test_context_trim_priority(self):
        """测试优先级裁剪"""
        ctx = ContextManager(
            max_tokens=500,
            trimming_strategy=TrimmingStrategy.PRIORITY
        )
        
        # 添加不同优先级的消息
        ctx.add_message(MessageRole.USER, "Low priority", priority=1)
        ctx.add_message(MessageRole.USER, "High priority", priority=10)
        
        # 触发裁剪
        for i in range(20):
            ctx.add_message(MessageRole.USER, f"Message {i}" * 10)
        
        # 高优先级消息应该保留
        contents = [m.content for m in ctx.messages]
        assert "High priority" in contents
    
    def test_context_save_load(self, tmp_path):
        """测试保存/加载"""
        ctx1 = ContextManager()
        ctx1.add_system_message("System")
        ctx1.add_message(MessageRole.USER, "Hello")
        
        filepath = tmp_path / "context.json"
        ctx1.save(str(filepath))
        
        ctx2 = ContextManager()
        ctx2.load(str(filepath))
        
        assert len(ctx2._system_messages) == 1
        assert len(ctx2.messages) == 1
    
    def test_context_usage_stats(self):
        """测试使用统计"""
        ctx = ContextManager()
        ctx.add_system_message("System")
        ctx.add_message(MessageRole.USER, "Hello")
        
        stats = ctx.get_usage_stats()
        assert "total_tokens" in stats
        assert "usage_percent" in stats
        assert "message_count" in stats


# ============================================
# P1 测试 — Agent 循环
# ============================================

class TestAgentLoop:
    """Agent 循环测试"""
    
    def test_agent_config_defaults(self):
        """测试默认配置"""
        config = AgentConfig()
        assert config.max_iterations == 20
        assert config.max_tokens == 8192
        assert config.temperature == 0.7
    
    def test_agent_initial_state(self):
        """测试初始状态"""
        registry = ToolRegistry()
        context = ContextManager()
        agent = AgentLoop(registry, context)
        
        assert agent.state == AgentState.IDLE
        assert agent.current_iteration == 0
    
    @pytest.mark.asyncio
    async def test_agent_run_basic(self):
        """测试基本运行"""
        registry = ToolRegistry()
        context = ContextManager()
        agent = AgentLoop(registry, context, AgentConfig(max_iterations=5))
        
        # Mock _call_model 返回完成响应
        agent._call_model = AsyncMock(return_value={"content": "Done"})
        agent._has_tool_calls = MagicMock(return_value=False)
        agent._has_content = MagicMock(return_value=True)
        agent._get_content = MagicMock(return_value="Result")
        
        result = await agent.run("Test prompt")
        
        assert result == "Result"
        assert agent.state == AgentState.DONE
    
    @pytest.mark.asyncio
    async def test_agent_max_iterations(self):
        """测试最大迭代限制"""
        registry = ToolRegistry()
        context = ContextManager()
        agent = AgentLoop(registry, context, AgentConfig(max_iterations=3))
        
        # Mock _call_model 返回工具调用 (导致无限循环)
        agent._call_model = AsyncMock(return_value={"tool_calls": [{"name": "test"}]})
        agent._has_tool_calls = MagicMock(return_value=True)
        agent._parse_tool_calls = MagicMock(return_value=[ToolCall(id="1", name="test", args={})])
        agent._execute_tool = AsyncMock(return_value={"result": "ok"})
        
        with pytest.raises(RuntimeError, match="Max iterations"):
            await agent.run("Test prompt")
    
    @pytest.mark.asyncio
    async def test_agent_tool_call(self):
        """测试工具调用"""
        registry = ToolRegistry()
        registry.register(WebSearchTool())
        context = ContextManager()
        agent = AgentLoop(registry, context)
        
        tool_call = ToolCall(id="1", name="web_search", args={"query": "test"})
        result = await agent._execute_tool(tool_call)
        
        assert result["status"] == "ok"
    
    def test_agent_get_state(self):
        """测试获取状态"""
        registry = ToolRegistry()
        context = ContextManager()
        agent = AgentLoop(registry, context)
        
        state = agent.get_state()
        
        assert "state" in state
        assert "iteration" in state
        assert "max_iterations" in state


# ============================================
# 边界测试
# ============================================

class TestEdgeCases:
    """边界测试"""
    
    def test_empty_tool_args(self):
        """测试空参数"""
        tool = WebSearchTool()
        # 应该返回错误而不是崩溃
        result = asyncio.run(tool.execute({}))
        assert "error" in result
    
    def test_very_long_context(self):
        """测试超长上下文"""
        ctx = ContextManager(max_tokens=1000)
        
        # 添加超长消息
        long_text = "Hello " * 10000
        ctx.add_message(MessageRole.USER, long_text)
        
        # 应该自动裁剪
        assert ctx.get_token_count() <= ctx.max_tokens
    
    def test_invalid_tool_name(self):
        """测试无效工具名"""
        registry = ToolRegistry()
        with pytest.raises(ValueError):
            asyncio.run(registry.execute("nonexistent", {}))
    
    def test_concurrent_streams(self):
        """测试并发流式"""
        async def create_stream():
            stream = StreamGenerator()
            await stream.status("Test")
            return stream
        
        async def test():
            streams = await asyncio.gather(*[create_stream() for _ in range(10)])
            assert len(streams) == 10
        
        asyncio.run(test())


# ============================================
# 运行测试
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=html"])
