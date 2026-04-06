#!/bin/bash
#
# 语音数据集处理统一 Pipeline
# ============================
# 一键执行 AISHELL 和其他数据集的完整预处理流程
#
# 创建者：Hulk 🟢
# 创建日期：2026-03-27
#
# 用法:
#   ./scripts/dataset_pipeline.sh check      # 检查环境和依赖
#   ./scripts/dataset_pipeline.sh aishell    # 处理 AISHELL-1
#   ./scripts/dataset_pipeline.sh elderly    # 处理老年语音数据集
#   ./scripts/dataset_pipeline.sh all        # 处理所有数据集
#   ./scripts/dataset_pipeline.sh features   # 仅提取特征
#   ./scripts/dataset_pipeline.sh validate   # 验证处理结果
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON="${PYTHON:-python3}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

# 检查 Python 依赖
check_dependencies() {
    log_info "检查 Python 依赖..."
    
    local missing=()
    
    for pkg in librosa numpy pandas soundfile tqdm; do
        if ! $PYTHON -c "import $pkg" 2>/dev/null; then
            missing+=("$pkg")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_warning "缺少依赖：${missing[*]}"
        log_info "安装命令：pip install ${missing[*]}"
        return 1
    fi
    
    log_success "所有依赖已安装"
    return 0
}

# 检查磁盘空间
check_disk_space() {
    log_info "检查磁盘空间..."
    
    local available=$(df -BG "$WORKSPACE_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')
    
    if [ "$available" -lt 20 ]; then
        log_warning "可用空间不足 20GB (${available}GB)"
        return 1
    fi
    
    log_success "可用空间：${available}GB"
    return 0
}

# 处理 AISHELL-1
process_aishell() {
    log_info "处理 AISHELL-1 数据集..."
    
    # 检查数据是否存在
    if [ ! -d "$WORKSPACE_DIR/data_aishell/wav" ]; then
        log_error "未找到 AISHELL 数据：$WORKSPACE_DIR/data_aishell/wav"
        return 1
    fi
    
    # 运行预处理
    $PYTHON "$SCRIPT_DIR/process_aishell.py" --all \
        --data-dir "$WORKSPACE_DIR/data_aishell" \
        --output-dir "$WORKSPACE_DIR/data/processed" \
        --sample-rate 16000 \
        --feature-limit 1000
    
    log_success "AISHELL-1 处理完成"
    
    # 显示结果
    echo ""
    log_info "输出目录结构:"
    ls -lh "$WORKSPACE_DIR/data/processed/" | head -15
}

# 处理老年语音数据集
process_elderly() {
    log_info "处理老年语音数据集..."
    
    $PYTHON "$SCRIPT_DIR/download_elderly_datasets.py" --list
    
    echo ""
    log_info "选择要下载的数据集:"
    echo "  ./scripts/dataset_pipeline.sh elderly-commonvoice  # Common Voice"
    echo "  ./scripts/dataset_pipeline.sh elderly-voxceleb     # VoxCeleb"
    echo "  ./scripts/dataset_pipeline.sh elderly-casia        # CASIA (需申请)"
}

process_elderly_commonvoice() {
    log_info "下载 Common Voice 数据集..."
    $PYTHON "$SCRIPT_DIR/download_elderly_datasets.py" --dataset common_voice --language zh-CN
}

process_elderly_voxceleb() {
    log_info "下载 VoxCeleb 数据集..."
    $PYTHON "$SCRIPT_DIR/download_elderly_datasets.py" --dataset voxceleb
}

process_elderly_casia() {
    log_info "CASIA 老年语音数据集..."
    $PYTHON "$SCRIPT_DIR/download_elderly_datasets.py" --dataset casia
}

# 提取特征
extract_features() {
    log_info "提取音频特征..."
    
    $PYTHON "$SCRIPT_DIR/extract_features.py" \
        --dir "$WORKSPACE_DIR/data/processed/audio" \
        --output "$WORKSPACE_DIR/data/processed/features" \
        --sample-rate 16000
    
    log_success "特征提取完成"
}

# 验证处理结果
validate_results() {
    log_info "验证处理结果..."
    
    $PYTHON "$SCRIPT_DIR/validate_dataset.py" "$WORKSPACE_DIR/data/processed"
    
    log_success "验证完成"
}

# 显示使用帮助
show_help() {
    cat << EOF
语音数据集处理 Pipeline
=======================

用法: $0 <command>

命令:
  check         检查环境和依赖
  aishell       处理 AISHELL-1 数据集
  elderly       老年语音数据集选项
  elderly-commonvoice   下载 Common Voice
  elderly-voxceleb      下载 VoxCeleb
  elderly-casia         CASIA 数据集说明
  all           处理所有数据集
  features      提取音频特征
  validate      验证处理结果
  help          显示此帮助

示例:
  $0 check           # 检查环境
  $0 aishell         # 处理 AISHELL
  $0 all             # 处理所有数据集

输出目录:
  $WORKSPACE_DIR/data/processed/

依赖安装:
  pip install librosa numpy pandas soundfile tqdm matplotlib

EOF
}

# 主入口
main() {
    case "${1:-help}" in
        check)
            check_dependencies
            check_disk_space
            ;;
        aishell)
            check_dependencies || exit 1
            process_aishell
            ;;
        elderly)
            process_elderly
            ;;
        elderly-commonvoice)
            process_elderly_commonvoice
            ;;
        elderly-voxceleb)
            process_elderly_voxceleb
            ;;
        elderly-casia)
            process_elderly_casia
            ;;
        features)
            extract_features
            ;;
        validate)
            validate_results
            ;;
        all)
            log_info "处理所有数据集..."
            check_dependencies || exit 1
            check_disk_space || exit 1
            process_aishell
            echo ""
            process_elderly
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令：$1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
