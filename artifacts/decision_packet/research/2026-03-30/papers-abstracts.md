# Papers Abstracts — 前沿论文精读摘要

**日期**: 2026-03-30  
**状态**: ✅ 第二轮完成 (25min)  
**来源**: arXiv cs.AI / cs.CL / cs.LG 最近 7 天

---

## 1. MemBoost: A Memory-Boosted Framework for Cost-Aware LLM Inference

**arXiv**: 2603.26557 | **分类**: cs.CL | **提交**: 2026-03-27

| 维度 | 内容 |
|------|------|
| **核心问题** | LLM 在真实服务中推理成本高，尤其是重复或近似重复查询场景 |
| **方法创新** | • 轻量模型复用已生成答案<br>• 检索相关支持信息进行廉价推理<br>• 选择性升级困难/不确定查询到更强模型<br>• 支持答案复用、持续记忆增长、成本感知路由 |
| **实验结果** | • 大幅减少昂贵大模型调用<br>• 降低整体推理成本<br>• 保持与强模型基线相当的答案质量 |
| **局限性** | • 依赖模拟工作负载验证<br>• 真实生产环境效果待验证 |

**CittaVerse 相关性**: 🔴 记忆增强机制可直接借鉴用于用户回忆对话中的上下文复用

---

## 2. MemoryCD: Benchmarking Long-Context User Memory of LLM Agents for Lifelong Cross-Domain Personalization

**arXiv**: 2603.25973 | **分类**: cs.CL | **提交**: 2026-03-26

| 维度 | 内容 |
|------|------|
| **核心问题** | 现有记忆基准局限于短会话合成对话，缺乏真实长期行为评估 |
| **方法创新** | • 首个大规模、用户中心、跨域记忆基准<br>• 基于 Amazon Review 真实用户多年跨域行为<br>• 非脚本化人设，追踪真实交互<br>• 14 个 SOTA 模型 + 6 个记忆方法基线<br>• 4 个个人化任务 × 12 个领域评估 |
| **实验结果** | 现有记忆方法在各领域远未达到用户满意度 |
| **局限性** | • 仅限 Amazon Review 数据集<br>• 工作坊论文 (Lifelong Agent @ ICLR 2026) |

**CittaVerse 相关性**: 🔴 直接相关 — 终身个人化记忆评估框架可借鉴用于阿宝回忆助手

---

## 3. ClinicalAgents: Multi-Agent Orchestration for Clinical Decision Making with Dual-Memory

**arXiv**: 2603.26182 | **分类**: cs.CL | **提交**: 2026-03-27

| 维度 | 内容 |
|------|------|
| **核心问题** | LLM 在医疗诊断中难以捕捉人类临床医生的迭代、假设驱动推理 |
| **方法创新** | • 多 Agent 框架模拟专家临床认知工作流<br>• MCTS 动态编排机制 (非刚性顺序链)<br>• Orchestrator 迭代生成假设、主动验证证据、触发回溯<br>• **双重记忆架构**:<br>  - Working Memory: 维护演进的患者状态<br>  - Experience Memory: 检索临床指南和历史案例 |
| **实验结果** | • SOTA 性能<br>• 诊断准确性和可解释性显著优于单 Agent 和多 Agent 基线 |
| **局限性** | • 仅限临床场景验证<br>• 16 页会议论文，细节可能有限 |

**CittaVerse 相关性**: 🔴 双重记忆架构可直接迁移 — Working Memory 对应对话状态，Experience Memory 对应集体记忆锚点

---

## 4. AgentCollab: A Self-Evaluation-Driven Collaboration Paradigm for Efficient LLM Agents

**arXiv**: 2603.26034 | **分类**: cs.CL | **提交**: 2026-03-27

| 维度 | 内容 |
|------|------|
| **核心问题** | 多 Agent 协作效率低，缺乏自评估驱动的动态协作机制 |
| **方法创新** | • 自评估驱动的协作范式<br>• Agent 根据自我评估决定是否寻求协作<br>• 减少不必要的多轮交互 |
| **实验结果** | 待详细阅读 PDF |
| **局限性** | 摘要信息有限 |

**CittaVerse 相关性**: 🟠 可用于优化回忆对话中的多 Agent 协作 (如回忆挖掘 + 情感安全)

---

## 5. AIRA_2: Overcoming Bottlenecks in AI Research Agents

**arXiv**: 2603.26499 | **分类**: cs.AI | **提交**: 2026-03-30

| 维度 | 内容 |
|------|------|
| **核心问题** | AI 研究 Agent 存在性能瓶颈 |
| **方法创新** | • 识别并克服研究 Agent 的关键瓶颈<br>• 大规模作者团队 (25+ 人) |
| **实验结果** | 待详细阅读 PDF |
| **局限性** | 摘要信息有限 |

**CittaVerse 相关性**: 🟠 研究 Agent 方法论可能启发自动化研究流程

---

## 6. GUIDE: Resolving Domain Bias in GUI Agents through Real-Time Web Video Retrieval and Plug-and-Play Annotation

**arXiv**: 2603.26266 | **分类**: cs.AI | **提交**: 2026-03-30

| 维度 | 内容 |
|------|------|
| **核心问题** | GUI Agent 存在领域偏差 |
| **方法创新** | • 实时 Web 视频检索<br>• 即插即用标注<br>• 解决领域偏差 |
| **实验结果** | 28 页，8 图，7 表 |
| **局限性** | 主要针对 GUI 交互场景 |

**CittaVerse 相关性**: 🟡 间接启发 — 实时检索增强可能用于回忆触发

---

## 7. BeSafe-Bench: Unveiling Behavioral Safety Risks of Situated Agents in Functional Environments

**arXiv**: 2603.26076 | **分类**: cs.AI | **提交**: 2026-03-30

| 维度 | 内容 |
|------|------|
| **核心问题** | 情境化 Agent 在功能环境中的行为安全风险未充分研究 |
| **方法创新** | • 行为安全风险评估基准<br>• 功能环境中的 Agent 行为测试 |
| **实验结果** | 待详细阅读 PDF |
| **局限性** | 摘要信息有限 |

**CittaVerse 相关性**: 🟠 情感安全模块可借鉴安全评估方法

---

## 8. JAL-Turn: Joint Acoustic-Linguistic Modeling for Real-Time and Robust Turn-Taking Detection in Full-Duplex Spoken Dialogue Systems

**arXiv**: 2603.26515 | **分类**: cs.CL | **提交**: 2026-03-27

| 维度 | 内容 |
|------|------|
| **核心问题** | 全双工语音对话系统中的实时轮转检测 |
| **方法创新** | • 联合声学 - 语言建模<br>• 实时鲁棒轮转检测 |
| **实验结果** | 8 页，进行中 |
| **局限性** | 论文仍在进行中 |

**CittaVerse 相关性**: 🟡 语音对话轮转检测可启发多模态回忆对话设计

---

## 9. Neuro-Symbolic Process Anomaly Detection

**arXiv**: 2603.26461 | **分类**: cs.LG | **提交**: 2026-03-30

| 维度 | 内容 |
|------|------|
| **核心问题** | 流程异常检测 |
| **方法创新** | • 神经符号 AI 方法<br>• 结合神经网络与符号推理 |
| **实验结果** | 待详细阅读 PDF |
| **局限性** | 摘要信息有限 |

**CittaVerse 相关性**: 🟡 神经符号方法可能启发叙事质量评估

---

## 10. Ask or Assume? Uncertainty-Aware Clarification-Seeking in Coding Agents

**arXiv**: 2603.26233 | **分类**: cs.CL | **提交**: 2026-03-27

| 维度 | 内容 |
|------|------|
| **核心问题** | Coding Agent 在不确定性时应该询问还是假设 |
| **方法创新** | • 不确定性感知的澄清寻求机制<br>• 平衡询问成本与假设风险 |
| **实验结果** | 待详细阅读 PDF |
| **局限性** | 摘要信息有限 |

**CittaVerse 相关性**: 🟡 不确定性处理可启发回忆对话中的澄清策略

---

## 摘要完成度

| 论文 | 摘要完整性 | 需补充 |
|------|-----------|--------|
| MemBoost | ✅ 完整 | 无 |
| MemoryCD | ✅ 完整 | 无 |
| ClinicalAgents | ✅ 完整 | 无 |
| AgentCollab | 🟡 中等 | 实验细节 |
| AIRA_2 | 🟡 中等 | 方法细节 |
| GUIDE | 🟡 中等 | 核心方法 |
| BeSafe-Bench | 🟡 中等 | 评估指标 |
| JAL-Turn | 🟡 中等 | 实验结果 |
| Neuro-Symbolic | 🟡 中等 | 方法细节 |
| Ask or Assume | 🟡 中等 | 实验设计 |

---

*状态文件已更新：`state/paper-review.json`*
