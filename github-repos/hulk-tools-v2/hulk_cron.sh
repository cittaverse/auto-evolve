#!/bin/bash
# Hulk v2.0 定时任务脚本 (带投递)

LOG_DIR="/Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/logs"
STATE_DIR="/Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2/.hulk-state"
WORK_DIR="/Users/moondy/.openclaw/workspace-hulk/github-repos/hulk-tools-v2"
MEMORY_DIR="/Users/moondy/.openclaw/workspace-hulk/memory"

# 创建目录
mkdir -p "$LOG_DIR" "$STATE_DIR"

# 记录开始时间
echo "[$(date -Iseconds)] 启动 Hulk v2.0 GEO 迭代" >> "$LOG_DIR/cron.log"

# 运行 Hulk v2.0 (单次 GEO 迭代)
cd "$WORK_DIR"
START_TIME=$(date +%s)
python3 hulk_main.py --auto --prompt "持续研究 AI Agent 自驱系统最新进展" >> "$LOG_DIR/hulk.log" 2>&1
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# 记录完成时间
echo "[$(date -Iseconds)] Hulk v2.0 GEO 迭代完成 (耗时：${DURATION}秒)" >> "$LOG_DIR/cron.log"
echo "" >> "$LOG_DIR/cron.log"

# 生成投递消息
LATEST_STATE=$(ls -t "$STATE_DIR"/hulk_state_*.json 2>/dev/null | head -1)
if [ -n "$LATEST_STATE" ]; then
    # 提取状态信息
    ITERATION=$(cat "$LATEST_STATE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('agent',{}).get('iteration',0))" 2>/dev/null)
    TOKENS=$(cat "$LATEST_STATE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('agent',{}).get('context_tokens',0))" 2>/dev/null)
    STATE=$(cat "$LATEST_STATE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('agent',{}).get('state','unknown'))" 2>/dev/null)
    
    # 生成投递消息
    cat > "$LOG_DIR/last_delivery.txt" << EOF
🟢 Hulk v2.0 GEO 迭代完成

**执行时间**: $(date -Iseconds)
**耗时**: ${DURATION}秒
**迭代次数**: ${ITERATION}
**Token 使用**: ${TOKENS}
**状态**: ${STATE}

**日志**: tail -f $LOG_DIR/hulk.log
**状态文件**: $LATEST_STATE
EOF

    # 投递到 Discord
    cd "$WORK_DIR"
    python3 delivery.py --file "$LOG_DIR/last_delivery.txt" >> "$LOG_DIR/delivery.log" 2>&1
    echo "[$(date -Iseconds)] 投递完成" >> "$LOG_DIR/cron.log"
else
    echo "[$(date -Iseconds)] ⚠️ 无状态文件，跳过投递" >> "$LOG_DIR/cron.log"
fi
