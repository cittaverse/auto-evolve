#!/bin/bash
# 数据集预处理快速执行脚本
# ========================================
# 用途：一键执行 AISHELL 及其他数据集的预处理流程
# 创建者：Hulk 🟢
# 创建日期：2026-03-25

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="/home/node/.openclaw/workspace-hulk"
PYTHON_SCRIPT="$SCRIPT_DIR/preprocess_datasets.py"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  数据集预处理工具 v1.0${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Python 环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误：未找到 python3${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Python 环境检查通过${NC}"
}

# 检查依赖
check_dependencies() {
    echo "检查 Python 依赖..."
    
    python3 -c "import librosa" 2>/dev/null && echo -e "${GREEN}✓ librosa 已安装${NC}" || {
        echo -e "${YELLOW}! librosa 未安装，特征提取功能将不可用${NC}"
        echo "  安装：pip install librosa numpy pandas soundfile tqdm"
    }
    
    python3 -c "import numpy" 2>/dev/null && echo -e "${GREEN}✓ numpy 已安装${NC}" || echo -e "${RED}✗ numpy 未安装${NC}"
    python3 -c "import pandas" 2>/dev/null && echo -e "${GREEN}✓ pandas 已安装${NC}" || echo -e "${YELLOW}! pandas 未安装${NC}"
    python3 -c "import soundfile" 2>/dev/null && echo -e "${GREEN}✓ soundfile 已安装${NC}" || echo -e "${YELLOW}! soundfile 未安装${NC}"
    python3 -c "import tqdm" 2>/dev/null && echo -e "${GREEN}✓ tqdm 已安装${NC}" || echo -e "${YELLOW}! tqdm 未安装${NC}"
    
    echo ""
}

# 检查数据
check_data() {
    echo "检查数据集..."
    
    if [ -d "$WORKSPACE/data_aishell" ]; then
        WAV_COUNT=$(find "$WORKSPACE/data_aishell/wav" -name "*.tar.gz" 2>/dev/null | wc -l)
        echo -e "${GREEN}✓ AISHELL 数据已找到 ($WAV_COUNT 个压缩文件)${NC}"
    else
        echo -e "${YELLOW}! AISHELL 数据目录不存在${NC}"
        echo "  请先运行：scripts/download_elderly_voice_datasets.sh"
    fi
    
    if [ -f "$WORKSPACE/data_aishell/transcript/aishell_transcript_v0.8.txt" ]; then
        echo -e "${GREEN}✓ AISHELL 标注文件已找到${NC}"
    else
        echo -e "${YELLOW}! AISHELL 标注文件未找到${NC}"
    fi
    
    echo ""
}

# 安装依赖
install_dependencies() {
    echo -e "${BLUE}正在安装 Python 依赖...${NC}"
    pip3 install librosa numpy pandas soundfile tqdm --quiet
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
    echo ""
}

# 执行预处理
run_preprocessing() {
    local dataset=${1:-aishell}
    local output_dir=${2:-"$WORKSPACE/data/processed"}
    
    echo -e "${BLUE}开始处理数据集：$dataset${NC}"
    echo -e "输出目录：$output_dir"
    echo ""
    
    python3 "$PYTHON_SCRIPT" \
        --dataset "$dataset" \
        --output-dir "$output_dir" \
        --sample-rate 16000 \
        --test-split 0.1 \
        --val-split 0.1 \
        --extract-features
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  预处理完成 ✓${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# 显示帮助
show_help() {
    echo "用法：$0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  check       检查环境和数据"
    echo "  install     安装 Python 依赖"
    echo "  run         执行预处理 (默认：aishell)"
    echo "  all         执行完整流程 (check + install + run)"
    echo "  help        显示此帮助信息"
    echo ""
    echo "选项:"
    echo "  --dataset   数据集名称 (aishell, common_voice, elderly_voice)"
    echo "  --output    输出目录 (默认：$WORKSPACE/data/processed)"
    echo ""
    echo "示例:"
    echo "  $0 all"
    echo "  $0 run --dataset aishell --output /path/to/output"
    echo "  $0 check"
    echo ""
}

# 主流程
main() {
    local command=${1:-help}
    shift || true
    
    case $command in
        check)
            check_python
            check_dependencies
            check_data
            ;;
        install)
            install_dependencies
            ;;
        run)
            run_preprocessing "$@"
            ;;
        all)
            check_python
            check_dependencies
            check_data
            install_dependencies
            run_preprocessing "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}未知命令：$command${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
