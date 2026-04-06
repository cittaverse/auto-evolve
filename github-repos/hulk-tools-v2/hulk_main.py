#!/usr/bin/env python3
"""
Hulk v2.0 主循环入口 — 持续自驱系统

核心功能:
1. 集成所有 v2.0 模块 (工具/流式/上下文/Hook/持久化)
2. GEO 迭代自动化
3. 自驱循环机制
4. 监控和日志
5. 状态恢复

使用方式:
    python hulk_main.py --prompt "研究 AI 趋势" --auto
    python hulk_main.py --resume  # 从中断处恢复
"""

import asyncio
import json
import sys
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tool_system import ToolRegistry, WebSearchTool, ExecTool
from context_manager import ContextManager, MessageRole
from agent_loop import AgentLoop, AgentConfig, AgentState
from streaming import StreamGenerator, TerminalStreamHandler, StreamExecutor
from hook_system import HulkHookEngine
from state_persistence import StatePersistence, ResumableAgentTask
from hulk_tui import HulkApp, TUIStreamExecutor


# ============================================
# Hulk v2.0 主类
# ============================================

class HulkV2:
    """
    Hulk v2.0 — 完整集成版本
    
    集成模块:
    - 工具系统 (ToolRegistry)
    - 上下文管理 (ContextManager)
    - Agent 循环 (AgentLoop)
    - 流式响应 (Streaming)
    - Hook 系统 (HulkHookEngine)
    - 状态持久化 (StatePersistence)
    - Terminal UI (HulkApp)
    """
    
    def __init__(
        self,
        use_tui: bool = False,
        hooks_enabled: bool = True,
        state_dir: str = ".hulk-state"
    ):
        self.use_tui = use_tui
        self.start_time = datetime.now()
        
        # 1. 工具注册表
        self.registry = ToolRegistry()
        self._register_default_tools()
        
        # 2. 上下文管理器
        self.context = ContextManager(
            max_tokens=128000,
            trimming_strategy="priority"
        )
        self.context.add_system_message(
            "You are Hulk, an AI research assistant for CittaVerse. "
            "Focus on evidence-based research, structured analysis, and actionable conclusions. "
            "Always provide sources and confidence levels."
        )
        
        # 3. Agent 循环 (集成 Hook)
        self.config = AgentConfig(
            model="qwen3.5-plus",
            max_iterations=20,
            max_tokens=8192,
            temperature=0.7
        )
        self.agent = AgentLoop(
            self.registry,
            self.context,
            self.config,
            hooks_enabled=hooks_enabled
        )
        
        # 4. 状态持久化
        self.persistence = StatePersistence(state_dir)
        
        # 5. 日志
        self.log_file = Path(state_dir) / "hulk.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._log("Hulk v2.0 initialized")
    
    def _register_default_tools(self):
        """注册默认工具"""
        self.registry.register(WebSearchTool())
        self.registry.register(ExecTool())
        # 可扩展：添加更多工具
        # self.registry.register(FileReadTool())
        # self.registry.register(FileWriteTool())
        # self.registry.register(GitTool())
    
    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        # 写入日志文件
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        # 控制台输出
        print(log_entry.strip())
    
    async def run(
        self,
        prompt: str,
        auto: bool = False,
        resume: bool = False
    ) -> Dict[str, Any]:
        """
        运行 Hulk
        
        Args:
            prompt: 用户输入
            auto: 是否自动模式 (持续迭代)
            resume: 是否从中断处恢复
            
        Returns:
            执行结果
        """
        self._log(f"Starting Hulk v2.0: '{prompt}'")
        
        # 检查是否需要恢复
        if resume and self.persistence.should_resume():
            self._log("Resuming from previous state...")
            state = self.persistence.load()
            if state and state.agent:
                self._restore_state(state)
        else:
            self.persistence.create_state()
        
        # 更新状态
        self.persistence.update_agent_state(
            state="thinking",
            iteration=0,
            max_iterations=self.config.max_iterations,
            context_tokens=self.context.get_token_count()
        )
        
        try:
            if self.use_tui:
                # TUI 模式
                result = await self._run_with_tui(prompt, auto)
            else:
                # 终端模式
                result = await self._run_terminal(prompt, auto)
            
            # 完成
            self.persistence.update_agent_state(
                state="done",
                iteration=self.agent.current_iteration,
                max_iterations=self.config.max_iterations,
                context_tokens=self.context.get_token_count()
            )
            self.persistence.save()
            
            self._log(f"Completed: {result.get('status', 'unknown')}")
            return result
            
        except KeyboardInterrupt:
            self._log("Interrupted by user")
            self.persistence.save()
            print("\n💾 状态已保存，恢复命令：python hulk_main.py --resume")
            return {"status": "interrupted"}
        except Exception as e:
            self._log(f"Error: {e}")
            self.persistence.update_agent_state(
                state="error",
                iteration=self.agent.current_iteration,
                max_iterations=self.config.max_iterations
            )
            self.persistence.save()
            raise
    
    async def _run_terminal(self, prompt: str, auto: bool) -> Dict:
        """终端模式运行"""
        handler = TerminalStreamHandler(show_timestamp=True)
        executor = StreamExecutor(handler)
        
        async def task(stream: StreamGenerator):
            if auto:
                # 自动模式：持续 GEO 迭代
                result = await self._run_auto_loop(prompt, stream)
            else:
                # 单次模式
                result = await self.agent.run(prompt, stream)
                result = {"status": "completed", "result": result}
            
            # Yield chunks from stream
            for chunk in stream.get_chunks():
                yield chunk
            
            # Store result for later access
            self._last_result = result
        
        await executor.execute(task)
        return getattr(self, '_last_result', {"status": "completed"})
    
    async def _run_with_tui(self, prompt: str, auto: bool) -> Dict:
        """TUI 模式运行"""
        app = HulkApp()
        executor = TUIStreamExecutor(app)
        
        async def tui_task(executor: TUIStreamExecutor):
            await executor.status("Starting Hulk v2.0...")
            
            if auto:
                result = await self._run_auto_loop(prompt, executor)
            else:
                result = await self.agent.run(prompt, executor)
            
            await executor.done(result)
            return result
        
        # app.run()  # 实际运行 TUI
        # 简化版：直接执行
        return await tui_task(executor)
    
    async def _run_auto_loop(
        self,
        initial_prompt: str,
        stream: StreamGenerator
    ) -> Dict:
        """
        自动循环模式 — 持续 GEO 迭代
        
        循环流程:
        1. 搜索/研究
        2. 综合分析
        3. 生成结论
        4. 保存状态
        5. 继续下一轮 (或达到限制)
        """
        max_loops = 5
        results = []
        
        for loop in range(max_loops):
            await stream.status(f"GEO Iteration {loop + 1}/{max_loops}")
            await stream.progress(loop + 1, max_loops, f"Iteration {loop + 1}")
            
            # 动态生成下一轮 prompt
            if loop == 0:
                current_prompt = initial_prompt
            else:
                current_prompt = f"Continue research on: {initial_prompt}. Build on previous findings."
            
            # 运行单轮
            try:
                result = await self.agent.run(current_prompt, stream)
                results.append(result)
                
                # 保存中间状态
                self.persistence.update_agent_state(
                    state="thinking",
                    iteration=loop + 1,
                    max_iterations=max_loops,
                    context_tokens=self.context.get_token_count()
                )
                self.persistence.save()
                
            except Exception as e:
                await stream.error(f"Iteration {loop + 1} failed: {e}")
                break
        
        # 综合结论
        await stream.status("Synthesizing conclusions...")
        summary = {
            "iterations": len(results),
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        await stream.done(summary)
        return summary
    
    def _restore_state(self, state):
        """恢复状态"""
        if state.agent:
            self.agent.current_iteration = state.agent.iteration
            self.agent.state = AgentState(state.agent.state)
        
        if state.context:
            # 恢复上下文
            for msg in state.context.system_messages:
                self.context._system_messages.append(
                    Message.from_dict(msg)
                )
            for msg in state.context.messages:
                self.context.messages.append(
                    Message.from_dict(msg)
                )
        
        self._log(f"State restored: iteration {self.agent.current_iteration}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "context_tokens": self.context.get_token_count(),
            "context_usage_percent": self.context.get_usage_stats()["usage_percent"],
            "agent_state": self.agent.state.value,
            "current_iteration": self.agent.current_iteration,
            "max_iterations": self.config.max_iterations
        }


# ============================================
# CLI 入口
# ============================================

def main():
    """CLI 入口"""
    parser = argparse.ArgumentParser(
        description="Hulk v2.0 — AI Research Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hulk_main.py --prompt "研究 AI 趋势"
  python hulk_main.py --prompt "研究 AI 趋势" --auto
  python hulk_main.py --resume
  python hulk_main.py --tui --prompt "研究 AI 趋势"
        """
    )
    
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        help="研究主题/问题"
    )
    parser.add_argument(
        "--auto", "-a",
        action="store_true",
        help="自动模式 (持续 GEO 迭代)"
    )
    parser.add_argument(
        "--resume", "-r",
        action="store_true",
        help="从中断处恢复"
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="使用 Terminal UI"
    )
    parser.add_argument(
        "--no-hooks",
        action="store_true",
        help="禁用 Hook 系统"
    )
    parser.add_argument(
        "--state-dir",
        type=str,
        default=".hulk-state",
        help="状态目录 (默认：.hulk-state)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="显示统计信息并退出"
    )
    
    args = parser.parse_args()
    
    # 创建 Hulk 实例
    hulk = HulkV2(
        use_tui=args.tui,
        hooks_enabled=not args.no_hooks,
        state_dir=args.state_dir
    )
    
    # 显示统计
    if args.stats:
        stats = hulk.get_stats()
        print(json.dumps(stats, indent=2))
        return
    
    # 运行
    if args.prompt:
        result = asyncio.run(hulk.run(
            args.prompt,
            auto=args.auto,
            resume=args.resume
        ))
        print(f"\n结果：{json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        # 交互模式
        print("Hulk v2.0 — AI Research Assistant")
        print("输入 'quit' 退出，'--stats' 显示统计")
        print()
        
        while True:
            try:
                prompt = input("🤖> ").strip()
                
                if prompt.lower() == "quit":
                    break
                elif prompt == "--stats":
                    stats = hulk.get_stats()
                    print(json.dumps(stats, indent=2))
                    continue
                elif not prompt:
                    continue
                
                result = asyncio.run(hulk.run(prompt))
                print(f"\n结果：{json.dumps(result, indent=2, ensure_ascii=False)}\n")
                
            except KeyboardInterrupt:
                print("\n💾 状态已保存")
                continue


if __name__ == "__main__":
    # 设置信号处理
    def signal_handler(sig, frame):
        print("\n⏸️  中断信号，保存状态...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    main()
