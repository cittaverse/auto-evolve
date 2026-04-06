#!/bin/bash
# 数据集预处理执行脚本 v3.0
# ========================================
# 用途：Cron 任务 #7744d4c5 - 数据集预处理
# 功能：音频清洗、分割、特征提取
#
# 创建者：Hulk 🟢
# 创建日期：2026-03-28
# 更新日期：2026-04-02
#
# 用法：
#   bash scripts/dataset_preprocess_v3.sh              # 处理所有数据集
#   bash scripts/dataset_preprocess_v3.sh aishell      # 仅 AISHELL
#   bash scripts/dataset_preprocess_v3.sh elderly      # 仅老年语音
#   bash scripts/dataset_preprocess_v3.sh validate     # 仅验证
#   bash scripts/dataset_preprocess_v3.sh aishell --reprocess  # 重新处理

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="/Users/moondy/.openclaw/workspace-hulk"
PYTHON_SCRIPT="$SCRIPT_DIR/preprocess_audio_datasets.py"
LOG_DIR="$WORKSPACE/output"
LOG_FILE="$LOG_DIR/dataset_preprocess_$(date +%Y%m%d_%H%M%S).log"

# 创建日志目录
mkdir -p "$LOG_DIR"

echo "========================================"
echo "🟢 数据集预处理 v3.0"
echo "========================================"
echo "工作目录：$WORKSPACE"
echo "日志文件：$LOG_FILE"
echo "开始时间：$(date)"
echo ""

# 检查 Python 脚本
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Python 脚本不存在：$PYTHON_SCRIPT"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import librosa, soundfile, numpy, pandas, matplotlib, scipy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  缺少依赖库，尝试安装..."
    pip3 install librosa soundfile numpy pandas matplotlib scipy tqdm
fi

echo ""

# 构建命令
CMD="python3 $PYTHON_SCRIPT"

if [ "$1" == "validate" ]; then
    CMD="$CMD --validate"
elif [ "$1" == "aishell" ]; then
    CMD="$CMD --dataset aishell"
    shift
    if [ "$1" == "--reprocess" ]; then
        CMD="$CMD --reprocess"
    fi
elif [ "$1" == "elderly" ]; then
    CMD="$CMD --dataset elderly"
    shift
    if [ "$1" == "--reprocess" ]; then
        CMD="$CMD --reprocess"
    fi
elif [ "$1" == "--all" ] || [ -z "$1" ]; then
    CMD="$CMD --all"
else
    CMD="$CMD --all"
fi

# 执行处理
echo "执行命令：$CMD"
echo ""
echo "----------------------------------------"

# 执行并记录日志
{
    echo "命令：$CMD"
    echo "开始：$(date)"
    echo ""
    $CMD 2>&1
    echo ""
    echo "结束：$(date)"
} | tee "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "----------------------------------------"
echo "完成时间：$(date)"
echo "退出码：$EXIT_CODE"
echo "日志：$LOG_FILE"

# 保存最新日志链接
ln -sf "$LOG_FILE" "$LOG_DIR/dataset_preprocess_latest.log"

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ 预处理成功完成"
else
    echo ""
    echo "❌ 预处理失败，请检查日志"
fi

exit $EXIT_CODE
