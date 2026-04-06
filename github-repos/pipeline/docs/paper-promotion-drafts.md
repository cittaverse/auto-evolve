# Paper Promotion Drafts — CittaVerse Narrative Scorer v0.5

> GEO #59 | 2026-03-23 | 待 V 审核后发布

---

## 1. Twitter/X Thread (English)

```
🧵 We're releasing our technical report: "CittaVerse Narrative Scorer v0.5 — Six-Dimension Assessment for Chinese Autobiographical Memory Quality"

What it does: Automatically scores the quality of life stories told by older adults with mild cognitive impairment (MCI), across 6 dimensions. No LLM API needed.

1/7

Why it matters: Reminiscence therapy works — meta-analyses show g=0.35-0.45 for cognition. But scaling it requires automated quality feedback. Manual coding takes trained raters and can't provide real-time results.

2/7

Our approach: A neuro-symbolic scorer combining rule-based Chinese NLP with research-derived heuristics. Six dimensions:
• Event richness
• Temporal coherence
• Causal coherence
• Emotional depth
• Identity integration
• Information density

3/7

Key design choices:
— Chinese-optimized vocabulary (temporal markers, causal connectives, emotion words)
— Weighted scoring: emotional depth & info density get 0.20 weight (stronger clinical correlation)
— Runs locally, no cloud LLM dependency

4/7

Currently deployed in a pilot RCT (N=50) testing AI-assisted reminiscence therapy for MCI. Screening questionnaire v1.1 with full skip-logic and PIPL-compliant data protection.

5/7

Open source under MIT license:
📄 Paper: [arXiv link pending]
💻 Code: github.com/cittaverse/narrative-scorer
🔬 Study protocol: github.com/cittaverse/pipeline

6/7

Next: LLM-enhanced v0.6, multi-dialect support, and clinical validation against human raters. Feedback welcome — especially from geriatrics, NLP, and digital health researchers.

7/7
```

---

## 2. LinkedIn Post (English)

```
🔬 Announcing: CittaVerse Narrative Scorer v0.5

We've built an automated tool to assess the quality of autobiographical narratives from older adults with mild cognitive impairment (MCI) — a key bottleneck in scaling reminiscence therapy.

The problem: Reminiscence therapy has solid evidence (Cochrane review, multiple RCTs), but quality assessment still relies on manual coding. This doesn't scale.

Our solution: A six-dimension scoring framework optimized for Chinese narratives, using neuro-symbolic AI (rule-based NLP + research-derived heuristics). No LLM API required.

Currently in pilot RCT (N=50) at community health centers in Hangzhou.

📄 Technical report ready for arXiv (cs.HC + cs.CL)
💻 Open source: github.com/cittaverse/narrative-scorer

Looking to connect with researchers in:
— Geriatric cognitive health
— Digital therapeutics / DTx
— Chinese NLP / computational linguistics
— Life narrative / reminiscence therapy

#DigitalHealth #AgingTech #NLP #CognitiveHealth #ReminsicenceTherapy #OpenScience
```

---

## 3. 知乎文章草稿 (中文)

```markdown
# 我们开源了一个「人生故事质量评分器」——为什么老年人讲故事的质量很重要？

## TL;DR

我们做了一个工具，能自动评估老年人讲述的人生故事的质量。六个维度打分，不需要 LLM API，完全本地运行。代码已开源。

## 背景

回忆疗法（Reminiscence Therapy）是一种有循证支持的非药物干预手段，对轻度认知障碍（MCI）老年人的认知功能和心理幸福感有中等效果（Hedges' g = 0.35-0.45）。

但有一个关键瓶颈：**怎么客观评估叙事质量？**

目前的做法是人工编码（Autobiographical Interview 等协议），需要训练有素的评分者，评分者间一致性只有 κ=0.6-0.7，无法提供实时反馈。这严重限制了数字化回忆疗法的规模化部署。

## 我们的方案

**CittaVerse Narrative Scorer v0.5**：一个自动化叙事质量评估工具，从六个维度评分：

| 维度 | 权重 | 核心指标 |
|------|------|---------|
| 事件丰富度 | 0.15 | 内部/外部细节数量 |
| 时间连贯性 | 0.15 | 时间标记词密度 |
| 因果连贯性 | 0.15 | 因果关联词密度 |
| 情感深度 | **0.20** | 情感词汇密度 |
| 自我认同整合 | 0.15 | 自我指代频率 |
| 信息密度分布 | **0.20** | 核心/边缘事件比例 |

为什么情感深度和信息密度权重更高？因为它们与治疗效果的关联更强（Westerhof & Bohlmeijer, 2024; Kensinger & Gutchess, 2026）。

## 技术特点

- **中文优化**：专为中文叙事设计的词汇表（时间标记、因果连接词、情感词、自我指代词）
- **神经符号架构**：规则提取 + 研究启发式评分，可解释、可复现
- **轻量部署**：不依赖 LLM API，社区健康中心的普通电脑就能跑
- **开源**：MIT 协议，代码、测试用例、示例叙事全部公开

## 当前进展

- ✅ 评分器 v0.5 开发完成
- ✅ Pilot RCT (N=50) 筛查问卷 v1.1 完成
- ✅ arXiv 技术报告 v1.1 准备提交（cs.HC + cs.CL）
- 🔜 v0.6：LLM 增强 + 多方言支持

## 链接

- 代码：[github.com/cittaverse/narrative-scorer](https://github.com/cittaverse/narrative-scorer)
- 论文：arXiv 提交中
- 更多资源：[github.com/cittaverse/awesome-digital-therapy](https://github.com/cittaverse/awesome-digital-therapy)

---

如果你在做老年认知健康、数字疗法、中文 NLP 相关的研究或产品，欢迎交流。

@CittaVerse / cittaverse@gmail.com
```

---

## 发布策略建议

| 平台 | 时机 | 前置条件 | 预期影响 |
|------|------|---------|---------|
| Twitter/X | arXiv 上线当天 | arXiv ID 获取 | 学术圈传播 |
| LinkedIn | arXiv 上线后 1-2 天 | 同上 | 行业+学术交叉 |
| 知乎 | arXiv 上线后 1-3 天 | 中文版优化 | 国内开发者/研究者 |
| 微信公众号 | 知乎发布后 | 排版优化 | 精准圈层 |

**注意**：所有文案中的 `[arXiv link pending]` 需在实际提交后替换为真实链接。

---

*Drafted by Hulk 🟢 | GEO #59*
