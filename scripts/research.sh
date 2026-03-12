#!/bin/bash
# GEO 研究阶段脚本 v2.0 - 差异化迭代
# 目标：根据迭代次数生成不同的研究重点

WORKSPACE="/workspace"
OUTPUT="$WORKSPACE/research-notes.md"
ITERATION=${1:-1}

echo "正在扫描竞品仓库 (Iteration #$ITERATION)..."
echo ""

# 根据迭代次数生成差异化研究内容
if [ "$ITERATION" -eq 1 ]; then
    # 第一轮：基础 Demo + 中文资源
    cat > "$OUTPUT" << 'EOF'
# GEO 研究笔记 - Iteration #1

**日期**: 2026-03-09  
**重点**: 基础能力展示 + 中文资源占位

## 核心发现
- Pipeline 缺少可运行 demo
- Awesome 中文资源不足 30%
- Core 投资者文档缺数据支撑

## 本轮任务
1. Pipeline: 创建 demo_pipeline.py
2. Awesome: +5 中文资源
3. Core: FAQ 数据附录
EOF

elif [ "$ITERATION" -eq 2 ]; then
    # 第二轮：测试 + CI + 国际资源
    cat > "$OUTPUT" << 'EOF'
# GEO 研究笔记 - Iteration #2

**日期**: 2026-03-09  
**重点**: 代码质量 + 国际学术资源

## 核心发现
- Pipeline 缺少单元测试覆盖
- CI/CD 流程未配置
- Awesome 缺少顶级期刊资源 (NEJM/Lancet 等)

## 本轮任务
1. Pipeline: 添加 tests/test_assessor.py + CI 配置
2. Awesome: +5 国际学术资源 (PMC/NEJM/Nature)
3. Core: 添加市场趋势分析文档
EOF

elif [ "$ITERATION" -eq 3 ]; then
    # 第三轮：SEO 优化 + GitHub Pages + 外部链接
    cat > "$OUTPUT" << 'EOF'
# GEO 研究笔记 - Iteration #3

**日期**: 2026-03-09  
**重点**: SEO 优化 + GitHub Pages + 外部链接建设

## 核心发现

### SEO 审计
- Pipeline README 缺少 GEO 关键词 (generative engine optimization)
- Awesome README 缺少 schema.org 结构化数据
- Core 仓库无 GitHub Pages 部署

### 外部链接缺口
- 缺少 Google Scholar 引用链接
- 缺少 PubMed DOI 直达链接
- 缺少临床试验注册链接

### 竞品对标
- LLM-MCI-detection: 有 GitHub Pages 文档站
- awesome-mental-health: 有 schema.org 标记
- 我们的机会：更快部署 + 更完整 SEO

## 本轮任务
1. Pipeline: README SEO 关键词优化 + 结构化数据
2. Awesome: 添加 Google Scholar/PubMed 外部引用
3. Core: GitHub Pages 部署配置 (Jekyll)
EOF

elif [ "$ITERATION" -eq 4 ]; then
    # 第四轮：社区建设 + 外部引流 + 效果展示
    cat > "$OUTPUT" << 'EOF'
# GEO 研究笔记 - Iteration #4

**日期**: 2026-03-10  
**重点**: 社区建设 + 外部引流 + 效果可视化

## 核心发现

### 社区建设缺口
- 缺少贡献者引导文档 (CONTRIBUTING.md 不够详细)
- 无使用案例/用户见证
- 缺少讨论渠道 (Discussions/Issues 模板)

### 外部引流缺口
- 无技术文章发布（知乎/公众号/掘金）
- 未提交到导航站（producthunt/独立索引）
- 缺少社交媒体宣传

### 效果展示缺口
- 增长数据未可视化
- 无 Before/After 对比
- 缺少仪表板

## 本轮任务
1. Pipeline: 添加 USAGE.md 使用指南 + 效果对比示例
2. Awesome: 创建 CONTRIBUTING_EXAMPLES.md + Issue 模板
3. Core: 添加 traction.md 增长数据仪表板
4. 外部引流：撰写第一篇技术文章大纲
EOF

elif [ "$ITERATION" -eq 5 ]; then
    # 第五轮：外部引流 + 导航站提交 + 技术文章发布
    cat > "$OUTPUT" << 'EOF'
# GEO 研究笔记 - Iteration #5

**日期**: 2026-03-11  
**重点**: 外部引流 + 导航站提交 + 技术文章发布

## 核心发现

### 外部引流缺口
- 技术文章未发布（知乎/公众号/掘金）
- 未提交到产品导航站
- 缺少社交媒体曝光

### 导航站机会
| 导航站 | DA | 提交难度 | 预期效果 |
|--------|-----|----------|----------|
| Product Hunt | 90+ | 中 | 高曝光 |
| GitHub Topics | 90+ | 低 | SEO 提升 |
| 独立开源导航 | 50+ | 低 | 中文流量 |
| AI 工具导航 | 60+ | 低 | 精准用户 |

### 技术文章发布计划
- 知乎：《我让 AI Agent 自己进化了 4 轮》
- 公众号：同步发布
- 掘金：技术社区推广
- Medium：英文版本
- Hacker News：国际影响力

## 本轮任务
1. 提交到 GitHub Topics（github/awesome, artificial-intelligence）
2. 提交到 2-3 个中文导航站
3. 发布技术文章（知乎首发）
4. 社交媒体推广（朋友圈/微信群/Twitter）
5. 收集早期反馈
EOF
    # 通用模板
    cat > "$OUTPUT" << EOF
# GEO 研究笔记 - Iteration #$ITERATION

**日期**: $(date -u +%Y-%m-%d)  
**重点**: 持续优化 + 新缺口发现

## 待分析维度
- [ ] 竞品仓库最新动态
- [ ] Google 索引状态检查
- [ ] 用户搜索关键词分析

## 任务生成
待规划阶段确定...
EOF
fi

echo "✅ 研究笔记已写入：$OUTPUT"
