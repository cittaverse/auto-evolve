# GEO Cron 配置指南

> OpenClaw Cron 是独立运行的定时任务系统，不依赖 crontab 命令。

---

## ✅ OpenClaw Cron 机制

OpenClaw Cron 是内置的定时任务系统，通过 `openclaw cron` 命令管理。

### 当前配置

| Job ID | 名称 | 频率 | 状态 |
|--------|------|------|------|
| `hulk-geo-iteration` | GEO 自驱迭代 | 每日 4 次（00/06/12/18 UTC） | ✅ 正常运行 |
| `hulk-research-heartbeat` | 研究心跳 | 每 30 分钟 | ✅ 正常运行 |
| `hulk-memory-consolidate` | 记忆固化 | 每日 22:00 | ⏸️ 待首次执行 |
| `hulk-evidence-scan` | 证据扫描 | 每周一 09:00 | ⏸️ 待首次执行 |

### 管理命令

```bash
# 查看所有 Cron 任务
openclaw cron list

# 查看单个任务执行历史
openclaw cron runs --id <job-id>

# 手动立即执行
openclaw cron run <job-id>

# 禁用/启用任务
openclaw cron disable <job-id>
openclaw cron enable <job-id>
```

### 执行日志

- 执行历史：`openclaw cron runs --id <job-id>`
- 会话日志：`memory/YYYY-MM-DD-geo-iteration-*.md`
- Heartbeat 日志：`memory/YYYY-MM-DD-heartbeat-*.md`

---

## ⚠️ 历史错误理解（已修正）

**错误**：认为 `crontab` 命令不存在 = Cron 不可用  
**真相**：OpenClaw Cron 是独立系统，不依赖 crontab 命令  
**修正日期**：2026-03-14 02:45 UTC

---

## 方案 B：宿主机 Cron + Docker Exec（备选）

在**宿主机**（你的 Mac）上设置 Cron，通过 `docker exec` 触发：

### 1. 获取容器 ID

```bash
docker ps | grep openclaw
```

### 2. 宿主机 Crontab

在你的 Mac 上运行 `crontab -e`，添加：

```cron
# GEO 周度追踪 - 每周日 17:00 北京时间
0 9 * * 0 docker exec openclaw-node bash -c "cd /home/node/.openclaw/workspace-hulk && ./scripts/track-metrics.sh weekly"

# GEO 月度汇总 - 每月 1 日 18:00 北京时间
0 10 1 * * docker exec openclaw-node bash -c "cd /home/node/.openclaw/workspace-hulk && ./scripts/track-monthly.sh"
```

### 3. 验证

```bash
crontab -l
```

---

## ✅ 方案 C：手动执行 + 日历提醒（临时）

创建日历事件或使用提醒工具：

### 每周日 17:00 北京时间

```bash
cd /home/node/.openclaw/workspace-hulk && ./scripts/track-metrics.sh weekly
```

### 每月 1 日 18:00 北京时间

```bash
cd /home/node/.openclaw/workspace-hulk && ./scripts/track-monthly.sh
```

---

## 📋 已创建的文件

| 文件 | 说明 | 状态 |
|------|------|------|
| `scripts/cron-wrapper.sh` | 失败重试包装脚本 | ✅ 就绪 |
| `scripts/track-monthly.sh` | 月度追踪脚本 | ✅ 就绪 |
| `scripts/install-cron.sh` | Cron 安装脚本 | ✅ 就绪（但 crontab 不可用） |
| `geo-cron` | Cron 配置文件 | ✅ 就绪（待宿主机使用） |

---

## 🎯 推荐方案

**短期**（本周）：方案 C - 手动执行，验证流程

**中期**（下周起）：方案 A - 配置 OpenClaw heartbeat

**长期**（稳定后）：方案 B - 宿主机 Cron 最可靠

---

## 🧪 测试脚本

手动测试追踪脚本：

```bash
cd /home/node/.openclaw/workspace-hulk
./scripts/track-metrics.sh weekly
```

测试包装脚本（模拟失败重试）：

```bash
./scripts/cron-wrapper.sh ./scripts/track-metrics.sh 3 60
```

---

*文档创建：2026-03-09 | Hulk 🟢*
