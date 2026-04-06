# Hulk v2.0 Cron 定时任务配置

**版本**: 2.0.0  
**配置时间**: 2026-04-01

---

## 快速配置

### 1. 打开 crontab

```bash
crontab -e
```

### 2. 添加定时任务

```bash
# 每 4 小时执行一次 GEO 迭代
0 */4 * * * /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/hulk_cron.sh

# 每天凌晨 2 点清理旧状态文件
0 2 * * * find /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/.hulk-state -name "*.json" -mtime +1 -delete

# 每天凌晨 3 点备份日志
0 3 * * * cp /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/logs/hulk.log /backup/hulk/$(date +\%Y\%m\%d).log
```

### 3. 验证配置

```bash
# 查看 crontab
crontab -l

# 查看 cron 日志 (macOS)
log show --predicate 'process == "cron"' --last 1h
```

---

## 定时任务说明

### 任务 1: GEO 迭代 (每 4 小时)

**时间**: `0 */4 * * *` (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)

**脚本**: `hulk_cron.sh`

**功能**:
- 运行 Hulk v2.0 自动 GEO 迭代 (5 轮)
- 日志输出到 `logs/hulk.log`
- 状态保存到 `.hulk-state/`

### 任务 2: 清理旧状态 (每天 02:00)

**时间**: `0 2 * * *`

**功能**:
- 删除超过 1 天的状态文件
- 防止状态文件积累过多

### 任务 3: 备份日志 (每天 03:00)

**时间**: `0 3 * * *`

**功能**:
- 备份当天日志到 `/backup/hulk/`
- 格式：`YYYYMMDD.log`

---

## 测试 Cron 脚本

### 手动运行测试

```bash
# 运行脚本
/Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/hulk_cron.sh

# 查看日志
tail -20 /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/logs/cron.log
tail -f /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/logs/hulk.log
```

### 检查 Cron 服务

```bash
# macOS 检查 cron 服务状态
sudo systemsetup -getcron

# 启动 cron 服务 (如果未运行)
sudo systemsetup -setcron 1
```

---

## 日志位置

| 日志文件 | 用途 | 查看命令 |
|---------|------|---------|
| `logs/hulk.log` | Hulk 运行日志 | `tail -f logs/hulk.log` |
| `logs/cron.log` | Cron 任务日志 | `tail -f logs/cron.log` |
| `.hulk-state/*.json` | 状态文件 | `ls -lh .hulk-state/` |

---

## 故障排查

### 问题 1: Cron 任务未执行

```bash
# 检查 cron 服务
sudo systemsetup -getcron

# 检查脚本权限
ls -l hulk_cron.sh
# 应该是 -rwxr-xr-x

# 手动测试脚本
./hulk_cron.sh
```

### 问题 2: Python 环境问题

```bash
# 检查 Python 路径
which python3

# 更新脚本中的 Python 路径 (如果需要)
# 编辑 hulk_cron.sh，将 python3 改为完整路径
# 例如：/usr/local/bin/python3
```

### 问题 3: 权限问题

```bash
# 确保脚本有执行权限
chmod +x hulk_cron.sh

# 确保日志目录可写
mkdir -p logs .hulk-state
chmod 755 logs .hulk-state
```

---

## 监控告警 (可选)

### 创建健康检查脚本

```bash
#!/bin/bash
# check_hulk_health.sh

LOG_FILE="/Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/logs/hulk.log"
CRON_LOG="/Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/logs/cron.log"

# 检查最新日志时间
if [ -f "$LOG_FILE" ]; then
    LAST_UPDATE=$(stat -f %m "$LOG_FILE" 2>/dev/null || stat -c %Y "$LOG_FILE" 2>/dev/null)
    NOW=$(date +%s)
    AGE=$((NOW - LAST_UPDATE))
    
    if [ $AGE -gt 14400 ]; then  # 超过 4 小时未更新
        echo "⚠️ Hulk v2.0 超过 4 小时未运行"
        exit 1
    fi
fi

# 检查 cron 日志错误
if grep -q "Error" "$CRON_LOG" 2>/dev/null; then
    echo "⚠️ Cron 任务执行出错"
    exit 2
fi

echo "✅ Hulk v2.0 健康状态正常"
exit 0
```

### 配置告警通知

```bash
# 添加到 crontab (每小时检查)
0 * * * * /path/to/check_hulk_health.sh && echo "健康" || echo "告警" | mail -s "Hulk v2.0 告警" your@email.com
```

---

## 完整 Crontab 示例

```bash
# 编辑 crontab
crontab -e

# 添加以下内容
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# Hulk v2.0 GEO 迭代 (每 4 小时)
0 */4 * * * /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/hulk_cron.sh

# 清理旧状态 (每天 02:00)
0 2 * * * find /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/.hulk-state -name "*.json" -mtime +1 -delete

# 备份日志 (每天 03:00)
0 3 * * * mkdir -p /backup/hulk && cp /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/logs/hulk.log /backup/hulk/$(date +\%Y\%m\%d).log

# 健康检查 (每小时)
0 * * * * /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/check_hulk_health.sh >> /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/logs/health.log 2>&1
```

---

## 验证配置

### 1. 查看已配置的定时任务

```bash
crontab -l
```

### 2. 等待第一次执行

```bash
# 查看 cron 日志
tail -f logs/cron.log

# 查看 Hulk 日志
tail -f logs/hulk.log
```

### 3. 检查状态文件

```bash
ls -lh .hulk-state/*.json
```

---

*Hulk v2.0 — 定时任务配置完成*
