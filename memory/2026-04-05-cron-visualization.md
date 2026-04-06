# 2026-04-05 Cron: 论文数据可视化

**Cron Job ID**: 5ce51121-6c22-4c64-88b8-2b6a040b08fb  
**Agent**: Hulk 🟢  
**Time**: 2026-04-05 01:45 UTC  
**Status**: ⚠️ Partial Complete (exec unavailable)

---

## 执行摘要

本轮 Cron 任务因 `exec` 工具配置问题无法直接生成 SVG 图表。已完成：
- ✅ 数据准备：整合 04-04 夜间长跑实验数据 (28 样本，5 次重复验证)
- ✅ 脚本编写：Python + Matplotlib 可视化脚本 (`pipeline/viz/generate_paper_figures.py`)
- ✅ 文档更新：`artifacts/visualizations/2026-04-05-paper-visualization-update.md`
- ⏳ 图表生成：待 exec 修复后执行

---

## 与 03-27 轮次对比

| 项目 | 03-27 | 04-05 | 变化 |
|------|-------|-------|------|
| 图表总数 | 11 | 11 | - |
| 新增图表 | Figure 7-9 | Figure 10-11 | +2 误差分析 |
| 数据来源 | methods-evaluation.md (设计) | 04-04 实验 (实际运行) | 更可靠 |
| 验证等级 | V3 (静态复核) | V4 (动态验证) | 提升 |
| SVG 生成 | ✅ 完成 | ❌ Blocked | exec 问题 |

---

## 新增数据 (04-04 夜间长跑实验)

### 核心指标

| 指标 | 数值 | 备注 |
|------|------|------|
| 样本数 | 28 | 覆盖 12 类别 |
| 成功率 | 100% | 28/28 |
| 平均评分 | 40.72 ± 6.63 | Mock event extraction |
| 实验重复 | 5 次 | 03-28/03-30/04-02/04-03/04-04 |
| 结果一致性 | 完全一致 | 证明系统稳定性 |

### 12 类别评分

| Category | N | Mean | Std | Group |
|----------|---|------|-----|-------|
| adversarial_emotion | 2 | 47.25 | 2.47 | adversarial |
| positive | 5 | 46.06 | 3.21 | normal |
| boundary_long | 1 | 49.80 | — | boundary |
| traumatic | 2 | 43.75 | 1.06 | normal |
| noise_typo | 2 | 43.50 | 0.71 | noise |
| negative | 3 | 42.90 | 2.85 | normal |
| reflective | 2 | 42.25 | 1.77 | normal |
| neutral | 2 | 40.00 | 0.00 | normal |
| cross_lingual | 2 | 39.45 | 0.64 | normal |
| adversarial_nonsense | 2 | 34.50 | 0.71 | adversarial |
| noise_asr | 2 | 31.50 | 0.71 | noise |
| boundary_short | 3 | 29.00 | 0.50 | boundary |

### 6 维度评分

| Dimension | Mean | Std | 备注 |
|-----------|------|-----|------|
| temporal_coherence | 100.00 | 0.00 | ⚠️ Mock 异常 |
| information_density | 67.08 | 12.45 | — |
| event_richness | 26.79 | 8.92 | ⚠️ Mock 偏低 |
| causal_coherence | 23.57 | 9.34 | — |
| identity_integration | 20.90 | 8.15 | — |
| emotional_depth | 8.05 | 4.23 | — |

---

## 产出物

### 文件清单

```
/Users/moondy/.openclaw/workspace-hulk/
├── artifacts/visualizations/
│   └── 2026-04-05-paper-visualization-update.md  ✅
├── pipeline/viz/
│   └── generate_paper_figures.py                  ✅
└── memory/
    └── 2026-04-05-cron-visualization.md           ✅ (本文件)
```

### 待生成图表 (exec 修复后)

```
artifacts/visualizations/2026-04-05/
├── figure7_ablation_components.svg        (待生成)
├── figure8_ablation_prompts.svg           (待生成)
├── figure9_llm_comparison.svg             (待生成)
├── figure10_robustness_by_category.svg    (新增)
├── figure11_dimension_distribution.svg    (新增)
└── figure_data.csv                        (待生成)
```

---

## 阻塞项

| 阻塞点 | 持续时间 | 影响 | 解决方式 |
|--------|---------|------|---------|
| `exec` 配置问题 | >1 session | 无法生成 SVG | V 修复 `tools.exec.node` 或切换 host 模式 |
| DASHSCOPE_API_KEY | >14 天 (since 03-28) | 无法真实 LLM 验证 | V 轮换 API Key |

---

## 下一步

1. **V 执行**: 修复 exec 配置
   ```
   选项 A: 修复 node `moondy-mac-node` 的 system.run 支持
   选项 B: 临时切换 `tools.exec.host` = "host" 或 "sandbox"
   ```

2. **V 执行**: 轮换 DASHSCOPE_API_KEY (已失效 >14 天)

3. **Hulk 执行** (待 exec 修复):
   ```bash
   cd /Users/moondy/.openclaw/workspace-hulk
   python pipeline/viz/generate_paper_figures.py --output artifacts/visualizations/2026-04-05/
   ```

4. **Hulk 执行** (待 API Key 轮换): 执行真实 LLM 验证实验

5. **Hulk 执行** (待 Pilot RCT): 用真实用户数据替换 mock 数据

---

## 验证等级

| 内容 | 等级 | 说明 |
|------|------|------|
| 实验数据 | V4 | 04-04 实际运行，5 次重复验证 |
| 图表设计 | V3 | 基于论文规范静态复核 |
| Python 脚本 | V3 | 代码已写，待执行验证 |
| SVG 生成 | V0 | 未执行 (exec blocked) |

---

*Hulk 🟢 - Cron Run Partial Complete*  
*下次执行：待 exec 修复后自动重试*
