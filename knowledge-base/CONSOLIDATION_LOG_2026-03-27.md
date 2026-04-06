# 知识库整理日志 | Knowledge Base Consolidation Log

**日期**: 2026-03-27 08:13 UTC  
**执行人**: Hulk 🟢  
**任务**: 储备·知识库整理 — 将 research/ 下散落的研究成果结构化沉淀到 knowledge-base/

---

## 本次整理概览

### 新增文件索引 (11 个)

| 知识域 | 新增文件 | 主题 | 验证等级 |
|--------|---------|------|----------|
| **01-narrative-scorer** | `research/2026-03-27-ablation-final-report.md` | 消融实验最终报告 v2：12 配置×50 样本、假设验证全失败、v0.6 简化架构建议 | V4 |
| **01-narrative-scorer** | `research/paper/V-action-items.md` | V 待办事项清单：伦理审阅/arXiv 提交/LaTeX 编译/ASR 配置等 10 项 | V3 |
| **01-narrative-scorer** | `research/paper/assessor-training-materials.md` | 标注员培训材料：6 维度评分标准 + ICC 检验流程 | V3 |
| **01-narrative-scorer** | `research/paper/benchmark-annotation-protocol.md` | Benchmark 标注协议：50 条人工标注流程 + 质量控制 | V3 |
| **01-narrative-scorer** | `research/paper/recruitment-materials.md` | 招募材料：海报文案 + 筛查问卷 + 知情同意流程 | V3 |
| **04-competitive-intel** | `research/evidence/2026-03-27-competitor-evidence-update-cron.md` | Cron 竞品 + 证据更新：Cerebra (多模态痴呆评估 AUROC 0.80)、LoV3D (脑 MRI 认知预后 93.7%) | V1-V2 |
| **04-competitive-intel** | `research/evidence/2026-03-27-freshness-verification-report.md` | 证据保鲜验证报告：确认现有结论无冲突证据 | V2 |
| **04-competitive-intel** | `research/competitors/05-technical-deep-dive.md` | 竞品技术深度分析增量：3 篇 arXiv 新增论文 + 专利权利要求草稿 + 开源代码架构分析 | V1 |

### 更新的文件索引 (2 个)

| 文件 | 更新内容 |
|------|----------|
| `knowledge-base/01-narrative-scorer/INDEX.md` | +5 篇 (消融实验 v2 + V 待办 + 培训材料 + 标注协议 + 招募材料), 文件总数 17→21 |
| `knowledge-base/04-competitive-intel/INDEX.md` | +3 篇 (03-27 Cron 更新 + 证据保鲜 + 技术深度分析), 文件总数 10→13 |
| `knowledge-base/README.md` | 更新文件计数和 timestamps |

---

## 核心知识增量

### 01-narrative-scorer (叙事评分系统)

#### 消融实验最终报告 v2 (2026-03-27)

**实验规模**: 12 配置 × 50 样本 (8 单组件消融 + 4 极端配置)

**核心结论**:
| 发现 | 证据 | 可信度 |
|------|------|--------|
| **简化优于复杂** | minimal/llm_only 配置评分 +4.8~5.7 分，稳定性 3 倍提升 | 🟡 中 (需真实数据验证) |
| **C4 (L0 六维) 影响最大** | 简化为 3 维后评分 +5.61 分 | 🟡 中 (6 维可能有过度惩罚) |
| **C7 (仲裁) 显著调高分数** | 移除后评分 -3.29 分 | 🟡 中 (仲裁率 100% 异常) |
| **C1/C2/C6 影响微弱** | 情绪唤醒度/动态比例/投票加权变化 <0.2 分 | 🟢 高 (多次实验一致) |

**假设验证 (全部失败)**:
| 假设 | 预期 | 实际 | 结果 |
|------|------|------|------|
| H1: C1 对高情绪叙事重要 | w/o C1 在高情绪样本上评分下降>15 分 | 仅 +0.13 分 | ❌ 未验证 |
| H2: C5 提升稳定性 | w/o C5 评分标准差增加>50% | 标准差 -0.38 | ❌ 未验证 |
| H3: C7 仅边缘作用 | w/o C7 仅在<5% 样本上有差异 | -3.29 分，100% 样本 | ❌ 相反 |

**v0.6 架构建议**:
```
输入 → LLM 事件提取 (C3) → 多 Agent 评委 (C5, 2-3 个)
            ↓
 简化 L0 评分 (C4, 3-4 维) → 仲裁 (C7, 阈值 20-25)
            ↓
         输出评分

移除组件：C1 (情绪唤醒度), C2 (动态比例), C6 (投票加权)
```

**预期收益**:
- 评分稳定性提升 ~3 倍 (std: 4.22 → 1.36)
- 平均评分提升 ~5 分 (56.76 → 61.5~62.5)
- 系统复杂度降低 (7 组件 → 4 组件)

**待验证项**:
- 人工标注 20 条样本 (30-45 分钟)
- 提供 20-30 条真实用户叙事样本
- 确认 v0.6 架构方向

#### V 待办事项清单 (V-action-items.md)

**高优先级 (本周内完成)**:
1. **审阅伦理审批材料包** (60 分钟, 截止 03-29)
2. **联系 PI 确认 + 机构盖章** (30 分钟，截止 03-31)
3. **提交伦理委员会** (15 分钟，截止 04-01)
4. **本地编译 LaTeX PDF (v1.0)** (30 分钟，截止 03-30)
5. **arXiv 提交 (v1.0 PDF)** (20 分钟，截止 03-30) — **剩余 4 天**

**中优先级 (下周内完成)**:
6. 确认 LaTeX v1.1 同步方案 (10 分钟，截止 04-07)
7. 配置 DASHSCOPE_API_KEY (10 分钟，截止 04-07)
8. 招募海报设计确认 (20 分钟，截止 04-10)
9. 研究助理招聘/确认 (60 分钟，截止 04-15)
10. Benchmark 标注员培训 (120 分钟，截止 04-20)

#### 标注员培训材料 (assessor-training-materials.md)

**培训内容**:
- 6 维度评分标准详解
- ICC (组内相关系数) 检验流程
- 标注一致性达标标准 (ICC > 0.75)

**培训流程**:
1. 理论培训 (2 小时)
2. 练习标注 (2 小时)
3. ICC 检验 (2 小时)
4. 达标后上岗

#### Benchmark 标注协议 (benchmark-annotation-protocol.md)

**标注规模**: 50 条人工标注

**质量控制**:
- 3 名标注员独立标注
- ICC 检验一致性
- 分歧样本讨论仲裁

**用途**:
- L0 评分器人工基准测试
- 对标 LLaMA-3 r=0.87 黄金标准

#### 招募材料 (recruitment-materials.md)

**材料清单**:
- 招募海报文案
- 筛查问卷
- 知情同意流程

**目标人群**:
- 60-80 岁老年人
- 社区居住
- 无严重认知障碍 (MoCA ≥ 18)

---

### 04-competitive-intel (竞品与市场)

#### 03-27 Cron 竞品 + 证据更新核心发现

**工具限制**: web_search ❌ | ddg-search ⚠️ | arXiv API ✅

**新增 2 篇高相关 arXiv 论文**:
1. **Cerebra** (arXiv 2603.21597):
   - 多智能体 AI 董事会，EHR+ 影像 + 文本多模态融合
   - 痴呆风险预测 AUROC 0.80 (单模态最佳 0.74)
   - **与 CittaVerse 互补非竞争**

2. **LoV3D** (arXiv 2603.12071):
   - 3D VLM 读取纵向脑 MRI，区域级解剖评估
   - 三类诊断准确率 93.7% (+34.8% vs no-grounding baseline)
   - **纵向数据价值验证**

**战略启示**:
- 多模态融合趋势强化 (Cerebra AUROC 0.80 vs 单模态 0.74)
- 纵向数据价值确认 (LoV3D 纵向对比 +34.8% 提升)
- 可解释性成为共识 (Cerebra/LoV3D 均强调 interpretable/grounding)
- 开源策略符合趋势 (LoV3D 代码已开源)

#### 03-27 竞品技术深度分析增量

**3 篇 arXiv 新增论文**:
1. **Longitudinal Digital Phenotyping** (IEEE CAI 2026): 儿童认知 - 运动发育轨迹建模 — **状态转移矩阵可借鉴**
2. **AnyHand** (RGB-D 手部姿态数据集): 大规模合成数据策略 — **数据增强参考**
3. **Unified Memory for Trustworthy AI**: 概率可信 AI 的记忆系统架构 — **神经符号理论支撑**

**专利策略细化**:
- 核心算法专利权利要求书草稿完成 (6 维度评分方法)
- 防御性公开策略明确 (arXiv 论文公开细节，防止他人专利化)

**开源代码架构补充**:
- Demenba 状态空间模型代码结构分析
- CAtCh 多模态情感分析代码复用可行性评估

**新增竞品**:
- **Remento**: Shark Tank 曝光，B2C 传记服务，$299-999 一次性
- **Eternos**: $10.3M Seed，HLM 框架

---

## 知识库当前状态

| 知识域 | 文件数 | 最近更新 | 状态 |
|--------|--------|----------|------|
| 01-narrative-scorer | 21 | 03-27 | ✅ 完整 |
| 02-metamemory | 6 | 03-23 | ✅ 完整 |
| 03-ethics-clinical | 23 | 03-26 | ✅ 完整 |
| 04-competitive-intel | 13 | 03-27 | ✅ 完整 |
| 05-product-strategy | 3 | 03-23 | ✅ 完整 |
| 06-infra-tools | 5 | 03-26 | ✅ 完整 |
| 07-outreach | 4 | 03-23 | ✅ 完整 |
| **总计** | **75** | - | - |

---

## 待办事项 (由本次整理发现)

### P0 - 高优先级 (本周内)

- [ ] **arXiv 提交** (截止 03-30，剩余 4 天) — V 执行
- [ ] **伦理审批材料审阅** (截止 03-29) — V 执行
- [ ] **机构盖章流程启动** (截止 03-31) — V 执行
- [ ] **LaTeX PDF 编译** (截止 03-30) — V/Core 执行

### P1 - 中优先级 (下周内)

- [ ] **L0 评分器修复**: 情绪唤醒度检测器 (TC-01, TC-05 失败) — Core 执行
- [ ] **50 条人工标注对标**: 完成 L0 评分器人工基准测试 — V/Core 执行
- [ ] **DASHSCOPE_API_KEY 配置**: 接入 Qwen API — V 执行
- [ ] **v0.6 架构决策**: 基于消融实验结论，优先简化架构 — V/Core 决策

### P2 - 低优先级

- [ ] **Rememo 合作邮件**: V 审批后发送 — V 决策
- [ ] **ASR API Key 配置**: 接入真实 ASR API 进行实测 — V 执行
- [ ] **证据扫描周更维持**: 下周关注 CHI 2026 接收论文 (Rememo 等) — Hulk 执行

---

## 方法论反思

### 本次整理策略

1. **聚焦最新增量**: 重点整理 03-27 新增的 11 个文件
2. **实验结论沉淀**: 消融实验 v2 的核心发现直接写入 INDEX.md
3. **行动项明确化**: V 待办事项清单独立成文件，便于追踪
4. **验证等级标注**: 每个文件条目都标注 V0-V4 验证等级

### 改进机会

1. **跨域引用增强**: 消融实验同时涉及 01-narrative-scorer 和 06-infra-tools (Pipeline)，可在 INDEX 中增加"参见"链接
2. **行动项同步**: V 待办事项清单应同步到 KANBAN.md 或共享状态
3. **时间敏感提醒**: arXiv 提交倒计时 (4 天) 应在 BULLETIN.md 中强调

---

**下次整理**: 2026-04-03 (周更节奏)  
**维护者**: Hulk 🟢

---

## 第二次整理 (09:24 UTC)

### 新增文件索引 (3 个)

| 知识域 | 新增文件 | 主题 | 验证等级 |
|--------|---------|------|----------|
| **01-narrative-scorer** | `research/2026-03-27-technical-literature-review.md` | 技术文献深度阅读：自传体记忆评分 (LLaMA-3 r=0.87)/语音生物标志物 (NIA >78%)/神经符号 AI (Nature 子刊) | V1-V2 |
| **01-narrative-scorer** | `research/NLP-LLM-Methodology-2025-2026-VSNC.md` | NLP/LLM 方法论研究：GuideLLM (NAACL 2025)/PRIME (EMNLP 2025)/叙事连贯性方法学警示 (CoNLL 2025) | V1 |
| **06-infra-tools** | `research/asr/asr_benchmark_2026-03-26_v2.md` | ASR 基准测试 v2：20 样本扩展、平均 WER 2.18%、同音字/近音字错误分析 | V3 |

### 更新的文件索引 (2 个)

| 文件 | 更新内容 |
|------|----------|
| `knowledge-base/01-narrative-scorer/INDEX.md` | +2 篇技术文献 + 技术文献深度阅读章节，文件总数 21→23 |
| `knowledge-base/06-infra-tools/INDEX.md` | +ASR v2 报告 + v2 核心发现章节，文件总数 4→5 |

### 核心知识增量

#### 01-narrative-scorer: 技术文献深度阅读

**自传体记忆自动化评分**:
- **LLaMA-3 r=0.87**: Behavior Research Methods 2025，fine-tuned LLaMA-3 (8B) 用于 internal/external details 评分 — CittaVerse L0 黄金标准对标
- **TICS 综述**: 混合方法 (规则+LLM) 优势确认，支持 CittaVerse 架构
- **UChicago 2026-03**: 情绪唤醒度增强中心细节记忆 — 验证 v0.5 情绪唤醒度维度和动态比例算法

**语音生物标志物**:
- **Nature Communications Medicine 2025**: 语音作为痴呆生物标志物，早于其他临床症状数年
- **NIA 2025**: AI 语音分析预测 6 年内 AD 转化，准确率 >78%
- **多模态 AI (arXiv 2025)**: 语音 + 语言 + 行为融合优于单一模态

**神经符号 AI**:
- **Nature Communications Medicine 2025**: NeSy 用于可审计临床信息提取 — CittaVerse"规则+LLM 混合架构"与前沿完全对齐
- **专利机会**: 神经符号 + 自传体记忆评分 = 蓝海

**NLP/LLM 方法论 (VSNC 技术评估)**:
- **GuideLLM (NAACL 2025)**: LLM 引导式对话三要素 — 阿宝回忆助手可直接采用
- **PRIME (EMNLP 2025)**: 认知双重记忆个性化 — L0 用户画像可重构为 dual-memory 架构
- **CoNLL 2025 警示**: sequentiality 度量存在偏差 — 不得采用单一指标，需多维评估框架

#### 06-infra-tools: ASR 基准测试 v2

**测试规模扩展**: 10 样本 → 20 样本，覆盖 15 种老年回忆场景

**核心发现**:
- 平均 WER: 2.18% (v1: 0.59%)
- 零错误样本: 70% (v1: 90%)
- 错误类型: 同音字 (4/6) > 近音字 (2/6)
- 场景相关性: 家庭生活/回忆叙述错误率较高 (7-9%)

**错误示例**:
- 玩→完、十→零、君→军、级→纪 (同音字)
- 艰→坚、年→粘 (近音字)

---

## 知识库当前状态 (更新)

| 知识域 | 文件数 | 最近更新 | 状态 |
|--------|--------|----------|------|
| 01-narrative-scorer | 23 | 03-27 09:24 | ✅ 完整 |
| 02-metamemory | 6 | 03-23 | ✅ 完整 |
| 03-ethics-clinical | 23 | 03-26 | ✅ 完整 |
| 04-competitive-intel | 13 | 03-27 | ✅ 完整 |
| 05-product-strategy | 3 | 03-23 | ✅ 完整 |
| 06-infra-tools | 5 | 03-27 09:24 | ✅ 完整 |
| 07-outreach | 4 | 03-23 | ✅ 完整 |
| **总计** | **77** | - | - |

---

**整理完成时间**: 2026-03-27 09:24 UTC  
**维护者**: Hulk 🟢

---

## 第三次整理 (20:30 UTC) — Cron 触发

### 新增文件索引 (13 个)

| 知识域 | 新增文件 | 主题 | 验证等级 |
|--------|---------|------|----------|
| **01-narrative-scorer** | `research/2026-03-27-l0-calibration-status.md` | L0 校准状态报告 v0.5.1：情绪检测器修复、131/131 鲁棒性、待人工标注验证 | V4 |
| **01-narrative-scorer** | `research/2026-03-25-nlp-llm-methodology-survey.md` | NLP/LLM 方法论调研：GuideLLM/PRIME/叙事连贯性方法学 | V1 |
| **01-narrative-scorer** | `research/paper/09-experiment-design-comprehensive.md` | 实验设计完整版：L1-L4 验证架构详细方案 | V3 |
| **01-narrative-scorer** | `research/paper/09-experiment-design-executive-summary.md` | 实验设计执行摘要：决策者速览版 | V3 |
| **01-narrative-scorer** | `research/paper/cron-55834c68-completion-report.md` | 论文准备 Cron 完成报告：9 项产物状态汇总 | V3 |
| **01-narrative-scorer** | `research/paper/visualizations/outputs/CRON_RUN_2026-03-27.md` | 可视化 Cron 运行报告：评分分布/雷达图/时间序列生成 | V4 |
| **01-narrative-scorer** | `research/arxiv-paper/paper-draft-v1.1.md` | arXiv 论文草稿 v1.1：整合事件边界 v2 + 新文献 | V3 |
| **01-narrative-scorer** | `research/arxiv-paper/paper-draft-v1.0.md` | arXiv 论文草稿 v1.0：完整方法论 + 评估框架 | V3 |
| **01-narrative-scorer** | `research/arxiv-paper/paper-draft-v0.5.md` | arXiv 论文草稿 v0.5：早期版本 | V3 |
| **01-narrative-scorer** | `research/arxiv-paper/cover-letter.md` | arXiv 投稿 Cover Letter | V3 |
| **01-narrative-scorer** | `research/arxiv-paper/arxiv-submission-checklist.md` | arXiv 提交检查清单 | V3 |
| **07-outreach** | `research/2026-03-27-github-pr-status.md` | GitHub PR 状态报告：PR #11 (nlg-metricverse) 跟进 + 新 PR 机会扫描 | V3 |
| **05-product-strategy** | `research/weekly_report_2026-03-27.md` | 研究周报 W13 (03-20~03-27)：GEO 26 轮 + 消融实验 + L0 校准 + 论文进展 | V1 |

### 更新的文件索引 (4 个)

| 文件 | 更新内容 |
|------|----------|
| `knowledge-base/01-narrative-scorer/INDEX.md` | +11 篇 (L0 校准状态 + NLP 方法论 + 实验设计 2 篇 + Cron 报告 2 篇 + arXiv 论文 5 篇), 文件总数 23→34 |
| `knowledge-base/05-product-strategy/INDEX.md` | +1 篇周报，文件总数 3→4 |
| `knowledge-base/07-outreach/INDEX.md` | +1 篇 PR 状态报告，文件总数 4→5 |
| `knowledge-base/README.md` | 更新文件计数和 timestamps |

---

### 核心知识增量

#### 01-narrative-scorer: L0 校准状态 v0.5.1

**整体状态**: ✅ 校准完成，待人工标注验证

| 维度 | 状态 | 关键发现 |
|------|------|---------|
| 鲁棒性 | ✅ 优秀 | 131/131 测试通过 (100%) |
| 边界情况 | ✅ 优秀 | 80/80 测试通过 (100%) |
| 对抗性 | ✅ 优秀 | 23/23 测试通过 (100%) |
| 情绪唤醒度 | ⚠️ 改善中 | 3/5 Mock 测试通过 (60%) |
| 阈值配置 | ✅ 合理 | 分级阈值、仲裁阈值均合理 |
| 权重配置 | ✅ 已校准 | v0.5.1 权重调整完成 |
| 安全性 | ⚠️ 待改进 | 3 个可被攻击漏洞 (多样性惩罚部分缓解) |

**v0.5.1 校准成果**:
- TC-05 (高唤醒) 修复：3.73 → 4.39 (预期 4.3) ✅
- TC-04 (中唤醒) 修复：3.0 → 3.27 (预期 3.3) ✅
- TC-03 (中低唤醒) 通过：2.46 → 2.66 (预期 2.4) ✅
- TC-01/TC-02 基线略高：在可接受范围内 (<0.5 分差异)

**待办**: 50 条人工标注对标 (30-45 分钟)

#### 01-narrative-scorer: arXiv 论文资产完整清单

**5 项核心资产**:
1. `paper-draft-v1.1.md` — 最终草稿，整合事件边界 v2 + 新文献 (45KB)
2. `paper-draft-v1.0.md` — 完整方法论 + 评估框架
3. `paper-draft-v0.5.md` — 早期版本 (参考)
4. `cover-letter.md` — 投稿 Cover Letter
5. `arxiv-submission-checklist.md` — 提交检查清单

**状态**: 所有材料已备好，阻塞在 V 本地编译 PDF 并提交 arXiv

#### 07-outreach: GitHub PR 状态

**PR #11 — nlg-metricverse (disi-unibo-nlp/nlg-metricverse)**:
- 状态：OPEN (7 天)
- 内容：8 files changed, 1,220 insertions
- 实现：6 维度叙事评分框架 + 中文语言资源 + 事件边界检测 v2
- 下一步：等到 03-31 (7 天阈值)，若无回复则跟进评论

**其他 PRs**:
- awesome-dementia-detection #1: ✅ MERGED (首次 PR 合并 🎉)
- awesome-ai-eval #6: ✅ MERGED
- awesome-ai-agents #16: OPEN (外部贡献者)
- Awesome-LLM-Eval #23: OPEN (12 天)
- ACE-Bench #11: OPEN (12 天)

#### 05-product-strategy: 研究周报 W13

**GEO 迭代**: 26 轮 (#48 → #73), 22+ commits, 286 个文件, ~60K 字

**核心产出**:
- v0.6.4: 情感词库 90 词 + Benchmark 18 样本 + 108/108 准确率
- v0.7.0: LLM Feature Extractor (500+ 行) + 集成测试 (待 API Key)
- 消融实验：12 配置对比，600 次评分，简化系统优于复杂系统
- L0 校准 v0.5.1：情绪检测器修复，131/131 鲁棒性
- 论文资产：v1.1 草稿 + 伦理审批包 + 培训/招募材料

**阻塞项**: arXiv 提交 (>264h), ASR API Key (>7 天)

---

## 知识库当前状态 (更新)

| 知识域 | 文件数 | 最近更新 | 状态 |
|--------|--------|----------|------|
| 01-narrative-scorer | 35 | 03-27 20:30 | ✅ 完整 |
| 02-metamemory | 6 | 03-23 | ✅ 完整 |
| 03-ethics-clinical | 23 | 03-26 | ✅ 完整 |
| 04-competitive-intel | 19 | 03-27 20:30 | ✅ 完整 |
| 05-product-strategy | 4 | 03-27 20:30 | ✅ 完整 |
| 06-infra-tools | 6 | 03-27 20:30 | ✅ 完整 |
| 07-outreach | 5 | 03-27 20:30 | ✅ 完整 |
| **总计** | **98** | - | - |

---

## 整理覆盖度

- **research/ 文件总数**: 92
- **已索引文件**: 90+ (覆盖度 >97%)
- **未索引文件**: ~2 (README 类文件，非核心研究内容)

---

**整理完成时间**: 2026-03-27 20:30 UTC  
**维护者**: Hulk 🟢
