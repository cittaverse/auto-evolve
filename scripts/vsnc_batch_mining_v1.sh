#!/bin/bash
# VSNC 批量挖掘启动脚本 v1.0
# 用法：./scripts/vsnc_batch_mining_v1.sh

set -e

WORKSPACE="/home/node/.openclaw/workspace-hulk"
cd "$WORKSPACE"

echo "========================================"
echo "VSNC 批量挖掘 v1.0"
echo "========================================"
echo ""

# 检查 API Key
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "❌ 错误：DASHSCOPE_API_KEY 未设置"
    echo "请确保 .env 文件已加载或环境变量已设置"
    exit 1
fi

# 检查 Python 依赖
echo "🔧 检查依赖..."
python3 -c "import ssl; import json; import urllib.request" 2>/dev/null || {
    echo "⚠️  Python 标准库检查通过"
}

# 可选：安装 PDF 解析库
echo "📦 检查 PDF 解析库..."
python3 -c "import pypdf" 2>/dev/null && echo "  ✅ pypdf 已安装" || {
    echo "  ⚠️  pypdf 未安装，将使用基础模式"
}

# 启动批量挖掘
echo ""
echo "🚀 启动批量挖掘..."
echo ""

python3 PROTOTYPES/vsnc_batch_miner_v1.py

echo ""
echo "✅ 批量挖掘完成"
echo "查看进度：cat VSNC/ledger.json"
echo "查看结果：ls -la VSNC/输出/"
