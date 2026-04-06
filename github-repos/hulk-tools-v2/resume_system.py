#!/usr/bin/env python3
"""
中断恢复系统 — 参考 Claude Code 优雅中断

核心思想:
1. 信号捕获 — Ctrl+C 不崩溃
2. 状态持久化 — JSON 保存中间状态
3. 自动恢复 — 启动时检查并恢复
"""

import signal
import json
import asyncio
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class StateManager:
    """状态管理器"""
    
    def __init__(self, state_file: str = ".hulk-state.json"):
        self.state_file = Path(state_file)
        self.state: Dict[str, Any] = {}
        self._setup_signal_handler()
    
    def _setup_signal_handler(self):
        """设置信号处理器"""
        def handler(signum, frame):
            print("\n\n⏸️  检测到中断，保存状态中...")
            self.save()
            print("✅ 状态已保存，恢复命令：hulk --resume")
            exit(0)
        
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
    
    def update(self, key: str, value: Any):
        """更新状态"""
        self.state[key] = value
        self.state["last_updated"] = datetime.now().isoformat()
    
    def save(self):
        """保存状态到文件"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
            print(f"📝 状态已保存到 {self.state_file}")
        except Exception as e:
            print(f"❌ 保存失败：{e}")
    
    def load(self) -> bool:
        """从文件加载状态"""
        if not self.state_file.exists():
            return False
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
            print(f"📥 已加载状态 (更新时间：{self.state.get('last_updated', '未知')})")
            return True
        except Exception as e:
            print(f"❌ 加载失败：{e}")
            return False
    
    def clear(self):
        """清除状态文件"""
        if self.state_file.exists():
            self.state_file.unlink()
            print("🗑️  状态文件已清除")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取状态值"""
        return self.state.get(key, default)
    
    def should_resume(self) -> bool:
        """判断是否应该恢复"""
        if not self.state_file.exists():
            return False
        
        # 检查状态文件是否太旧 (超过 24 小时)
        try:
            mtime = self.state_file.stat().st_mtime
            age_hours = (datetime.now().timestamp() - mtime) / 3600
            if age_hours > 24:
                print(f"⚠️  状态文件已过时 ({age_hours:.1f} 小时前)，建议重新开始")
                return False
            return True
        except:
            return True


class ResumableTask:
    """可恢复任务基类"""
    
    def __init__(self, state_manager: StateManager):
        self.state = state_manager
        self.current_step = 0
        self.results = []
    
    async def run(self, resume: bool = False):
        """
        运行任务 (支持恢复)
        
        Args:
            resume: 是否从上次中断处恢复
        """
        if resume and self.state.should_resume():
            print("🔄 从上次中断处恢复...")
            self.current_step = self.state.get("current_step", 0)
            self.results = self.state.get("results", [])
            print(f"   恢复到步骤 {self.current_step}, 已完成 {len(self.results)} 个结果")
        else:
            print("🚀 开始新任务")
            self.current_step = 0
            self.results = []
        
        # 模拟多步骤任务
        for i in range(self.current_step, 5):
            self.current_step = i
            self.state.update("current_step", i)
            self.state.update("results", self.results)
            
            print(f"\n步骤 {i+1}/5...")
            await asyncio.sleep(1)  # 模拟工作
            
            # 模拟 Ctrl+C 测试
            # if i == 2:
            #     raise KeyboardInterrupt
            
            self.results.append(f"结果 {i+1}")
            self.state.save()
        
        print("\n✅ 任务完成!")
        self.state.clear()
        return self.results


# 使用示例
async def main():
    import sys
    
    state = StateManager()
    task = ResumableTask(state)
    
    # 检查是否需要恢复
    resume = "--resume" in sys.argv or "-r" in sys.argv
    
    try:
        results = await task.run(resume=resume)
        print(f"\n最终结果：{results}")
    except KeyboardInterrupt:
        print("\n⏸️  任务中断，状态已保存")
        print("   恢复命令：python resume_system.py --resume")


if __name__ == "__main__":
    asyncio.run(main())
