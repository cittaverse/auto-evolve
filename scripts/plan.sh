#!/bin/bash
# GEO 规划阶段脚本 v2.0 - 差异化迭代
# 目标：根据迭代次数生成不同的执行计划

WORKSPACE="/workspace"
OUTPUT="$WORKSPACE/plan.md"
ITERATION=${1:-1}

echo "正在生成执行计划 (Iteration #$ITERATION)..."
echo ""

# 根据迭代次数生成差异化计划
if [ "$ITERATION" -eq 2 ]; then
    cat > "$OUTPUT" << 'EOF'
# GEO 执行计划 - Iteration #2

**日期**: 2026-03-09  
**时间预算**: 15 分钟  
**重点**: 代码质量 + 国际学术资源

---

## 本轮任务清单

### 任务 1: Pipeline - 单元测试 + CI
**文件**: `tests/test_assessor.py` + `.github/workflows/ci.yml`  
**内容**: 
- 事件提取测试 (3 个用例)
- 图论计分测试 (边界值/正常值)
- GitHub Actions CI 配置
**优先级**: 🔴 高  
**预计时间**: 8 分钟

### 任务 2: Awesome - 国际学术资源
**文件**: `README.md`  
**内容**: 添加 5 个顶级期刊/数据库
- New England Journal of Medicine (NEJM)
- PubMed Central 数字疗法专栏
- Nature Aging 认知研究
- The Lancet Healthy Longevity
- Cochrane Library 系统评价
**优先级**: 🟡 中  
**预计时间**: 4 分钟

### 任务 3: Core - 市场趋势分析
**文件**: `docs/market-trends.md`  
**内容**: 
- 全球数字疗法市场规模 (2024-2030)
- 中国老龄化趋势与支付意愿
- 竞品融资动态追踪
**优先级**: 🟡 中  
**预计时间**: 3 分钟

---

## 执行顺序

1. ✅ 任务 1 (Pipeline 测试+CI) - 代码质量基础设施
2. ✅ 任务 2 (Awesome 国际资源) - 学术可信度
3. ⏸️ 任务 3 (Core 市场趋势) - 如时间允许

---

## 成功标准

- [ ] 测试覆盖率 >80%
- [ ] CI 自动运行通过
- [ ] README 新增 5 个权威链接
- [ ] 市场趋势文档 >2000 字

---

*规划完成。下一步：执行阶段*
EOF

elif [ "$ITERATION" -eq 3 ]; then
    cat > "$OUTPUT" << 'EOF'
# GEO 执行计划 - Iteration #3

**日期**: 2026-03-09  
**时间预算**: 15 分钟  
**重点**: SEO 优化 + GitHub Pages + 外部链接建设

---

## 本轮任务清单

### 任务 1: Pipeline - README SEO 优化 + 结构化数据
**文件**: `README.md`  
**内容**: 
- 标题优化：包含"GEO"、"neuro-symbolic"、"cognitive assessment"
- 关键词密度：GEO (3-5 次)、神经符号 (2-3 次)、认知评估 (2-3 次)
- 添加 schema.org JSON-LD 结构化数据
- 优化 meta description (150-160 字符)
**优先级**: 🔴 高  
**预计时间**: 6 分钟

### 任务 2: Awesome - 外部权威引用
**文件**: `README.md`  
**内容**: 
- 所有论文添加 Google Scholar 引用数链接
- 所有医学论文添加 PubMed DOI 直达链接
- 添加 ClinicalTrials.gov 临床试验注册链接
**优先级**: 🟡 中  
**预计时间**: 5 分钟

### 任务 3: Core - GitHub Pages 部署
**文件**: `.github/workflows/pages.yml` + `_config.yml`  
**内容**: 
- Jekyll 静态站点配置
- GitHub Pages 自动部署工作流
- 基础布局模板
**优先级**: 🟡 中  
**预计时间**: 4 分钟

---

## 执行顺序

1. ✅ 任务 1 (Pipeline SEO) - 搜索引擎可见度
2. ✅ 任务 2 (Awesome 外部引用) - 学术权威性
3. ⏸️ 任务 3 (Core Pages) - 如时间允许

---

## 成功标准

- [ ] README 关键词密度达标
- [ ] schema.org 结构化数据验证通过
- [ ] 外部引用链接 >10 个
- [ ] GitHub Pages 可访问

---

*规划完成。下一步：执行阶段*
EOF

elif [ "$ITERATION" -eq 4 ]; then
    cat > "$OUTPUT" << 'EOF'
# GEO 执行计划 - Iteration #4

**日期**: 2026-03-10  
**时间预算**: 15 分钟  
**重点**: 社区建设 + 效果展示 + 外部引流准备

---

## 本轮任务清单

### 任务 1: Pipeline - 使用指南 + 效果对比
**文件**: `USAGE.md` + `examples/before-after.md`  
**内容**: 
- 详细使用指南（5 分钟快速上手）
- 效果对比示例（Before/After 数据）
- 常见问题 FAQ
**优先级**: 🔴 高  
**预计时间**: 8 分钟

### 任务 2: Awesome - 贡献者引导
**文件**: `CONTRIBUTING_EXAMPLES.md` + `.github/ISSUE_TEMPLATE/`  
**内容**: 
- 贡献示例（3 个典型场景）
- Issue 模板（功能请求/资源添加/Bug 报告）
- 贡献者行为准则补充
**优先级**: 🟡 中  
**预计时间**: 4 分钟

### 任务 3: Core - 增长数据仪表板
**文件**: `docs/traction.md`  
**内容**: 
- Stars/Views 增长图表
- Google 索引变化追踪
- 用户/机构采用案例
**优先级**: 🟡 中  
**预计时间**: 3 分钟

---

## 执行顺序

1. ✅ 任务 1 (Pipeline 使用指南) - 降低使用门槛
2. ✅ 任务 2 (Awesome 贡献引导) - 社区建设基础
3. ⏸️ 任务 3 (Core 数据仪表板) - 如时间允许

---

## 成功标准

- [ ] USAGE.md 包含完整上手流程
- [ ] 效果对比有真实数据支撑
- [ ] Issue 模板可用
- [ ] traction.md 有基线数据

---

*规划完成。下一步：执行阶段*
EOF

elif [ "$ITERATION" -eq 5 ]; then
    cat > "$OUTPUT" << 'EOF'
# GEO 执行计划 - Iteration #5

**日期**: 2026-03-11  
**时间预算**: 15 分钟  
**重点**: 外部引流 + 导航站提交 + 技术文章发布

---

## 本轮任务清单

### 任务 1: GitHub Topics 提交
**文件**: 仓库设置  
**内容**: 
- 添加 topics: github-seo, ai-agent, automation
- 添加 website 链接
- 完善 repository description
**优先级**: 🔴 高  
**预计时间**: 5 分钟

### 任务 2: 导航站提交
**目标**: 2-3 个中文导航站  
**内容**: 
- 提交到"独立开源导航"
- 提交到"AI 工具导航"
- 记录提交链接
**优先级**: 🟡 中  
**预计时间**: 5 分钟

### 任务 3: 技术文章发布准备
**文件**: `docs/articles/`  
**内容**: 
- 确认文章已撰写完成
- 准备社交媒体文案
- 准备发布检查清单
**优先级**: 🟡 中  
**预计时间**: 5 分钟

---

## 执行顺序

1. ✅ 任务 1 (GitHub Topics) - SEO 基础建设
2. ✅ 任务 2 (导航站提交) - 外部引流
3. ✅ 任务 3 (文章发布准备) - 为发布做准备

---

## 成功标准

- [ ] Topics 添加完成
- [ ] 导航站提交 ≥2 个
- [ ] 文章发布包完整

---

*规划完成。下一步：执行阶段*
EOF
    # 通用模板
    cat > "$OUTPUT" << EOF
# GEO 执行计划 - Iteration #$ITERATION

**日期**: $(date -u +%Y-%m-%d)  
**时间预算**: 15 分钟

---

## 本轮任务

待研究阶段输出后动态生成...

---

*规划完成。下一步：执行阶段*
EOF
fi

echo "✅ 执行计划已写入：$OUTPUT"
