#!/bin/bash
# research.sh - GEO 迭代阶段 1: 研究

set -e

echo "📚 Starting Research Phase..."

# 1. 竞品分析
echo "  → Analyzing competitors..."
COMPETITORS=(
  "yanghangit/LLM-MCI-detection"
  "awesomelistsio/awesome-ai-healthcare"
  "dreamingechoes/awesome-mental-health"
)

for repo in "${COMPETITORS[@]}"; do
  echo "    - Checking $repo"
  curl -s "https://api.github.com/repos/$repo" | jq -r '.name, .stargazers_count, .updated_at'
done

# 2. 索引检查
echo "  → Checking search index status..."
# Google
GOOGLE_RESULTS=$(curl -s "https://www.google.com/search?q=site:github.com/cittaverse" | grep -o "约 [0-9,]* 个结果" || echo "未检测到")
echo "    - Google: $GOOGLE_RESULTS"

# Bing
BING_RESULTS=$(curl -s "https://www.bing.com/search?q=site:github.com/cittaverse" | grep -o "[0-9,]* 个结果" || echo "未检测到")
echo "    - Bing: $BING_RESULTS"

# 3. 关键词研究
echo "  → Researching keywords..."
curl -s -X POST "https://google.serper.dev/search" \
  -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q": "narrative assessment elderly AI cognitive training", "num": 10}' \
  | jq '.organic[] | {title, snippet}' > iteration_logs/keywords_$(date +%Y%m%d_%H%M%S).json

# 4. 生成研究报告
echo "  → Generating research report..."
cat > iteration_logs/research_$(date +%Y%m%d_%H%M%S).json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "phase": "research",
  "status": "complete",
  "competitors_analyzed": ${#COMPETITORS[@]},
  "keywords_found": 10
}
EOF

echo "✅ Research Phase complete"
