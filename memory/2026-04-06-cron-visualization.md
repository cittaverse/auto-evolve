# 2026-04-06 Cron: 论文数据可视化

**Cron Job ID**: 5ce51121-6c22-4c64-88b8-2b6a040b08fb  
**Agent**: Hulk 🟢  
**Time**: 2026-04-06 02:10 UTC  
**Task**: 为论文生成数据可视化图表：性能对比、消融实验、误差分析

---

## 执行摘要

本次 Cron 任务完成了**9 个可视化图表**的生成和状态确认：
- **6 个基于实测数据** (V4 验证等级): ASR v11 + Robustness 30 测试
- **3 个基于实验设计** (V3 验证等级): methods-evaluation.md 预期值

---

## 已生成图表 (9 个)

### Fig 1-6: 实测数据图表 (V4)

| Figure | 文件名 | 说明 | 数据源 |
|--------|--------|------|--------|
| Fig 1 | `fig1_asr_performance.svg` | ASR 性能分布 (直方图 + 饼图) | ASR v11 (40 样本) |
| Fig 2 | `fig2_error_analysis.svg` | 错误类型分析 (条形图) | ASR v11 (7 错误样本) |
| Fig 3 | `fig3_ablation_noise.svg` | 噪声类型消融 (柱状图) | Robustness (30 测试) |
| Fig 4 | `fig4_lref_stages.svg` | LREF 阶段分布 (柱状图) | Robustness (30 测试) |
| Fig 5 | `fig5_robustness_boxplot.svg` | 鲁棒性箱线图 | Robustness (3 类别) |
| Fig 6 | `fig6_dimension_radar.svg` | 六维度雷达图 | Robustness (30 测试) |

### Fig 7-9: 实验设计图表 (V3 — 预期值)

| Figure | 文件名 | 说明 | 数据源 |
|--------|--------|------|--------|
| Fig 7 | `fig7_component_ablation.svg` | 组件消融 (柱状图) | methods-evaluation.md §3.3.6 |
| Fig 8 | `fig8_prompt_ablation.svg` | Prompt 消融 (双柱图) | methods-evaluation.md §3.3.7 |
| Fig 9 | `fig9_model_comparison.svg` | 模型对比 (散点图) | methods-evaluation.md §3.3.8 |

**输出目录**: `/Users/moondy/.openclaw/workspace-hulk/artifacts/visualizations/2026-04-06/`

---

## 关键数据

### ASR 基准测试 (v11, 2026-04-05)
- 样本数：40
- 平均 WER：1.30%
- 零错误样本：33 (82.5%)

### 鲁棒性测试 (2026-03-28)
- 总测试数：30
- ASR 噪声：8 (🟢 Low)
- 边界情况：12 (🟡 Medium)
- 对抗样本：10 (🔴 High)
- 总体评级：🟡 Medium (5 个关键问题待修复)

---

## 验证等级

| 等级 | 含义 | 本批图表 |
|------|------|---------|
| V3 | 静态复核 (实验设计预期值) | Fig 7-9 |
| V4 | 动态验证 (已实际运行) | Fig 1-6 |

**重要说明**: Fig 7-9 基于实验设计预期值，非实测数据。待 Pilot RCT 执行后需用真实数据替换。

---

## 缺失图表 (待实测数据)

以下图表需要实际实验数据，当前无法生成：
- System Architecture (可复用 03-27 版本)
- Confusion Matrix (待 L1b Benchmark 人工标注)
- Score Correlation (待人工标注 50+ 样本)
- Improvement Over Time (待 Pilot RCT 纵向数据)
- Feedback Adoption (待用户交互数据)
- Demographics Table (待招募完成)
- Reliability Table (待人工标注完成)

---

## 生成脚本

1. **Fig 1-6**: `pipeline/viz/generate_paper_figures_v2.py`
2. **Fig 7-9**: `pipeline/viz/generate_ablation_figures.py`

---

## 下一步

1. **立即**: 9 个图表可插入论文 Section 4 (Results) 初稿
2. **待 V 决策**: Pilot RCT 启动 → 用真实数据替换 Fig 7-9
3. **待 V 决策**: L1b Benchmark 人工标注 → 生成混淆矩阵/相关性图
4. **储备任务**: 为 9 个图表撰写 Figure Caption

---

## 状态报告

完整状态报告：`artifacts/visualizations/2026-04-06/VISUALIZATION_STATUS.md`

---

*Hulk 🟢 - Cron Run Complete*
