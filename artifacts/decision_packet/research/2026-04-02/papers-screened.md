# 前沿论文筛选报告 · 2026-04-02

**扫描范围**: arXiv cs.AI / cs.CL / cs.LG (最近 7 天: 2026-03-27 ~ 2026-04-02)  
**筛选标准**: 记忆 / 叙事 / Agent / 老年科技相关性  
**纳入数量**: Top 10

---

## 筛选结果总览

| # | arXiv ID | 标题 | 相关性维度 | 优先级 |
|---|----------|------|------------|--------|
| 1 | 2604.01007 | OmniMem: Autoresearch-Guided Discovery of Lifelong Multimodal Agent Memory | 记忆 + Agent | 🔴 高 |
| 2 | 2604.00931 | PsychAgent: An Experience-Driven Lifelong Learning Agent for Self-Evolving Psychological Counselor | 记忆 + 老年科技 | 🔴 高 |
| 3 | 2604.00901 | Experience as a Compass: Multi-agent RAG with Evolving Orchestration and Agent Prompts | Agent + 记忆 | 🟡 中 |
| 4 | 2604.01212 | YC-Bench: Benchmarking AI Agents for Long-Term Planning and Consistent Execution | Agent + 长期规划 | 🟡 中 |
| 5 | 2604.01152 | Brainstacks: Cross-Domain Cognitive Capabilities via Frozen MoE-LoRA Stacks for Continual LLM Learning | 记忆 + 持续学习 | 🟡 中 |
| 6 | 2604.00842 | Proactive Agent Research Environment: Simulating Active Users to Evaluate Proactive Assistants | Agent + 评估 | 🟡 中 |
| 7 | 2604.01073 | Narrative Fingerprints: Multi-Scale Author Identification via Novelty Curve Dynamics | 叙事 | 🟢 低 |
| 8 | 2604.00997 | Uncertainty-Aware Variational Reward Factorization via Probabilistic Preference Bases for LLM Personalization | 个性化 | 🟢 低 |
| 9 | 2604.01113 | CARE: Privacy-Compliant Agentic Reasoning with Evidence Discordance | Agent + 隐私 | 🟢 低 |
| 10 | 2604.01170 | Online Reasoning Calibration: Test-Time Training Enables Generalizable Conformal LLM Reasoning | 推理效率 | 🟢 低 |

---

## 高优先级论文 (🔴)

### 1. OmniMem (2604.01007)
**核心关联**: 终身多模态记忆架构，直接对应 CittaVerse 的长期记忆存储需求

**关键发现**:
- 使用自主研究 pipeline 自动探索记忆架构设计空间
- 在 LoCoMo 基准上 F1 从 0.117 提升至 0.598 (+411%)
- 发现 bug 修复 (+175%)、架构变更 (+44%)、提示工程 (+188%) 比超参调优更有效

**CittaVerse 关联**: 阿宝回忆助手需要存储和管理用户多年跨模态回忆（语音、文本、照片），OmniMem 的自动发现方法可借鉴

---

### 2. PsychAgent (2604.00931)
**核心关联**: 心理咨询 Agent，经验驱动的终身学习，与阿宝回忆助手高度同构

**关键发现**:
- Memory-Augmented Planning Engine 支持纵向多会话交互
- Skill Evolution Engine 从历史咨询轨迹中提取新技能
- Reinforced Internalization Engine 通过拒绝微调整合技能
- 优于 GPT-5.4、Gemini-3 等基线

**CittaVerse 关联**: 阿宝同样是多会话、需要记忆连续性、需要从用户互动中自我演化的对话系统

---

## 中优先级论文 (🟡)

### 3. HERA (2604.00901)
**核心关联**: 多 Agent RAG 框架，演化的编排策略

**关键发现**:
- 全局层：奖励引导采样 + 经验积累优化 Agent 拓扑
- 局部层：Role-Aware Prompt Evolution 实现角色条件化改进
- 6 个知识密集型基准上平均提升 38.69%

**CittaVerse 关联**: 回忆挖掘可能涉及多 Agent 协作（引导 Agent、评估 Agent、叙事 Agent）

---

### 4. YC-Bench (2604.01212)
**核心关联**: 长期规划与执行一致性基准

**关键发现**:
- 模拟 startup 运营一年跨度（数百轮交互）
- Scratchpad 使用是成功的最强预测因子
- 47% 的破产源于对抗性客户检测失败

**CittaVerse 关联**: 阿宝与用户的互动也是长期、多轮的，需要维护战略连贯性

---

### 5. Brainstacks (2604.01152)
**核心关联**: 持续学习的 MoE-LoRA 架构

**关键发现**:
- 冻结的 adapter stack 组合，支持跨域认知能力
- 零遗忘 (zero forgetting) 通过 null-space projection
- 发现 domain stack 编码可迁移的认知原语而非领域知识

**CittaVerse 关联**: 阿宝需要持续学习新用户特征而不遗忘已有能力

---

### 6. PARE (2604.00842)
**核心关联**: 主动 Agent 评估环境，用户模拟框架

**关键发现**:
- 将应用建模为有限状态机，支持状态化导航
- PARE-Bench 包含 143 个任务，覆盖沟通、生产力、调度、生活应用
- 测试上下文观察、目标推断、干预时机、多应用编排

**CittaVerse 关联**: 可用于评估阿宝的主动回忆引导能力

---

## 低优先级论文 (🟢)

### 7. Narrative Fingerprints (2604.01073)
**核心关联**: 叙事指纹，作者识别

**关键发现**:
- 信息论新颖性曲线可识别作者特征
- 书籍级别：43% 作者可被显著高于随机识别
- 章节级别：SAX motif 模式达到 30 倍随机准确率

**CittaVerse 关联**: 可能用于识别用户叙事风格，但关联度较弱

---

### 8. VRF (2604.00997)
**核心关联**: LLM 个性化，不确定性感知奖励分解

**关键发现**:
- 变分奖励分解，将用户偏好表示为变分分布
- 在少样本场景和未见用户上优于基线

**CittaVerse 关联**: 阿宝需要个性化适配不同用户的叙事偏好

---

### 9. CARE (2604.01113)
**核心关联**: 隐私合规的 Agent 推理，处理证据冲突

**关键发现**:
- 多阶段框架：远程 LLM 提供结构化类别，本地 LLM 处理敏感数据
- 在 MIMIC-DOS 医疗数据集上表现优于基线

**CittaVerse 关联**: 阿宝处理用户回忆时可能遇到矛盾信息，但隐私架构关联度有限

---

### 10. ORCA (2604.01170)
**核心关联**: 在线推理校准，测试时训练

**关键发现**:
- 结合 conformal prediction 和 test-time training
- 在分布外设置下将 MATH-500 节省从 24.8% 提升至 67.0%

**CittaVerse 关联**: 推理效率优化，但非核心需求

---

## 下一步

- 进入第二轮：精读摘要
- 逐篇提取：核心问题、方法创新、实验结果、局限性
- 输出：`papers-abstracts.md`

---

**状态更新**: `state/paper-review.json`
```json
{
  "round": 1,
  "papers_screened": 10,
  "papers_abstracted": 0,
  "key_trends": ["终身记忆架构", "经验驱动学习", "多 Agent 演化", "持续学习零遗忘"],
  "last_updated": "2026-04-02T09:45:00Z"
}
```
