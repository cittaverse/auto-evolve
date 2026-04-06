# 论文数据可视化状态报告 | 2026-04-06

**Cron Job ID**: 5ce51121-6c22-4c64-88b8-2b6a040b08fb  
**执行时间**: 2026-04-06 02:10 UTC  
**状态**: ✅ 完成 (9 个图表生成 + 状态确认)  
**作者**: Hulk 🟢

---

## 执行摘要

本次 Cron 任务完成了论文所需的**9 个可视化图表**：
- **6 个基于实测数据** (ASR v11 + Robustness 30 测试，验证等级 V4)
- **3 个基于实验设计** (methods-evaluation.md 预期值，验证等级 V3)

---

## 已生成图表清单 (9 个)

### 实测数据图表 (V4 验证等级)

| Figure | 文件名 | 类型 | 数据源 | 验证等级 | 尺寸 |
|--------|--------|------|--------|---------|------|
| **Fig 1** | `fig1_asr_performance.svg` | ASR 性能分布 (直方图 + 饼图) | ASR v11 (40 样本) | V4 | 39K |
| **Fig 2** | `fig2_error_analysis.svg` | 错误类型分析 (条形图) | ASR v11 (7 错误样本) | V4 | 38K |
| **Fig 3** | `fig3_ablation_noise.svg` | 噪声类型消融 (柱状图) | Robustness (30 测试) | V4 | 75K |
| **Fig 4** | `fig4_lref_stages.svg` | LREF 阶段分布 (柱状图) | Robustness (30 测试) | V4 | 27K |
| **Fig 5** | `fig5_robustness_boxplot.svg` | 鲁棒性箱线图 | Robustness (3 类别) | V4 | 42K |
| **Fig 6** | `fig6_dimension_radar.svg` | 六维度雷达图 | Robustness (30 测试) | V4 | 55K |

### 实验设计图表 (V3 验证等级 — 预期值)

| Figure | 文件名 | 类型 | 数据源 | 验证等级 | 尺寸 |
|--------|--------|------|--------|---------|------|
| **Fig 7** | `fig7_component_ablation.svg` | 组件消融 (柱状图) | methods-evaluation.md | V3 | 41K |
| **Fig 8** | `fig8_prompt_ablation.svg` | Prompt 消融 (双柱图) | methods-evaluation.md | V3 | 49K |
| **Fig 9** | `fig9_model_comparison.svg` | 模型对比 (散点图) | methods-evaluation.md | V3 | 45K |

**输出目录**: `/Users/moondy/.openclaw/workspace-hulk/artifacts/visualizations/2026-04-06/`

---

## 数据源详情

### ASR 基准测试 (v11, 2026-04-05)

| 指标 | 数值 |
|------|------|
| 样本数 | 40 |
| 平均 WER | 1.30% |
| 平均 CER | 1.30% |
| 零错误样本 | 33 (82.5%) |
| 最佳样本 | 001 (WER=0%) |
| 最差样本 | 011 (WER=7.14%) |

### 鲁棒性测试 (2026-03-28)

| 类别 | 测试数 | 风险等级 | 关键发现 |
|------|--------|---------|---------|
| ASR 噪声 | 8 | 🟢 Low | 同音字/漏字影响<15% |
| 边界情况 | 12 | 🟡 Medium | 空输入处理缺失 |
| 对抗样本 | 10 | 🔴 High | Prompt 注入部分成功 |

**总体鲁棒性评级**: 🟡 Medium (5 个关键问题待修复)

---

## 缺失图表 (待实测数据)

以下图表需要实际实验数据，当前无法生成：

| Figure | 标题 | 状态 | 阻塞原因 |
|--------|------|------|---------|
| System Architecture | 系统架构图 | ⏸️ 暂停 | 可复用 03-27 版本，无需更新 |
| Confusion Matrix | 混淆矩阵 (Grade Classification) | ⏸️ 暂停 | 待 L1b Benchmark 人工标注完成 |
| Score Correlation | LLM vs Human 相关性散点图 | ⏸️ 暂停 | 待人工标注完成 (需 50+ 样本) |
| Improvement Over Time | 用户进步趋势折线图 | ⏸️ 暂停 | 待 Pilot RCT 纵向数据 |
| Feedback Adoption | 反馈采纳率柱状图 | ⏸️ 暂停 | 待用户交互数据 |
| Demographics Table | 参与者人口学表 | ⏸️ 暂停 | 待招募完成 |
| Reliability Table | 评分者间一致性表 | ⏸️ 暂停 | 待人工标注完成 |

---

## 验证等级说明

| 等级 | 含义 | 本批图表 |
|------|------|---------|
| V0 | 未验证/仅推断 | — |
| V1 | 单一来源确认 | — |
| V2 | 多来源交叉确认 | — |
| **V3** | **静态复核 (实验设计预期值)** | ✅ Fig 7-9 |
| **V4** | **动态验证 (已实际运行)** | ✅ Fig 1-6 |

---

## 下一步建议

### 立即执行 (Hulk)
1. ✅ 本批 9 个图表已生成，可插入论文
2. ✅ 更新论文 Section 4 (Results) 初稿，引用这些图表

### 待 V 决策
1. **Pilot RCT 启动**: 生成 Figure 7-9 所需的真实用户数据 (替换 V3 为 V4)
2. **人工标注**: 完成 L1b Benchmark 验证，生成混淆矩阵和相关性图
3. **多模型测试**: 执行 LLM Backend 对比，更新 Figure 9

### 储备任务 (Hulk)
1. 整理 03-27 版本的 mock 图表，标注"待真实数据替换"
2. 为 9 个已生成图表撰写 Figure Caption
3. 检查图表是否符合期刊格式要求 (字体、尺寸、配色)

---

## 图表使用指南

### LaTeX 插入示例

```latex
% Figure 1: ASR 性能分布
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{artifacts/visualizations/2026-04-06/fig1_asr_performance.pdf}
  \caption{ASR Word Error Rate distribution across 40 test samples. 
           Mean WER = 1.30\%, with 82.5\% zero-error samples.}
  \label{fig:asr-performance}
\end{figure}

% Figure 5: 鲁棒性箱线图
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{artifacts/visualizations/2026-04-06/fig5_robustness_boxplot.pdf}
  \caption{L0 Score robustness across three noise categories. 
           Box shows IQR, whiskers extend to 1.5×IQR, red line = median.}
  \label{fig:robustness-boxplot}
\end{figure}

% Figure 7: 组件消融实验
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{artifacts/visualizations/2026-04-06/fig7_component_ablation.pdf}
  \caption{Component ablation study (expected values). Full system achieves 
           highest narrative quality; removing social cues causes largest drop (-23.4).}
  \label{fig:component-ablation}
\end{figure}
```

### 格式转换 (如需 PNG/TIFF)

```bash
# SVG → PDF (推荐用于 LaTeX)
inkscape --export-pdf=fig1.pdf fig1_asr_performance.svg

# SVG → PNG (300 DPI, 用于期刊投稿)
inkscape --export-png=fig1.png --export-dpi=300 fig1_asr_performance.svg

# SVG → TIFF (300 DPI, 部分期刊要求)
inkscape --export-png=fig1_temp.png --export-dpi=300 fig1_asr_performance.svg
convert fig1_temp.png fig1.tiff
```

---

## 生成脚本

### 实测数据图表 (Fig 1-6)
**脚本路径**: `/Users/moondy/.openclaw/workspace-hulk/pipeline/viz/generate_paper_figures_v2.py`

**执行命令**:
```bash
cd /Users/moondy/.openclaw/workspace-hulk
python3 pipeline/viz/generate_paper_figures_v2.py
```

### 消融实验图表 (Fig 7-9)
**脚本路径**: `/Users/moondy/.openclaw/workspace-hulk/pipeline/viz/generate_ablation_figures.py`

**执行命令**:
```bash
cd /Users/moondy/.openclaw/workspace-hulk
python3 pipeline/viz/generate_ablation_figures.py
```

**依赖**:
```bash
pip install matplotlib>=3.7.5 numpy>=1.26.4 pandas>=2.3.1
```

---

## 附录：图表设计规范

### 通用规范
- **格式**: SVG (矢量图，可无损缩放)
- **尺寸**: 双栏 180mm / 单栏 88mm
- **字体**: Arial/Helvetica (无衬线，期刊友好)
- **字号**: 标题 10pt, 轴标签 8pt, 刻度 7pt
- **品牌色**: `#0ea5e9` (CittaVerse Blue)
- **配色方案**: Colorblind-safe (viridis/Set2)

### 质量检查清单
- [x] 所有坐标轴标签清晰可读
- [x] 图例位置合理，不遮挡数据
- [x] 误差线/置信区间正确标注
- [x] 统计显著性标注 (如适用)
- [x] 文件名语义化 (fig{N}_{description}.svg)
- [x] 生成报告包含数据源和统计摘要
- [x] V3 图表已标注"预期值"免责声明

---

*Hulk 🟢 - Cron Run Complete*  
*下次执行：按 cron 计划自动触发*
