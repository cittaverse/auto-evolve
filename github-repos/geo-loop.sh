#!/bin/bash
# geo-loop.sh - GEO 自主迭代主循环
# Inspired by Karpathy's auto-research

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/iteration_logs"
MAX_ITERATIONS_PER_DAY=${MAX_ITERATIONS:-4}

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
  echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
  echo -e "${GREEN}✓${NC} $1"
}

warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

error() {
  echo -e "${RED}✗${NC} $1"
}

# 主函数
main() {
  local iteration=${1:-1}
  
  log "🚀 Starting GEO iteration #$iteration"
  log "📁 Working directory: $SCRIPT_DIR"
  
  # 创建日志目录
  mkdir -p "$LOG_DIR"
  
  # 记录开始时间
  START_TIME=$(date +%s)
  
  # Phase 1: Research (5 min)
  log ""
  log "📚 Phase 1: Research (5 min)"
  if bash "$SCRIPT_DIR/scripts/research.sh"; then
    success "Research complete"
  else
    error "Research failed"
    exit 1
  fi
  
  # Phase 2: Plan (5 min)
  log ""
  log "📋 Phase 2: Plan (5 min)"
  if bash "$SCRIPT_DIR/scripts/plan.sh"; then
    success "Plan complete"
  else
    error "Plan failed"
    exit 1
  fi
  
  # Phase 3: Execute (15 min)
  log ""
  log "⚙️ Phase 3: Execute (15 min)"
  if bash "$SCRIPT_DIR/scripts/execute.sh"; then
    success "Execute complete"
  else
    error "Execute failed"
    exit 1
  fi
  
  # Phase 4: Verify (3 min)
  log ""
  log "✅ Phase 4: Verify (3 min)"
  if bash "$SCRIPT_DIR/scripts/verify.sh"; then
    success "Verify complete"
  else
    error "Verify failed"
    exit 1
  fi
  
  # Phase 5: Learn (2 min)
  log ""
  log "🧠 Phase 5: Learn (2 min)"
  if bash "$SCRIPT_DIR/scripts/learn.sh"; then
    success "Learn complete"
  else
    error "Learn failed"
    exit 1
  fi
  
  # 计算耗时
  END_TIME=$(date +%s)
  DURATION=$((END_TIME - START_TIME))
  
  log ""
  log "================================"
  success "✅ Iteration #$iteration complete"
  log "   Duration: ${DURATION}s (~$((DURATION/60)) min)"
  log "   Logs: $LOG_DIR/"
  log "================================"
  
  # 生成迭代摘要
  cat > "$LOG_DIR/iteration_${iteration}_summary.json" << EOF
{
  "iteration": $iteration,
  "timestamp": "$(date -Iseconds)",
  "duration_seconds": $DURATION,
  "status": "success",
  "phases_completed": 5
}
EOF
}

# 显示帮助
show_help() {
  cat << EOF
GEO 自主迭代循环

用法：$0 [迭代次数]

参数:
  迭代次数    迭代编号 (默认：1)

示例:
  $0          # 第 1 轮迭代
  $0 5        # 第 5 轮迭代

环境变量:
  MAX_ITERATIONS    每日最大迭代次数 (默认：4)
  GITHUB_TOKEN      GitHub API token
  SERPER_API_KEY    Serper API key

EOF
}

# 入口
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  show_help
else
  main "$@"
fi
