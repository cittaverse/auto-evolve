# Hulk Cron 自驱动机制

> OpenClaw 原生 Cron 配置，最后更新 2026-03-18。

---

## Hulk 任务列表

| Job ID | 名称 | 频率 | 时间 (CST) | Timeout | 说明 |
|--------|------|------|-----------|---------|------|
| `hulk-geo-iteration` | GEO 自驱迭代 | 每日 4 次 | 00/06/12/18 | 1800s | GEO + GitHub 项目迭代 |
| `hulk-research-heartbeat` | 研究心跳 | 每 2 小时 | 每偶数小时 | 600s | 检查 BULLETIN/KANBAN 研究请求 |
| `hulk-memory-consolidate` | 记忆固化 | 每日 | 22:00 | 900s | 固化当日记忆到 MEMORY.md |
| `hulk-evidence-scan` | 证据扫描 | 每周一 | 09:00 | 1200s | 扫描研究领域新论文/证据 |
| `hulk-heartbeat-update` | HEARTBEAT 更新 | 每日 2 次 | 10:00/22:00 | 600s | 自动更新 HEARTBEAT.md |
| `hulk-weekly-report` | 研究周报 | 每周五 | 18:00 | 1200s | 生成研究周报到 Discord |

## 全局任务列表

| 归属 | 任务 | 频率 | 状态 |
|------|------|------|------|
| Core | morning-report | 工作日 09:30 | ✅ ok |
| Core | core-content-gen | 每日 02:00 | ⚠️ skipped (quiet-hours) |
| Core | core-content-push | 每日 09:00 | ✅ ok |
| Core | core-audit-morning | 每日 08:00 | ✅ ok |
| Core | core-audit-afternoon | 每日 14:00 | ✅ ok |
| Core | core-audit-evening | 每日 20:00 | ✅ ok |
| Core | Odin Morning/Afternoon/Evening | 08/16/22 UTC | 🔧 已修复 (agent+delivery) |
| Core | self-improvement-wednesday | 周三 09:00 | ✅ ok |
| Jobs | 惊喜提醒 | 每 2 小时 | ✅ ok |
| Jobs | 饮品订阅 | 每日 5 次 | ✅ ok |
| Jobs | MacBook Pro 价格监控 | 每日 09:00 | ✅ ok |
| Jobs | 竞品反馈扫描 | 每周一 09:00 | ✅ ok |
| Jobs | Jobs 周报推送 | 每周五 18:00 | ✅ ok |
| Midas | midas-workday-start | 每日 10:00 | ✅ ok |
| Hulk | (见上方表格) | - | 🔧 已修复 |

## 2026-03-18 修复记录

### 已修复

| 任务 | 问题 | 修复 |
|------|------|------|
| `hulk-research-heartbeat` | timeout (300s 不够) + 频率过高 (30min) | timeout → 600s，频率 → 每 2 小时，prompt 精简 |
| `hulk-memory-consolidate` | timeout (600s 不够) | timeout → 900s |
| `hulk-evidence-scan` | delivery 报错 | timeout → 1200s，关闭 delivery |
| `hulk-geo-iteration` | 无 timeout (默认 30s) | timeout → 1800s |
| Odin × 3 | Unknown Channel (用户 ID ≠ 频道 ID) + 无 agent | to → 频道 ID，agent → main，timeout → 300s |

### 已清理

| 任务 | 原因 |
|------|------|
| `jina-weekly-monitor` (旧版) | 与 v2 重复 |
| `core-self-improve-scan` | 与 self-improvement-wednesday 重复 |

### 已新增

| 任务 | 说明 |
|------|------|
| `hulk-heartbeat-update` | 每日 2 次自动更新 HEARTBEAT.md |
| `hulk-weekly-report` | 每周五研究周报，deliver 到 Discord |

## 管理命令

```bash
openclaw cron list                    # 查看所有任务
openclaw cron run <job-id>            # 手动立即执行
openclaw cron runs --id <job-id>      # 查看执行历史
openclaw cron disable/enable <job-id> # 禁用/启用
openclaw cron rm <job-id>             # 删除
openclaw cron edit <job-id> --timeout-seconds 600  # 修改配置
openclaw cron add --agent hulk --name "新任务" --cron "0 9 * * *" --tz "Asia/Shanghai" --session isolated --message "..." --timeout-seconds 600
```

---

*Hulk 🟢 — 自驱动引擎运行中*
