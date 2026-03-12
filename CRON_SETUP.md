# GEO Cron 配置指南

> 由于容器环境限制，`crontab` 不可用。使用替代方案。

---

## ⚠️ 现状

Docker 容器内无 `crontab` 命令，需要替代方案。

---

## ✅ 方案 A：OpenClaw Heartbeat 触发（推荐）

在 `hulk` agent 配置中添加 heartbeat 触发器：

### 1. 修改 `~/.openclaw/openclaw.json`

在 `agents.list` 中找到 `hulk`，添加或修改 `heartbeat` 配置：

```json
{
  "id": "hulk",
  "name": "Hulk",
  "heartbeat": {
    "every": "30m",
    "target": "self",
    "actions": {
      "sunday_0900": {
        "cron": "0 9 * * 0",
        "command": "./scripts/track-metrics.sh weekly"
      },
      "monthly_1000": {
        "cron": "0 10 1 * *",
        "command": "./scripts/track-monthly.sh"
      }
    }
  }
}
```

### 2. 重启 OpenClaw

```bash
openclaw gateway restart
```

---

## ✅ 方案 B：宿主机 Cron + Docker Exec

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
