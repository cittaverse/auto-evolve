#!/bin/bash
# GEO 月度指标追踪脚本
# 用法：./scripts/track-monthly.sh

set -e

WORKSPACE="/workspace"
METRICS_DIR="$WORKSPACE/metrics"
MEMORY="$WORKSPACE/memory"
DATE=$(date -u +%Y-%m-%d)
MONTH=$(date -u +%Y-%m)
OUTPUT="$METRICS_DIR/monthly-$MONTH.md"

echo "🟢 GEO 月度指标汇总 - $MONTH"
echo "================================"
echo "日期：$DATE"
echo ""

# 获取本周期的周度报告
WEEKLY_REPORTS=$(find "$METRICS_DIR" -name "summary-*.md" -newer "$METRICS_DIR/monthly-$(date -u -d 'last month' +%Y-%m).md" 2>/dev/null | sort || echo "")

# 统计本周期的关键数据
TOTAL_COMMITS=0
TOTAL_FILES=0
TOTAL_WORDS=0

# 仓库列表
REPOS=("pipeline" "awesome-digital-therapy" "core")

for repo in "${REPOS[@]}"; do
    REPO_PATH="$WORKSPACE/github-repos/$repo"
    
    if [ -d "$REPO_PATH" ]; then
        # 统计文件数
        MD_FILES=$(find "$REPO_PATH" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        WORDS=$(find "$REPO_PATH" -name "*.md" -exec cat {} \; 2>/dev/null | wc -c | tr -d ' ')
        
        TOTAL_FILES=$((TOTAL_FILES + MD_FILES))
        TOTAL_WORDS=$((TOTAL_WORDS + WORDS))
    fi
done

# 统计迭代轮次
ITERATION_COUNT=$(find "$MEMORY" -name "*geo-iteration*.md" 2>/dev/null | wc -l | tr -d ' ')

# 生成月度报告
cat > "$OUTPUT" << EOF
# GEO 月度指标汇总 - $MONTH

**生成日期**: $DATE  
**追踪者**: Hulk 🟢  
**报告类型**: 月度汇总

---

## 📊 本月关键指标

| 指标 | 月初值 | 月末值 | 增长率 |
|------|--------|--------|--------|
| GitHub Stars (总计) | 待追踪 | 待 API | 待计算 |
| 仓库 Views (总计) | 待追踪 | 待 API | 待计算 |
| Markdown 文件数 | 待追踪 | $TOTAL_FILES | - |
| 文档总字数 | 待追踪 | ~$TOTAL_WORDS | - |
| 迭代轮次 | 待追踪 | $ITERATION_COUNT | - |

---

## 📈 仓库明细

### pipeline

| 指标 | 数值 |
|------|------|
| Markdown 文件 | $(find "$WORKSPACE/github-repos/pipeline" -name "*.md" 2>/dev/null | wc -l | tr -d ' ') |
| 文档字数 | ~$(find "$WORKSPACE/github-repos/pipeline" -name "*.md" -exec cat {} \; 2>/dev/null | wc -c | tr -d ' ') |
| Commits | $(git -C "$WORKSPACE/github-repos/pipeline" rev-list --count HEAD 2>/dev/null || echo "N/A") |

### awesome-digital-therapy

| 指标 | 数值 |
|------|------|
| Markdown 文件 | $(find "$WORKSPACE/github-repos/awesome-digital-therapy" -name "*.md" 2>/dev/null | wc -l | tr -d ' ') |
| 文档字数 | ~$(find "$WORKSPACE/github-repos/awesome-digital-therapy" -name "*.md" -exec cat {} \; 2>/dev/null | wc -c | tr -d ' ') |
| Commits | $(git -C "$WORKSPACE/github-repos/awesome-digital-therapy" rev-list --count HEAD 2>/dev/null || echo "N/A") |

### core

| 指标 | 数值 |
|------|------|
| Markdown 文件 | $(find "$WORKSPACE/github-repos/core" -name "*.md" 2>/dev/null | wc -l | tr -d ' ') |
| 文档字数 | ~$(find "$WORKSPACE/github-repos/core" -name "*.md" -exec cat {} \; 2>/dev/null | wc -c | tr -d ' ') |
| Commits | $(git -C "$WORKSPACE/github-repos/core" rev-list --count HEAD 2>/dev/null || echo "N/A") |

---

## 📅 本周度报告列表

$(if [ -n "$WEEKLY_REPORTS" ]; then
    echo "$WEEKLY_REPORTS" | while read report; do
        basename "$report"
    done | sed 's/^/- /'
else
    echo "- 无本周度报告"
fi)

---

## 🎯 目标进度 (30 天)

| 指标 | 目标 | 当前 | 进度 |
|------|------|------|------|
| Stars 增长 | +50 | 待 API | 待计算 |
| Views 增长 | +500 | 待 API | 待计算 |
| 文件增长 | +10 | $TOTAL_FILES | 待计算 |
| 迭代轮次 | 10 | $ITERATION_COUNT | $((ITERATION_COUNT * 10))% |

---

## 📝 关键洞察

- [ ] 待填充（根据实际数据）

---

## 📋 下月目标

- [ ] 根据本月数据调整
- [ ] 持续优化 GEO 策略

---

*报告生成完成 | GEO Monthly Tracker v1.0*
EOF

echo "✅ 月度汇总已生成：$OUTPUT"
echo ""
echo "📊 关键数据摘要:"
echo "   - Markdown 文件：$TOTAL_FILES 个"
echo "   - 文档字数：~$TOTAL_WORDS"
echo "   - 迭代轮次：$ITERATION_COUNT"
echo ""
echo "📄 报告文件：$OUTPUT"
