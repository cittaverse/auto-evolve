#!/bin/bash
# GEO Cron 包装脚本 - 带失败重试机制
# 用法：./cron-wrapper.sh <script> [max_retries] [retry_delay]

set -e

SCRIPT=$1
MAX_RETRIES=${2:-3}
RETRY_DELAY=${3:-60}
LOG_DIR="/home/node/.openclaw/workspace-hulk/metrics"
LOG_FILE="$LOG_DIR/cron-$(basename $SCRIPT .sh).log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    echo "[$(date -u +%Y-%m-%d_%H:%M:%S_UTC)] $1" | tee -a "$LOG_FILE"
}

# 通知函数（失败时记录详细错误）
notify_failure() {
    local attempt=$1
    local error=$2
    log "❌ 第 $attempt 次尝试失败：$error"
}

notify_success() {
    local attempts=$1
    log "✅ 执行成功 (尝试次数：$attempts/$MAX_RETRIES)"
}

# 主执行逻辑
log "🚀 开始执行：$SCRIPT (最大重试：$MAX_RETRIES, 间隔：${RETRY_DELAY}s)"

attempt=0
success=false

while [ $attempt -lt $MAX_RETRIES ]; do
    attempt=$((attempt + 1))
    log "📍 尝试 #$attempt / $MAX_RETRIES"
    
    # 执行脚本
    if bash "$SCRIPT" >> "$LOG_FILE" 2>&1; then
        success=true
        notify_success $attempt
        break
    else
        error_code=$?
        notify_failure $attempt "退出码：$error_code"
        
        if [ $attempt -lt $MAX_RETRIES ]; then
            log "⏳ ${RETRY_DELAY}s 后重试..."
            sleep $RETRY_DELAY
        fi
    fi
done

if [ "$success" = false ]; then
    log "❌ 最终失败：$SCRIPT 在 $MAX_RETRIES 次尝试后仍失败"
    exit 1
fi

log "✅ 完成：$SCRIPT"
exit 0
