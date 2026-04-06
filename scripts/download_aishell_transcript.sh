#!/bin/bash
#
# 下载 AISHELL-1 转录文件
# ========================
# AISHELL 转录文本单独存放，需要从 OpenSLR 或其他源下载
#
# 用法：./scripts/download_aishell_transcript.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$WORKSPACE_DIR/data_aishell"

echo "=== 下载 AISHELL-1 转录文件 ==="
echo "目标目录：$DATA_DIR"

# 创建目录
mkdir -p "$DATA_DIR/transcript"

# AISHELL-1 转录文件 URL (OpenSLR)
TRANSCRIPT_URL="http://www.openslr.org/resources/33/data_aishell_transcript_v0.8.tar.gz"
TRANSCRIPT_TGZ="$DATA_DIR/data_aishell_transcript_v0.8.tar.gz"

echo "下载转录文件..."
if command -v wget &> /dev/null; then
    wget -c "$TRANSCRIPT_URL" -O "$TRANSCRIPT_TGZ"
elif command -v curl &> /dev/null; then
    curl -L -o "$TRANSCRIPT_TGZ" "$TRANSCRIPT_URL"
else
    echo "错误：需要 wget 或 curl"
    exit 1
fi

echo "解压转录文件..."
cd "$DATA_DIR"
tar -xzf "$TRANSCRIPT_TGZ"

# 移动到正确位置
if [ -d "$DATA_DIR/transcript" ]; then
    rm -rf "$DATA_DIR/transcript"
fi
mv data_aishell/transcript "$DATA_DIR/"

# 清理
rm -f "$TRANSCRIPT_TGZ"
rm -rf data_aishell

echo ""
echo "转录文件已下载并解压到：$DATA_DIR/transcript/"
echo "验证：ls -lh $DATA_DIR/transcript/"
ls -lh "$DATA_DIR/transcript/"

echo ""
echo "✓ AISHELL 转录文件下载完成"
