#!/bin/bash
# AISHELL 标注文件下载脚本
# ========================================
# AISHELL 主数据可从 OpenSLR 下载，但标注文件需要单独获取
# 来源：https://www.openslr.org/33/
# 创建者：Hulk 🟢
# 创建日期：2026-03-29

set -e

WORKSPACE="/Users/moondy/.openclaw/workspace-hulk"
AISHELL_DIR="$WORKSPACE/data_aishell"
TRANSCRIPT_DIR="$AISHELL_DIR/transcript"

echo "=== AISHELL 标注文件下载脚本 ==="
echo "目标目录：$TRANSCRIPT_DIR"
echo ""

# 创建目录
mkdir -p "$TRANSCRIPT_DIR"

# 标注文件
TRANSCRIPT_FILE="$TRANSCRIPT_DIR/aishell_transcript_v0.8.txt"

if [ -f "$TRANSCRIPT_FILE" ] && [ -s "$TRANSCRIPT_FILE" ]; then
    LINE_COUNT=$(wc -l < "$TRANSCRIPT_FILE")
    echo "✓ 标注文件已存在：$LINE_COUNT 行"
    echo "  路径：$TRANSCRIPT_FILE"
else
    echo "↓ 下载 AISHELL 标注文件..."
    
    # 尝试多个来源
    SOURCES=(
        "https://www.openslr.org/resources/33/aishell_transcript_v0.8.txt"
        "https://huggingface.co/datasets/aishell/resolve/main/aishell_transcript_v0.8.txt"
    )
    
    DOWNLOADED=false
    
    for SOURCE in "${SOURCES[@]}"; do
        echo "  尝试：$SOURCE"
        if curl -sI "$SOURCE" | grep -q "200 OK"; then
            if curl -L -o "$TRANSCRIPT_FILE" "$SOURCE"; then
                echo "  ✓ 下载成功"
                DOWNLOADED=true
                break
            fi
        fi
    done
    
    if [ "$DOWNLOADED" = false ]; then
        echo "✗ 所有来源均下载失败"
        echo ""
        echo "手动下载方案:"
        echo "1. 访问：https://www.openslr.org/33/"
        echo "2. 下载 'aishell_transcript_v0.8.txt'"
        echo "3. 放置到：$TRANSCRIPT_FILE"
        exit 1
    fi
fi

# 验证标注文件格式
echo ""
echo "验证标注文件..."
if head -n 3 "$TRANSCRIPT_FILE" | grep -q "BAC009S"; then
    echo "✓ 标注文件格式验证通过"
    LINE_COUNT=$(wc -l < "$TRANSCRIPT_FILE")
    echo "  总行数：$LINE_COUNT"
else
    echo "⚠ 标注文件格式可能不正确"
    echo "  前 3 行内容:"
    head -n 3 "$TRANSCRIPT_FILE"
fi

echo ""
echo "=== 完成 ==="
echo ""
echo "下一步：重新运行预处理以加载标注"
echo "  python3 scripts/process_all_datasets.py --dataset aishell --reprocess"
