#!/usr/bin/env python3
"""
流式响应系统 — 参考 Claude Code 实时反馈设计

核心思想:
1. 异步生成器 — async for chunk in stream()
2. 类型分发 — 根据 chunk.type 处理不同类型
3. 实时反馈 — 用户看到实时进展，不是等待最终结果

深度实现:
- 支持多种 chunk 类型 (text/tool_call/search_result/summary)
- 支持进度追踪
- 支持取消
"""

import asyncio
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional, Callable, Any, Dict, List, Union
from datetime import datetime


# === Chunk 类型定义 ===

class ChunkType(str, Enum):
    """流式块类型"""
    STATUS = "status"           # 状态更新
    SEARCH_RESULT = "search"    # 搜索结果
    TEXT = "text"               # 文本内容
    TOOL_CALL = "tool_call"     # 工具调用开始
    TOOL_RESULT = "tool_result" # 工具调用结果
    PROGRESS = "progress"       # 进度更新
    ERROR = "error"             # 错误
    DONE = "done"               # 完成


@dataclass
class StreamChunk:
    """流式数据块"""
    type: ChunkType
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


# === 流式处理器基类 ===

class StreamHandler:
    """流式处理器基类 — 用户可继承自定义处理逻辑"""
    
    async def on_chunk(self, chunk: StreamChunk):
        """处理每个 chunk — 子类重写"""
        pass
    
    async def on_status(self, status: str):
        """状态更新"""
        pass
    
    async def on_text(self, text: str):
        """文本内容"""
        pass
    
    async def on_tool_call(self, tool_name: str, args: Dict):
        """工具调用开始"""
        pass
    
    async def on_tool_result(self, tool_name: str, result: Any):
        """工具调用结果"""
        pass
    
    async def on_progress(self, current: int, total: int, message: str):
        """进度更新"""
        pass
    
    async def on_error(self, error: str):
        """错误"""
        pass
    
    async def on_done(self, result: Any):
        """完成"""
        pass


# === 终端流式处理器 ===

class TerminalStreamHandler(StreamHandler):
    """终端流式处理器 — 彩色输出"""
    
    def __init__(self, show_timestamp: bool = False):
        self.show_timestamp = show_timestamp
        self._colors = {
            ChunkType.STATUS: "\033[90m",      # 灰色
            ChunkType.TEXT: "\033[0m",        # 默认
            ChunkType.TOOL_CALL: "\033[94m",  # 蓝色
            ChunkType.TOOL_RESULT: "\033[92m", # 绿色
            ChunkType.PROGRESS: "\033[93m",   # 黄色
            ChunkType.ERROR: "\033[91m",      # 红色
            ChunkType.DONE: "\033[95m",       # 紫色
        }
        self._reset = "\033[0m"
    
    def _timestamp_str(self) -> str:
        if self.show_timestamp:
            return f"[{datetime.now().strftime('%H:%M:%S')}]"
        return ""
    
    async def on_chunk(self, chunk: StreamChunk):
        """路由到具体处理方法"""
        handler = getattr(self, f'on_{chunk.type.value}', None)
        if handler:
            await handler(chunk.content)
    
    async def on_status(self, status: str):
        print(f"{self._colors[ChunkType.STATUS]}{self._timestamp_str()} 💭 {status}{self._reset}")
    
    async def on_text(self, text: str):
        print(f"{self._colors[ChunkType.TEXT]}{self._timestamp_str()} {text}{self._reset}")
    
    async def on_tool_call(self, data: Dict):
        tool_name = data.get('tool', 'unknown')
        args = data.get('args', {})
        print(f"{self._colors[ChunkType.TOOL_CALL]}{self._timestamp_str()} 🔧 Calling {tool_name}({json.dumps(args)}){self._reset}")
    
    async def on_tool_result(self, data: Dict):
        tool_name = data.get('tool', 'unknown')
        print(f"{self._colors[ChunkType.TOOL_RESULT]}{self._timestamp_str()} ✅ {tool_name} completed{self._reset}")
    
    async def on_progress(self, data: Dict):
        current = data.get('current', 0)
        total = data.get('total', 100)
        message = data.get('message', '')
        percent = (current / total) * 100 if total > 0 else 0
        bar_length = 30
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r{self._colors[ChunkType.PROGRESS]}{self._timestamp_str()} [{bar}] {percent:.0f}% {message}{self._reset}", end='', flush=True)
        if percent >= 100:
            print()  # 完成后换行
    
    async def on_error(self, error: str):
        print(f"{self._colors[ChunkType.ERROR]}{self._timestamp_str()} ❌ Error: {error}{self._reset}")
    
    async def on_done(self, result: Any):
        print(f"{self._colors[ChunkType.DONE]}{self._timestamp_str()} ✅ Done!{self._reset}")


# === 流式生成器 ===

class StreamGenerator:
    """流式生成器 — 产生 StreamChunk"""
    
    def __init__(self):
        self._cancelled = False
        self._chunks: List[StreamChunk] = []
    
    def cancel(self):
        """取消流式"""
        self._cancelled = True
    
    async def emit(self, chunk: StreamChunk) -> bool:
        """
        发出 chunk
        
        Returns:
            bool: 是否成功 (False 表示已取消)
        """
        if self._cancelled:
            return False
        self._chunks.append(chunk)
        return True
    
    async def status(self, message: str) -> bool:
        return await self.emit(StreamChunk(
            type=ChunkType.STATUS,
            content=message
        ))
    
    async def text(self, text: str) -> bool:
        return await self.emit(StreamChunk(
            type=ChunkType.TEXT,
            content=text
        ))
    
    async def tool_call(self, tool_name: str, args: Dict) -> bool:
        return await self.emit(StreamChunk(
            type=ChunkType.TOOL_CALL,
            content={"tool": tool_name, "args": args}
        ))
    
    async def tool_result(self, tool_name: str, result: Any) -> bool:
        return await self.emit(StreamChunk(
            type=ChunkType.TOOL_RESULT,
            content={"tool": tool_name, "result": result}
        ))
    
    async def progress(self, current: int, total: int, message: str = "") -> bool:
        return await self.emit(StreamChunk(
            type=ChunkType.PROGRESS,
            content={"current": current, "total": total, "message": message}
        ))
    
    async def error(self, error: str) -> bool:
        return await self.emit(StreamChunk(
            type=ChunkType.ERROR,
            content=error
        ))
    
    async def done(self, result: Any = None) -> bool:
        return await self.emit(StreamChunk(
            type=ChunkType.DONE,
            content=result
        ))
    
    def get_chunks(self) -> List[StreamChunk]:
        """获取所有 chunk (用于测试/日志)"""
        return self._chunks.copy()


# === 流式执行引擎 ===

class StreamExecutor:
    """流式执行引擎 — 执行任务并流式输出"""
    
    def __init__(self, handler: Optional[StreamHandler] = None):
        self.handler = handler or TerminalStreamHandler()
    
    async def execute(
        self,
        task: Callable[[StreamGenerator], AsyncIterator[StreamChunk]]
    ) -> Any:
        """
        执行任务并流式输出
        
        Args:
            task: 异步生成器函数，接收 StreamGenerator
            
        Returns:
            任务结果
        """
        stream = StreamGenerator()
        result = None
        
        try:
            async for chunk in task(stream):
                if not await self.handler.on_chunk(chunk):
                    break
                if chunk.type == ChunkType.DONE:
                    result = chunk.content
                    break
        except asyncio.CancelledError:
            stream.cancel()
            await self.handler.on_error("Task cancelled")
            raise
        except Exception as e:
            await self.handler.on_error(str(e))
            raise
        
        return result


# === 使用示例 ===

async def example_geo_task(stream: StreamGenerator) -> AsyncIterator[StreamChunk]:
    """GEO 迭代任务示例"""
    await stream.status("Starting GEO iteration...")
    
    # 步骤 1: 网络搜索
    await stream.progress(1, 5, "Searching web...")
    await stream.tool_call("web_search", {"query": "AI news"})
    await asyncio.sleep(0.5)  # 模拟搜索
    await stream.tool_result("web_search", {"results": 10})
    
    # 步骤 2: 内容获取
    await stream.progress(2, 5, "Fetching content...")
    for i in range(3):
        await stream.text(f"Reading article {i+1}/3...")
        await asyncio.sleep(0.3)
    
    # 步骤 3: 综合分析
    await stream.progress(3, 5, "Analyzing...")
    await asyncio.sleep(0.5)
    
    # 步骤 4: 生成结论
    await stream.progress(4, 5, "Generating conclusion...")
    await stream.text("Key finding: AI agents are becoming more autonomous.")
    
    # 步骤 5: 完成
    await stream.progress(5, 5, "Complete!")
    await stream.done({"iterations": 5, "findings": 1})
    
    # 生成器必须 yield 所有 chunk
    for chunk in stream.get_chunks():
        yield chunk


async def main():
    """主函数 — 演示流式执行"""
    executor = StreamExecutor(TerminalStreamHandler(show_timestamp=True))
    
    print("=" * 60)
    print("流式响应系统演示")
    print("=" * 60)
    print()
    
    result = await executor.execute(example_geo_task)
    
    print()
    print(f"最终结果：{result}")


if __name__ == "__main__":
    asyncio.run(main())
