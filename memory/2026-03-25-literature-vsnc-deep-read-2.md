# 2026-03-25 — VSNC 技术文献深度阅读 #2

**时间**: 2026-03-25 08:45 UTC  
**触发**: cron hulk-reserve-literature-001  
**状态**: ✅ 完成  
**验证等级**: V2（arXiv API + Semantic Scholar 交叉确认）  
**前序**: memory/2026-03-24-literature-vsnc-deep-read.md（第 1 轮，10 篇）

---

## Question

第 1 轮覆盖了 VSNC v0.6 四大 Pillar 的核心论文。本轮目标：
1. 填补 Parking Lot 中三个探索方向（vocal biomarkers、multimodal narrative、neuro-symbolic）
2. 扩展 Pillar D（叙事 NLP 前沿）+ Pillar B（ASR 老年口语）的证据密度
3. 发现直接匹配 VSNC 的新论文

## Bottom Line

**本轮发现 9 篇高价值新论文 + 1 篇数据集**，最大亮点：

1. **LLM-Based Narrative Memory Scoring**（Semantic Scholar, 2025 ICDMW）— 有人已经用 LLM 对叙事记忆做评分，且发现**情绪唤醒增强核心信息但牺牲外围细节** → 直接验证 VSNC 的 hybrid scoring 方向可行
2. **SeniorTalk**（arXiv 2503.16578, 2025-03）— **首个中国超高龄老年人对话语音数据集**，55.53h，202 人，含方言标注 → 直接补齐 VSNC Pillar B 的中文老年语音评估 benchmark 空白
3. **PARLO Dementia Corpus**（arXiv 2603.03471, 2026-03）— 首个公开德语多中心 AD 语料库，含 LLM-based classification baseline → 跨语言方法论参考

---

## Key Findings

### 新 Pillar A: LLM-as-Judge 扩展

#### 11. ★★★ LLM-Based Scoring of Narrative Memories (2025, ICDMW)
- **论文**: "LLM-Based Scoring of Narrative Memories Reveals That Emotional Arousal Enhances Central Information at the Expense of Peripheral Information"
- **来源**: IEEE ICDM Workshop 2025 (via Semantic Scholar, paperId: 1eb6aff2)
- **核心**:
  - **直接用 LLM 对叙事记忆进行评分**
  - 发现：情绪唤醒度高的叙事，核心信息（central details）更丰富，但外围信息（peripheral details）被牺牲
  - 验证了 LLM 可以区分叙事中不同层次的信息密度
- **VSNC 启示**:
  - **这是目前找到的与 VSNC 最直接对标的论文**：别人已经在做"用 LLM 评分叙事记忆质量"
  - 情绪唤醒 → 核心/外围信息分化，恰好印证我们 v0.5 情绪唤醒度检测器的设计逻辑
  - 可以用同样的 central/peripheral 分析框架来评估阿宝回忆叙事
  - 必须在论文 Related Work 中引用
- **验证等级**: V1（仅 Semantic Scholar 确认，待获取全文深读）

#### 12. Automated MMI Scoring — Multi-agent Prompting (2026-02)
- **论文**: "Automated Multiple Mini Interview (MMI) Scoring"
- **链接**: https://arxiv.org/abs/2602.02360
- **核心**:
  - 多 agent prompting 框架：transcript refinement → criterion-specific scoring
  - 3-shot in-context learning，Avg QWK 0.62 vs fine-tuned baseline 0.32
  - 在 ASAP benchmark 上泛化性能可比 domain-specific SOTA
- **VSNC 启示**:
  - **multi-agent scoring pipeline 设计直接可参考**：先 transcript refinement（对应我们的 ASR → 文本清洗），再 criterion-specific scoring（对应叙事维度评分）
  - 验证了"结构化 prompt engineering > 重度 fine-tuning"在主观评分任务上的优势
  - 与 CheckEval (#1) + AutoChecklist (#2) 形成 LLM 评分方法论三角验证
- **验证等级**: V2（arXiv + ASAP benchmark 交叉验证）

#### 13. PTSD Severity Estimation with LLMs (2026-02)
- **论文**: "A Systematic Evaluation of LLMs for PTSD Severity Estimation"
- **链接**: https://arxiv.org/abs/2602.06015
- **核心**:
  - 1,437 个体，11 个 SOTA LLMs 系统性评估
  - **关键发现**: 提供详细 construct definitions + narrative context 时 LLM 最准确
  - Reasoning effort ↑ → 准确度 ↑
  - 开源模型 >70B 参数后性能 plateau；闭源模型（o3-mini, gpt-5）持续提升
  - **Ensemble (supervised + zero-shot LLM) = 最佳**
- **VSNC 启示**:
  - **直接指导我们的 hybrid scoring 架构设计**：rule-based (supervised) + LLM (zero-shot) ensemble
  - "Detailed construct definitions" = 我们需要为每个叙事评分维度写精确定义
  - Reasoning model 优势再次确认（与 #3 Healthcare LLM-Judge 一致）
  - 样本量 1,437 给了 VSNC pilot study 设计参考
- **验证等级**: V2（大规模系统性评估）

### 新 Pillar B: ASR + 语音生物标志物

#### 14. ★★★ SeniorTalk — 中国超高龄老年人对话数据集 (2025-03)
- **论文**: "SeniorTalk: A Chinese Conversation Dataset with Rich Annotations for Super-Aged Seniors"
- **链接**: https://arxiv.org/abs/2503.16578
- **核心**:
  - **55.53 小时**语音，101 场自然对话，**202 人（75 岁以上）**
  - 性别/地区/年龄均衡
  - 多维度标注：speaker verification, diarization, ASR, speech editing
  - 含方言特征标注
- **VSNC 启示**:
  - **直接解决 VSNC 缺少中文老年语音评估 benchmark 的痛点**
  - 可以用 SeniorTalk 评估 Dolphin (#4) 在中国老年人语音上的 WER
  - 方言变异数据可用于验证多方言 ASR 的泛化性
  - 75+ 年龄段 = 阿宝目标用户群
  - 必须确认数据公开可下载
- **验证等级**: V1（论文声称公开，需验证获取路径）

#### 15. PARLO Dementia Corpus — 德语多中心 AD 资源 (2026-03)
- **论文**: "The PARLO Dementia Corpus: A German Multi-Center Resource for Alzheimer's Disease"
- **链接**: https://arxiv.org/abs/2603.03471
- **核心**:
  - 9 家德国学术记忆诊所，MCI + mild-moderate AD + 健康对照
  - 8 项标准化神经心理学任务：confrontation naming, verbal fluency, word repetition, picture description, story reading, **recall tasks**
  - 含 ASR benchmarking + automated test evaluation + **LLM-based classification** baseline
  - **recall-driven speech production 诊断价值最高**
- **VSNC 启示**:
  - 方法论跨语言参考：他们的 8 项任务测试 battery 设计可参考
  - **recall-driven speech production 诊断价值 > 其他任务** — 与我们"回忆叙事"为核心的设计方向一致
  - LLM-based classification baseline 可用于比较
  - 跨语言研究合作方向
- **验证等级**: V2（多中心 + 公开数据集）

#### 16. MINT — MRI-to-Speech Knowledge Transfer (2026-02)
- **论文**: "MINT: Multimodal Imaging-to-Speech Knowledge Transfer for Early Alzheimer's Screening"
- **链接**: https://arxiv.org/abs/2602.23994
- **核心**:
  - 将 MRI 脑影像的 biomarker 结构迁移到语音编码器
  - **推理时只需语音，不需要扫描仪**
  - AUC 0.720 (speech aligned) vs 0.711 (speech only baseline)
  - 多模态融合 AUC 0.973
- **VSNC 启示**:
  - **概念启发**：如果有临床合作，可以用类似方法将神经影像 ground truth 迁移到语音/文本特征
  - 当前 VSNC 不涉及 MRI，但该方法论验证了"语音中携带认知状态信息"的假设
  - 长期方向：语音 → 认知状态推断的 grounding
- **验证等级**: V2（ADNI-4 数据集验证）

### 新 Pillar D: 语音+NLP 痴呆检测前沿

#### 17. SpeechCARE — NIA PREPARE Challenge 最佳方案 (2025-11)
- **论文**: "SpeechCARE: Early Detection of Cognitive Impairment via Multimodal Speech Processing"
- **链接**: https://arxiv.org/abs/2511.08132
- **核心**:
  - 多模态 pipeline：pretrained acoustic + linguistic transformer + demographic
  - **MoE (Mixture of Experts) 动态融合架构**
  - LLM-based anomaly detection + task identification 预处理
  - SHAP 可解释性 + LLM reasoning
  - AUC=0.88, F1=0.72 (HC/MCI/AD); AUC=0.90 for MCI detection
- **VSNC 启示**:
  - **Pipeline 架构高度参考价值**：acoustic + linguistic + metadata 三路融合
  - MoE 动态融合 → VSNC 可以用类似方法融合 rule-based + LLM + acoustic features
  - LLM-based anomaly detection 预处理 → 我们可以用 LLM 预处理 ASR 转写中的异常
  - F1=0.72 on 3-class = 当前 SOTA，VSNC 可对标
- **验证等级**: V2（NIA PREPARE Challenge 评测）

#### 18. Speech-Based Cognitive Screening: LLM Adaptation Strategies (2025-08)
- **论文**: "Speech-Based Cognitive Screening: A Systematic Evaluation of LLM Adaptation Strategies"
- **链接**: https://arxiv.org/abs/2509.03525
- **核心**:
  - 9 text-only + 3 multimodal audio-text LLMs
  - 适配策略：ICL, reasoning-augmented prompting, PEFT, multimodal integration
  - **class-centroid demonstrations = 最佳 ICL 策略**
  - Reasoning 改善小模型性能
  - Token-level fine-tuning 一般最优
  - **Adapted open-weight models ≥ commercial systems**
- **VSNC 启示**:
  - **LLM 适配策略实验设计直接可复用**
  - class-centroid ICL 可用于 VSNC 叙事评分的 few-shot 示例选择
  - 验证了 open-weight models 经适配后可匹配商业系统 → 支持我们用本地部署开源模型
- **验证等级**: V2（DementiaBank 评测）

#### 19. LLMCARE — LLM 合成数据增强认知筛查 (2025-08)
- **论文**: "LLMCARE: Early Detection of Cognitive Impairment via Transformer Models Enhanced by LLM-Generated Synthetic Data"
- **链接**: https://arxiv.org/abs/2508.10027
- **核心**:
  - Transformer embeddings + handcrafted linguistic features + **LLM synthetic data augmentation**
  - 外部验证评估泛化性（MCI-only cohort）
- **VSNC 启示**:
  - **合成数据增强**：当 VSNC pilot 样本量不足时，可用 LLM 生成合成叙事样本扩充训练集
  - 外部验证设计可参考
- **验证等级**: V1（待深读 full paper）

#### 20. Conversational Robot Speech Biomarkers for Dementia (2025-02)
- **论文**: "Developing Conversational Speech Systems for Robots to Detect Speech Biomarkers of Cognition in People Living with Dementia"
- **链接**: https://arxiv.org/abs/2502.10896
- **核心**:
  - 6 种语音生物标志物：Altered Grammar, Pragmatic Impairments, Anomia, Disrupted Turn-Taking, Slurred Pronunciation, Prosody Changes
  - LLM fine-tuned for dementia 做实时对话
  - Composite biomarker > individual biomarkers
  - **Human-robot vs human-human 对话场景差异显著**
- **VSNC 启示**:
  - **6 种 speech biomarkers 框架可直接参考**：阿宝对话中可以实时提取这些指标
  - composite biomarker 方法 → VSNC 可以融合多维叙事指标为综合分
  - human-AI 对话 vs human-human 差异 → 阿宝作为 AI 对话系统，必须注意评分基线差异
  - **最接近 CittaVerse 产品形态的论文**（conversational AI + speech biomarkers + real-time）
- **验证等级**: V2（DementiaBank + Indiana 两个数据集）

### Parking Lot 补充: Neuro-symbolic

#### 21. Sentience Quest — Hybrid Neuro-symbolic Memory Architecture (2025-05)
- **论文**: "Sentience Quest: Towards Embodied, Emotionally Adaptive, Self-Evolving AGI"
- **链接**: https://arxiv.org/abs/2505.12229
- **核心**:
  - 认知架构整合：Global Workspace Theory (Baars) + Somatic Mind (Damasio) + IIT (Tononi) + Narrative Self (Hofstadter)
  - **Hybrid neuro-symbolic memory**: 将 AI 生命事件记录为 structured dynamic story objects
  - Story Weaver workspace 用于内部叙事与自适应目标追踪
- **VSNC 启示**:
  - 概念层面参考：structured story objects 与我们的叙事分块+评分有映射关系
  - neuro-symbolic memory 的"事件→故事对象"转换 = 我们的"回忆→叙事结构"提取
  - 偏理论/愿景论文，实际可落地技术有限
- **验证等级**: V0（理论框架，无实验验证）

---

## Evidence Quality Summary

| # | 论文 | 直接相关度 | 验证等级 | 对 VSNC Pillar | 新增/已有 |
|---|------|-----------|---------|---------------|----------|
| 11 | LLM Narrative Memory Scoring | ★★★ | V1 | A (核心对标) | 新增 |
| 12 | MMI Multi-agent Scoring | ★★☆ | V2 | A (架构参考) | 新增 |
| 13 | PTSD LLM Severity Estimation | ★★★ | V2 | A (方法论) | 新增 |
| 14 | SeniorTalk 中国老年语音 | ★★★ | V1 | B (benchmark) | 新增 |
| 15 | PARLO Dementia Corpus | ★★☆ | V2 | B+D (跨语言) | 新增 |
| 16 | MINT MRI-to-Speech | ★☆☆ | V2 | 长期方向 | 新增 |
| 17 | SpeechCARE | ★★★ | V2 | B+D (pipeline) | 新增 |
| 18 | LLM Adaptation for Screening | ★★★ | V2 | A+D (策略) | 新增 |
| 19 | LLMCARE Synthetic Data | ★★☆ | V1 | D (增强) | 新增 |
| 20 | Robot Speech Biomarkers | ★★★ | V2 | B+D (产品形态) | 新增 |
| 21 | Sentience Quest | ★☆☆ | V0 | 理论参考 | 新增 |

---

## 两轮累计覆盖 (21 篇)

| Pillar | 第 1 轮 | 第 2 轮 | 合计 | 核心缺口 |
|--------|--------|--------|------|---------|
| A: LLM-as-Judge 混合评分 | 3 | 3 | 6 | 中文叙事实验验证 |
| B: 多方言 ASR | 2 | 2 | 4 | SeniorTalk 获取+实测 |
| C: 事件边界/叙事分割 | 2 | 0 | 2 | 已较充分 |
| D: 叙事 NLP 前沿+竞品 | 3 | 4 | 7 | 持续跟踪 |
| 长期/理论 | 0 | 2 | 2 | 不紧急 |

---

## Implications for VSNC v0.6 (增量更新)

### 即刻可行动

1. **获取 SeniorTalk 数据集** (#14) → 用于评估 Dolphin ASR 在中国老年人语音上的 WER（RB-001 解阻）
2. **获取 LLM Narrative Memory Scoring 全文** (#11) → 理解 central/peripheral 评分框架，直接对标 VSNC 评分设计
3. **多 agent scoring pipeline 设计参考** (#12 MMI + #13 PTSD + 第 1 轮 #1 CheckEval):
   - transcript refinement → criterion-specific scoring → ensemble
   - 提供 detailed construct definitions 提升 LLM 准确度
   - rule-based + zero-shot LLM ensemble = 最优

### 中期规划

4. **Speech biomarker 框架** (#20): 在阿宝对话中实时提取 6 种语音生物标志物
5. **SpeechCARE MoE 架构** (#17): 三路（acoustic + linguistic + metadata）动态融合
6. **LLM 合成数据增强** (#19): pilot 样本不足时用 LLM 生成合成叙事训练数据

### 论文写作

7. Related Work 必须新增引用:
   - #11 LLM Narrative Memory Scoring (最直接对标)
   - #14 SeniorTalk (中文老年语音 benchmark)
   - #15 PARLO (recall-driven speech production 诊断价值)
   - #17 SpeechCARE (SOTA pipeline)

---

## Confidence / Uncertainty

- **高置信**: LLM 评分叙事记忆方向已有初步验证 (#11)，与我们路线一致（V1-V2）
- **高置信**: 中文老年语音数据集存在且可能公开 (#14)（V1，需确认获取）
- **高置信**: multi-agent scoring + detailed construct definitions = 最佳 LLM 评分策略（V2，多来源交叉）
- **中置信**: speech biomarkers 实时提取在 AI 对话场景的可行性 (#20)（V2，但非中文验证）
- **低置信**: neuro-symbolic memory 对 VSNC 的实际可落地价值 (#21)（V0）

---

## Research Backlog 更新建议

| ID | 主题 | 优先级 | 状态 | 备注 |
|----|------|--------|------|------|
| RB-006 | SeniorTalk 数据集获取与评估 | P1 | 🟢 可执行 | 解阻 RB-001 |
| RB-007 | LLM Narrative Memory Scoring 全文深读 | P1 | 🟢 可执行 | VSNC 核心对标 |
| RB-008 | Speech Biomarker 框架中文适配评估 | P2 | 🟢 可执行 | 产品增值 |
| RB-009 | Multi-agent Scoring Pipeline 详细设计 | P1 | 🟡 待 Core 启动 | A 架构升级 |

---

## Next Owner / Handoff

本轮为储备文献阅读，不产生直接 handoff。成果供以下消费者使用:

- **Hulk 自身**: RB-006/007 为下次可执行的研究任务
- **Core**: SeniorTalk 数据集获取可能需要注册/申请
- **论文写作**: Related Work 新增 4 条引用
- **产品**: Robot Speech Biomarkers (#20) 框架对阿宝 V0.3+ 有直接产品启示
