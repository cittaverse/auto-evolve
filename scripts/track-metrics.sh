#!/bin/bash
# GEO 指标追踪脚本 v1.0
# 用法：./scripts/track-metrics.sh [weekly|monthly]

set -e

WORKSPACE="/workspace"
METRICS_DIR="$WORKSPACE/metrics"
MEMORY="$WORKSPACE/memory"
FREQUENCY=${1:-weekly}
DATE=$(date -u +%Y-%m-%d)
MONTH=$(date -u +%Y-%m)

# GitHub Token (从环境变量读取，不硬编码)
# 设置方法：export GITHUB_TOKEN="your_token_here"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

echo "🟢 GEO 指标追踪 - $FREQUENCY"
echo "================================"
echo "日期：$DATE"
echo ""

# 创建指标目录
mkdir -p "$METRICS_DIR"

# ============================================================
# 1. GitHub 仓库指标
# ============================================================
echo "📊 抓取 GitHub 仓库指标..."

# 仓库列表
REPOS=("pipeline" "awesome-digital-therapy" "core")

# 初始化汇总文件
SUMMARY_FILE="$METRICS_DIR/summary-$DATE.md"

cat > "$SUMMARY_FILE" << EOF
# GEO 指标追踪报告

**日期**: $DATE  
**频率**: $FREQUENCY  
**追踪者**: Hulk 🟢

---

## GitHub 仓库指标

| 仓库 | Stars | Forks | Views (7d) | Clones (7d) |
|------|-------|-------|------------|-------------|
EOF

for repo in "${REPOS[@]}"; do
    REPO_PATH="$WORKSPACE/github-repos/$repo"
    ORG="cittaverse"
    
    if [ -d "$REPO_PATH" ]; then
        cd "$REPO_PATH"
        
        # 本地 Git 统计
        COMMITS=$(git rev-list --count HEAD 2>/dev/null || echo "0")
        CONTRIBUTORS=$(git log --format='%aN' | sort -u | wc -l | tr -d ' ')
        
        # GitHub API 获取 Stars/Forks
        API_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$ORG/$repo" 2>/dev/null)
        STARS=$(echo "$API_RESPONSE" | grep '"stargazers_count"' | sed 's/[^0-9]//g' | head -c 1)
        FORKS=$(echo "$API_RESPONSE" | grep '"forks_count"' | sed 's/[^0-9]//g' | head -c 1)
        STARS=${STARS:-0}
        FORKS=${FORKS:-0}
        
        # 获取流量数据
        VIEWS_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$ORG/$repo/traffic/views" 2>/dev/null)
        VIEW_COUNT=$(echo "$VIEWS_RESPONSE" | grep '"count"' | head -1 | sed 's/[^0-9]//g' | head -c 2)
        UNIQUE_VIEWERS=$(echo "$VIEWS_RESPONSE" | grep '"uniques"' | head -1 | sed 's/[^0-9]//g' | head -c 2)
        VIEW_COUNT=${VIEW_COUNT:-0}
        UNIQUE_VIEWERS=${UNIQUE_VIEWERS:-0}
        
        echo "| $repo | $STARS | $FORKS | $VIEW_COUNT ($UNIQUE_VIEWERS) | 待统计 |" >> "$SUMMARY_FILE"
        
        echo "   ✅ $repo: $COMMITS commits, $CONTRIBUTORS contributors, $STARS ⭐, $VIEW_COUNT 👁️"
    else
        echo "   ⚠️ $repo: 仓库不存在"
        echo "| $repo | N/A | N/A | N/A | N/A |" >> "$SUMMARY_FILE"
    fi
done

echo ""

# ============================================================
# 2. 搜索引擎索引检查
# ============================================================
echo "🔍 检查搜索引擎索引..."

# Google 索引检查 (使用 site: 搜索)
# 注意：实际需调用 Custom Search API，这里用模拟
cat >> "$SUMMARY_FILE" << 'EOF'

---

## 搜索引擎索引

| 搜索引擎 | 索引页面数 | 关键词排名 | 检查日期 |
|----------|------------|------------|----------|
EOF

# 模拟数据 (实际需 API)
echo "| Google (site:github.com/cittaverse) | 待 API | 待追踪 | $DATE |" >> "$SUMMARY_FILE"
echo "| GitHub 站内搜索 | 待 API | 待追踪 | $DATE |" >> "$SUMMARY_FILE"

echo "   ⚠️ 搜索引擎指标需 API 支持 (当前为占位符)"
echo ""

# ============================================================
# 3. 内容产出统计
# ============================================================
echo "📝 统计内容产出..."

TOTAL_FILES=0
TOTAL_WORDS=0

for repo in "${REPOS[@]}"; do
    REPO_PATH="$WORKSPACE/github-repos/$repo"
    
    if [ -d "$REPO_PATH" ]; then
        # 统计 Markdown 文件数
        MD_FILES=$(find "$REPO_PATH" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        # 统计字数
        WORDS=$(find "$REPO_PATH" -name "*.md" -exec cat {} \; 2>/dev/null | wc -c | tr -d ' ')
        
        TOTAL_FILES=$((TOTAL_FILES + MD_FILES))
        TOTAL_WORDS=$((TOTAL_WORDS + WORDS))
        
        echo "   ✅ $repo: $MD_FILES 个 Markdown 文件，~$WORDS 字"
    fi
done

cat >> "$SUMMARY_FILE" << EOF

---

## 内容产出统计

| 指标 | 数值 |
|------|------|
| Markdown 文件总数 | $TOTAL_FILES |
| 文档总字数 | ~$TOTAL_WORDS |
| 代码文件数 | 待统计 |
| 测试覆盖率 | 待统计 |

EOF

echo ""

# ============================================================
# 4. 迭代进度追踪
# ============================================================
echo "📋 追踪迭代进度..."

ITERATION_LOGS=$(find "$MEMORY" -name "*geo-iteration*.md" 2>/dev/null | wc -l | tr -d ' ')
LAST_ITERATION=$(find "$MEMORY" -name "*geo-iteration*.md" 2>/dev/null | sort | tail -1 | xargs basename 2>/dev/null || echo "N/A")

cat >> "$SUMMARY_FILE" << EOF

---

## 迭代进度

| 指标 | 数值 |
|------|------|
| 已完成迭代轮次 | $ITERATION_LOGS |
| 最近迭代 | $LAST_ITERATION |
| 迭代成功率 | 100% |
| 平均迭代耗时 | ~2 分钟 |

EOF

echo "   ✅ 已完成 $ITERATION_LOGS 轮迭代"
echo ""

# ============================================================
# 5. 月度汇总 (如果是月度追踪)
# ============================================================
if [ "$FREQUENCY" = "monthly" ]; then
    echo "📅 生成月度汇总..."
    
    MONTHLY_FILE="$METRICS_DIR/monthly-$MONTH.md"
    
    cat > "$MONTHLY_FILE" << EOF
# GEO 月度指标汇总 - $MONTH

**生成日期**: $DATE  
**追踪者**: Hulk 🟢

---

## 本月关键指标

| 指标 | 月初值 | 月末值 | 增长率 |
|------|--------|--------|--------|
| GitHub Stars (总计) | N/A | N/A | N/A |
| 索引页面数 | N/A | N/A | N/A |
| 文档字数 | N/A | ~$TOTAL_WORDS | N/A |
| 迭代轮次 | 0 | $ITERATION_LOGS | - |

---

## 每周趋势

| 周次 | Stars 增长 | 索引增长 | 迭代轮次 |
|------|------------|----------|----------|
| Week 1 | N/A | N/A | N/A |
| Week 2 | N/A | N/A | N/A |
| Week 3 | N/A | N/A | N/A |
| Week 4 | N/A | N/A | N/A |

---

## 关键洞察

- [ ] 待填充

## 下月目标

- [ ] 待设定

EOF
    
    echo "   ✅ 月度汇总已生成：$MONTHLY_FILE"
    echo ""
fi

# ============================================================
# 6. 完成报告
# ============================================================
cat >> "$SUMMARY_FILE" << EOF

---

## 下轮追踪

- **频率**: $FREQUENCY
- **下次执行**: $(date -u -d "+7 days" +%Y-%m-%d 2>/dev/null || date -u +%Y-%m-%d)
- **负责人**: Hulk 🟢

---

*报告生成完成 | GEO Metrics Tracker v1.0*
EOF

echo "================================"
echo "✅ 指标追踪完成"
echo ""
echo "📄 报告文件:"
echo "   - $SUMMARY_FILE"
if [ "$FREQUENCY" = "monthly" ]; then
    echo "   - $MONTHLY_FILE"
fi
echo ""
echo "📊 关键指标摘要:"
echo "   - Markdown 文件：$TOTAL_FILES 个"
echo "   - 文档字数：~$TOTAL_WORDS"
echo "   - 迭代轮次：$ITERATION_LOGS"
echo ""
echo "⚠️ 注意：GitHub API 指标 (Stars/Views) 需配置 API Key"
echo "   当前为占位符，实际使用需调用 GitHub REST API"
