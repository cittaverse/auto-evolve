# Hulk v2.0 自驱循环配置

**版本**: 2.0.0  
**更新**: 2026-03-31

---

## 核心循环机制

### 1. GEO 迭代循环

```
研究主题 → 网络搜索 → 内容分析 → 综合结论 → 保存状态
    ↑                                        ↓
    └──────────── 继续下一轮 ────────────────┘
```

**配置**:
- 最大迭代数：5 轮
- 每轮超时：300 秒
- 状态保存：每轮结束后
- 中断恢复：支持

### 2. 定时任务循环

```
Cron 触发 → 加载状态 → 执行任务 → 保存结果 → 发送通知
```

**预设定时任务**:
| 任务 | 频率 | 时间 |
|------|------|------|
| GEO 迭代 | 每 4 小时 | 0/4/8/12/16/20 点 |
| PR 监控 | 每 6 小时 | 0/6/12/18 点 |
| 心跳检查 | 每 30 分钟 | */30 * * * * |
| 状态清理 | 每天 | 02:00 |

### 3. 事件驱动循环

```
事件触发 (用户输入/API 调用/文件变化)
    ↓
Hook 检查 (PreToolUse)
    ↓
执行工具
    ↓
Hook 审计 (PostToolUse)
    ↓
保存状态 → 通知
```

---

## 配置文件

### `.hulk/config.json`

```json
{
  "agent": {
    "model": "qwen3.5-plus",
    "max_iterations": 20,
    "max_tokens": 8192,
    "temperature": 0.7
  },
  "context": {
    "max_tokens": 128000,
    "trimming_strategy": "priority"
  },
  "hooks": {
    "enabled": true,
    "rules_dir": "hooks/rules"
  },
  "persistence": {
    "state_dir": ".hulk-state",
    "auto_save": true,
    "save_interval": 60
  },
  "auto_loop": {
    "enabled": true,
    "max_iterations": 5,
    "continue_prompt": "Continue research. Build on previous findings."
  },
  "logging": {
    "level": "info",
    "file": ".hulk-state/hulk.log",
    "max_size_mb": 100,
    "backup_count": 5
  }
}
```

---

## 启动方式

### 1. 单次执行

```bash
python hulk_main.py --prompt "研究 AI 趋势"
```

### 2. 自动循环

```bash
python hulk_main.py --prompt "研究 AI 趋势" --auto
```

### 3. 中断恢复

```bash
python hulk_main.py --resume
```

### 4. TUI 模式

```bash
python hulk_main.py --tui --prompt "研究 AI 趋势"
```

### 5. 守护进程 (持续运行)

```bash
# 使用 nohup
nohup python hulk_main.py --auto --prompt "持续研究 AI 趋势" > hulk.log 2>&1 &

# 或使用 systemd
sudo systemctl start hulk-v2
```

---

## 监控指标

### 实时指标

| 指标 | 命令 |
|------|------|
| 当前状态 | `python hulk_main.py --stats` |
| 日志尾随 | `tail -f .hulk-state/hulk.log` |
| 状态文件 | `ls -lh .hulk-state/*.json` |

### 健康检查

```bash
# 检查进程
ps aux | grep hulk_main

# 检查最新状态
cat .hulk-state/hulk_state_*.json | tail -20

# 检查 Token 使用
python -c "from hulk_main import HulkV2; h = HulkV2(); print(h.get_stats())"
```

---

## 故障恢复

### 场景 1: 进程意外终止

```bash
# 自动恢复
python hulk_main.py --resume
```

### 场景 2: 状态文件损坏

```bash
# 清除旧状态，重新开始
rm .hulk-state/*.json
python hulk_main.py --prompt "新任务"
```

### 场景 3: Hook 阻塞

```bash
# 临时禁用 Hook
python hulk_main.py --prompt "任务" --no-hooks
```

---

## 扩展点

### 添加新工具

```python
# 1. 创建工具类
class MyCustomTool(Tool):
    name = "my_tool"
    description = "..."
    parameters = {...}
    async def execute(self, args): ...

# 2. 注册到 HulkV2
def _register_default_tools(self):
    self.registry.register(WebSearchTool())
    self.registry.register(MyCustomTool())  # 新增
```

### 添加新 Hook

```bash
# 1. 创建 Hook 脚本
cat > hooks/rules/custom.local.md << 'EOF'
---
name: custom_rule
enabled: true
event: pre_bash
conditions:
  - field: command
    operator: contains
    pattern: "dangerous"
action: block
---
⚠️ 自定义规则阻止
EOF

# 2. 自动生效 (无需重启)
```

### 添加定时任务

```python
# 编辑 crontab
crontab -e

# 添加任务
0 */4 * * * cd /path/to/hulk && python hulk_main.py --auto --prompt "持续研究"
```

---

## 性能优化

### 缓存策略

```python
# 启用 LRU 缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def compile_regex(pattern: str):
    return re.compile(pattern)
```

### 异步优化

```python
# 并发执行独立任务
results = await asyncio.gather(
    search_web(query1),
    search_web(query2),
    search_web(query3)
)
```

### Token 优化

```python
# 上下文裁剪策略
context = ContextManager(
    max_tokens=128000,
    trimming_strategy="priority"  # 按优先级裁剪
)
```

---

## 最佳实践

### 1. 定期清理状态

```bash
# 每天清理超过 24 小时的状态文件
find .hulk-state -name "*.json" -mtime +1 -delete
```

### 2. 监控日志大小

```bash
# 日志轮转
logrotate /etc/logrotate.d/hulk-v2
```

### 3. 备份重要状态

```bash
# 每天备份最新状态
cp .hulk-state/hulk_state_*.json /backup/hulk/$(date +%Y%m%d).json
```

---

*Hulk v2.0 — 持续自驱循环系统*
