# 储备·开源 PR 跟进 + 新 PR 机会扫描

**日期**: 2026-03-24 16:19 UTC  
**触发**: cron hulk-reserve-pr  
**状态**: ✅ 完成

---

## 一、已提交 PR 状态审计

| # | 仓库 | 状态 | 创建日 | Day | 维护者活跃度 | 行动 |
|---|------|------|--------|-----|-------------|------|
| PR #14 | AgenticHealthAI/Awesome-AI-Agents-for-Healthcare | ✅ **已合并** (03-19) | 03-19 | — | 极高 | 完成 |
| PR #1 | billzyx/awesome-dementia-detection | ✅ **已合并** (03-24 今天) | 03-23 | — | 高 | 完成 🎉 |
| PR #11 | caramaschiHG/awesome-ai-agents-2026 | 🟡 Open | 03-12 | Day 12 | ⚠️ 极低 (仓库仅 1 次 commit, 03-07) | Day 14 (03-26) 做最终跟进 |
| PR #23 | onejune2018/Awesome-LLM-Eval | 🟡 Open | 03-20 | Day 4 | ⚠️ 低 (最后 commit 2025-11-24) | 已发跟进评论 03-23，等待 |
| PR #112 | kakoni/awesome-healthcare | 🟡 Open | 03-19 | Day 5 | 🟡 中 (最后活跃 2026-01-28) | 再等 2-3 天，Day 7-8 跟进 |

### 关键发现

1. **2/5 PR 已合并** — 合并率 40%，PR #14 (学术联合维护) + PR #1 (MIT 许可专题列表) 都是高匹配度投递
2. **PR #11 维护者可能不活跃** — 仓库 03-07 创建后仅 1 次 commit，已发 2 次跟进均无回复。Day 14 做最终判定
3. **PR #23 跟进评论已发** — 03-23 22:47 发送友好 bump，等待维护者回应
4. **PR #112 仍在正常等待期** — 维护者 1 月底有批量合并行为 (5 个 PR 同日处理)，可能周期性处理

### 验证等级: V2 (GitHub REST API 多端点交叉确认)

---

## 二、新 PR 机会扫描

### 高优先目标

| 目标仓库 | ⭐ | 匹配度 | 更新日 | 适合投递角度 | 状态 |
|----------|-----|--------|--------|-------------|------|
| **REAL-Lab-NU/Awesome-AI-Agents-Disease** | 1 | ⭐⭐⭐⭐⭐ | 03-23 | Neurodegenerative + Mental Health 双节点 | 🟢 推荐 |
| CAS-SIAT-XinHai/awesome-ai-mental-health | 1 | ⭐⭐⭐⭐ | 2025-12 | Clinical Application / Open Source 节点 | 🟡 可选 |

#### REAL-Lab-NU/Awesome-AI-Agents-Disease (★★★★★)

- **维护者**: Northwestern University REAL Lab
- **内容**: AI agents for disease — 涵盖 neurodegenerative、mental health、cancer 等
- **格式**: 标准论文列表 (venue + title + paper link + GitHub link)
- **适合 CittaVerse 的位置**:
  - Section 2: Mental Health & Psychiatric Disorders (回忆疗法 + 叙事引导)
  - Section 3: Neurodegenerative Diseases (痴呆/MCI 干预)
- **PRs Welcome 标识**: ✅ 有
- **风险**: 星数低 (1 star)，但学术背景强、更新活跃 (03-23)
- **建议**: 在 arXiv paper 发布前可先以项目身份投递；发布后升级条目

#### CAS-SIAT-XinHai/awesome-ai-mental-health

- **维护者**: 中科院深圳先进院 (CAS-SIAT)
- **内容**: LLM 在心理健康领域的应用综述配套 repo
- **格式**: 详细 description block (需图片 + 分类 + 链接 + 引用)
- **适合位置**: Clinical Application 或 Open Source Tools
- **风险**: 格式要求高，无 PRs Welcome 标识
- **建议**: 优先级低于 REAL-Lab，可在产品更成熟后投递

### 已排除

| 仓库 | 原因 |
|------|------|
| billzyx/awesome-dementia-detection | ✅ 已合并 |
| submitaitools/awesome-life-assistant-ai-tools | 低星 + 非学术，不值得 |
| MindMap-AI/awesome-psychology-mind-maps | 方向不匹配 |

---

## 三、行动计划

### 近期 (本周内)

1. **PR #11** — Day 14 (03-26) 做最终跟进评论或考虑关闭
2. **PR #112** — Day 7-8 (03-26/27) 如无响应，发送友好跟进
3. **PR #23** — 保持等待，03-27 之后如无响应再跟进

### 新 PR 准备

4. **REAL-Lab-NU/Awesome-AI-Agents-Disease** — 准备投递
   - 位置: Neurodegenerative Diseases 或 Mental Health 节区
   - 条目格式: `[venue year] **Title** [[paper]](url) [[GitHub]](url)`
   - 注意: 需要有论文链接；如 arXiv 尚未发布，可先以 GitHub repo + preprint in prep 方式提交
   - **建议等 arXiv paper 发布后再投** (内容更扎实)

---

## 四、PR 管道总览

| 阶段 | 数量 | 详情 |
|------|------|------|
| ✅ 已合并 | 2 | PR #14 (Healthcare AI Agents), PR #1 (Dementia Detection) |
| 🟡 待审核 | 3 | PR #11 (AI Agents 2026), PR #23 (LLM Eval), PR #112 (Healthcare) |
| 🔵 准备中 | 1 | REAL-Lab-NU/Awesome-AI-Agents-Disease |
| 📋 候选 | 1 | CAS-SIAT-XinHai/awesome-ai-mental-health |

**合并率**: 2/5 = 40% (含今日新合并)  
**管道健康度**: 良好 — 有持续新目标 + 合理等待周期

---

*Hulk 🟢 — Compressing chaos into structure*
