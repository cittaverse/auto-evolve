#!/usr/bin/env python3
"""
Hulk Hook 系统 — 参考 Claude Code Hookify

核心功能:
1. PreToolUse Hook — 工具执行前检查
2. PostToolUse Hook — 工具执行后审计
3. Stop Hook — Agent 停止时处理
4. UserPromptSubmit Hook — 用户输入过滤

深度实现:
- 声明式规则 (Markdown + YAML frontmatter)
- 条件匹配 (regex/contains/equals)
- 动作执行 (warn/block)
- 超时控制 + 错误不阻塞
"""

import json
import sys
import os
import re
import subprocess
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime


# ============================================
# 数据结构
# ============================================

@dataclass
class HookCondition:
    """Hook 条件"""
    field: str  # "command", "file_path", "content", "tool_name"
    operator: str  # "regex_match", "contains", "equals", "starts_with"
    pattern: str
    
    def matches(self, value: str) -> bool:
        """检查条件是否匹配"""
        if not value:
            return False
        
        if self.operator == 'regex_match':
            return bool(re.search(self.pattern, value, re.IGNORECASE))
        elif self.operator == 'contains':
            return self.pattern.lower() in value.lower()
        elif self.operator == 'equals':
            return self.pattern.lower() == value.lower()
        elif self.operator == 'starts_with':
            return value.lower().startswith(self.pattern.lower())
        
        return False


@dataclass
class HookRule:
    """Hook 规则"""
    name: str
    enabled: bool
    event: str  # "pre_bash", "pre_file_write", "pre_web_search", "stop", "user_prompt"
    conditions: List[HookCondition]
    action: str  # "warn" or "block"
    message: str
    timeout: int = 10  # 超时 (秒)
    
    @classmethod
    def from_frontmatter(cls, frontmatter: Dict, message: str) -> 'HookRule':
        """从 frontmatter 创建规则"""
        conditions = []
        
        # 解析条件
        if 'conditions' in frontmatter:
            for c in frontmatter['conditions']:
                conditions.append(HookCondition(
                    field=c.get('field', ''),
                    operator=c.get('operator', 'regex_match'),
                    pattern=c.get('pattern', '')
                ))
        
        return cls(
            name=frontmatter.get('name', 'unnamed'),
            enabled=frontmatter.get('enabled', True),
            event=frontmatter.get('event', 'all'),
            conditions=conditions,
            action=frontmatter.get('action', 'warn'),
            message=message.strip(),
            timeout=frontmatter.get('timeout', 10)
        )


# ============================================
# Hook 引擎
# ============================================

class HulkHookEngine:
    """Hulk Hook 引擎"""
    
    def __init__(self, hooks_dir: str = ".hulk/hooks"):
        self.hooks_dir = Path(hooks_dir)
        self.rules: List[HookRule] = []
        self.hook_scripts: Dict[str, List[str]] = {}
        self._load_rules()
        self._load_hook_scripts()
    
    def _load_rules(self):
        """加载规则文件"""
        if not self.hooks_dir.exists():
            self.hooks_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # 加载所有 .local.md 规则文件 (包括子目录)
        for rule_file in self.hooks_dir.rglob("*.local.md"):
            try:
                content = rule_file.read_text(encoding='utf-8')
                rules = self._parse_rule_file(content)
                self.rules.extend(rules)
            except Exception as e:
                print(f"⚠️ 加载规则失败 {rule_file}: {e}", file=sys.stderr)
    
    def _parse_rule_file(self, content: str) -> List[HookRule]:
        """解析规则文件 (Markdown + YAML frontmatter)"""
        if not content.startswith('---'):
            return []
        
        # 分割 frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return []
        
        # 解析 YAML frontmatter (简单解析)
        frontmatter = {}
        for line in parts[1].strip().split('\n'):
            if ':' in line and not line.strip().startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # 处理布尔值
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                # 处理整数
                elif value.isdigit():
                    value = int(value)
                
                frontmatter[key] = value
        
        # 解析 conditions (简化版)
        if 'conditions' in content:
            # 简化处理：从 content 中提取条件
            pass
        
        message = parts[2].strip()
        return [HookRule.from_frontmatter(frontmatter, message)]
    
    def _load_hook_scripts(self):
        """加载 Hook 脚本配置"""
        config_file = self.hooks_dir / "hooks.json"
        if not config_file.exists():
            # 创建默认配置
            self._create_default_config()
            return
        
        try:
            config = json.loads(config_file.read_text())
            self.hook_scripts = config.get('hooks', {})
        except Exception as e:
            print(f"⚠️ 加载 Hook 配置失败：{e}", file=sys.stderr)
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认 Hook 配置"""
        default_config = {
            "hooks": {
                "pre_bash": [
                    {
                        "type": "command",
                        "command": "python3 ${HULK_HOOKS_ROOT}/hooks/pre_bash.py",
                        "timeout": 10
                    }
                ],
                "pre_file_write": [
                    {
                        "type": "command",
                        "command": "python3 ${HULK_HOOKS_ROOT}/hooks/pre_file_write.py",
                        "timeout": 10
                    }
                ],
                "stop": [
                    {
                        "type": "command",
                        "command": "python3 ${HULK_HOOKS_ROOT}/hooks/stop.py",
                        "timeout": 10
                    }
                ]
            }
        }
        
        config_file = self.hooks_dir / "hooks.json"
        config_file.write_text(json.dumps(default_config, indent=2))
        self.hook_scripts = default_config['hooks']
    
    def evaluate(self, event: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估 Hook
        
        Args:
            event: Hook 事件类型 (pre_bash, pre_file_write, stop, ...)
            input_data: Hook 输入数据
            
        Returns:
            Hook 结果 (允许/阻止/警告)
        """
        result = {"decision": "allow"}
        
        # 1. 评估规则
        rule_result = self._evaluate_rules(event, input_data)
        if rule_result.get("decision") == "block":
            return rule_result
        elif rule_result.get("decision") == "warn":
            result["systemMessage"] = rule_result.get("reason", "")
        
        # 2. 执行 Hook 脚本
        script_result = self._execute_hook_scripts(event, input_data)
        if script_result.get("decision") == "block":
            return script_result
        elif script_result.get("systemMessage"):
            if result.get("systemMessage"):
                result["systemMessage"] += "\n\n" + script_result["systemMessage"]
            else:
                result["systemMessage"] = script_result["systemMessage"]
        
        return result
    
    def _evaluate_rules(
        self,
        event: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估规则"""
        blocking_rules = []
        warning_rules = []
        
        for rule in self.rules:
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
    
    def _rule_matches(self, rule: HookRule, input_data: Dict) -> bool:
        """检查规则是否匹配"""
        for cond in rule.conditions:
            value = self._get_field_value(cond.field, input_data)
            if not cond.matches(value):
                return False
        return True
    
    def _get_field_value(self, field: str, data: Dict) -> str:
        """获取字段值 (支持嵌套)"""
        parts = field.split('.')
        value = data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, '')
            else:
                return ''
        return str(value)
    
    def _execute_hook_scripts(
        self,
        event: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行 Hook 脚本"""
        scripts = self.hook_scripts.get(event, [])
        if not scripts:
            return {"decision": "allow"}
        
        combined_result = {"decision": "allow"}
        
        for script_config in scripts:
            try:
                result = self._execute_single_hook(script_config, event, input_data)
                
                # 合并结果
                if result.get("decision") == "block":
                    return result  # 阻止立即返回
                elif result.get("systemMessage"):
                    if combined_result.get("systemMessage"):
                        combined_result["systemMessage"] += "\n\n" + result["systemMessage"]
                    else:
                        combined_result["systemMessage"] = result["systemMessage"]
                
            except Exception as e:
                # 错误不阻塞
                print(f"⚠️ Hook 执行失败：{e}", file=sys.stderr)
        
        return combined_result
    
    def _execute_single_hook(
        self,
        script_config: Dict,
        event: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行单个 Hook 脚本"""
        command = script_config.get("command", "")
        timeout = script_config.get("timeout", 10)
        
        # 替换环境变量
        command = command.replace("${HULK_HOOKS_ROOT}", str(self.hooks_dir))
        
        # 执行脚本
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(
                input=json.dumps(input_data),
                timeout=timeout
            )
            
            # 解析输出
            if stdout.strip():
                return json.loads(stdout.strip())
            return {"decision": "allow"}
            
        except subprocess.TimeoutExpired:
            return {
                "systemMessage": f"⚠️ Hook 超时 ({timeout}s)"
            }
        except json.JSONDecodeError:
            return {
                "systemMessage": "⚠️ Hook 输出格式错误"
            }
        except Exception as e:
            return {
                "systemMessage": f"⚠️ Hook 执行错误：{str(e)}"
            }


# ============================================
# Hook 输入/输出格式
# ============================================

def create_pre_bash_input(command: str, cwd: str = "") -> Dict:
    """创建 Pre-Bash Hook 输入"""
    return {
        "hook_event": "pre_bash",
        "tool_name": "Bash",
        "command": command,
        "cwd": cwd,
        "timestamp": datetime.now().isoformat()
    }


def create_pre_file_write_input(
    file_path: str,
    content: str,
    old_content: str = ""
) -> Dict:
    """创建 Pre-File-Write Hook 输入"""
    return {
        "hook_event": "pre_file_write",
        "tool_name": "Write",
        "file_path": file_path,
        "content": content,
        "old_content": old_content,
        "timestamp": datetime.now().isoformat()
    }


def create_stop_input(
    reason: str = "",
    iteration: int = 0,
    context_tokens: int = 0
) -> Dict:
    """创建 Stop Hook 输入"""
    return {
        "hook_event": "stop",
        "reason": reason,
        "iteration": iteration,
        "context_tokens": context_tokens,
        "timestamp": datetime.now().isoformat()
    }


# ============================================
# 使用示例
# ============================================

def example_usage():
    """使用示例"""
    print("=" * 60)
    print("Hulk Hook 系统演示")
    print("=" * 60)
    print()
    
    engine = HulkHookEngine()
    
    # 示例 1: Pre-Bash Hook
    print("【示例 1】Pre-Bash Hook")
    print("-" * 50)
    input_data = create_pre_bash_input("rm -rf /tmp/*")
    result = engine.evaluate("pre_bash", input_data)
    print(f"输入：{input_data}")
    print(f"结果：{result}")
    print()
    
    # 示例 2: Pre-File-Write Hook
    print("【示例 2】Pre-File-Write Hook")
    print("-" * 50)
    input_data = create_pre_file_write_input(
        file_path=".env",
        content="API_KEY=secret123"
    )
    result = engine.evaluate("pre_file_write", input_data)
    print(f"输入：{input_data}")
    print(f"结果：{result}")
    print()
    
    # 示例 3: Stop Hook
    print("【示例 3】Stop Hook")
    print("-" * 50)
    input_data = create_stop_input(
        reason="Task completed",
        iteration=10,
        context_tokens=50000
    )
    result = engine.evaluate("stop", input_data)
    print(f"输入：{input_data}")
    print(f"结果：{result}")
    print()


if __name__ == "__main__":
    example_usage()
