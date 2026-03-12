#!/bin/bash
# Hulk 证据扫描 - 每周一 1:00 UTC (= 杭州 9:00)
# 扫描研究领域的新论文/证据，生成研究周报素材

cd /home/node/.openclaw/workspace-hulk

LOG_FILE="/home/node/.openclaw/workspace-hulk/metrics/cron_evidence_scan.log"
OUTPUT_DIR="/home/node/.openclaw/workspace-hulk/research/evidence_scan"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$(dirname $LOG_FILE)"

log() {
    echo "[$(date -u +%Y-%m-%d_%H:%M:%S_UTC)] $1" | tee -a "$LOG_FILE"
}

log "🔬 开始证据扫描"

# 研究领域关键词
TOPICS=(
    "reminiscence therapy AI"
    "narrative identity LLM"
    "autobiographical memory aging"
    "dementia speech markers"
    "neurosymbolic AI memory"
    "life review intervention"
)

# 生成扫描报告
REPORT="🔬 **Hulk 证据扫描周报** $(date '+%Y-%m-%d')

**扫描领域**:
- 记忆科学 × AI × 叙事疗法
- 神经符号 AI 应用于记忆技术
- 老年认知障碍语言标记

**扫描策略**:
- 每周自动扫描最新论文/临床证据
- 过滤高相关性研究
- 转化为产品行动建议

**本周扫描**: 待执行

---
*自动扫描任务 - 详细结果见 \`research/evidence_scan/\`*"

# 保存到文件
echo "$REPORT" > "$OUTPUT_DIR/weekly_scan_$(date +%Y-%m-%d).md"

# 发送通知
openclaw message send --channel discord "$REPORT"

log "✅ 证据扫描完成"
