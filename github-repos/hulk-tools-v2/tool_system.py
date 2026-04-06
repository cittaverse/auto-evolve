#!/usr/bin/env python3
"""
Hulk 工具系统 v2.1 — 参考 Claude Code buildTool 工厂模式

核心改进:
1. 工具接口规范化 (name/description/parameters/execute)
2. 自描述 — 模型能理解工具用途
3. 纯函数 — 便于测试和 mock
4. **保守默认 (Fail-Closed)** — 默认假设工具不安全，需显式声明
5. **build_tool 工厂** — 统一填充默认值，避免重复代码

Claude Code 核心思想:
- is_concurrency_safe=False (保守：默认不安全)
- is_read_only=False (保守：默认会写)
- is_destructive=False (需显式声明破坏性)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Callable, Optional
from dataclasses import dataclass, field
import asyncio


# ============================================================================
# Claude Code 风格工具工厂模式
# ============================================================================

# 保守默认值 (Fail-Closed 设计)
TOOL_DEFAULTS = {
    'is_enabled': True,
    'is_concurrency_safe': False,  # ❌ 保守：默认不安全
    'is_read_only': False,         # ❌ 保守：默认会写
    'is_destructive': False,       # ❌ 保守：默认非破坏性
}


@dataclass
class ToolMetadata:
    """工具元数据 — Claude Code 风格"""
    name: str
    description: str
    parameters: Dict[str, Any]
    is_enabled: bool = True
    is_concurrency_safe: bool = False  # 默认不安全
    is_read_only: bool = False         # 默认会写
    is_destructive: bool = False       # 默认非破坏性
    
    def to_dict(self) -> Dict:
        """转换为模型可理解的格式"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'metadata': {
                'is_enabled': self.is_enabled,
                'is_concurrency_safe': self.is_concurrency_safe,
                'is_read_only': self.is_read_only,
                'is_destructive': self.is_destructive,
            }
        }


def build_tool(
    name: str,
    description: str,
    parameters: Dict[str, Any],
    execute_fn: Callable,
    is_enabled: Optional[bool] = None,
    is_concurrency_safe: Optional[bool] = None,
    is_read_only: Optional[bool] = None,
    is_destructive: Optional[bool] = None,
) -> ToolMetadata:
    """
    构建工具 — 填充保守默认值
    
    设计原则 (Claude Code 思想):
    1. is_concurrency_safe=False — 默认假设工具不安全，需显式声明
    2. is_read_only=False — 默认假设工具会写，需显式声明只读
    3. is_destructive=False — 默认假设非破坏性，破坏性工具需显式声明
    
    示例:
    ```python
    # 只读工具 (安全)
    web_search = build_tool(
        name='web_search',
        description='Search the web',
        parameters={...},
        execute_fn=search_fn,
        is_read_only=True,  # ✅ 显式声明只读
        is_concurrency_safe=True,  # ✅ 显式声明并发安全
    )
    
    # 写操作工具 (需谨慎)
    file_write = build_tool(
        name='file_write',
        description='Write to file',
        parameters={...},
        execute_fn=write_fn,
        is_read_only=False,  # ❌ 会写
        is_destructive=True,  # ⚠️ 可能覆盖文件
    )
    ```
    """
    return ToolMetadata(
        name=name,
        description=description,
        parameters=parameters,
        is_enabled=is_enabled if is_enabled is not None else TOOL_DEFAULTS['is_enabled'],
        is_concurrency_safe=is_concurrency_safe if is_concurrency_safe is not None else TOOL_DEFAULTS['is_concurrency_safe'],
        is_read_only=is_read_only if is_read_only is not None else TOOL_DEFAULTS['is_read_only'],
        is_destructive=is_destructive if is_destructive is not None else TOOL_DEFAULTS['is_destructive'],
    )


class Tool(ABC):
    """工具基类 — 所有工具必须继承此类 (兼容旧代码)"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称 — 英文，无空格"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述 — 清晰说明用途，模型根据此决定调用"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        参数定义 — JSON Schema 格式
        示例:
        {
            "query": {
                "type": "string",
                "description": "搜索关键词",
                "required": True
            }
        }
        """
        pass
    
    @abstractmethod
    async def execute(self, args: Dict[str, Any]) -> Any:
        """执行工具 — 纯异步函数，返回结构化结果"""
        pass
    
    def to_dict(self) -> Dict:
        """转换为模型可理解的格式"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class WebSearchTool(Tool):
    """网络搜索工具"""
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web using search engine. Use for finding recent information, news, or public data."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "Search query string"
            },
            "count": {
                "type": "integer",
                "description": "Number of results (1-10, default: 5)",
                "default": 5
            }
        }
    
    async def execute(self, args: Dict[str, Any]) -> Any:
        query = args.get("query")
        count = args.get("count", 5)
        
        if not query:
            return {"error": "Missing required parameter: query"}
        
        # 实际调用 web_search 工具
        # result = await web_search(query=query, count=count)
        return {"status": "ok", "query": query, "count": count}


class ExecTool(Tool):
    """Shell 命令执行工具 — 敏感操作"""
    
    @property
    def name(self) -> str:
        return "exec"
    
    @property
    def description(self) -> str:
        return "Execute a shell command. Use for file operations, git commands, or system tasks."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "command": {
                "type": "string",
                "description": "Shell command to execute"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 60)",
                "default": 60
            }
        }
    
    async def execute(self, args: Dict[str, Any]) -> Any:
        command = args.get("command")
        timeout = args.get("timeout", 60)
        
        if not command:
            return {"error": "Missing required parameter: command"}
        
        # 实际执行
        # result = await asyncio.wait_for(exec(command), timeout=timeout)
        return {"status": "ok", "command": command, "timeout": timeout}


class ToolRegistry:
    """工具注册表 — 管理所有可用工具"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.tool_metadata: Dict[str, ToolMetadata] = {}
    
    def register(self, tool: Tool, metadata: Optional[ToolMetadata] = None):
        """注册工具"""
        self.tools[tool.name] = tool
        if metadata:
            self.tool_metadata[tool.name] = metadata
    
    def register_from_metadata(self, metadata: ToolMetadata, execute_fn: Callable):
        """
        从 build_tool 结果注册工具
        
        示例:
        ```python
        web_search = build_tool(...)
        registry.register_from_metadata(web_search, search_fn)
        ```
        """
        self.tool_metadata[metadata.name] = metadata
        # 包装为可执行工具
        class DynamicTool(Tool):
            @property
            def name(self): return metadata.name
            @property
            def description(self): return metadata.description
            @property
            def parameters(self): return metadata.parameters
            async def execute(self, args): return await execute_fn(args)
        self.tools[metadata.name] = DynamicTool()
    
    def get(self, name: str) -> Tool:
        """获取工具"""
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        return self.tools[name]
    
    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        """获取工具元数据 (包含保守默认值)"""
        return self.tool_metadata.get(name)
    
    def list_tools(self) -> list:
        """列出所有工具 (给模型看)"""
        # 优先使用元数据 (包含保守默认值)
        if self.tool_metadata:
            return [meta.to_dict() for meta in self.tool_metadata.values()]
        return [tool.to_dict() for tool in self.tools.values()]
    
    async def execute(self, name: str, args: Dict[str, Any]) -> Any:
        """执行工具"""
        tool = self.get(name)
        return await tool.execute(args)


# ============================================================================
# 初始化注册表 (兼容旧代码 + 新工厂模式)
# ============================================================================

registry = ToolRegistry()

# 旧代码兼容 (直接注册 Tool 子类)
registry.register(WebSearchTool())
registry.register(ExecTool())

# 新工厂模式示例
async def web_search_execute(args: Dict[str, Any]) -> Any:
    """网络搜索执行函数"""
    query = args.get("query")
    count = args.get("count", 5)
    if not query:
        return {"error": "Missing required parameter: query"}
    return {"status": "ok", "query": query, "count": count}

async def exec_execute(args: Dict[str, Any]) -> Any:
    """Shell 命令执行函数"""
    command = args.get("command")
    timeout = args.get("timeout", 60)
    if not command:
        return {"error": "Missing required parameter: command"}
    return {"status": "ok", "command": command, "timeout": timeout}

# 使用 build_tool 注册 (保守默认值)
web_search_meta = build_tool(
    name='web_search',
    description='Search the web using search engine. Use for finding recent information, news, or public data.',
    parameters={
        "query": {"type": "string", "description": "Search query string"},
        "count": {"type": "integer", "description": "Number of results (1-10, default: 5)", "default": 5}
    },
    execute_fn=web_search_execute,
    is_read_only=True,         # ✅ 显式声明只读
    is_concurrency_safe=True,  # ✅ 显式声明并发安全
)
registry.register_from_metadata(web_search_meta, web_search_execute)

exec_meta = build_tool(
    name='exec',
    description='Execute a shell command. Use for file operations, git commands, or system tasks.',
    parameters={
        "command": {"type": "string", "description": "Shell command to execute"},
        "timeout": {"type": "integer", "description": "Timeout in seconds (default: 60)", "default": 60}
    },
    execute_fn=exec_execute,
    is_read_only=False,    # ❌ 会写
    is_destructive=False,  # ⚠️ 可能破坏，需权限确认
)
registry.register_from_metadata(exec_meta, exec_execute)


# 使用示例
async def main():
    # 列出工具 (给模型看)
    print("可用工具:")
    for tool in registry.list_tools():
        print(f"  - {tool['name']}: {tool['description']}")
    
    # 执行工具
    result = await registry.execute("web_search", {"query": "AI news", "count": 3})
    print(f"结果：{result}")


if __name__ == "__main__":
    asyncio.run(main())
