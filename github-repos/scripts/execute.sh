#!/bin/bash
# execute.sh - GEO 迭代阶段 3: 执行

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_DIR="$SCRIPT_DIR/.."

echo "⚙️ Starting Execute Phase..."

# 读取最新计划
LATEST_PLAN=$(ls -t "$SCRIPT_DIR/../iteration_logs/plan_*.yaml" | head -1)

if [ -z "$LATEST_PLAN" ]; then
  echo "❌ No plan found. Run research.sh first."
  exit 1
fi

echo "  → Reading plan: $LATEST_PLAN"

# 解析目标仓库
TARGET_REPO=$(grep "target_repository:" "$LATEST_PLAN" | awk '{print $2}')
if [ -z "$TARGET_REPO" ]; then
  TARGET_REPO="pipeline"
fi
echo "  → Target repository: $TARGET_REPO"

# 切换到目标仓库目录
cd "$REPOS_DIR/$TARGET_REPO"
echo "  → Working directory: $(pwd)"

# 执行文件创建 (示例)
echo "  → Creating files..."

# 确保 examples 目录存在
mkdir -p examples

# 示例：创建高级用法示例
cat > examples/advanced.py << 'PYEOF'
"""
Advanced Usage Examples for CittaVerse Pipeline

This module demonstrates advanced usage patterns:
- Batch assessment
- Custom scoring weights
- Report generation
"""

from src.assessor import NarrativeAssessor
from src.report import ReportGenerator

def main():
    # Initialize assessor
    assessor = NarrativeAssessor(model="qwen-plus", language="zh-CN")
    
    # Batch assessment
    texts = [
        "那是我年轻时候的事情了...",
        "记得 1978 年，我在纺织厂工作...",
    ]
    
    results = assessor.batch_assess(texts, output_file="results.json")
    
    # Generate group report
    generator = ReportGenerator()
    report = generator.generate_group_report(results, output_file="group_report.json")
    
    print(f"Assessed {len(results)} texts")
    print(f"Average score: {sum(r.overall_score for r in results) / len(results):.1f}")

if __name__ == "__main__":
    main()
PYEOF

echo "    + examples/advanced.py"

# 质量检查
echo "  → Running quality checks..."

# Lint
if command -v flake8 &> /dev/null; then
  flake8 examples/advanced.py --max-line-length=100 || echo "⚠️ Lint warnings found"
fi

# 提交
echo "  → Committing changes..."
git add -A
git commit -m "GEO iteration: Add advanced usage examples" || echo "⚠️ No changes to commit"

echo "✅ Execute Phase complete"
