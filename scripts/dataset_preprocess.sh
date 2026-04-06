#!/bin/bash
# 数据集预处理执行脚本
# ========================================
# 用途：Cron 任务 #7744d4c5 - 数据集预处理
# 功能：AISHELL 和其他数据集的清洗、分割、特征提取
#
# 用法:
#   bash scripts/dataset_preprocess.sh [OPTIONS]
#
# 选项:
#   --dataset aishell|elderly|all  指定数据集 (默认：all)
#   --reprocess                    重新处理已有数据
#   --extract-features             仅提取特征
#   --validate                     仅验证
#   --help                         显示帮助
#
# 创建者：Hulk 🟢
# 创建日期：2026-03-30

set -e

WORKSPACE="/Users/moondy/.openclaw/workspace-hulk"
SCRIPTS_DIR="$WORKSPACE/scripts"
LOG_FILE="$WORKSPACE/output/dataset_preprocess_$(date +%Y%m%d_%H%M%S).log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

# 创建输出目录
mkdir -p "$WORKSPACE/output"

log "========================================"
log "数据集预处理脚本"
log "========================================"
log "工作目录：$WORKSPACE"
log "日志文件：$LOG_FILE"
log ""

# 检查 Python 依赖
log "检查 Python 依赖..."
python3 -c "import librosa, numpy, pandas, soundfile, tqdm" 2>/dev/null
if [ $? -ne 0 ]; then
    warning "缺少 Python 依赖，尝试安装..."
    pip3 install librosa numpy pandas soundfile tqdm matplotlib
fi
success "Python 依赖检查完成"

# 解析参数
DATASET="all"
REPROCESS=""
EXTRACT_FEATURES=""
VALIDATE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dataset)
            DATASET="$2"
            shift 2
            ;;
        --reprocess)
            REPROCESS="--reprocess"
            shift
            ;;
        --extract-features)
            EXTRACT_FEATURES="--extract-features"
            shift
            ;;
        --validate)
            VALIDATE="--validate"
            shift
            ;;
        --help)
            echo "用法：bash scripts/dataset_preprocess.sh [OPTIONS]"
            echo ""
            echo "选项:"
            echo "  --dataset aishell|elderly|all  指定数据集 (默认：all)"
            echo "  --reprocess                    重新处理已有数据"
            echo "  --extract-features             仅提取特征"
            echo "  --validate                     仅验证"
            echo "  --help                         显示帮助"
            exit 0
            ;;
        *)
            error "未知选项：$1"
            exit 1
            ;;
    esac
done

log "配置:"
log "  数据集：$DATASET"
log "  重新处理：$REPROCESS"
log "  仅特征提取：$EXTRACT_FEATURES"
log "  仅验证：$VALIDATE"
log ""

# 解压 AISHELL 音频文件（如果尚未解压）
if [ "$DATASET" = "aishell" ] || [ "$DATASET" = "all" ]; then
    log "检查 AISHELL 音频文件..."
    WAV_COUNT=$(find "$WORKSPACE/data_aishell/wav" -name "*.wav" 2>/dev/null | wc -l | tr -d ' ')
    
    if [ "$WAV_COUNT" -lt 1000 ]; then
        log "发现 $WAV_COUNT 个 WAV 文件，开始解压..."
        
        cd "$WORKSPACE/data_aishell/wav"
        for tarball in S*.tar.gz; do
            if [ -f "$tarball" ]; then
                log "  解压：$tarball"
                tar -xzf "$tarball" 2>/dev/null || warning "解压失败：$tarball"
            fi
        done
        
        NEW_WAV_COUNT=$(find "$WORKSPACE/data_aishell/wav" -name "*.wav" 2>/dev/null | wc -l | tr -d ' ')
        success "解压完成：$NEW_WAV_COUNT 个 WAV 文件"
    else
        success "已有 $WAV_COUNT 个 WAV 文件，跳过解压"
    fi
fi

# 运行 Python 处理脚本
log ""
log "运行数据处理脚本..."
cd "$WORKSPACE"

python3 "$SCRIPTS_DIR/process_all_datasets.py" \
    --dataset "$DATASET" \
    $REPROCESS \
    $EXTRACT_FEATURES \
    $VALIDATE \
    2>&1 | tee -a "$LOG_FILE"

# 检查执行结果
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    success "数据处理完成"
else
    error "数据处理失败"
    exit 1
fi

# 生成报告摘要
log ""
log "========================================"
log "处理摘要"
log "========================================"

if [ -f "$WORKSPACE/data/processed/processing_report_v2.json" ]; then
    log "处理报告：$WORKSPACE/data/processed/processing_report_v2.json"
    
    # 使用 Python 格式化输出
    python3 -c "
import json
with open('$WORKSPACE/data/processed/processing_report_v2.json') as f:
    report = json.load(f)
    print(f\"状态：{report.get('status', 'unknown')}\")
    if 'steps' in report:
        for k, v in report['steps'].items():
            if isinstance(v, dict):
                print(f\"  {k}: {v}\")
            else:
                print(f\"  {k}: {v}\")
" 2>&1 | tee -a "$LOG_FILE"
fi

log ""
log "日志文件：$LOG_FILE"
log "========================================"
log "✅ 数据集预处理完成"
log "========================================"
