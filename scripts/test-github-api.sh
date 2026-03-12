#!/bin/bash
# 临时测试脚本 - 手动设置 Token 后运行

# TODO: 将下面的 xxx 替换为你的实际 Token
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

echo "🧪 测试 GitHub API..."
echo ""

# 测试 1: 基本信息
echo "📊 仓库基本信息 (pipeline):"
curl -s -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/cittaverse/pipeline \
    | grep -E '"stargazers_count"|"forks_count"|"size"'

echo ""

# 测试 2: 流量统计（需要 Token）
echo "📈 流量统计 (pipeline):"
curl -s -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/cittaverse/pipeline/traffic/views

echo ""
echo "✅ 测试完成"
