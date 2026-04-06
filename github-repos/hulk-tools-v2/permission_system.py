#!/usr/bin/env python3
"""
敏感操作确认系统 — 参考 Claude Code 权限控制

核心思想:
1. 白名单机制 — 明确定义敏感工具
2. 用户确认 — 危险操作前询问
3. 拒绝处理 — 用户拒绝后返回错误，不崩溃
"""

import asyncio
from typing import Set, Callable, Any, Dict


# 敏感工具白名单
SENSITIVE_TOOLS: Set[str] = {
    "exec",              # Shell 命令执行
    "write_file",        # 文件写入
    "delete_file",       # 文件删除
    "git_push_force",    # Git force push
    "rm_rf",             # 递归删除
}


class PermissionManager:
    """权限管理器"""
    
    def __init__(self, auto_confirm: bool = False):
        """
        Args:
            auto_confirm: 自动确认模式 (用于测试/CI)
        """
        self.auto_confirm = auto_confirm
        self.confirmed_tools: Set[str] = set()
    
    async def confirm(self, tool_name: str, args: Dict[str, Any]) -> bool:
        """
        确认敏感操作
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            
        Returns:
            bool: 用户是否确认
        """
        if tool_name not in SENSITIVE_TOOLS:
            return True  # 非敏感工具，直接通过
        
        if self.auto_confirm:
            return True  # 自动确认模式
        
        if tool_name in self.confirmed_tools:
            return True  # 已确认过的工具
        
        # 显示确认提示
        print(f"\n⚠️  敏感操作确认:")
        print(f"   工具：{tool_name}")
        print(f"   参数：{args}")
        print()
        
        # 交互式确认
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: input("确认执行？(y/N): ").strip().lower()
            )
            confirmed = response in ('y', 'yes')
        except (EOFError, KeyboardInterrupt):
            print("\n操作取消")
            confirmed = False
        
        if confirmed:
            self.confirmed_tools.add(tool_name)
        
        return confirmed


class SafeToolExecutor:
    """安全工具执行器"""
    
    def __init__(self, permission_manager: PermissionManager):
        self.pm = permission_manager
        self.tool_registry = {}  # 实际使用时注入
    
    async def execute(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        执行工具 (带权限检查)
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            
        Returns:
            执行结果
        """
        # 权限检查
        if not await self.pm.confirm(tool_name, args):
            return {"error": "User denied", "tool": tool_name}
        
        # 实际执行
        # tool = self.tool_registry.get(tool_name)
        # return await tool.execute(args)
        return {"status": "ok", "tool": tool_name}


# 使用示例
async def main():
    pm = PermissionManager()
    executor = SafeToolExecutor(pm)
    
    # 非敏感工具 — 直接执行
    result = await executor.execute("web_search", {"query": "AI news"})
    print(f"web_search: {result}")
    
    # 敏感工具 — 需要确认
    result = await executor.execute("exec", {"command": "ls -la"})
    print(f"exec: {result}")


if __name__ == "__main__":
    asyncio.run(main())
