#!/usr/bin/env python3
"""
上下文管理器 — 参考 Claude Code 滑动窗口设计

核心思想:
1. 滑动窗口 — 保留最近对话，移除早期消息
2. Token 计数 — 精确控制上下文大小
3. 系统消息保护 — 不移除 system role 的消息

深度实现:
- 多种裁剪策略 (FIFO/重要性/摘要)
- Token 精确计数 (tiktoken)
- 消息优先级管理
"""

import json
import tiktoken
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum


# === 消息类型定义 ===

class MessageRole(str, Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """对话消息"""
    role: MessageRole
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    priority: int = 5  # 1-10, 越高越重要
    token_count: int = 0  # 缓存 token 数
    
    def to_dict(self) -> Dict:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "priority": self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            metadata=data.get("metadata", {}),
            priority=data.get("priority", 5)
        )


# === Token 计数器 ===

class TokenCounter:
    """Token 计数器 — 支持多种模型"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            # 模型不支持，回退到 cl100k_base
            self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def count(self, text: str) -> int:
        """计算文本 token 数"""
        return len(self.encoder.encode(text))
    
    def count_message(self, message: Message) -> int:
        """计算消息 token 数"""
        if message.token_count > 0:
            return message.token_count
        
        # 基础开销
        tokens = 4  # 每条消息的基础 token
        
        # 角色开销
        tokens += self.count(message.role.value)
        
        # 内容开销
        if isinstance(message.content, str):
            tokens += self.count(message.content)
        elif isinstance(message.content, (list, dict)):
            tokens += self.count(json.dumps(message.content))
        else:
            tokens += self.count(str(message.content))
        
        # 缓存
        message.token_count = tokens
        return tokens
    
    def count_messages(self, messages: List[Message]) -> int:
        """计算多条消息总 token 数"""
        return sum(self.count_message(msg) for msg in messages)


# === 裁剪策略 ===

class TrimmingStrategy(str, Enum):
    """裁剪策略"""
    FIFO = "fifo"              # 先进先出
    PRIORITY = "priority"      # 按优先级
    SUMMARY = "summary"        # 摘要压缩


class ContextManager:
    """上下文管理器 — 滑动窗口实现"""
    
    def __init__(
        self,
        max_tokens: int = 128000,
        model: str = "gpt-4",
        trimming_strategy: TrimmingStrategy = TrimmingStrategy.PRIORITY
    ):
        self.max_tokens = max_tokens
        self.strategy = trimming_strategy
        self.messages: List[Message] = []
        self.token_counter = TokenCounter(model)
        self._system_messages: List[Message] = []
    
    def add_system_message(self, content: str, priority: int = 10):
        """添加系统消息 (不受裁剪影响)"""
        msg = Message(
            role=MessageRole.SYSTEM,
            content=content,
            priority=priority
        )
        msg.token_count = self.token_counter.count_message(msg)
        self._system_messages.append(msg)
    
    def add_message(
        self,
        role: MessageRole,
        content: Any,
        priority: int = 5,
        metadata: Dict = None
    ):
        """添加消息"""
        msg = Message(
            role=role,
            content=content,
            priority=priority,
            metadata=metadata or {}
        )
        msg.token_count = self.token_counter.count_message(msg)
        self.messages.append(msg)
        self._trim_if_needed()
    
    def _trim_if_needed(self):
        """如果超出限制则裁剪"""
        current_tokens = self.token_counter.count_messages(self.messages)
        
        while current_tokens > self.max_tokens and len(self.messages) > 0:
            removed = self._trim_one_message()
            if not removed:
                break
            current_tokens = self.token_counter.count_messages(self.messages)
    
    def _trim_one_message(self) -> bool:
        """裁剪一条消息"""
        if not self.messages:
            return False
        
        if self.strategy == TrimmingStrategy.FIFO:
            # 移除最早的非系统消息
            for i, msg in enumerate(self.messages):
                if msg.role != MessageRole.SYSTEM:
                    self.messages.pop(i)
                    return True
        
        elif self.strategy == TrimmingStrategy.PRIORITY:
            # 移除优先级最低的消息
            min_priority = float('inf')
            min_index = -1
            for i, msg in enumerate(self.messages):
                if msg.role != MessageRole.SYSTEM and msg.priority < min_priority:
                    min_priority = msg.priority
                    min_index = i
            if min_index >= 0:
                self.messages.pop(min_index)
                return True
        
        elif self.strategy == TrimmingStrategy.SUMMARY:
            # TODO: 实现摘要压缩
            # 暂时回退到 FIFO
            return self._trim_fifo()
        
        return False
    
    def _trim_fifo(self) -> bool:
        """FIFO 裁剪"""
        for i, msg in enumerate(self.messages):
            if msg.role != MessageRole.SYSTEM:
                self.messages.pop(i)
                return True
        return False
    
    def get_messages(self) -> List[Dict]:
        """获取消息列表 (给模型)"""
        all_messages = self._system_messages + self.messages
        return [msg.to_dict() for msg in all_messages]
    
    def get_token_count(self) -> int:
        """获取当前 token 数"""
        system_tokens = self.token_counter.count_messages(self._system_messages)
        message_tokens = self.token_counter.count_messages(self.messages)
        return system_tokens + message_tokens
    
    def get_usage_stats(self) -> Dict:
        """获取使用统计"""
        system_tokens = self.token_counter.count_messages(self._system_messages)
        message_tokens = self.token_counter.count_messages(self.messages)
        total_tokens = system_tokens + message_tokens
        
        return {
            "system_tokens": system_tokens,
            "message_tokens": message_tokens,
            "total_tokens": total_tokens,
            "max_tokens": self.max_tokens,
            "usage_percent": (total_tokens / self.max_tokens) * 100,
            "message_count": len(self.messages),
            "system_message_count": len(self._system_messages)
        }
    
    def clear(self):
        """清除所有消息"""
        self.messages.clear()
    
    def save(self, filepath: str):
        """保存到文件"""
        data = {
            "system_messages": [msg.to_dict() for msg in self._system_messages],
            "messages": [msg.to_dict() for msg in self.messages],
            "max_tokens": self.max_tokens,
            "strategy": self.strategy.value
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, filepath: str):
        """从文件加载"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._system_messages = [Message.from_dict(m) for m in data.get("system_messages", [])]
        self.messages = [Message.from_dict(m) for m in data.get("messages", [])]
        self.max_tokens = data.get("max_tokens", 128000)
        self.strategy = TrimmingStrategy(data.get("strategy", "priority"))


# === 使用示例 ===

def main():
    """演示上下文管理器"""
    print("=" * 60)
    print("上下文管理器演示 — 滑动窗口")
    print("=" * 60)
    print()
    
    # 创建上下文管理器
    ctx = ContextManager(
        max_tokens=1000,  # 小窗口用于演示
        model="gpt-4",
        trimming_strategy=TrimmingStrategy.PRIORITY
    )
    
    # 添加系统消息
    ctx.add_system_message("You are a helpful AI assistant.")
    
    # 添加对话
    print("添加对话...")
    for i in range(20):
        ctx.add_message(MessageRole.USER, f"Question {i}", priority=5)
        ctx.add_message(MessageRole.ASSISTANT, f"Answer {i}", priority=5)
        
        stats = ctx.get_usage_stats()
        print(f"  Message {i+1}: {stats['total_tokens']} tokens ({stats['usage_percent']:.0f}%)")
    
    print()
    print("最终状态:")
    stats = ctx.get_usage_stats()
    print(f"  总 token: {stats['total_tokens']}")
    print(f"  使用率：{stats['usage_percent']:.0f}%")
    print(f"  消息数：{stats['message_count']}")
    print(f"  裁剪策略：{ctx.strategy.value}")
    
    # 保存/加载演示
    ctx.save("/tmp/context-demo.json")
    print()
    print("已保存到 /tmp/context-demo.json")
    
    # 加载验证
    ctx2 = ContextManager()
    ctx2.load("/tmp/context-demo.json")
    print(f"加载后消息数：{len(ctx2.messages)}")


if __name__ == "__main__":
    main()
