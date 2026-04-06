#!/bin/bash
#
# 语音数据集预处理完整流程
# 支持：AISHELL, LibriSpeech, Common Voice, THCHS-30 等
#
# Usage:
#   ./run_pipeline.sh --dataset aishell --data_dir /path/to/data --output_dir /path/to/output
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 默认参数
DATASET=""
DATA_DIR=""
OUTPUT_DIR=""
SAMPLE_RATE=16000
DO_AUGMENT=false
DO_SPLIT=true
SPLIT_METHOD="stratified"
N_JOBS=4

# 打印帮助
print_help() {
    cat << EOF
语音数据集预处理流程

用法:
  $0 --dataset <name> --data_dir <path> --output_dir <path> [选项]

必需参数:
  --dataset       数据集名称 (aishell, librispeech, common_voice, thchs30)
  --data_dir      原始数据目录
  --output_dir    输出目录

可选参数:
  --sample_rate   采样率 (默认：16000)
  --augment       启用数据增强
  --no_split      跳过数据集分割
  --split_method  分割方法 (random, stratified, speaker_independent, duration_balanced)
  --n_jobs        并行处理线程数 (默认：4)
  --help          显示帮助信息

示例:
  # 处理 AISHELL-1
  $0 --dataset aishell --data_dir /data/AISHELL-1 --output_dir /data/processed/aishell

  # 处理 LibriSpeech + 数据增强
  $0 --dataset librispeech --data_dir /data/LibriSpeech --output_dir /data/processed/librispeech --augment

  # 说话人独立分割
  $0 --dataset aishell --data_dir /data/AISHELL-1 --output_dir /data/processed/aishell --split_method speaker_independent

EOF
}

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --dataset)
            DATASET="$2"
            shift 2
            ;;
        --data_dir)
            DATA_DIR="$2"
            shift 2
            ;;
        --output_dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --sample_rate)
            SAMPLE_RATE="$2"
            shift 2
            ;;
        --augment)
            DO_AUGMENT=true
            shift
            ;;
        --no_split)
            DO_SPLIT=false
            shift
            ;;
        --split_method)
            SPLIT_METHOD="$2"
            shift 2
            ;;
        --n_jobs)
            N_JOBS="$2"
            shift 2
            ;;
        --help)
            print_help
            exit 0
            ;;
        *)
            log_error "未知参数：$1"
            print_help
            exit 1
            ;;
    esac
done

# 验证必需参数
if [[ -z "$DATASET" ]]; then
    log_error "缺少必需参数：--dataset"
    print_help
    exit 1
fi

if [[ -z "$DATA_DIR" ]]; then
    log_error "缺少必需参数：--data_dir"
    exit 1
fi

if [[ -z "$OUTPUT_DIR" ]]; then
    log_error "缺少必需参数：--output_dir"
    exit 1
fi

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    log_error "未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查依赖
log_info "检查 Python 依赖..."
python3 -c "import librosa" 2>/dev/null || {
    log_warning "未找到 librosa，尝试安装..."
    pip3 install librosa soundfile tqdm numpy
}

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo ""
echo "========================================"
echo "  语音数据集预处理流程"
echo "========================================"
echo "  数据集：$DATASET"
echo "  输入：$DATA_DIR"
echo "  输出：$OUTPUT_DIR"
echo "  采样率：$SAMPLE_RATE Hz"
echo "  数据增强：$DO_AUGMENT"
echo "  数据集分割：$DO_SPLIT ($SPLIT_METHOD)"
echo "  并行线程：$N_JOBS"
echo "========================================"
echo ""

# Step 1: 数据预处理和特征提取
log_info "Step 1/3: 数据预处理和特征提取..."

case $DATASET in
    aishell)
        python3 "$SCRIPT_DIR/preprocess_aishell.py" \
            --data_dir "$DATA_DIR" \
            --output_dir "$OUTPUT_DIR/processed" \
            --sample_rate "$SAMPLE_RATE" \
            --splits train dev test
        ;;
    librispeech|common_voice|thchs30)
        python3 "$SCRIPT_DIR/preprocess_common.py" \
            --dataset "$DATASET" \
            --data_dir "$DATA_DIR" \
            --output_dir "$OUTPUT_DIR/processed" \
            --sample_rate "$SAMPLE_RATE" \
            --split train \
            --n_jobs "$N_JOBS"
        ;;
    *)
        log_error "不支持的数据集：$DATASET"
        exit 1
        ;;
esac

log_success "Step 1 完成"
echo ""

# Step 2: 数据增强（可选）
if [[ "$DO_AUGMENT" == true ]]; then
    log_info "Step 2/3: 数据增强..."
    
    python3 "$SCRIPT_DIR/data_augmentation.py" \
        --input_dir "$OUTPUT_DIR/processed/wav" \
        --output_dir "$OUTPUT_DIR/augmented" \
        --methods noise,gain,pitch \
        --n_copies 2
    
    log_success "Step 2 完成"
else
    log_info "Step 2/3: 跳过数据增强"
fi
echo ""

# Step 3: 数据集分割
if [[ "$DO_SPLIT" == true ]]; then
    log_info "Step 3/3: 数据集分割..."
    
    python3 "$SCRIPT_DIR/split_dataset.py" \
        --metadata "$OUTPUT_DIR/processed/metadata/train.json" \
        --output_dir "$OUTPUT_DIR/splits" \
        --method "$SPLIT_METHOD" \
        --train_ratio 0.8 \
        --dev_ratio 0.1 \
        --test_ratio 0.1
    
    log_success "Step 3 完成"
else
    log_info "Step 3/3: 跳过数据集分割"
fi
echo ""

# 生成处理报告
log_info "生成处理报告..."

cat > "$OUTPUT_DIR/processing_report.json" << EOF
{
    "dataset": "$DATASET",
    "input_dir": "$DATA_DIR",
    "output_dir": "$OUTPUT_DIR",
    "sample_rate": $SAMPLE_RATE,
    "augmentation_enabled": $DO_AUGMENT,
    "split_enabled": $DO_SPLIT,
    "split_method": "$SPLIT_METHOD",
    "processing_date": "$(date -Iseconds)",
    "output_structure": {
        "processed": "$OUTPUT_DIR/processed",
        "augmented": "$OUTPUT_DIR/augmented",
        "splits": "$OUTPUT_DIR/splits"
    }
}
EOF

echo ""
echo "========================================"
echo "  处理完成!"
echo "========================================"
echo ""
echo "输出结构:"
echo "  $OUTPUT_DIR/"
echo "  ├── processed/"
echo "  │   ├── wav/          (原始音频)"
echo "  │   ├── features/     (提取的特征)"
echo "  │   └── metadata/     (元数据)"
echo "  ├── augmented/        (增强数据，如启用)"
echo "  ├── splits/           (数据集划分)"
echo "  └── processing_report.json"
echo ""
log_success "所有步骤完成!"
