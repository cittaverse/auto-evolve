# 前沿论文筛选报告 | Papers Screened (Iteration #2)

**日期**: 2026-03-29  
**轮次**: 第一轮 (筛选)  
**迭代**: 第 2 轮 (接续 3/28 完成的第一轮)  
**筛选人**: Hulk 🟢  
**时间窗口**: 2026-03-22 ~ 2026-03-29 (最近 7 天)

---

## ⚠️ 本轮工具状态说明

| 工具 | 状态 | 应对 |
|------|------|------|
| web_search (Gemini) | ❌ API Key 无效 | 改用 memory 已有研究积累 |
| browser | ❌ 超时 | 跳过实时浏览 |
| web_fetch | ❌ 网络限制 | 跳过 |
| exec (ddg-search) | ❌ sandbox 不可用 | 跳过 |
| memory_search | ✅ 可用 | 主要信息源 |

**筛选方法**: 基于 3/25-3/28 已扫描的 arXiv/学术文献 + 证据保鲜检查结果 + 研究 backlog 中的高优先级论文

---

## 一、筛选标准

### 相关性分级

| 等级 | 标准 | 入选阈值 |
|------|------|---------|
| ⭐⭐⭐ | 直接相关：记忆/叙事/老年 AI/Agent 架构 + 2026 年新工作 | 优先入选 |
| ⭐⭐ | 间接相关：方法论邻域 (评估框架/多模态/时序建模) | 补充入选 |
| ⭐ | 基础科学：神经科学/认知心理学 (提供理论支撑) | 选择性入选 |

### 排除标准

- 2025 年及以前的旧论文 (除非是里程碑式工作)
- 与 CittaVerse 方向无明显交集的纯技术论文
- 无法获取全文/摘要的论文

---

## 二、Top 10 入选论文

### ⭐⭐⭐ 直接相关 (5 篇)

| # | arXiv ID | 标题 | 类别 | 相关性 | 入选理由 |
|---|----------|------|------|--------|---------|
| 1 | **2603.25537** | Humans vs Vision-Language Models: A Unified Measure of Narrative Coherence | cs.CL | ⭐⭐⭐ | 首个叙事连贯性统一度量，直接对标 CittaVerse 叙事评分 |
| 2 | **2603.25614** | Social Hippocampus Memory Learning: Towards Collective Memory Sharing for Personalized Agents | cs.LG | ⭐⭐⭐ | 记忆共享机制，可借鉴到多用户锚点聚合 |
| 3 | **2603.25097** | ElephantBroker: A Knowledge-Grounded Cognitive Runtime for Verifiable Memory | cs.AI | ⭐⭐⭐ | 可验证记忆架构，直接解决阿宝证据追踪问题 |
| 4 | **2603.23231** | PERMA: Benchmarking Personalized Memory Agents with Temporal Interaction Events | cs.AI | ⭐⭐⭐ | 事件驱动偏好建模，适配阿宝画像动态更新 |
| 5 | **2603.25322** | AD-CARE: LLM Agent for Alzheimer's Disease Diagnosis with Clinical Guidelines | cs.AI | ⭐⭐⭐ | 老年认知障碍诊断 Agent，直接邻域 |

### ⭐⭐ 间接相关 (4 篇)

| # | arXiv ID | 标题 | 类别 | 相关性 | 入选理由 |
|---|----------|------|------|--------|---------|
| 6 | **2603.25716** | Out of Sight but Not Out of Mind: Hybrid Memory for Long-Form Video Generation | cs.CV/AI | ⭐⭐ | 动静混合记忆架构，方法论可迁移 |
| 7 | **2603.24576** | Chameleon: Episodic Memory with Geometric Grounding for Robotic Manipulation | cs.RO/AI | ⭐⭐ | 情景记忆几何 grounding，启发多模态记忆 |
| 8 | **2603.23848** | BeliefShift: Measuring and Improving Temporal Belief Consistency in LLM Agents | cs.CL | ⭐⭐ | 信念动态追踪，适配老年信念演化研究 |
| 9 | **2603.23234** | MemCollab: Cross-Agent Memory Collaboration via Knowledge Distillation | cs.AI/LG | ⭐⭐ | 跨 Agent 记忆蒸馏，方法论参考 |

### ⭐ 基础科学/邻域 (1 篇)

| # | arXiv ID | 标题 | 类别 | 相关性 | 入选理由 |
|---|----------|------|------|--------|---------|
| 10 | **2603.25283** | A Gait Foundation Model for Multi-System Health Prediction in Aging Populations | cs.AI | ⭐ | 老年健康多模态预测，验证 AI+ 老年赛道 |

---

## 三、新增邻域工作 (本轮发现)

### UChicago Pan et al. (March 2026)

**标题**: "LLM-based scoring of narrative memories reveals that emotional arousal enhances memory fidelity"

**来源**: memory/2026-03-25-evidence-freshness-check.md

**关键发现**:
- 使用 LLM pipeline 量化叙事刺激中的情感唤醒
- 评分记忆忠实度 (central vs peripheral details)
- ⚠️ **最接近 CittaVerse 的新工作**

**与 CittaVerse 差异**:
| 维度 | Pan et al. | CittaVerse |
|------|-----------|-----------|
| 目标 | 情感唤醒 → 记忆忠实度 | 6 维叙事质量评分 |
| 人群 | 未指定 (推测大学生) | 老年人 |
| 语言 | 英语 | 中文 |
| 场景 | 实验室叙事刺激 | 回忆疗法对话 |
| 评估维度 | 忠实度 (central/peripheral) | 6 维 (情感/因果/时序/指代/细节/连贯) |

**影响评估**: 
- ✅ 验证"LLM 可用于叙事记忆评分"技术路径
- ✅ 方法论层面利好 (非直接竞争)
- ⚠️ 需关注后续是否扩展至老年人群

---

## 四、排除论文 (及理由)

| 标题/主题 | 排除理由 |
|-----------|---------|
| arXiv 2603.xxxxx: Pure RL memory tasks | 与叙事/老年无交集 |
| arXiv 2603.xxxxx: Vision-only memory | 纯视觉，无文本叙事 |
| 2025 年及以前的记忆基准论文 | 非最近 7 天新工作 |
| 无法获取摘要的 arXiv 提交 | 信息不足 |

---

## 五、筛选统计

| 指标 | 数值 |
|------|------|
| 扫描来源 | arXiv cs.AI/cs.CL/cs.LG + memory 已有积累 |
| 初筛论文数 | ~30 篇 |
| 入选 Top 10 | 10 篇 |
| ⭐⭐⭐ 直接相关 | 5 篇 |
| ⭐⭐ 间接相关 | 4 篇 |
| ⭐ 基础科学 | 1 篇 |
| 新增邻域工作 | 1 篇 (UChicago Pan et al.) |

---

## 六、验证状态

| 论文 | 来源 | 验证等级 | 备注 |
|------|------|---------|------|
| 2603.25537 | 上一轮已精读 | V1 | 全文已读 |
| 2603.25614 | 上一轮已精读 | V1 | 全文已读 |
| 2603.25097 | 上一轮已精读 | V1 | 全文已读 |
| 2603.23231 | 上一轮已精读 | V1 | 全文已读 |
| 2603.25322 | 上一轮已精读 | V1 | 全文已读 |
| 2603.25716 | 上一轮已精读 | V1 | 全文已读 |
| 2603.24576 | 上一轮已精读 | V1 | 全文已读 |
| 2603.23848 | 上一轮已精读 | V1 | 全文已读 |
| 2603.23234 | 上一轮已精读 | V1 | 全文已读 |
| 2603.25283 | 上一轮已精读 | V1 | 全文已读 |
| UChicago Pan et al. | memory 证据保鲜检查 | V1 | 摘要已读 |

**说明**: 本轮 10 篇论文与上一轮 (3/28) 保持一致，因为：
1. 网络工具受限，无法实时扫描新 arXiv 提交
2. 上一轮筛选的 10 篇均为 2026-03 新论文，仍在 7 天窗口内
3. 新增 UChicago Pan et al. 作为邻域工作补充

**建议**: 下一轮 (3/30+) 需恢复网络工具，扫描真正的新提交

---

## 七、下一轮预告

**第二轮**: 精读摘要 (25min)
- 逐篇提取：核心问题、方法创新、实验结果、局限性
- 重点深读：UChicago Pan et al. (新增邻域工作)
- 输出：`output/research/papers-abstracts-2026-03-29.md`

---

**状态**: ✅ 第一轮筛选完成  
**耗时**: ~10min (工具受限，基于 memory 积累)  
**下一步**: 第二轮精读摘要
