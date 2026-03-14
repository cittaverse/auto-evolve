#!/bin/bash
# 老年语音数据集下载脚本 v2.0
# 备选方案：Common Voice AWS bucket 移除后的替代数据集
# 创建日期：2026-03-14
# 执行者：Hulk 🟢

set -e

DATA_DIR="/home/node/.openclaw/workspace-hulk/data/elderly_voice"
mkdir -p "$DATA_DIR"

echo "=== 老年语音数据集下载脚本 v2.0 ==="
echo "目标目录：$DATA_DIR"
echo ""

# 数据集 1: AISHELL (中文，开源，可商用)
# 来源：https://www.openslr.org/33/
# 大小：~10GB
# 说话者：400 人（年龄分布均匀，包含老年说话者）
echo "[1/3] AISHELL 数据集检查..."
AISHELL_URL="https://www.openslr.org/resources/33/data_aishell.tgz"
AISHELL_FILE="$DATA_DIR/data_aishell.tgz"

if [ -f "$AISHELL_FILE" ] && [ $(stat -f%z "$AISHELL_FILE" 2>/dev/null || stat -c%s "$AISHELL_FILE" 2>/dev/null) -gt 1000000 ]; then
    echo "  ✓ AISHELL 已下载，跳过"
else
    echo "  ↓ 下载 AISHELL (约 10GB，需 10-30 分钟)..."
    echo "  来源：$AISHELL_URL"
    curl -L -o "$AISHELL_FILE" "$AISHELL_URL"
    echo "  ✓ AISHELL 下载完成"
fi

# 数据集 2: ST-CMDS (中文普通话，单说话者)
# 来源：https://www.openslr.org/62/
# 大小：~500MB
# 说话者：1 人（标准普通话）
# 注意：2026-03-14 检查 404，尝试备用链接
echo ""
echo "[2/3] ST-CMDS 数据集检查..."
STCMDS_URL="https://www.openslr.org/resources/62/st-cmds20170002_1-OS.tar.gz"
STCMDS_FILE="$DATA_DIR/st-cmds.tar.gz"

# 备用链接（HuggingFace）
STCMDS_BACKUP="https://huggingface.co/datasets/st-cmds/resolve/main/st-cmds20170002_1-OS.tar.gz"

if [ -f "$STCMDS_FILE" ] && [ $(stat -f%z "$STCMDS_FILE" 2>/dev/null || stat -c%s "$STCMDS_FILE" 2>/dev/null) -gt 1000000 ]; then
    echo "  ✓ ST-CMDS 已下载，跳过"
else
    echo "  ↓ 尝试主链接..."
    if curl -sI "$STCMDS_URL" | grep -q "200 OK"; then
        echo "  ↓ 下载 ST-CMDS (约 500MB)..."
        curl -L -o "$STCMDS_FILE" "$STCMDS_URL"
        echo "  ✓ ST-CMDS 下载完成"
    else
        echo "  ⚠ 主链接 404，尝试备用链接 (HuggingFace)..."
        if curl -sI "$STCMDS_BACKUP" | grep -q "200 OK"; then
            curl -L -o "$STCMDS_FILE" "$STCMDS_BACKUP"
            echo "  ✓ ST-CMDS 从备用链接下载完成"
        else
            echo "  ✗ ST-CMDS 所有链接均不可用，跳过"
        fi
    fi
fi

# 数据集 3: Common Voice (备用 HuggingFace 链接)
# 原 AWS S3 bucket 已移除，改用 HuggingFace
echo ""
echo "[3/3] Common Voice 中文 (HuggingFace 备用)..."
CV_DIR="$DATA_DIR/common_voice"
CV_URL="https://huggingface.co/datasets/mozilla-foundation/common_voice_11_0/resolve/main/zh-CN.tar.gz"

if [ -d "$CV_DIR" ] && [ "$(ls -A $CV_DIR 2>/dev/null)" ]; then
    echo "  ✓ Common Voice 已下载，跳过"
else
    echo "  ↓ Common Voice 需使用 HuggingFace CLI 或手动下载"
    echo "  来源：https://huggingface.co/datasets/mozilla-foundation/common_voice_11_0"
    echo "  提示：使用 'huggingface-cli download mozilla-foundation/common_voice_11_0 zh-CN.tar.gz'"
    echo "  或手动下载后解压到 $CV_DIR"
fi

echo ""
echo "=== 下载完成 ==="
echo ""
echo "下一步:"
echo "1. 解压数据集:"
echo "   cd $DATA_DIR"
echo "   tar -xzf data_aishell.tgz"
echo ""
echo "2. 筛选 60+ 岁说话者样本 (需查看元数据)"
echo ""
echo "3. 使用 ASR 评估脚本测试:"
echo "   python3 pipeline/asr_evaluation_test.py --samples=10 --services=azure,iflytek,whisper"
echo ""
echo "数据来源:"
echo "- AISHELL: https://www.openslr.org/33/"
echo "- ST-CMDS: https://www.openslr.org/62/ (备用：HuggingFace)"
echo "- Common Voice: https://huggingface.co/datasets/mozilla-foundation/common_voice_11_0"
