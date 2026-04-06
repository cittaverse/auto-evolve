#!/usr/bin/env python3
"""
Terminal UI — 基于 textual 库的深度实现

参考 Claude Code 的 Ink (React for CLI) 设计思想，
使用 Python 的 textual 库实现声明式 TUI。

核心功能:
1. 声明式 UI — 组件化设计
2. 实时刷新 — 状态驱动渲染
3. 键盘交互 — 快捷键支持
4. 进度条/日志/状态面板

深度实现:
- 多面板布局
- 流式日志输出
- 进度追踪
- 键盘中断处理
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log, ProgressBar, Button
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from textual.reactive import reactive
from datetime import datetime
from typing import Optional, Dict, Any, List
import asyncio


# === 状态显示面板 ===

class StatusPanel(Static):
    """状态显示面板"""
    
    status = reactive("Idle")
    iteration = reactive(0)
    max_iterations = reactive(20)
    
    def compose(self) -> ComposeResult:
        yield Static(id="status-icon")
        yield Static(id="status-text")
        yield Static(id="iteration-text")
    
    def on_mount(self):
        self.update_display()
    
    def watch_status(self, new_status: str):
        self.update_display()
    
    def watch_iteration(self, new_iteration: int):
        self.update_display()
    
    def update_display(self):
        # 状态图标
        icon_map = {
            "Idle": "⏸️",
            "Thinking": "💭",
            "Acting": "🔧",
            "Observing": "👁️",
            "Done": "✅",
            "Error": "❌"
        }
        icon = icon_map.get(self.status, "⏳")
        self.query_one("#status-icon", Static).update(icon)
        
        # 状态文本
        self.query_one("#status-text", Static).update(f"[bold]{self.status}[/bold]")
        
        # 迭代计数
        if self.max_iterations > 0:
            percent = (self.iteration / self.max_iterations) * 100
            self.query_one("#iteration-text", Static).update(
                f"Iteration {self.iteration}/{self.max_iterations} ({percent:.0f}%)"
            )


# === 日志面板 ===

class LogPanel(Log):
    """日志面板 — 流式输出"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, max_lines=1000, **kwargs)
        self._timestamps: Dict[int, datetime] = {}
    
    def append_log(self, message: str, log_type: str = "info"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 类型图标
        icon_map = {
            "info": "ℹ️",
            "status": "💭",
            "tool": "🔧",
            "result": "✅",
            "error": "❌",
            "progress": "📊"
        }
        icon = icon_map.get(log_type, "•")
        
        # 格式化
        styled = f"[dim]{timestamp}[/dim] {icon} {message}"
        self.write_line(styled)
        
        # 自动滚动
        self.scroll_end(animate=False)


# === 进度面板 ===

class ProgressPanel(Static):
    """进度面板"""
    
    current = reactive(0)
    total = reactive(100)
    message = reactive("")
    
    def compose(self) -> ComposeResult:
        yield Static(id="progress-label")
        yield ProgressBar(id="progress-bar", show_eta=False)
    
    def watch_current(self, value: int):
        self.update_bar()
    
    def watch_total(self, value: int):
        self.update_bar()
    
    def watch_message(self, value: str):
        self.update_label()
    
    def update_bar(self):
        bar = self.query_one("#progress-bar", ProgressBar)
        if self.total > 0:
            bar.progress = (self.current / self.total) * 100
        else:
            bar.progress = 0
    
    def update_label(self):
        self.query_one("#progress-label", Static).update(self.message)
    
    def set_progress(self, current: int, total: int, message: str = ""):
        self.current = current
        self.total = total
        self.message = message


# === 主应用 ===

class HulkApp(App):
    """Hulk Terminal UI 应用"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    Container {
        height: 100%;
    }
    
    #top-panel {
        height: 4;
        border: solid $primary;
        margin: 1 1 0 1;
    }
    
    #middle-panel {
        height: 1fr;
        margin: 0 1;
    }
    
    #bottom-panel {
        height: 6;
        border: solid $secondary;
        margin: 0 1 1 1;
    }
    
    #status-icon {
        width: 6;
        content-align: center middle;
    }
    
    #status-text {
        width: 20;
        padding: 0 1;
    }
    
    #iteration-text {
        width: 30;
        padding: 0 1;
        color: $text-muted;
    }
    
    Log {
        background: $surface-darken-1;
        border: solid $primary-background;
    }
    
    #progress-label {
        margin: 0 0 1 0;
        text-style: bold;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("c", "cancel", "Cancel", show=True),
        Binding("r", "restart", "Restart", show=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode", show=True),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task_result: Optional[Any] = None
        self._is_running = False
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container():
            # 顶部：状态面板
            with Horizontal(id="top-panel"):
                yield StatusPanel()
            
            # 中间：日志面板
            with Vertical(id="middle-panel"):
                yield LogPanel(id="log-panel")
            
            # 底部：进度面板
            with Vertical(id="bottom-panel"):
                yield ProgressPanel()
        
        yield Footer()
    
    def on_mount(self) -> None:
        """应用启动时"""
        self.title = "Hulk Agent"
        self.sub_title = "AI Research Assistant"
        
        # 初始化状态
        status = self.query_one(StatusPanel)
        status.status = "Idle"
        status.iteration = 0
        status.max_iterations = 20
    
    def action_toggle_dark(self) -> None:
        """切换深色模式"""
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"
    
    def action_cancel(self) -> None:
        """取消当前任务"""
        if self._is_running:
            self.notify("Task cancelled", severity="warning")
            self._is_running = False
    
    def action_restart(self) -> None:
        """重启应用"""
        self.notify("Restarting...", severity="information")
        # 实际重启逻辑
    
    # === 公共 API — 供外部调用 ===
    
    def set_status(self, status: str):
        """设置状态"""
        status_panel = self.query_one(StatusPanel)
        status_panel.status = status
    
    def set_iteration(self, current: int, max_iter: int):
        """设置迭代计数"""
        status_panel = self.query_one(StatusPanel)
        status_panel.iteration = current
        status_panel.max_iterations = max_iter
    
    def log(self, message: str, log_type: str = "info"):
        """添加日志"""
        log_panel = self.query_one(LogPanel)
        log_panel.append_log(message, log_type)
    
    def set_progress(self, current: int, total: int, message: str = ""):
        """设置进度"""
        progress = self.query_one(ProgressPanel)
        progress.set_progress(current, total, message)
    
    def set_result(self, result: Any):
        """设置任务结果"""
        self._task_result = result
    
    def get_result(self) -> Any:
        """获取任务结果"""
        return self._task_result
    
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._is_running
    
    def set_running(self, running: bool):
        """设置运行状态"""
        self._is_running = running


# === 流式执行器 (集成 TUI) ===

class TUIStreamExecutor:
    """TUI 流式执行器"""
    
    def __init__(self, app: HulkApp):
        self.app = app
    
    async def execute(self, task_func):
        """执行任务"""
        self.app.set_running(True)
        self.app.set_status("Starting...")
        self.app.log("Task started", "info")
        
        try:
            # 执行任务
            result = await task_func(self)
            self.app.set_result(result)
            self.app.set_status("Done")
            self.app.log("Task completed", "result")
            return result
        except asyncio.CancelledError:
            self.app.set_status("Cancelled")
            self.app.log("Task cancelled by user", "error")
            raise
        except Exception as e:
            self.app.set_status("Error")
            self.app.log(f"Error: {str(e)}", "error")
            raise
        finally:
            self.app.set_running(False)
    
    # === 流式 API ===
    
    async def status(self, message: str):
        """状态更新"""
        self.app.set_status(message)
        self.app.log(message, "status")
        await asyncio.sleep(0)  # 让出控制权
    
    async def text(self, text: str):
        """文本输出"""
        self.app.log(text, "info")
        await asyncio.sleep(0)
    
    async def tool_call(self, tool_name: str, args: Dict):
        """工具调用"""
        self.app.log(f"Calling {tool_name}({args})", "tool")
        await asyncio.sleep(0)
    
    async def tool_result(self, tool_name: str, result: Any):
        """工具结果"""
        self.app.log(f"{tool_name} completed", "result")
        await asyncio.sleep(0)
    
    async def progress(self, current: int, total: int, message: str = ""):
        """进度更新"""
        self.app.set_progress(current, total, message)
        self.app.set_iteration(current, total)
        await asyncio.sleep(0)
    
    async def error(self, error: str):
        """错误"""
        self.app.log(f"Error: {error}", "error")
        await asyncio.sleep(0)
    
    async def done(self, result: Any = None):
        """完成"""
        self.app.set_status("Done")
        self.app.set_result(result)
        self.app.log(f"Result: {result}", "result")
        await asyncio.sleep(0)


# === 使用示例 ===

async def example_task(executor: TUIStreamExecutor):
    """示例任务"""
    await executor.status("Starting GEO iteration...")
    
    for i in range(5):
        await executor.progress(i + 1, 5, f"Iteration {i + 1}/5")
        await executor.status(f"Searching web (iteration {i + 1})...")
        
        await executor.tool_call("web_search", {"query": f"AI news {i}"})
        await asyncio.sleep(0.5)  # 模拟搜索
        
        await executor.tool_result("web_search", {"results": 10})
        await executor.text(f"Found 10 results for iteration {i + 1}")
    
    await executor.done({"iterations": 5, "findings": 50})
    return {"iterations": 5, "findings": 50}


async def main():
    """主函数"""
    app = HulkApp()
    executor = TUIStreamExecutor(app)
    
    # 运行应用并执行任务
    async with app.run_test() as pilot:
        # 在后台执行任务
        asyncio.create_task(executor.execute(example_task))
        
        # 等待任务完成
        while app.is_running():
            await pilot.pause()
            await asyncio.sleep(0.1)
        
        # 获取结果
        result = app.get_result()
        print(f"\nTask result: {result}")


if __name__ == "__main__":
    # 实际运行时用: python -m textual run hulk_tui.py
    app = HulkApp()
    app.run()
