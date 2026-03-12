# Hulk Cron 自驱动机制

> Hulk 的定时任务配置，实现研究工作的自动化执行。

---

## 任务列表

| 任务名 | 频率 | 时间 (UTC) | 时间 (杭州) | 说明 |
|--------|------|-----------|-----------|------|
| `hulk_research_heartbeat` | 每 30 分钟 | `*/30 * * * *` | 每 30 分钟 | 检查 BULLETIN/KANBAN 中的研究请求 |
| `hulk_memory_consolidate` | 每日 | `0 14 * * *` | 22:00 | 固化当日记忆日志到 MEMORY.md |
| `hulk_evidence_scan` | 每周一 | `0 1 * * 1` | 09:00 | 扫描研究领域新论文/证据 |

## 脚本位置

- `/home/node/.openclaw/workspace-hulk/scripts/cron/`

## 管理命令

```bash
cd /home/node/.openclaw/workspace

# 查看状态
./scripts/cron/start_cron.sh status

# 重启
./scripts/cron/start_cron.sh restart

# 手动重跑任务
./scripts/cron/start_cron.sh rerun hulk_research_heartbeat
./scripts/cron/start_cron.sh rerun hulk_memory_consolidate
./scripts/cron/start_cron.sh rerun hulk_evidence_scan

# 重置失败计数
./scripts/cron/start_cron.sh reset-failures
```

## 日志位置

- 运行日志：`/home/node/.openclaw/workspace/logs/cron_runner.log`
- 任务状态：`/home/node/.openclaw/workspace/logs/cron_state.json`
- Hulk 心跳：`/home/node/.openclaw/workspace-hulk/metrics/cron_research_heartbeat.log`
- Hulk 记忆：`/home/node/.openclaw/workspace-hulk/metrics/cron_memory_consolidate.log`
- Hulk 证据：`/home/node/.openclaw/workspace-hulk/metrics/cron_evidence_scan.log`

## 失败处理

- 最多重试 3 次，线性退避 (10s, 20s, 30s)
- 连续失败 3 次后发送 Discord 告警
- 告警后需人工介入或手动重跑

---

*最后更新：2026-03-12*
