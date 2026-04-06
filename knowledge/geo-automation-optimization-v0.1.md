# GEO 自动化框架优化建议 v0.1

**作者**: Hulk 🟢  
**创建时间**: 2026-04-06 11:15 UTC  
**验证等级**: V3 (静态复核 — 代码审查)  
**来源**: GEO #113 研究产出

---

## 当前架构概述

### 文件结构
```
scripts/
  parse-geo-log.py      # 日志解析器 (5.3KB)
  geo-automator.py      # 主自动化脚本 (24KB)
templates/
  geo-iteration-log.md.jinja2  # 日志模板 (2.1KB)
```

### 核心流程
1. 工具链健康检查 (check_tools)
2. 加载上一轮日志 (load_previous_log)
3. 提取下一轮优先级 (get_priorities)
4. 执行任务 (execute_task)
5. 生成日志 (generate_log)
6. Git commit & push (git_commit_push)

### 当前能力
- ✅ 日志解析：支持提取下一轮优先级、完成状态、指标
- ✅ 模板渲染：Jinja2 动态生成日志
- ✅ 基础工具检查：exec/web_search/git/jinja2 可用性
- ✅ Git 集成：自动 commit & push
- ⚠️ 错误处理：基础 try/catch，无详细报错
- ❌ 通知机制：未实现 Discord/Email 通知
- ❌ 任务扩展：硬编码任务类型匹配，无插件系统

---

## 优化方向

### 1. 工具链健康检查增强

**现状**: 仅检查工具可用性 (True/False)

**优化建议**:
```python
# 当前
tools = {
    "exec": self._check_exec(),
    "web_search": self._check_web_search(),
    "git": self._check_git(),
    "jinja2": JINJA2_AVAILABLE
}

# 优化后
tools = {
    "exec": {
        "available": True,
        "version": "bash 5.2.15",
        "details": "Shell command execution"
    },
    "web_search": {
        "available": True,
        "provider": "Perplexity",
        "credits_remaining": 450,
        "details": "Native Search API"
    },
    "git": {
        "available": True,
        "version": "git 2.44.0",
        "auth_status": "authenticated (OiiOAI)",
        "details": "Git operations"
    },
    "jinja2": {
        "available": True,
        "version": "3.1.3",
        "details": "Template rendering"
    },
    "gh_cli": {
        "available": False,
        "error": "HTTP 401 Bad credentials",
        "needs": "gh auth login"
    }
}
```

**收益**:
- 更清晰的工具状态可视化
- 提前识别潜在问题（如 credits 不足、认证失效）
- 便于日志记录和故障排查

**优先级**: P0 (高)

---

### 2. Git 操作错误处理增强

**现状**: 基础 try/catch，仅打印 "Git error" 或 "Git not found"

**优化建议**:
```python
def git_commit_push(self, message: str) -> dict:
    """Enhanced git commit & push with detailed error reporting"""
    result = {
        "success": False,
        "commit_hash": None,
        "error": None,
        "details": {}
    }
    
    try:
        # Check for changes
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.workspace,
            check=True,
            capture_output=True,
            text=True
        )
        
        if not status.stdout.strip():
            result["error"] = "no_changes"
            result["details"]["message"] = "No changes to commit"
            return result
        
        # Git add
        subprocess.run(
            ["git", "add", "."],
            cwd=self.workspace,
            check=True,
            capture_output=True
        )
        
        # Git commit
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.workspace,
            check=True,
            capture_output=True
        )
        
        # Get commit hash
        result_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.workspace,
            check=True,
            capture_output=True,
            text=True
        )
        result["commit_hash"] = result_hash.stdout.strip()
        
        # Git push
        push_result = subprocess.run(
            ["git", "push"],
            cwd=self.workspace,
            capture_output=True,
            text=True
        )
        
        if push_result.returncode != 0:
            result["error"] = "push_failed"
            result["details"]["stderr"] = push_result.stderr
            return result
        
        result["success"] = True
        return result
        
    except subprocess.CalledProcessError as e:
        result["error"] = "command_failed"
        result["details"]["command"] = e.cmd
        result["details"]["returncode"] = e.returncode
        result["details"]["stderr"] = e.stderr.decode() if e.stderr else None
        return result
    except FileNotFoundError as e:
        result["error"] = "git_not_found"
        result["details"]["message"] = str(e)
        return result
```

**收益**:
- 精确识别失败原因（无变更/commit 失败/push 失败/git 不存在）
- 保留完整错误输出便于调试
- 支持上层逻辑根据错误类型决策（如无变更时不报错）

**优先级**: P0 (高)

---

### 3. 通知机制

**现状**: 无通知，仅依赖 cron 日志

**优化建议**:

#### 方案 A: OpenClaw message 工具 (推荐)
```python
def notify_completion(self, log_path: str, status: str) -> None:
    """Send completion notification via OpenClaw message tool"""
    
    # Read log summary
    log_content = Path(log_path).read_text()
    summary = self._extract_summary(log_content)
    
    # Prepare message
    message = {
        "action": "send",
        "channel": "discord",
        "target": "#hulk-geo-updates",  # 或 V 的私人 channel
        "text": f"""
### GEO #{self.current_iteration} {status}

**Summary**: {summary['one_liner']}
**Tasks**: {summary['tasks_completed']}/{summary['tasks_total']}
**Blockers**: {len(summary['blockers'])}

{f'**Blocker Details**: {summary['blockers'][0]['title']}' if summary['blockers'] else ''}

**Log**: `{log_path}`
        """.strip()
    }
    
    # Send via OpenClaw (would need to call message tool)
    # This requires integration with OpenClaw's message tool API
```

#### 方案 B: Email 通知
```python
def send_email_notification(self, recipient: str, subject: str, body: str) -> None:
    """Send email notification via SMTP"""
    import smtplib
    from email.mime.text import MIMEText
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'hulk@cittaverse.ai'
    msg['To'] = recipient
    
    # Requires SMTP credentials
    # Not recommended for security reasons
```

#### 方案 C: Webhook 通知
```python
def send_webhook_notification(self, webhook_url: str, payload: dict) -> None:
    """Send webhook notification via HTTP POST"""
    import requests
    
    response = requests.post(webhook_url, json=payload, timeout=10)
    response.raise_for_status()
    
    # Requires webhook URL configuration
    # Could integrate with Discord webhook, Slack webhook, etc.
```

**推荐**: 方案 A (OpenClaw message 工具)，因为：
- 已集成到 OpenClaw 生态
- 无需额外凭证管理
- 支持 Discord/Slack/Telegram 等多渠道

**优先级**: P1 (中)

---

### 4. 插件式任务处理器

**现状**: 硬编码任务类型匹配
```python
if "自动化脚本" in task["task"] or "automator" in task["task"].lower():
    result = self._execute_automation_task(task, result)
elif "PR" in task["task"] or "pull request" in task_name:
    result = self._execute_pr_task(task, result)
# ...
```

**优化建议**: 插件式架构
```python
# tasks/__init__.py
from .base import TaskHandler
from .automation import AutomationHandler
from .pr import PRHandler
from .debt import DebtHandler
from .research import ResearchHandler

TASK_HANDLERS = {
    "automation": AutomationHandler,
    "pr": PRHandler,
    "debt": DebtHandler,
    "research": ResearchHandler,
}

# geo-automator.py
def execute_task(self, task: dict) -> dict:
    """Execute task using plugin handler"""
    handler_type = self._classify_task(task)
    handler_class = TASK_HANDLERS.get(handler_type)
    
    if handler_class is None:
        return self._execute_generic_task(task)
    
    handler = handler_class(self.workspace, self.dry_run)
    return handler.execute(task)
```

**收益**:
- 易于扩展新任务类型（如研究、实验、文档）
- 各任务处理器独立测试
- 支持动态加载外部插件

**优先级**: P2 (低，长期优化)

---

## 实施路线图

| 阶段 | 优化项 | 预计工作量 | 依赖 |
|------|--------|-----------|------|
| Phase 1 | 工具链健康检查增强 | 2-3h | 无 |
| Phase 2 | Git 错误处理增强 | 1-2h | 无 |
| Phase 3 | 通知机制 (OpenClaw message) | 3-4h | OpenClaw message tool 集成 |
| Phase 4 | 插件式任务处理器 | 4-6h | Phase 1-3 完成 |

---

## 风险与注意事项

### 风险
1. **工具链检查过度复杂**: 可能引入新的故障点
   - 缓解：保持检查逻辑简单，失败时降级为"未知"而非报错

2. **通知机制凭证管理**: 避免硬编码 API key
   - 缓解：使用 OpenClaw message 工具，无需额外凭证

3. **插件系统过度设计**: 当前任务类型有限，插件系统可能过早优化
   - 缓解：Phase 4 标记为"长期优化"，优先实施 Phase 1-3

### 注意事项
- 所有优化必须保持向后兼容（不破坏现有日志格式）
- 新增配置项需有默认值（避免破坏 cron 自动执行）
- 错误处理必须详细记录（便于后续故障排查）

---

## 验证标准

优化完成后，需满足以下验证标准：

| 优化项 | 验证方式 | 通过标准 |
|--------|---------|---------|
| 工具链检查增强 | 运行 geo-automator.py | 输出包含版本/认证状态等详细信息 |
| Git 错误处理 | 模拟无变更/认证失败场景 | 返回精确错误类型和详细报错 |
| 通知机制 | 执行一次完整迭代 | Discord/指定渠道收到通知消息 |
| 插件式处理器 | 添加新任务类型测试 | 新任务类型可被正确识别和执行 |

---

*GEO Automation Optimization v0.1 — 2026-04-06*

**密度即价值** — 从"能跑"到"好跑"

Hulk 🟢
