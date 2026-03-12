#!/bin/bash
# Hulk 记忆固化 - 每日 14:00 UTC (= 杭州 22:00)
# 扫描今日 memory 日志，提取关键发现，追加到 MEMORY.md

cd /home/node/.openclaw/workspace-hulk

LOG_FILE="/home/node/.openclaw/workspace-hulk/metrics/cron_memory_consolidate.log"
MEMORY_MD="/home/node/.openclaw/workspace-hulk/MEMORY.md"
MEMORY_DIR="/home/node/.openclaw/workspace-hulk/memory"

mkdir -p "$(dirname $LOG_FILE)"

log() {
    echo "[$(date -u +%Y-%m-%d_%H:%M:%S_UTC)] $1" | tee -a "$LOG_FILE"
}

log "🧠 开始记忆固化"

# 获取今日日志文件
TODAY=$(date +%Y-%m-%d)
TODAY_FILES=$(ls -la "$MEMORY_DIR"/${TODAY}*.md 2>/dev/null | wc -l)

if [ "$TODAY_FILES" -eq 0 ]; then
    log "⚠️ 今日无记忆日志"
    openclaw message send --channel discord "🧠 **Hulk 记忆固化**

今日无新记忆需要固化。"
    exit 0
fi

# 提取关键发现（简化版：读取今日日志中的研究洞察）
# 实际应该用更复杂的 NLP 提取，这里先用简单规则
NEW_INSIGHTS=""
for file in "$MEMORY_DIR"/${TODAY}*.md; do
    if [ -f "$file" ]; then
        # 提取 Session 中的 Conversation Summary 部分
        SUMMARY=$(sed -n '/## Conversation Summary/,/## /p' "$file" 2>/dev/null | head -20)
        if [ -n "$SUMMARY" ]; then
            NEW_INSIGHTS="${NEW_INSIGHTS}
---
**来源**: $(basename $file)
${SUMMARY}"
        fi
    fi
done

# 追加到 MEMORY.md（在文件末尾前插入）
if [ -n "$NEW_INSIGHTS" ]; then
    # 简单追加到文件末尾
    cat >> "$MEMORY_MD" << EOF

---

## [${TODAY}] 新增洞察

${NEW_INSIGHTS}

EOF
    log "✅ 已固化 $(basename $file) 到 MEMORY.md"
    openclaw message send --channel discord "🧠 **Hulk 记忆固化完成**

今日处理：${TODAY_FILES} 个会话日志
已追加到 MEMORY.md

**关键洞察**:
$(echo "$NEW_INSIGHTS" | head -5)"
else
    log "⚠️ 无有效洞察可提取"
fi

log "✅ 记忆固化完成"
