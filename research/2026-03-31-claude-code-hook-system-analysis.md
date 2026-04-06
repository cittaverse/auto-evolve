# Claude Code Hook 系统源码深度分析

**研究时间**: 2026-03-31 15:30 UTC  
**来源**: `/tmp/claude-code-study/plugins/hookify/` (实际源码)  
**目标**: 提取可直接用于 Hulk v2.0 的 Hook 系统

---

## 一、Hook 系统架构

### 1.1 Hook 类型

Claude Code 支持 4 种 Hook：

| Hook 类型 | 触发时机 | 用途 |
|----------|---------|------|
| **PreToolUse** | 工具执行前 | 权限检查/命令验证 |
| **PostToolUse** | 工具执行后 | 结果审计/日志记录 |
| **Stop** | Agent 停止时 | 完成检查/状态保存 |
| **UserPromptSubmit** | 用户提交提示时 | 输入过滤/意图分析 |

### 1.2 Hook 配置 (`hooks.json`)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/pretooluse.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [...],
    "Stop": [...],
    "UserPromptSubmit": [...]
  }
}
```

**关键点**:
1. ✅ Hook 是独立 Python 脚本
2. ✅ 通过 stdin 接收输入
3. ✅ 通过 stdout 返回 JSON 结果
4. ✅ 有超时限制 (10 秒)

---

## 二、Hook 输入/输出格式

### 2.1 PreToolUse 输入

```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/*"
  },
  "conversation_history": [...],
  "session_id": "abc123"
}
```

### 2.2 PreToolUse 输出

**允许执行**:
```json
{}
```

**阻止执行**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny"
  },
  "systemMessage": "⚠️ Dangerous command detected: rm -rf"
}
```

**错误处理**:
```json
{
  "systemMessage": "Hookify error: [error details]"
}
```

---

## 三、规则引擎核心代码

### 3.1 规则定义 (`config_loader.py`)

```python
@dataclass
class Condition:
    """单个条件"""
    field: str       # "command", "new_text", "file_path"
    operator: str    # "regex_match", "contains", "equals"
    pattern: str     # 匹配模式

@dataclass
class Rule:
    """规则定义"""
    name: str
    enabled: bool
    event: str       # "bash", "file", "stop", "all"
    conditions: List[Condition]
    action: str      # "warn" or "block"
    message: str     # Markdown 消息体
```

### 3.2 规则引擎 (`rule_engine.py`)

```python
class RuleEngine:
    """规则评估引擎"""
    
    def evaluate_rules(
        self,
        rules: List[Rule],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估所有规则并返回组合结果"""
        
        blocking_rules = []
        warning_rules = []
        
        for rule in rules:
            if self._rule_matches(rule, input_data):
                if rule.action == 'block':
                    blocking_rules.append(rule)
                else:
                    warning_rules.append(rule)
        
        # 阻止规则优先
        if blocking_rules:
            messages = [f"**[{r.name}]**\n{r.message}" for r in blocking_rules]
            combined_message = "\n\n".join(messages)
            
            return {
                "hookSpecificOutput": {
                    "permissionDecision": "deny"
                },
                "systemMessage": combined_message
            }
        
        # 警告规则
        if warning_rules:
            messages = [f"**[{r.name}]**\n{r.message}" for r in warning_rules]
            return {"systemMessage": "\n\n".join(messages)}
        
        # 无匹配规则
        return {}
    
    def _rule_matches(self, rule: Rule, input_data: Dict) -> bool:
        """检查单条规则是否匹配"""
        for condition in rule.conditions:
            if not self._condition_matches(condition, input_data):
                return False
        return True
    
    def _condition_matches(
        self,
        condition: Condition,
        input_data: Dict
    ) -> bool:
        """检查单个条件是否匹配"""
        value = self._get_field_value(condition.field, input_data)
        
        if condition.operator == 'regex_match':
            return bool(re.search(condition.pattern, value, re.IGNORECASE))
        elif condition.operator == 'contains':
            return condition.pattern in value
        elif condition.operator == 'equals':
            return condition.pattern == value
        
        return False
    
    def _get_field_value(self, field: str, input_data: Dict) -> str:
        """获取字段值"""
        # 支持嵌套字段：tool_input.command
        parts = field.split('.')
        value = input_data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, '')
            else:
                return ''
        return str(value)
```

---

## 四、可直接用的代码模式

### 4.1 Hulk Hook 系统基础架构

```python
# hulk_hooks/core/hook_engine.py
#!/usr/bin/env python3
"""Hulk Hook 系统 — 参考 Claude Code Hookify"""

import json
import sys
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re


@dataclass
class HookCondition:
    """Hook 条件"""
    field: str
    operator: str  # "regex_match", "contains", "equals"
    pattern: str


@dataclass
class HookRule:
    """Hook 规则"""
    name: str
    enabled: bool
    event: str  # "bash", "file_write", "web_search", "stop"
    conditions: List[HookCondition]
    action: str  # "warn" or "block"
    message: str


class HulkHookEngine:
    """Hulk Hook 引擎"""
    
    def __init__(self):
        self.rules: List[HookRule] = []
    
    def load_rules(self, event: str) -> List[HookRule]:
        """加载规则 (从文件或内存)"""
        # 实现规则加载逻辑
        pass
    
    def evaluate(
        self,
        event: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估 Hook"""
        rules = self.load_rules(event)
        
        blocking_rules = []
        warning_rules = []
        
        for rule in rules:
            if not rule.enabled:
                continue
            if rule.event != event and rule.event != 'all':
                continue
            
            if self._rule_matches(rule, input_data):
                if rule.action == 'block':
                    blocking_rules.append(rule)
                else:
                    warning_rules.append(rule)
        
        # 阻止优先
        if blocking_rules:
            messages = [f"**[{r.name}]** {r.message}" for r in blocking_rules]
            return {
                "decision": "block",
                "reason": "\n\n".join(messages)
            }
        
        # 警告
        if warning_rules:
            messages = [f"**[{r.name}]** {r.message}" for r in warning_rules]
            return {
                "decision": "warn",
                "reason": "\n\n".join(messages)
            }
        
        return {"decision": "allow"}
    
    def _rule_matches(
        self,
        rule: HookRule,
        input_data: Dict
    ) -> bool:
        """检查规则是否匹配"""
        for cond in rule.conditions:
            if not self._condition_matches(cond, input_data):
                return False
        return True
    
    def _condition_matches(
        self,
        cond: HookCondition,
        input_data: Dict
    ) -> bool:
        """检查条件是否匹配"""
        value = self._get_field(cond.field, input_data)
        
        if cond.operator == 'regex_match':
            return bool(re.search(cond.pattern, value, re.I))
        elif cond.operator == 'contains':
            return cond.pattern in value
        elif cond.operator == 'equals':
            return cond.pattern == value
        
        return False
    
    def _get_field(self, field: str, data: Dict) -> str:
        """获取字段值 (支持嵌套)"""
        parts = field.split('.')
        value = data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, '')
            else:
                return ''
        return str(value)
```

### 4.2 Hulk Hook 实现示例

```python
# hulk_hooks/hooks/pre_bash.py
#!/usr/bin/env python3
"""Pre-Bash Hook — 命令执行前检查"""

import json
import sys
import os

# 导入 Hook 引擎
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.hook_engine import HulkHookEngine


def main():
    try:
        # 从 stdin 读取输入
        input_data = json.load(sys.stdin)
        
        # 示例输入:
        # {
        #   "hook_event": "pre_bash",
        #   "command": "rm -rf /tmp/*",
        #   "cwd": "/home/user/project"
        # }
        
        engine = HulkHookEngine()
        result = engine.evaluate("bash", input_data)
        
        # 输出结果
        if result.get("decision") == "block":
            print(json.dumps({
                "decision": "deny",
                "reason": result.get("reason", "Blocked by hook")
            }))
        elif result.get("decision") == "warn":
            print(json.dumps({
                "systemMessage": result.get("reason", "")
            }))
        else:
            print(json.dumps({}))  # 允许执行
        
        sys.exit(0)
    
    except Exception as e:
        # 错误时允许执行
        print(json.dumps({
            "systemMessage": f"Hook error: {str(e)}"
        }))
        sys.exit(0)


if __name__ == "__main__":
    main()
```

### 4.3 Hulk Hook 配置

```json
// hulk_hooks/config/hooks.json
{
  "hooks": {
    "pre_bash": [
      {
        "type": "command",
        "command": "python3 /path/to/hooks/pre_bash.py",
        "timeout": 10
      }
    ],
    "pre_file_write": [...],
    "pre_web_search": [...],
    "stop": [...]
  }
}
```

### 4.4 Hulk Hook 规则示例

```markdown
<!-- .hulk/hooks/security.local.md -->
---
name: dangerous_command
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: "rm\\s+-rf\\s+/"
action: block
---
⚠️ **危险命令检测**

检测到可能危险的命令：`rm -rf /`

这会删除系统文件，可能导致系统崩溃。请使用更安全的替代方案：
- 使用 `rm -rf ./specific_dir` 指定目录
- 使用 Docker 容器进行测试
- 使用虚拟机进行测试
```

---

## 五、Hulk v2.0 直接采用

### 5.1 立即实现 (P0)

| 组件 | 文件 | 行数 | 状态 |
|------|------|------|------|
| Hook 引擎 | `hulk_hooks/core/hook_engine.py` | 150 | ⏳ 待实现 |
| Pre-Bash Hook | `hulk_hooks/hooks/pre_bash.py` | 50 | ⏳ 待实现 |
| Pre-File Hook | `hulk_hooks/hooks/pre_file_write.py` | 50 | ⏳ 待实现 |
| Stop Hook | `hulk_hooks/hooks/stop.py` | 50 | ⏳ 待实现 |
| Hook 配置 | `hulk_hooks/config/hooks.json` | 30 | ⏳ 待实现 |

### 5.2 与现有 v2.0 集成

| Hulk v2.0 模块 | Hook 集成点 |
|---------------|------------|
| `permission_system.py` | 替换为 Hook 引擎 |
| `tool_system.py` | PreToolUse Hook |
| `state_persistence.py` | Stop Hook |
| `agent_loop.py` | Hook 调用点 |

---

## 六、总结

### Claude Code Hook 系统核心优势

1. **模块化** — 每个 Hook 是独立脚本
2. **声明式** — Markdown 规则文件
3. **可扩展** — 轻松添加新 Hook
4. **安全** — 超时限制 + 错误不阻塞
5. **灵活** — 支持正则/包含/等于多种条件

### Hulk v2.0 采用计划

| 阶段 | 行动 | 时间 |
|------|------|------|
| P0 | 实现 Hook 引擎 + Pre-Bash Hook | 2h |
| P1 | 实现 Pre-File + Stop Hook | 2h |
| P2 | 集成到 Agent 循环 | 2h |
| P3 | 添加规则文件示例 | 1h |

---

*Hulk 🟢 — Claude Code Hook 系统源码分析完成*
