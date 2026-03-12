#!/bin/bash
# GitHub API 指标抓取脚本
# 用法：./scripts/fetch-github-stats.sh [owner/repo]

set -e

REPO_ARG=${1:-"cittaverse/pipeline"}
GITHUB_TOKEN="${GITHUB_TOKEN:-}"  # 可选，无 token 时速率限制 60 次/小时

echo "📊 抓取 GitHub 统计：$REPO_ARG"

# 解析 owner/repo
OWNER=$(echo "$REPO_ARG" | cut -d'/' -f1)
REPO=$(echo "$REPO_ARG" | cut -d'/' -f2)

# API 端点
API_BASE="https://api.github.com"
REPO_URL="$API_BASE/repos/$OWNER/$REPO"
TRAFFIC_URL="$API_BASE/repos/$OWNER/$REPO/traffic/views"
CLONES_URL="$API_BASE/repos/$OWNER/$REPO/traffic/clones"

# 构建请求头
HEADERS=""
if [ -n "$GITHUB_TOKEN" ]; then
    HEADERS="-H \"Authorization: token $GITHUB_TOKEN\""
fi

# 获取仓库基本信息
echo "正在获取仓库基本信息..."
RESPONSE=$(curl -s $HEADERS "$REPO_URL" 2>/dev/null || echo "{}")

STARS=$(echo "$RESPONSE" | grep -o '"stargazers_count":[0-9]*' | cut -d':' -f2 || echo "0")
FORKS=$(echo "$RESPONSE" | grep -o '"forks_count":[0-9]*' | cut -d':' -f2 || echo "0")
WATCHERS=$(echo "$RESPONSE" | grep -o '"watchers_count":[0-9]*' | cut -d':' -f2 || echo "0")
OPEN_ISSUES=$(echo "$RESPONSE" | grep -o '"open_issues_count":[0-9]*' | cut -d':' -f2 || echo "0")

echo ""
echo "📈 仓库统计 ($OWNER/$REPO):"
echo "   ⭐ Stars: $STARS"
echo "   🍴 Forks: $FORKS"
echo "   👁️ Watchers: $WATCHERS"
echo "   📋 Open Issues: $OPEN_ISSUES"

# 获取流量统计 (需要 token)
if [ -n "$GITHUB_TOKEN" ]; then
    echo ""
    echo "正在获取流量统计..."
    
    VIEWS_RESPONSE=$(curl -s $HEADERS "$TRAFFIC_URL" 2>/dev/null || echo "{}")
    CLONES_RESPONSE=$(curl -s $HEADERS "$CLONES_URL" 2>/dev/null || echo "{}")
    
    # 解析 views
    VIEW_COUNT=$(echo "$VIEWS_RESPONSE" | grep -o '"count":[0-9]*' | head -1 | cut -d':' -f2 || echo "0")
    UNIQUE_VIEWERS=$(echo "$VIEWS_RESPONSE" | grep -o '"uniques":[0-9]*' | head -1 | cut -d':' -f2 || echo "0")
    
    # 解析 clones
    CLONE_COUNT=$(echo "$CLONES_RESPONSE" | grep -o '"count":[0-9]*' | head -1 | cut -d':' -f2 || echo "0")
    UNIQUE_CLONERS=$(echo "$CLONES_RESPONSE" | grep -o '"uniques":[0-9]*' | head -1 | cut -d':' -f2 || echo "0")
    
    echo ""
    echo "📊 流量统计 (14 天):"
    echo "   👁️ Views: $VIEW_COUNT (独立访客：$UNIQUE_VIEWERS)"
    echo "   📥 Clones: $CLONE_COUNT (独立克隆：$UNIQUE_CLONERS)"
else
    echo ""
    echo "⚠️ 流量统计需要 GITHUB_TOKEN"
    echo "   设置环境变量后重试：export GITHUB_TOKEN=your_token"
fi

# 输出 JSON 格式 (供其他脚本使用)
echo ""
echo "📄 JSON 输出:"
cat << EOF
{
  "repository": "$OWNER/$REPO",
  "stars": $STARS,
  "forks": $FORKS,
  "watchers": $WATCHERS,
  "open_issues": $OPEN_ISSUES,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
