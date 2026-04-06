# Evidence Freshness Check — 2026-03-25

**执行时间**: 2026-03-25 02:45-03:05 UTC
**方法**: arXiv browser search (full) + DuckDuckGo web search (partial, anti-bot triggered after first batch)
**覆盖范围**: arXiv 全库搜索 (最新排序) + DDG 发现的期刊/会议论文
**窗口**: 2026-03-18 ~ 2026-03-25 (7 天)
**上一轮**: 2026-03-24 — 6 条结论均未被推翻

---

## 搜索覆盖情况

| 通道 | 状态 | 说明 |
|------|------|------|
| arXiv (browser) | ✅ 可用 | 全库搜索，多关键词组合 |
| DDG (CLI) | ⚠️ 部分可用 | 首批 2 次搜索成功 (20 条结果)，后续被 anti-bot 封锁 |
| Serper/Google | ❌ credits exhausted | 仍无额度 |
| Google Scholar | ❌ headless 检测 | tab 被关闭 |
| PubMed | ❌ 连接失败 | net::ERR_CONNECTION_CLOSED |
| Semantic Scholar | ❌ 429 | rate limited |
| ScienceDirect | ❌ headless 检测 | 返回错误页 |
| Springer | ❌ CAPTCHA | 无法通过 |

**改进**: 本轮 DDG 成功返回了 20 条结果（上轮 DDG 完全不可用），扩大了期刊论文覆盖面。

---

## 已验证结论及状态

### 结论 1: Rememo vs CittaVerse = 互补而非竞争
**原始来源**: GEO #54 (2026-03-21)
**本轮验证结果**: ✅ **未被推翻**
- arXiv "reminiscence therapy AI" 全库仍仅 2 篇，最新仍是 Rememo (2602.17083, Feb 2026)
- 过去 7 天无新 RT AI 论文出现在 arXiv
- DDG 搜索发现 **Remi chatbot** (ScienceDirect S1064748125002210, AMDA 2026) — 一个 LLM-powered chatbot for conversational reminiscence therapy
  - ⚠️ **需要关注**: Remi 定位为"AI chatbot 直接递送 RT"，与 Rememo (therapist-tool) 和 CittaVerse (assessment) 都不同
  - Remi 是递送端 (delivery)，CittaVerse 是评估端 (assessment)，**不直接竞争**
  - 但 Remi 验证了 LLM + RT 的市场认可度，对 CittaVerse 是利好
- **验证等级**: V3 (arXiv 全库复核 + DDG 期刊扫描)

### 结论 2: 无直接竞品做中文老年人叙事质量自动评分
**原始来源**: GEO #54, Evidence Deep Dive (2026-03-16)
**本轮验证结果**: ✅ **未被推翻，但邻域有新工作**
- arXiv 搜索 `"narrative quality" "autobiographical memory"` → **0 结果** (与上轮一致)
- arXiv 搜索 `LLM narrative scoring autobiographical memory` → **0 结果**
- DDG 发现 3 篇相关但**不直接竞争**的论文：
  1. **Pan et al. (UChicago, March 2026)**: "LLM-based scoring of narrative memories reveals that emotional arousal..."
     - 使用 LLM pipeline 量化叙事刺激中的情感唤醒 + 评分记忆忠实度 (central vs peripheral details)
     - ⚠️ **最接近 CittaVerse 的新工作** — 也用 LLM 做叙事记忆评分
     - **关键差异**: 聚焦情感唤醒 → 记忆忠实度方向，非自传体记忆的 6 维叙事质量评分
     - **影响评估**: 验证了"LLM 可用于叙事记忆评分"这一技术路径，对 CittaVerse 是方法论层面的利好；但**不针对中文、不针对老年人、不针对回忆疗法**
  2. **Springer/Behav Res Methods (2026)**: "Assessing autobiographical memory consistency: Machine and human scoring"
     - 引入标准化手工评分流程 + 评估 NLP 模型自动化可能性
     - 关注**记忆一致性** (consistency) 而非叙事质量
     - **与 CittaVerse 的差异**: CittaVerse 评 6 维叙事质量 (内部细节、外部细节、情感效价、叙事连贯性等)，该论文评记忆重述一致性
  3. **Trends in Cognitive Sciences (2026)**: "Studying memory narratives with natural language processing"
     - 综述性文章，讨论 NLP 用于记忆叙事分析的前沿
     - 强化了"NLP + 记忆叙事"领域的学术热度，对 CittaVerse 定位是利好
- **验证等级**: V2 (arXiv + DDG 多来源交叉确认)

### 结论 3: Limbic Nature Medicine — AI 临床推理层 +43% (CBT)
**原始来源**: Evidence Deep Dive (2026-03-16)
**本轮验证结果**: ✅ **未被推翻**
- DDG 发现 Nature 新文 "AI in geriatric psychiatry: precision meets human experience" (s41386-026-02328-y)
  - 综述 AI 在老年精神科的进展
  - 进一步验证了 AI-in-the-loop 路线在临床中的接受度
- 无新论文挑战 Limbic 的 +43% 发现
- **验证等级**: V2 (DDG 发现 + 已有结论)

### 结论 4: CittaVerse 四项独特价值主张 (UVPs) 仍成立
**原始来源**: GEO #54, GEO #55
**本轮验证结果**: ✅ **未被推翻，但需更新竞争地图**
- UVP #1 (6 维理论框架): Pan et al. 的 LLM scoring 聚焦 2 维 (arousal + fidelity)，CittaVerse 的 6 维覆盖仍最全面
- UVP #2 (中文特异性): 无新中文叙事评分工具出现
- UVP #3 (可解释性/可复现性): 仍无竞品
- UVP #4 (产品迭代支持): 仍无竞品
- **验证等级**: V3 (arXiv 全库复核 + DDG 期刊扫描)

### 结论 5: AI-in-the-loop (非全自动) 是 RT 的验证路径
**原始来源**: Evidence Deep Dive (2026-03-16), Rememo 分析
**本轮验证结果**: ✅ **未被推翻，且趋势加强**
- Remi chatbot (AMDA 2026) 提供了全自动 AI chatbot RT 的案例，但仍在会议摘要阶段
- Nature "AI in geriatric psychiatry" 综述继续强调 human-AI collaboration
- DDG 还发现 "Exploring AI Agents for Reminiscence Therapy in Long-Term Care" (会议论文)
  - 探索 AI agent 在长期护理中的 RT 应用，但仍在探索阶段
- 总体趋势：全自动 RT chatbot 开始出现，但主流仍认为人类参与不可替代
- **验证等级**: V2 (多来源交叉确认)

### 结论 6: SUS 作为主要可用性终点
**原始来源**: GEO #43 Evidence-to-Pilot Integration
**本轮验证结果**: ✅ **未被推翻**
- 无新论文挑战 SUS 在数字健康老年人群体中的适用性
- **验证等级**: V1 (无反面证据)

---

## 本轮新发现论文 (DDG 渠道)

| # | 论文/来源 | 发表时间 | 相关性 | 对 CittaVerse 的影响 |
|---|-----------|----------|--------|---------------------|
| 1 | **Remi**: AI chatbot for conversational RT (ScienceDirect/AMDA) | 2026 | ⭐⭐⭐ 邻域-递送 | 验证 LLM+RT 市场，不竞争评估赛道 |
| 2 | **Pan et al.**: LLM-based scoring of narrative memories (UChicago) | 2026-03 | ⭐⭐⭐ 方法论近邻 | 最接近的新工作，但方向不同(情感唤醒 vs 叙事质量) |
| 3 | **Springer BRM**: AM consistency — machine vs human scoring | 2026 | ⭐⭐ 方法论 | 关注一致性非质量，不直接竞争 |
| 4 | **TiCS**: Studying memory narratives with NLP | 2026 | ⭐⭐ 综述-利好 | 验证领域热度 |
| 5 | **Nature Neuropsychopharmacology**: AI in geriatric psychiatry | 2026 | ⭐⭐ 综述-利好 | 验证 AI+老年精神科趋势 |
| 6 | **LLM-powered chatbots for elderly** (Springer Network Modeling) | 2026 | ⭐⭐ 综述 | 综述 LLM chatbot 在老年人群体中的应用 |
| 7 | **AI agents for RT in long-term care** (会议论文) | 2026 | ⭐⭐ 邻域-递送 | 仍在探索阶段 |
| 8 | **bioRxiv**: Sequential narrative binding by hippocampal CA2/3 | 2026-03-19 | ⭐ 基础科学 | 记忆组织的神经机制，间接相关 |
| 9 | **Frontiers Psych**: Separating details while maintaining story | 2026 | ⭐⭐ 方法论 | 使用 Levine 评分协议变体，验证评分框架 |

---

## 重点关注 — Pan et al. (UChicago) LLM Memory Scoring

**为什么重要**: 这是过去 7 天内发现的**最接近 CittaVerse 赛道的新工作**。

**已知信息** (来自 DDG snippet):
- 引入 generative AI pipeline 量化叙事刺激中的情感唤醒 + 评分回忆转录的记忆忠实度
- 区分 central vs peripheral details

**与 CittaVerse 的关键差异**:
| 维度 | Pan et al. | CittaVerse |
|------|-----------|-----------|
| 评分目标 | 情感唤醒 + 记忆忠实度 | 6 维叙事质量 |
| 语言 | 英文 (推测) | 中文 |
| 人群 | 一般人群 (推测) | 老年人 |
| 治疗场景 | 实验室记忆研究 | 回忆疗法临床/产品 |
| 方法 | LLM pipeline | Neuro-symbolic (LLM + 规则) |

**建议**: 论文全文访问后 (PDF 在 UChicago voices 站点)，V 或 Core 应详细阅读方法部分，评估是否有可借鉴的 prompting 策略。

---

## Bottom Line

**过去 7 天（2026-03-18 ~ 2026-03-25），CittaVerse 的 6 条核心研究结论均未被推翻。**

与上轮 (03-24) 相比的增量变化：
- **新竞争信号**: Pan et al. (UChicago) LLM-based memory scoring — 方法论最近邻，但方向不同
- **新市场信号**: Remi chatbot (AMDA) — LLM 直接递送 RT，验证市场需求
- **领域热度上升**: TiCS 综述 + Nature 综述 + 多篇会议论文，"NLP/LLM + 记忆叙事" 正在成为 2026 年热点赛道
- **CittaVerse 独特定位保持**: 6 维中文老年人叙事质量评分 — 仍然无直接竞品

**置信度**: 中高。本轮 arXiv 全库覆盖充分 + DDG 扩展了期刊覆盖面。PubMed 仍未能扫描。

**验证等级**: V3 (静态复核 — arXiv 全库搜索 + DDG 期刊扫描 + 已有结论对照)

---

## 下一轮建议

1. **优先访问 Pan et al. PDF**: `https://bpb-us-w2.wpmucdn.com/voices.uchicago.edu/dist/7/3210/files/2026/03/Pan_llmMemoryScoring.pdf`
2. **恢复 Serper 额度后**: 补充 PubMed 和 Google Scholar 扫描，覆盖临床试验注册库
3. **关注 Remi chatbot 后续**: 是否有完整论文发表、临床试验数据
4. **更新 CittaVerse competitive landscape**: 加入 Pan et al. 和 Remi 作为邻域参照点
