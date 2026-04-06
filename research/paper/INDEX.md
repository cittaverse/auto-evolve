# 学术论文产物清单索引 (Paper Deliverables Index)

**生成时间**: 2026-04-05 17:45 UTC  
**版本**: v1.7 (Run #22)  
**用途**: 方便 V 快速定位所有论文相关文件

---

## ⚠️ 逾期提醒 (当前：2026-04-05 17:45 UTC)

| 任务 | 原截止日期 | 逾期时间 | 状态 |
|------|------------|----------|------|
| **arXiv 提交** | 2026-03-31 | +5 天 | ⚠️ **已逾期** |
| **伦理审批提交** | 2026-04-01 | +4 天 | ⚠️ **已逾期** |

**建议**: 48 小时内完成，总耗时约 95 分钟
- LaTeX 编译 (30 分钟) + arXiv 提交 (20 分钟) + 伦理填写 (30 分钟) + 伦理提交 (15 分钟)

---

## 📦 核心产物 (按优先级排序)

### 1. arXiv 提交包 (最高优先级)

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `arxiv-submission-v1.1.tar.gz` | `research/arxiv-paper/` | 23KB | ✅ 就绪 | **直接上传 arXiv** |
| `paper.tex` | `research/arxiv-paper/` | 34KB | ✅ v1.1 | LaTeX 论文正文 (555 行) |
| `references.bib` | `research/arxiv-paper/` | 21KB | ✅ v2 | BibTeX 引用库 (72+ 条) |
| `cover-letter.md` | `research/arxiv-paper/` | 3.5KB | ✅ | 投稿封面信 |
| `arxiv-submission-checklist.md` | `research/arxiv-paper/` | 8.9KB | ✅ | 提交清单 |

**V 待办**: 
- 本地编译 PDF: `cd research/arxiv-paper && pdflatex paper.tex` (运行 3 次)
- 上传 arXiv: 使用 `arxiv-submission-v1.1.tar.gz`

---

### 2. 伦理审批材料 (最高优先级)

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `05-ethics-approval-package.md` | `research/paper/` | 17KB | ⚠️ 待填写 | **伦理委员会提交** |
| `recruitment-materials.md` | `research/paper/` | 11KB | ✅ | 招募海报/脚本/流程 |
| `09-experiment-design-comprehensive.md` | `research/paper/` | 36KB | ✅ | 综合实验设计方案 |

**V 待办**:
- 填写 4 个占位符：PI 姓名、职称、GCP 证书编号、联系方式
- 联系 PI 确认 + 机构盖章
- 提交伦理委员会

**占位符位置** (`05-ethics-approval-package.md`):
```
第 X 行：| 姓名 | [待填写] |
第 X 行：| 职称 | [待填写] |
第 X 行：| GCP 培训 | 是 (证书编号：[待填写]) |
第 X 行：| 联系方式 | [待填写] |
```

---

### 3. 实验设计系列 (高优先级)

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `15-experiment-design-v7-multimodal.md` | `research/paper/` | 19KB | ✅ **NEWEST** | **v7.0 2026-04-05 多模态融合版：整合语音 Biomarkers (Run #22)** |
| `14-experiment-design-v6-updated.md` | `research/paper/` | 25KB | ✅ | **v6.0 2026-04 更新：整合 EXP-001 + 抗堆砌机制 (Run #21)** |
| `12-experiment-design-arxiv-final.md` | `research/paper/` | 34KB | ✅ | **v5.0 arXiv Methods 终稿：整合 CONSORT/SPIRIT 指南 (Run #14)** |
| `11-experiment-design-refined.md` | `research/paper/` | 19KB | ✅ | **v4.0 精炼执行版：伦理审批 + 预注册 + 执行参考 (Run #13)** |
| `10-experiment-design-arxiv.md` | `research/paper/` | 20KB | ✅ | **arXiv 论文 Methods 章节素材** |
| `09-experiment-design-comprehensive.md` | `research/paper/` | 36KB | ✅ | **综合设计方案 (推荐审阅)** |
| `06-experiment-design-final.md` | `research/paper/` | 23KB | ✅ | 实验设计终稿 v3.0 |
| `07-experiment-timeline.md` | `research/paper/` | 9.1KB | ✅ | 53 周时间线 |
| `08-variable-control-checklist.md` | `research/paper/` | 11KB | ✅ | 变量控制执行清单 |
| `02-experiment-design-refined.md` | `research/paper/` | 27KB | ✅ | 实验设计完善版 v2.0 |
| `02-experiment-design.md` | `research/paper/` | 8.5KB | ✅ | 实验设计原版 v1.0 |
| `09-experiment-design-executive-summary.md` | `research/paper/` | 6.5KB | ✅ | 执行摘要 (快速阅读) |

**推荐审阅顺序**: 
- **arXiv 提交 (Section 3)**: `15-experiment-design-v7-multimodal.md` (v7.0 最新版，整合多模态融合 + 语音 Biomarkers)
- **单模态基线**: `14-experiment-design-v6-updated.md` (v6.0, 文本单模态最新版)
- **伦理审批/预注册**: `12-experiment-design-arxiv-final.md` (v5.0 终稿，整合 CONSORT/SPIRIT 指南)
- **综合方案审阅**: `09-experiment-design-comprehensive.md` (完整背景 + rationale)
- **快速概览**: `09-experiment-design-executive-summary.md` (6.5KB, 10 分钟阅读)

---

### 4. 数据分析框架

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `03-statistical-analysis-plan.md` | `research/paper/` | 11KB | ✅ | 统计分析计划 (SAP) |
| `04-reference-audit.md` | `research/paper/` | 8.8KB | ✅ | 引用审计报告 |
| `exp-001-analysis-code-framework.md` | `research/experiments/` | 28KB | ✅ **NEW** | **EXP-001 数据分析代码框架 (Run #18)** |
| `exp-001-analysis-report-template.md` | `research/experiments/` | 11KB | ✅ **NEW** | **EXP-001 分析报告模板 (Run #18)** |

---

### 4b. EXP-001 实验验证系列 (新增)

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `exp-001-annotation-protocol.md` | `research/experiments/` | 12KB | ✅ | **EXP-001 人工标注协议 (Run #17/GEO #99)** |
| `exp-001-sample-preparation-protocol.md` | `research/experiments/` | 5.8KB | ✅ **NEW** | **EXP-001 样本准备方案 (Run #18)** |
| `exp-001-analysis-code-framework.md` | `research/experiments/` | 28KB | ✅ **NEW** | **EXP-001 数据分析代码框架 (Run #18)** |
| `exp-001-analysis-report-template.md` | `research/experiments/` | 11KB | ✅ **NEW** | **EXP-001 分析报告模板 (Run #18)** |

**EXP-001 时间线**:
| 阶段 | 日期 | 状态 | 负责人 |
|------|------|------|--------|
| Phase 0 (样本准备) | 2026-04-03 | 🟡 今日 | 研究助理 |
| Phase 0 (标注员培训) | 2026-04-03 | 🟡 今日 | Core/研究协调员 |
| Phase 1 (正式标注) | 2026-04-04 至 04-08 | ⏳ 待启动 | 标注员 |
| Phase 2 (仲裁 + 金标准) | 2026-04-09 | ⏳ 待启动 | 仲裁员 |
| Phase 3 (自动评分) | 2026-04-09 | ⏳ 待启动 | Hulk/Core |
| Phase 4 (效度分析) | 2026-04-10 | ⏳ 待启动 | Hulk |
| Phase 5 (抗堆砌验证) | 2026-04-11 | ⏳ 待启动 | Hulk |
| Phase 6 (性能基准) | 2026-04-12 | ⏳ 待启动 | Hulk |
| **分析报告** | **2026-04-12** | ⏳ 待启动 | **Hulk** |

**核心假设**:
- H1: L1 LLM 仲裁层能显著提升边界案例的评分效度 (vs. L0 单独评分)
- H2: 抗 Reward Hacking 模块能有效识别并惩罚关键词堆砌样本
- H3: 验证强度控制器能在保持效度的前提下将 L1 触发率控制在 20% ± 5%
- H4: 多 Agent 融合评分与人工标注的相关系数 r > 0.75

**样本设计**: N = 200 条 (正常 140 + 边界 40 + 堆砌 20)

---

### 5. 文献综述

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `01-literature-review.md` | `research/paper/` | 21KB | ✅ | 独立文献综述 v1.1 |

---

### 6. 研究执行材料 (伦理批准后使用)

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `recruitment-materials.md` | `research/paper/` | 11KB | ✅ | 招募材料 (海报/脚本/流程/短信) |
| `benchmark-annotation-protocol.md` | `research/paper/` | 11KB | ✅ | Benchmark 标注方案 |
| `assessor-training-materials.md` | `research/paper/` | 13KB | ✅ | 评估者培训材料 |

---

### 7. Supplementary Materials (新增)

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `13-supplementary-materials.md` | `research/paper/` | 8KB | ✅ **NEW** | **v1.0: Prompt 模板 + 评估量表中文版 (Run #15)** |

**内容**:
- Appendix A: LLM Prompt 模板 (事件边界检测、六维评分、元记忆策略)
- Appendix B: 评估量表中文版 (SUS, NPS, 技术焦虑, 隐私关注)
- Appendix C: 代码仓库说明 (安装、使用、引用)

**用途**: arXiv 论文 Appendix 直接素材，伦理审批附件

---

### 8. V 待办事项

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `V-action-items.md` | `research/paper/` | 9.2KB | ✅ | **10 项待 V 执行任务清单** |

---

### 8. 方法论文档 (论文章节素材)

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `methods-overview.md` | `research/paper/` | 2.3KB | ✅ | 方法概述 |
| `methods-architecture.md` | `research/paper/` | 9.3KB | ✅ | 系统架构 |
| `methods-scoring.md` | `research/paper/` | 7.1KB | ✅ | 评分算法 |
| `methods-evaluation.md` | `research/paper/` | 4.7KB | ✅ | 评估方法 |
| `methods-implementation.md` | `research/paper/` | 5.7KB | ✅ | 实现细节 |

---

### 9. 状态看板

| 文件 | 路径 | 大小 | 状态 | 用途 |
|------|------|------|------|------|
| `00-paper-prep-status.md` | `research/paper/` | 20KB | ✅ | **总状态看板 (推荐阅读)** |
| `cron-55834c68-completion-report.md` | `research/paper/` | 4.0KB | ✅ | Cron 完成报告 |

---

## 📊 可视化图表

### visualizations/outputs/ (SVG 矢量图，11 个)

| 文件 | 类型 | 用途 |
|------|------|------|
| `figure1_system_architecture.svg` | 流程图 | 系统架构 |
| `figure2_confusion_matrix.svg` | 热力图 | 混淆矩阵 |
| `figure3_score_correlation.svg` | 散点图 | 评分相关性 |
| `figure4_feedback_adoption.svg` | 柱状图 | 反馈采纳率 |
| `figure5_radar_profile.svg` | 雷达图 | 六维评分剖面 |
| `figure6_improvement_over_time.svg` | 折线图 | 时间序列改进 |
| `figure7_ablation_components.svg` | 柱状图 | 组件消融 |
| `figure8_ablation_prompts.svg` | 分组柱状图 | 提示词消融 |
| `figure9_model_comparison.svg` | 柱状图 | 模型对比 |
| `table1_demographics.svg` | 表格 | 人口统计 |
| `table2_reliability.svg` | 表格 | 信度表 |

### output/figures/ (PNG 位图，7 个)

| 文件 | 类型 | 用途 |
|------|------|------|
| `figure1_performance_comparison.png` | 柱状图 | 性能对比 |
| `figure2_ablation_study.png` | 柱状图 | 消融实验 |
| `figure3_latency_tradeoff.png` | 散点图 | 延迟权衡 |
| `figure4_asr_error_analysis.png` | 热力图 | ASR 误差分析 |
| `figure5_weight_sensitivity.png` | 折线图 | 权重敏感性 |
| `figure6_narrative_robustness.png` | 箱线图 | 叙事鲁棒性 |
| `figure7_edge_cases.png` | 表格 | 边界案例 |

---

## 📝 论文正文版本历史

| 文件 | 版本 | 大小 | 日期 | 备注 |
|------|------|------|------|------|
| `paper-draft-v0.5.md` | v0.5 | 29KB | 2026-03-20 | 初始完整草稿 |
| `paper-draft-v1.0.md` | v1.0 | 30KB | 2026-03-20 | 第一次修订 |
| `paper-draft-v1.1.md` | v1.1 | 42KB | 2026-03-26 | **当前最新版 (v0.6 内容)** |
| `paper-v1.0.tex` | v1.0 | 34KB | 2026-03-20 | LaTeX 旧版 |
| `paper.tex` | v1.1 | 34KB | 2026-03-28 | **LaTeX 当前版 (已同步 v0.6)** |

---

## 📋 快速检查清单

### arXiv 提交前检查
- [ ] LaTeX 编译成功 (无错误)
- [ ] PDF 检查通过 (参考文献完整、图表位置正确)
- [ ] arXiv 账号登录 (cittaverse@gmail.com)
- [ ] 提交包准备 (`arxiv-submission-v1.1.tar.gz`)
- [ ] 元数据准备 (标题、作者、摘要、分类)

### 伦理审批提交前检查
- [ ] 填写所有 `[待填写]` 占位符
- [ ] PI 审阅确认
- [ ] 机构盖章
- [ ] 在线系统注册
- [ ] 材料上传 (研究方案、知情同意、招募材料、研究者资质)

---

## 🔗 文件路径速查

```bash
# 核心目录
PAPER_DIR=/home/node/.openclaw/workspace-hulk/research/paper
ARXIV_DIR=/home/node/.openclaw/workspace-hulk/research/arxiv-paper
VIZ_DIR=/home/node/.openclaw/workspace-hulk/research/paper/visualizations/outputs
FIGURES_DIR=/home/node/.openclaw/workspace-hulk/output/figures
MEMORY_DIR=/home/node/.openclaw/workspace-hulk/memory

# 关键文件
echo $PAPER_DIR/00-paper-prep-status.md        # 总状态看板
echo $PAPER_DIR/V-action-items.md              # V 待办事项
echo $PAPER_DIR/05-ethics-approval-package.md  # 伦理审批包
echo $PAPER_DIR/09-experiment-design-comprehensive.md  # 综合实验设计
echo $ARXIV_DIR/arxiv-submission-v1.1.tar.gz   # arXiv 提交包
echo $ARXIV_DIR/paper.tex                      # LaTeX 正文
echo $ARXIV_DIR/references.bib                 # 引用库
```

---

*Generated by Hulk 🟢 — Paper Prep Run #9 (2026-03-28 12:21 UTC)*
