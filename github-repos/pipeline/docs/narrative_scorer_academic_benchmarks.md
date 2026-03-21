# CittaVerse 叙事评分器 — 学术对标与技术路径

> v0.5 设计基准与差异化论证

## 概述

CittaVerse 叙事评分器 (Narrative Quality Scorer) 的技术路径已被 2024-2025 年多项国际研究验证。本文档整理直接对标的学术工作，明确我们的技术定位和创新点。

---

## 国际对标

### 方法论对比

| 维度 | van Genugten 2024 | Klus 2025 | CittaVerse v0.5 |
|------|-------------------|-----------|------------------|
| **模型** | distilBERT 微调 | LLM (GPT 系) | LLM + 规则引擎混合 |
| **语言** | 英文 | 英文 | 中文 + 英文 |
| **评分维度** | 内部/外部细节 (2 维) | 内部/外部细节 (2 维) | 6 维度 |
| **任务** | 自传访谈 (AI) | 自传记忆+未来思维 | 老年人口述叙事 |
| **人群** | 健康成人 | 健康成人 | 老年人 (60+, MCI 含) |
| **部署** | 实验室 | 实验室 | 微信生态 |
| **被引** | 45+ | 3 | — |

### 我们的 6 维度评分体系

| 维度 | 定义 | 对标工作 | 创新性 |
|------|------|----------|--------|
| 1. 内部细节 (Internal Details) | 情景性记忆细节 | van Genugten 2024, Klus 2025 | 扩展至中文 |
| 2. 外部细节 (External Details) | 语义性/通用信息 | van Genugten 2024, Klus 2025 | 扩展至中文 |
| 3. 事件分段 (Event Segmentation) | 叙事中的事件边界识别 | — | **全新维度** |
| 4. 叙事连贯性 (Narrative Coherence) | 时间+因果+主题连贯 | Mansfield 2026 (相关) | **全新维度** |
| 5. 情感丰富度 (Emotional Richness) | 情感词汇多样性+深度 | — | **全新维度** |
| 6. 时间定向 (Temporal Orientation) | 时间标记准确性+密度 | — | **全新维度** |

**关键创新**: 现有工作仅覆盖维度 1-2，我们新增维度 3-6 是全球首次在自动评分框架中纳入。

---

## 技术路径验证

### 已验证路径 (国际同行)

1. **Transformer 模型可以区分内部/外部细节** — van Genugten 2024 (被引 45+)
2. **LLM 在叙事评分任务上表现可靠** — Klus 2025
3. **NLP 可以分类 5 种自传记忆类型** — Mistica 2024 (被引 11)
4. **AI 可以揭示叙事者未意识到的模式** — Mansfield 2026 (Nature)

### 我们的技术优势

1. **中文 NLP 优化** — 现有工作全部基于英文，中文叙事评分无竞品
2. **LLM + 规则引擎混合架构** — 比纯 LLM 更可控，比纯规则更灵活
3. **6 维度评分** — 临床信息量远超 2 维度评分
4. **微信生态部署** — 从实验室到社区的技术桥梁
5. **老年人群适配** — 考虑语速慢、方言、重复等老年语言特征

---

## Pilot RCT 中的评分器角色

```
老年人口述叙事
    ↓ ASR 转录
文本叙事
    ↓ 叙事评分器 v0.5
6 维度评分 + 可视化
    ↓
临床研究终点 (前后对比)
```

### 评分器输出指标

| 指标 | 基线 (D0) | 结束 (D14) | 效应方向 |
|------|-----------|-----------|----------|
| 内部细节密度 | 测量 | 测量 | 期望↑ |
| 外部细节比例 | 测量 | 测量 | 期望↓ |
| 事件分段数 | 测量 | 测量 | 期望↑ |
| 叙事连贯性分 | 测量 | 测量 | 期望↑ |
| 情感丰富度分 | 测量 | 测量 | 期望↑ |
| 时间定向分 | 测量 | 测量 | 期望↑ |

---

## 参考文献

1. van Genugten, R.D.I. & Schacter, D.L. (2024). Automated scoring of the autobiographical interview with natural language processing. *Behavior Research Methods*. PMC10990986.
2. Klus, J. et al. (2025). Automated Scoring of Autobiographical Detail Narration using Large Language Models. PubMed: 40750940.
3. Mansfield, C.D. et al. (2026). What might we learn about autobiographical narrative processing from AI. *Nature HSSC*. DOI: 10.1057/s41599-025-06426-y.
4. Mistica, M. et al. (2024). A natural language model to automate scoring of autobiographical memories. *Behavior Research Methods*. DOI: 10.3758/s13428-024-02385-5.

---

*Last updated: 2026-03-18 | GEO Iteration #40*
