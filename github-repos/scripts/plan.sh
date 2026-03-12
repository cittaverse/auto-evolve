#!/bin/bash
# plan.sh - GEO 迭代阶段 2: 规划

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../iteration_logs"

echo "📋 Starting Plan Phase..."

# 读取最新研究报告
LATEST_RESEARCH=$(ls -t "$LOG_DIR"/research_*.json 2>/dev/null | head -1)

if [ -z "$LATEST_RESEARCH" ]; then
  echo "❌ No research report found. Run research.sh first."
  exit 1
fi

echo "  → Reading research report: $LATEST_RESEARCH"

# 生成迭代计划
cat > "$LOG_DIR/plan_$(date +%Y%m%d_%H%M%S).yaml" << EOF
# GEO Iteration Plan
# Generated: $(date -Iseconds)

iteration: $(ls iteration_logs/plan_*.yaml 2>/dev/null | wc -l | xargs -I {} expr {} + 1)
target_repository: pipeline

actions:
  - file: examples/advanced.py
    type: create
    priority: P0
    description: "Add advanced usage examples"
  
  - file: README.md
    type: update
    section: "Installation"
    priority: P1
    description: "Add pip install instructions"

success_criteria:
  - files_created: 1
  - files_updated: 1
  - ci_passed: true
  - no_lint_errors: true

estimated_duration_minutes: 15
EOF

echo "  → Plan generated"
echo "✅ Plan Phase complete"
