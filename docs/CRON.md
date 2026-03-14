# Hulk Cron 自驱动机制

> OpenClaw 原生 Cron 配置，实现 Hulk 研究工作的自动化执行。

---

## 任务列表

| Job ID | 名称 | 频率 | 时间 (CST) | 说明 |
|--------|------|------|-----------|------|
| `hulk-geo-iteration` | GEO 自驱迭代 | 每日 4 次 | 00:00/06:00/12:00/18:00 | GEO + GitHub 项目迭代 |
| `hulk-research-heartbeat` | 研究心跳 | 每 30 分钟 | 每 30 分钟 | 检查 BULLETIN/KANBAN 研究请求 |
| `hulk-memory-consolidate` | 记忆固化 | 每日 | 22:00 | 固化当日记忆到 MEMORY.md |
| `hulk-evidence-scan` | 证据扫描 | 每周一 | 09:00 | 扫描研究领域新论文/证据 |

## 管理命令

```bash
# 查看所有 Hulk 任务
openclaw cron list | grep hulk

# 查看单个任务详情
openclaw cron runs --job <job-id>

# 手动立即执行
openclaw cron run <job-id>

# 禁用/启用任务
openclaw cron disable <job-id>
openclaw cron enable <job-id>

# 删除任务
openclaw cron rm <job-id>
```

## 任务配置详情

### hulk-research-heartbeat
- **Schedule**: `*/30 * * * *` (每 30 分钟)
- **Timeout**: 300s
- **职责**: 自动发现并执行研究请求，检查过期任务

### hulk-memory-consolidate
- **Schedule**: `0 22 * * *` (每日 22:00)
- **Timeout**: 600s
- **职责**: 提取当日关键洞察，追加到 MEMORY.md

### hulk-evidence-scan
- **Schedule**: `0 9 * * 1` (每周一 9:00)
- **Timeout**: 900s
- **职责**: 周度文献扫描，生成研究周报素材

### hulk-geo-iteration
- **Schedule**: `0 0,6,12,18 * * *` (每日 4 次)
- **Timeout**: 默认 30s
- **职责**: GEO 持续迭代，GitHub 项目维护

## 执行日志

- Cron 运行历史：`openclaw cron runs --job <job-id>`
- 会话日志：`memory/YYYY-MM-DD*.md`
- BULLETIN 公告：`shared/BULLETIN.md`

## 故障处理

| 问题 | 排查步骤 |
|------|---------|
| 任务未执行 | `openclaw cron list` 检查 enabled 状态 |
| 执行超时 | 检查 `openclaw cron runs --job <id>` 的 lastDurationMs |
| 连续错误 | 查看 lastError 字段，调整 timeout-seconds |
| 需要修改 | `openclaw cron edit <job-id> --cron "新表达式"` |

---

*最后更新：2026-03-13 | OpenClaw 原生 Cron*
