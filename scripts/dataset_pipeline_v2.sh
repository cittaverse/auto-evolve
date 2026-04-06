#!/bin/bash
#
# 语音数据集预处理完整流程 v2
# 支持：AISHELL, LibriSpeech, Common Voice, THCHS-30, 老年语音
#
# Usage:
#   ./dataset_pipeline_v2.sh --dataset aishell --mode full
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

# 默认参数
DATASET="aishell"
MODE="full"  # full, lite, features-only, validate
SAMPLE_RATE=16000
N_JOBS=4
MAX_SAMPLES=""

# 打印帮助
print_help() {
    cat << EOF
语音数据集预处理流程 v2

用法:
  $0 --dataset <name> --mode <mode> [选项]

数据集:
  aishell         AISHELL-1 中文普通话数据集
  librispeech     LibriSpeech 英文数据集
  common_voice    Mozilla Common Voice
  thchs30         THCHS-30 中文数据集
  elderly         老年语音数据集

模式:
  full            完整流程 (清洗 + 分割 + 特征提取)
  lite            轻量模式 (1000 样本快速预览)
  features-only   仅特征提取
  validate        仅验证现有数据

选项:
  --sample_rate   采样率 (默认：16000)
  --n_jobs        并行线程数 (默认：4)
  --max_samples   最大样本数 (用于测试)
  --help          显示帮助

示例:
  # AISHELL 完整处理
  $0 --dataset aishell --mode full

  # 轻量预览
  $0 --dataset aishell --mode lite

  # 仅特征提取
  $0 --dataset aishell --mode features-only

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

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --dataset)
            DATASET="$2"
            shift 2
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        --sample_rate)
            SAMPLE_RATE="$2"
            shift 2
            ;;
        --n_jobs)
            N_JOBS="$2"
            shift 2
            ;;
        --max_samples)
            MAX_SAMPLES="--max_samples $2"
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

# 检查 Python 环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查必要依赖
    log_info "检查 Python 依赖..."
    python3 -c "import librosa, numpy, soundfile, tqdm" 2>/dev/null || {
        log_warning "部分依赖缺失，尝试安装..."
        pip3 install librosa numpy soundfile tqdm --quiet
    }
}

# 修复 AISHELL 标注
fix_aishell_transcript() {
    log_step "修复 AISHELL 标注文件..."
    python3 "$SCRIPT_DIR/fix_aishell_transcript.py" --data_dir "$WORKSPACE_DIR/data_aishell"
}

# 处理 AISHELL
process_aishell() {
    local data_dir="$WORKSPACE_DIR/data_aishell"
    local output_dir="$WORKSPACE_DIR/data/processed_aishell_v2"
    
    if [[ "$MODE" == "lite" ]]; then
        MAX_SAMPLES="--max_samples 1000"
        output_dir="$WORKSPACE_DIR/data/processed_aishell_lite"
    fi
    
    log_step "处理 AISHELL 数据集 (模式：$MODE)..."
    python3 "$SCRIPT_DIR/preprocess_aishell_v2.py" \
        --data_dir "$data_dir" \
        --output_dir "$output_dir" \
        --sample_rate "$SAMPLE_RATE" \
        $MAX_SAMPLES
}

# 处理其他数据集
process_other_dataset() {
    log_step "处理 $DATASET 数据集..."
    
    case $DATASET in
        librispeech)
            log_info "LibriSpeech 处理待实现"
            ;;
        common_voice)
            log_info "Common Voice 处理待实现"
            ;;
        thchs30)
            log_info "THCHS-30 处理待实现"
            ;;
        elderly)
            log_info "老年语音数据集处理待实现"
            ;;
        *)
            log_error "未知数据集：$DATASET"
            exit 1
            ;;
    esac
}

# 验证数据集
validate_dataset() {
    log_step "验证数据集..."
    python3 "$SCRIPT_DIR/validate_dataset.py" \
        --data_dir "$WORKSPACE_DIR/data/processed_aishell_v2"
}

# 生成质量报告
generate_quality_report() {
    log_step "生成质量报告..."
    
    local report_file="$WORKSPACE_DIR/data/processed_aishell_lite/quality_report.md"
    
    if [[ "$MODE" != "lite" ]]; then
        report_file="$WORKSPACE_DIR/data/processed_aishell_v2/quality_report.md"
    fi
    
    cat > "$report_file" << 'EOF'
# AISHELL 数据集质量报告

## 处理统计

- 总样本数：待更新
- 有效样本：待更新
- 总时长：待更新
- 说话人数：待更新

## 数据分布

### 时长分布
- 短 (<2s): 待更新
- 中 (2-5s): 待更新
- 长 (>5s): 待更新

### 训练/验证/测试分割
- Train: 80%
- Val: 10%
- Test: 10%

## 特征统计

### MFCC (13 维 + delta + delta-delta)
- 均值：待计算
- 标准差：待计算

### Log Mel Spectrogram (40 维)
- 频率范围：0-8000 Hz
- 帧移：10ms

## 质量检查

- [ ] 音频质量抽检
- [ ] 标注对齐验证
- [ ] 特征有效性验证

EOF
    
    log_success "质量报告：$report_file"
}

# 主流程
main() {
    echo -e "${CYAN}"
    echo "========================================"
    echo "  语音数据集预处理流程 v2"
    echo "========================================"
    echo -e "${NC}"
    
    log_info "数据集：$DATASET"
    log_info "模式：$MODE"
    log_info "采样率：$SAMPLE_RATE Hz"
    log_info "工作目录：$WORKSPACE_DIR"
    echo
    
    # 检查环境
    check_python
    
    # 根据数据集执行不同流程
    case $DATASET in
        aishell)
            # 修复标注
            fix_aishell_transcript
            
            # 处理数据
            process_aishell
            
            # 验证
            if [[ "$MODE" != "lite" ]]; then
                validate_dataset
            fi
            
            # 生成报告
            generate_quality_report
            ;;
        *)
            process_other_dataset
            ;;
    esac
    
    echo
    log_success "✅ 流程完成"
    echo
}

# 执行
main
