#!/bin/bash
# Hulk 研究心跳 - 每 30 分钟
# 检查 BULLETIN/KANBAN 是否有新的研究请求，自动执行或升级

cd /home/node/.openclaw/workspace-hulk

LOG_FILE="/home/node/.openclaw/workspace-hulk/metrics/cron_research_heartbeat.log"
mkdir -p "$(dirname $LOG_FILE)"

log() {
    echo "[$(date -u +%Y-%m-%d_%H:%M:%S_UTC)] $1" | tee -a "$LOG_FILE"
}

log "🔍 Hulk 研究心跳检查"

# 检查 BULLETIN 中最近 24 小时是否有 Hulk 的请求
BULLETIN_REQUESTS=$(grep -E '^\|.*Hulk.*\| 请求 \|' /home/node/.openclaw/shared/BULLETIN.md 2>/dev/null | head -3)

# 检查 KANBAN 中 Hulk owner 的过期任务 (>48h 未更新)
KANBAN_OVERDUE=$(grep -E '^\|.*Hulk.*\|' /home/node/.openclaw/shared/KANBAN.md 2>/dev/null | grep -E '2026-03-(0[5-9]|1[01])' | head -3)

# 生成报告
REPORT="🟢 **Hulk 研究心跳** $(date '+%Y-%m-%d %H:%M UTC')

**新研究请求**:
${BULLETIN_REQUESTS:-无}

**过期任务**:
${KANBAN_OVERDUE:-无}

**状态**: 待命"

# 发送到 Discord
openclaw message send --channel discord "$REPORT"

log "✅ 心跳完成"
