# 储备·开源 PR 跟进 + 新 PR 机会扫描

**日期**: 2026-03-25 12:52 UTC  
**触发**: cron hulk-reserve-pr-001  
**状态**: ✅ 完成

---

## 一、已提交 PR 状态审计

| # | 仓库 | ⭐ | 状态 | Day | 维护者活跃度 | 行动 |
|---|------|----|------|-----|-------------|------|
| PR #14 | AgenticHealthAI/Awesome-AI-Agents-for-Healthcare | — | ✅ 已合并 (03-19) | — | — | 完成 |
| PR #1 | billzyx/awesome-dementia-detection | — | ✅ 已合并 (03-24) | — | — | 完成 |
| PR #11 | caramaschiHG/awesome-ai-agents-2026 | ~1 | 🟡 OPEN | Day 13 | ❌ 极低 (仅 1 次 commit, 03-07) | **明天 Day 14 发最终跟进** |
| PR #23 | onejune2018/Awesome-LLM-Eval | 621 | 🟡 OPEN | Day 5 | ⚠️ 低 (最后 commit 2025-11) | 等待至 Day 10 (03-30) |
| PR #112 | kakoni/awesome-healthcare | ~5.8k | 🟡 OPEN | Day 6 | 🟡 中 (批量合并模式, 上次 01-28) | **明天 Day 7 发跟进** |
| PR #11 | disi-unibo-nlp/nlg-metricverse | 94 | 🟡 OPEN | Day 1 | ⚠️ 低 (最后 commit 2023-12) | 观察，太新无需跟进 |
| PR #6 | Vvkmnn/awesome-ai-eval | 71 | �� OPEN | Day 2 | 🟡 中 (03-22 有 push) | 观察 |

### 关键发现

1. **合并率 2/7 = 29%** — 略低于昨天的 40% (分母增加)，但绝对数在增长
2. **无新活动** — 5 个 OPEN PR 均无维护者回复/审核
3. **PR #11 (caramaschiHG) 即将到期** — 明天 Day 14，发最终跟进；若 Day 21 仍无响应则关闭
4. **PR #112 (kakoni) 进入跟进窗口** — 维护者有 01-28 批量合并 5 PR 的行为模式，可能在月底再批量处理
5. **nlg-metricverse (94⭐)** — 最有技术价值的 PR，但仓库自 2023-12 未 commit。5 个 open issue 也未处理。低概率合并但高影响力
6. **awesome-ai-eval (71⭐)** — 仓库 03-22 有 push，活跃度尚可，需观察

### 维护者活跃度分析 (kakoni/awesome-healthcare)

最近关闭的 PR：
- #96 merged 01-28 (OpenScribe)
- #93 merged 01-28 (FlashDeconv + Scanpy)
- #92 merged 01-28 (OpenWearables)
- #99 CLOSED (not merged) — MetaReview
- #91 CLOSED (not merged) — PDT section

**模式**: 月末批量处理。PR #112 有机会在 03 月底或 04 月初被处理。

### 验证等级: V4 (GitHub REST API 查询确认)

---

## 二、新 PR 机会扫描

### 扫描结果

| 目标仓库 | ⭐ | 最后活跃 | 适合度 | 状态 |
|----------|-----|----------|--------|------|
| REAL-Lab-NU/Awesome-AI-Agents-Disease | 1 | 03-19 push | ⭐⭐⭐⭐⭐ | 🟡 等 arXiv paper 再投 |
| CAS-SIAT-XinHai/awesome-ai-mental-health | 1 | 2025-12 | ⭐⭐⭐⭐ | 🟡 格式要求高，暂缓 |
| SuperBruceJia/Awesome-Text-Generation-Evaluation | 3 | 03-05 | ⭐⭐ | ❌ 星数过低 |

### 结论

**无新高价值目标**。当前管道已有 5 个 OPEN PR + 1 个准备中 (REAL-Lab)，覆盖了主要学术 awesome-list 渠道。新增投递的边际收益下降。

**下一波机会窗口**: arXiv paper 发布后，可用论文引用升级 REAL-Lab PR 投递 + 更新已有 PR 描述。

---

## 三、行动计划

### 明天 (03-26)

1. **PR #11 (caramaschiHG)** — Day 14 最终跟进
   - 内容: 温和的最终 bump，说明如 2 周内无回复将关闭
   - 如 Day 21 (04-02) 仍无响应 → 关闭

2. **PR #112 (kakoni)** — Day 7 首次跟进
   - 内容: 简短友好 bump，提及 CittaVerse 与 healthcare 的契合度
   - 维护者可能月底批量处理，保持耐心

### 本周内

3. **PR #23 (Awesome-LLM-Eval)** — 继续等待至 Day 10 (03-30)
4. **PR #11 (nlg-metricverse)** — 继续观察
5. **PR #6 (awesome-ai-eval)** — 继续观察

### 条件性

6. **REAL-Lab PR 准备** — 当 arXiv paper 发布后立即投递

---

## 四、PR 管道总览

| 阶段 | 数量 | 详情 |
|------|------|------|
| ✅ 已合并 | 2 | PR #14 (Healthcare AI Agents), PR #1 (Dementia Detection) |
| 🟡 待审核 | 5 | PR #11×2 (AI Agents 2026 + nlg-metricverse), PR #23 (LLM Eval), PR #112 (Healthcare), PR #6 (AI Eval) |
| 🔵 准备中 | 1 | REAL-Lab-NU/Awesome-AI-Agents-Disease |
| 📋 候选 | 1 | CAS-SIAT-XinHai/awesome-ai-mental-health |

**总投递**: 7 | **合并**: 2 | **合并率**: 29%  
**管道健康度**: 良好 — 5 个 PR 在不同审核周期，风险分散

---

*Hulk 🟢 — Compressing chaos into structure*
