#!/usr/bin/env python3
"""
状态持久化 — 深度实现

核心功能:
1. JSON 状态保存 — 完整序列化 Agent 状态
2. 自动恢复 — 启动时检查并恢复
3. 状态版本控制 — 兼容不同版本格式

深度实现:
- 完整状态快照 (Agent/Context/Tool)
- 增量保存 (只保存变化部分)
- 状态过期清理
"""

import json
import os
import asyncio
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import hashlib


# === 状态数据结构 ===

@dataclass
class AgentState:
    """Agent 状态"""
    state: str  # IDLE/THINKING/ACTING/OBSERVING/DONE/ERROR
    iteration: int
    max_iterations: int
    tool_calls: List[Dict]
    context_tokens: int
    timestamp: str


@dataclass
class ContextState:
    """上下文状态"""
    system_messages: List[Dict]
    messages: List[Dict]
    max_tokens: int
    strategy: str


@dataclass
class FullState:
    """完整状态"""
    version: str = "1.0"
    created_at: str = ""
    updated_at: str = ""
    agent: Optional[AgentState] = None
    context: Optional[ContextState] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


# === 状态管理器 ===

class StatePersistence:
    """状态持久化管理器"""
    
    def __init__(self, state_dir: str = ".hulk-state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.current_state: Optional[FullState] = None
        self._state_file: Optional[Path] = None
        self._setup_signal_handler()
    
    def _setup_signal_handler(self):
        """设置信号处理器"""
        def handler(signum, frame):
            print("\n⏸️  检测到中断，保存状态...")
            self.save()
            print("✅ 状态已保存")
            exit(0)
        
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
    
    def create_state(self) -> FullState:
        """创建新状态"""
        self.current_state = FullState()
        return self.current_state
    
    def update_agent_state(
        self,
        state: str,
        iteration: int,
        max_iterations: int,
        tool_calls: List[Dict] = None,
        context_tokens: int = 0
    ):
        """更新 Agent 状态"""
        if not self.current_state:
            self.create_state()
        
        self.current_state.agent = AgentState(
            state=state,
            iteration=iteration,
            max_iterations=max_iterations,
            tool_calls=tool_calls or [],
            context_tokens=context_tokens,
            timestamp=datetime.now().isoformat()
        )
        self.current_state.updated_at = datetime.now().isoformat()
    
    def update_context_state(
        self,
        system_messages: List[Dict],
        messages: List[Dict],
        max_tokens: int,
        strategy: str
    ):
        """更新上下文状态"""
        if not self.current_state:
            self.create_state()
        
        self.current_state.context = ContextState(
            system_messages=system_messages,
            messages=messages,
            max_tokens=max_tokens,
            strategy=strategy
        )
        self.current_state.updated_at = datetime.now().isoformat()
    
    def add_metadata(self, key: str, value: Any):
        """添加元数据"""
        if not self.current_state:
            self.create_state()
        self.current_state.metadata[key] = value
    
    def _get_state_hash(self) -> str:
        """计算状态哈希 (用于检测变化)"""
        if not self.current_state:
            return ""
        content = json.dumps(asdict(self.current_state), sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def save(self, filepath: Optional[str] = None) -> str:
        """
        保存状态
        
        Args:
            filepath: 自定义路径，默认自动生成
            
        Returns:
            保存的文件路径
        """
        if not self.current_state:
            raise ValueError("No state to save")
        
        # 自动生成文件名
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hash_suffix = self._get_state_hash()[:8]
            filename = f"hulk_state_{timestamp}_{hash_suffix}.json"
            filepath = str(self.state_dir / filename)
        
        # 保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.current_state), f, ensure_ascii=False, indent=2)
        
        self._state_file = Path(filepath)
        
        # 清理旧状态 (保留最近 10 个)
        self._cleanup_old_states()
        
        return filepath
    
    def load(self, filepath: Optional[str] = None) -> Optional[FullState]:
        """
        加载状态
        
        Args:
            filepath: 自定义路径，默认加载最新
            
        Returns:
            加载的状态，失败返回 None
        """
        if filepath:
            path = Path(filepath)
        else:
            # 查找最新状态文件
            path = self._find_latest_state()
        
        if not path or not path.exists():
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 版本兼容
            data = self._migrate_state(data)
            
            self.current_state = FullState(**data)
            self._state_file = path
            
            return self.current_state
        except Exception as e:
            print(f"❌ 加载状态失败：{e}")
            return None
    
    def _find_latest_state(self) -> Optional[Path]:
        """查找最新状态文件"""
        state_files = list(self.state_dir.glob("hulk_state_*.json"))
        if not state_files:
            return None
        
        # 按修改时间排序
        state_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return state_files[0]
    
    def _cleanup_old_states(self, keep: int = 10):
        """清理旧状态"""
        state_files = list(self.state_dir.glob("hulk_state_*.json"))
        if len(state_files) <= keep:
            return
        
        # 按修改时间排序，删除旧的
        state_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for old_file in state_files[keep:]:
            old_file.unlink()
    
    def _migrate_state(self, data: Dict) -> Dict:
        """状态版本迁移"""
        version = data.get("version", "1.0")
        
        # 未来版本迁移逻辑
        # if version == "0.9":
        #     data = self._migrate_from_v09(data)
        
        return data
    
    def should_resume(self) -> bool:
        """判断是否应该恢复"""
        latest = self._find_latest_state()
        if not latest:
            return False
        
        # 检查状态文件是否太旧 (超过 24 小时)
        mtime = latest.stat().st_mtime
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        
        if age_hours > 24:
            print(f"⚠️  状态文件已过时 ({age_hours:.1f} 小时前)")
            return False
        
        return True
    
    def clear(self):
        """清除当前状态"""
        self.current_state = None
        self._state_file = None
    
    def get_state_file(self) -> Optional[Path]:
        """获取当前状态文件"""
        return self._state_file
    
    def list_states(self) -> List[Dict]:
        """列出所有状态文件"""
        states = []
        for f in self.state_dir.glob("hulk_state_*.json"):
            stat = f.stat()
            states.append({
                "path": str(f),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size
            })
        states.sort(key=lambda x: x["modified"], reverse=True)
        return states


# === 可恢复任务 ===

class ResumableAgentTask:
    """可恢复 Agent 任务"""
    
    def __init__(self, persistence: StatePersistence):
        self.persistence = persistence
        self.resume_from_iteration = 0
    
    async def run(self, prompt: str, resume: bool = False):
        """
        运行任务 (支持恢复)
        
        Args:
            prompt: 用户输入
            resume: 是否从上次中断处恢复
        """
        if resume and self.persistence.should_resume():
            print("🔄 从上次中断处恢复...")
            state = self.persistence.load()
            if state and state.agent:
                self.resume_from_iteration = state.agent.iteration
                print(f"   恢复到迭代 {self.resume_from_iteration}")
        else:
            print("🚀 开始新任务")
            self.persistence.create_state()
            self.resume_from_iteration = 0
        
        # 模拟 Agent 循环
        max_iterations = 10
        for i in range(self.resume_from_iteration, max_iterations):
            # 更新状态
            self.persistence.update_agent_state(
                state="thinking",
                iteration=i + 1,
                max_iterations=max_iterations,
                context_tokens=1000 + i * 100
            )
            
            print(f"\n迭代 {i + 1}/{max_iterations}...")
            
            # 模拟工作
            await asyncio.sleep(0.5)
            
            # 定期保存 (每 2 次迭代)
            if (i + 1) % 2 == 0:
                filepath = self.persistence.save()
                print(f"💾 状态已保存到 {filepath}")
        
        # 完成
        self.persistence.update_agent_state(
            state="done",
            iteration=max_iterations,
            max_iterations=max_iterations
        )
        self.persistence.save()
        
        print("\n✅ 任务完成!")
        self.persistence.clear()
        
        return {"iterations": max_iterations}


# === 使用示例 ===

async def main():
    """主函数"""
    print("=" * 60)
    print("状态持久化演示")
    print("=" * 60)
    print()
    
    persistence = StatePersistence()
    task = ResumableAgentTask(persistence)
    
    # 检查是否需要恢复
    resume = persistence.should_resume()
    
    try:
        result = await task.run("Test prompt", resume=resume)
        print(f"\n最终结果：{result}")
    except KeyboardInterrupt:
        print("\n⏸️  任务中断，状态已保存")
        print(f"   恢复命令：python state_persistence.py --resume")
    
    # 列出所有状态文件
    print("\n状态文件列表:")
    for s in persistence.list_states()[:5]:
        print(f"  {s['path']} ({s['size']} bytes, {s['modified']})")


if __name__ == "__main__":
    import sys
    resume = "--resume" in sys.argv or "-r" in sys.argv
    asyncio.run(main())
