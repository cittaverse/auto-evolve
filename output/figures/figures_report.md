# 论文数据可视化图表生成报告

**生成时间**: 2026-03-28T05:16:39.938879  
**输出目录**: `/home/node/.openclaw/workspace-hulk/output/figures`  
**图表格式**: PNG, 300 DPI, 宽度≥1200px (符合 JMIR Aging 要求)

---

## 生成的图表清单

| 图号 | 文件名 | 描述 |
|------|--------|------|
| Figure 1 | `figure1_performance_comparison.png` | 性能对比 - 不同配置的平均分数 |
| Figure 2 | `figure2_ablation_study.png` | 消融实验 - 组件贡献度分析 |
| Figure 3 | `figure3_latency_tradeoff.png` | 延迟 - 性能权衡分析 |
| Figure 4 | `figure4_asr_error_analysis.png` | ASR 误差分布分析 (4 子图) |
| Figure 5 | `figure5_weight_sensitivity.png` | 权重敏感性分析 |
| Figure 6 | `figure6_narrative_robustness.png` | 叙事类型鲁棒性分析 |
| Figure 7 | `figure7_edge_cases.png` | 边界条件压力测试 (2 子图) |

---

## 数据源

1. **消融实验数据**: `/pipeline/results/ablation_results_20260326_154717.json`
   - 12 种系统配置
   - 50 个样本
   - 包含分数、延迟、仲裁率等指标

2. **ASR 误差数据**: `/research/asr/results_v3.json`
   - 30 个语音样本
   - WER/CER 指标
   - 误差类型分解 (替换/删除/插入)

3. **夜间实验数据**: `/output/experiments/night_experiment_20260327_172138.json`
   - 权重敏感性分析 (5 种配置)
   - 叙事类型鲁棒性 (5 类叙事)
   - 边界条件压力测试 (6 种边界情况)

---

## 关键发现

### 性能对比 (Figure 1)
- 最佳配置：**llm_only** (62.48 分)
- 基准配置 (full): 56.76 分
- 最差配置：无仲裁机制 (53.46 分)

### 消融实验 (Figure 2)
- **正向贡献**: 简化 L0 评分 (+5.61), 仅 LLM 组件 (+5.73)
- **负向贡献**: 无仲裁机制 (-3.29), 无 LLM 事件提取 (-1.72)
- **关键洞察**: 仲裁机制和 LLM 事件提取是核心组件

### ASR 性能 (Figure 4)
- 平均 WER: **1.48%**
- 零错误样本: **80%** (24/30)
- 误差类型：主要是替换错误 (6 个)

### 权重敏感性 (Figure 5)
- 5 种权重配置差异 < 0.02 分
- 系统对权重选择相对鲁棒
- 推荐维持 60/40 默认配置

### 叙事类型鲁棒性 (Figure 6)
- 创伤叙事评分最高 (83.57±1.21)
- 中性叙事评分最低 (57.53±1.33)
- 符合心理学预期

---

## 使用建议

1. **论文投稿**: 所有图表符合 JMIR Aging 格式要求
2. **演示文稿**: 可直接用于 PPT/Keynote
3. **补充材料**: 建议将 Figure 4 和 Figure 7 作为补充材料

---

*报告生成脚本：`generate_figures.py`*
