# Hulk v2.0 生产部署脚本

**版本**: 2.0.0  
**部署时间**: 2026-04-01  
**环境**: Python 3.10+

---

## 快速部署

### 1. 安装依赖

```bash
cd /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2
pip3 install textual tiktoken pytest pytest-asyncio
```

### 2. 首次运行测试

```bash
python3 hulk_main.py --prompt "研究 AI Agent 自驱系统" --stats
```

### 3. 部署守护进程

```bash
# 创建日志目录
mkdir -p /var/log/hulk-v2

# 后台运行
nohup python3 hulk_main.py --auto --prompt "持续研究 AI Agent 进展" > /var/log/hulk-v2/hulk.log 2>&1 &

# 检查进程
ps aux | grep hulk_main

# 查看日志
tail -f /var/log/hulk-v2/hulk.log
```

### 4. 配置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加任务 (每 4 小时执行一次)
0 */4 * * * cd /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2 && python3 hulk_main.py --auto --prompt "持续研究 AI Agent 进展" >> /var/log/hulk-v2/cron.log 2>&1
```

---

## systemd 服务 (Linux)

### 创建服务文件

```bash
sudo tee /etc/systemd/system/hulk-v2.service > /dev/null << 'EOF'
[Unit]
Description=Hulk v2.0 AI Research Assistant
After=network.target

[Service]
Type=simple
User=moondy
WorkingDirectory=/Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2
ExecStart=/usr/bin/python3 hulk_main.py --auto --prompt "持续研究 AI Agent 进展"
Restart=always
RestartSec=10
StandardOutput=append:/var/log/hulk-v2/hulk.log
StandardError=append:/var/log/hulk-v2/hulk.error.log

[Install]
WantedBy=multi-user.target
EOF
```

### 启动服务

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start hulk-v2

# 设置开机自启
sudo systemctl enable hulk-v2

# 查看状态
sudo systemctl status hulk-v2

# 查看日志
sudo journalctl -u hulk-v2 -f
```

---

## 监控脚本

### 健康检查

```bash
#!/bin/bash
# check_hulk_health.sh

cd /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2

# 检查进程
if ! pgrep -f "hulk_main.py" > /dev/null; then
    echo "❌ Hulk v2.0 进程未运行"
    exit 1
fi

# 检查最新状态文件
LATEST_STATE=$(ls -t .hulk-state/hulk_state_*.json 2>/dev/null | head -1)
if [ -z "$LATEST_STATE" ]; then
    echo "❌ 无状态文件"
    exit 1
fi

# 检查状态文件时间 (超过 1 小时未更新告警)
FILE_AGE=$(( $(date +%s) - $(stat -f %m "$LATEST_STATE" 2>/dev/null || stat -c %Y "$LATEST_STATE" 2>/dev/null) ))
if [ $FILE_AGE -gt 3600 ]; then
    echo "⚠️ 状态文件超过 1 小时未更新"
    exit 2
fi

echo "✅ Hulk v2.0 健康状态正常"
exit 0
```

### 自动重启脚本

```bash
#!/bin/bash
# auto_restart_hulk.sh

LOG_FILE="/var/log/hulk-v2/restart.log"

echo "[$(date)] 检查 Hulk v2.0 状态..." >> $LOG_FILE

if ! /path/to/check_hulk_health.sh > /dev/null 2>&1; then
    echo "[$(date)] Hulk v2.0 异常，尝试重启..." >> $LOG_FILE
    
    # 杀死旧进程
    pkill -f "hulk_main.py"
    sleep 5
    
    # 启动新进程
    cd /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2
    nohup python3 hulk_main.py --auto --prompt "持续研究 AI Agent 进展" > /var/log/hulk-v2/hulk.log 2>&1 &
    
    echo "[$(date)] Hulk v2.0 已重启" >> $LOG_FILE
else
    echo "[$(date)] Hulk v2.0 运行正常" >> $LOG_FILE
fi
```

---

## 日志轮转

### 创建 logrotate 配置

```bash
sudo tee /etc/logrotate.d/hulk-v2 > /dev/null << 'EOF'
/var/log/hulk-v2/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 moondy staff
    postrotate
        # 可选：重启服务
        # sudo systemctl restart hulk-v2
    endscript
}
EOF
```

### 测试日志轮转

```bash
sudo logrotate -d /etc/logrotate.d/hulk-v2
```

---

## 备份策略

### 状态文件备份

```bash
#!/bin/bash
# backup_hulk_state.sh

BACKUP_DIR="/backup/hulk-v2/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份状态文件
cp /Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/.hulk-state/*.json $BACKUP_DIR/

# 备份日志
cp /var/log/hulk-v2/hulk.log $BACKUP_DIR/

# 压缩
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# 清理超过 30 天的备份
find /backup/hulk-v2 -name "*.tar.gz" -mtime +30 -delete

echo "[$(date)] 备份完成：$BACKUP_DIR.tar.gz"
```

---

## 性能调优

### 环境变量优化

```bash
# 设置 Python 优化
export PYTHONOPTIMIZE=2

# 设置异步协处理器
export UVLOOP=1

# 设置日志级别
export HULK_LOG_LEVEL=info
```

### 系统限制调整

```bash
# 增加文件描述符限制
ulimit -n 65536

# 增加进程数限制
ulimit -u 4096
```

---

## 故障排查

### 常见问题

**问题 1: 进程意外终止**
```bash
# 查看错误日志
tail -100 /var/log/hulk-v2/hulk.error.log

# 从中断处恢复
python3 hulk_main.py --resume
```

**问题 2: Hook 阻塞**
```bash
# 临时禁用 Hook
python3 hulk_main.py --prompt "任务" --no-hooks
```

**问题 3: Token 超限**
```bash
# 清理上下文
rm .hulk-state/*.json
python3 hulk_main.py --prompt "新任务"
```

---

## 监控仪表板 (可选)

### Grafana + Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'hulk-v2'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### 关键指标

- `hulk_uptime_seconds`: 运行时间
- `hulk_context_tokens`: Token 使用数
- `hulk_iteration_count`: 迭代次数
- `hulk_hook_blocks`: Hook 阻止次数
- `hulk_error_count`: 错误次数

---

*Hulk v2.0 — 生产部署完成*
