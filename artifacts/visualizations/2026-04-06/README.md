# 论文数据可视化 — 2026-04-06

## 概览

本目录包含 6 个出版级 SVG 图表，用于 VSNC/L0 相关论文与演示。

**生成时间**: 2026-04-06 00:38 UTC  
**数据源**: 
- `research/vsnc-l0-robustness-results.json` (30 条鲁棒性测试)
- ASR 基准测试数据 (40 条样本)

---

## 图表清单

| 文件名 | 说明 | 尺寸 |
|--------|------|------|
| `fig1_asr_performance.svg` | ASR 性能对比 (WER/CER/延迟) | 39K |
| `fig2_error_analysis.svg` | 错误分析分布 | 38K |
| `fig3_ablation_noise.svg` | 噪声消融实验结果 | 75K |
| `fig4_lref_stages.svg` | LREF 阶段分布 | 27K |
| `fig5_robustness_boxplot.svg` | 鲁棒性测试箱线图 | 42K |
| `fig6_dimension_radar.svg` | 六维度雷达图 | 55K |

---

## 使用建议

- **论文插入**: SVG 格式可直接嵌入 LaTeX (pgfsvg) 或转换为 PDF
- **演示文稿**: SVG 可无损缩放到任意尺寸
- **网页展示**: 原生支持，无需转换

---

## 生成脚本

```bash
python3 pipeline/viz/generate_paper_figures_v2.py
```

**依赖**: matplotlib 3.7.5, numpy 1.26.4, pandas 2.3.1

---

*生成者：Hulk 🟢*
