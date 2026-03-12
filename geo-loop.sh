#!/bin/bash
# GEO 自主迭代主循环 v2.0 - 差异化迭代
# 用法：./geo-loop.sh [iteration_number]

set -e

WORKSPACE="/workspace"
SCRIPTS="$WORKSPACE/scripts"
MEMORY="$WORKSPACE/memory"
ITERATION=${1:-1}

echo "🟢 GEO Iteration #$ITERATION 启动"
echo "================================"
echo "工作目录：$WORKSPACE"
echo "时间：$(date -u +%Y-%m-%d_%H:%M)"
echo ""

# 阶段 1: 研究 (5min)
echo "📚 阶段 1/5: 研究"
echo "----------------"
if [ -x "$SCRIPTS/research.sh" ]; then
    bash "$SCRIPTS/research.sh" "$ITERATION"
else
    echo "[SKIP] research.sh 不存在"
fi
echo ""

# 阶段 2: 规划 (5min)
echo "📋 阶段 2/5: 规划"
echo "----------------"
if [ -x "$SCRIPTS/plan.sh" ]; then
    bash "$SCRIPTS/plan.sh" "$ITERATION"
else
    echo "[SKIP] plan.sh 不存在"
fi
echo ""

# 阶段 3: 执行 (15min)
echo "⚡ 阶段 3/5: 执行"
echo "----------------"
if [ -x "$SCRIPTS/execute.sh" ]; then
    bash "$SCRIPTS/execute.sh" "$ITERATION"
else
    echo "[SKIP] execute.sh 不存在"
fi
echo ""

# 阶段 4: 验证 (3min)
echo "✅ 阶段 4/5: 验证"
echo "----------------"
if [ -x "$SCRIPTS/verify.sh" ]; then
    bash "$SCRIPTS/verify.sh"
else
    echo "[SKIP] verify.sh 不存在"
fi
echo ""

# 阶段 5: 学习 (2min)
echo "🧠 阶段 5/5: 学习"
echo "----------------"
if [ -x "$SCRIPTS/learn.sh" ]; then
    bash "$SCRIPTS/learn.sh" "$ITERATION"
else
    echo "[SKIP] learn.sh 不存在"
fi
echo ""

echo "================================"
echo "🟢 GEO Iteration #$ITERATION 完成"
echo "完成时间：$(date -u +%Y-%m-%d_%H:%M)"
