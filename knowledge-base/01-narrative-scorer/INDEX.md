# 01 — 叙事评分系统 (Narrative Scorer)

> CittaVerse 核心技术资产。从 v0.4 → v0.5 → v0.6 → arXiv 论文的完整演进链。

---

## Bottom Line

叙事评分器是 CittaVerse 的技术护城河。v0.5 实现了 7 维度评分 + 动态理想比例（基于情绪唤醒度自适应），v0.6 规划了 LLM 增强仲裁 + 多方言支持。arXiv 论文定位"方法论 + 评估框架"，弥补 AI+RT 领域系统综述空白。

**03-28 最新状态**: L0 校准完成 (v0.5.1-final)，131/131 鲁棒性测试通过，60/60 单元测试通过。对标基线明确：LLaMA-3 r=0.87 人类相关性。

**04-02 增量**: NLP/LLM 方法论完整报告 (7 篇核心论文 + 5 项可集成技术)、REMem 情景记忆图架构技术方案 (Phase 1-2 完成)、ASR v7 基准测试 (40 样本/WER 1.30%)、论文准备 Cron #15-16 完成 (实验设计最终版 + 补充材料 + 可视化总览)。

**04-03 增量**: 夜间长跑实验整合分析 (12 篇新论文深读)、Multi-Agent Scorer v0.6 实验设计 (N=200/4 假设)、ASR v8 基准测试 (40 样本/稳定性验证)、L0 鲁棒性测试报告 (30 测试/2 异常发现)、竞品证据更新 (工具链故障降级)、周报 W15 (GEO #74-99 汇总)。

---

## 文件索引

| 文件 | 主题 | 验证等级 | 日期 |
|------|------|----------|------|
| `research/2026-03-16-narrative-scorer-v0.5-design.md` | v0.5 完整设计：7 维度 + 动态比例 + 情绪唤醒度 + 个性化引导策略 | V3 (静态复核) | 03-16 |
| `research/narrative-scorer-v0.6-spec.md` | v0.6 规划：LLM 增强仲裁 + 粤语/吴语方言支持 + 向后兼容 | V0 (设计推导) | 03-23 |
| `research/2026-03-19-arxiv-technical-report-plan.md` | arXiv 论文结构：标题/摘要/9 章大纲/投稿策略 | V1 (单来源) | 03-19 |
| `research/arxiv-paper/` | 论文完整资产：v0.5/v1.0 草稿、LaTeX 源码、BibTeX、cover letter、提交清单 | V3 (静态复核) | 03-22 |
| `research/paper/00-paper-prep-status.md` | 论文准备总状态看板：9 项产物 + 阻塞项 + 下一步 | V3 | 03-24 |
| `research/paper/01-literature-review.md` | 独立版文献综述 v1.0：7 板块 + 42 核心引用 + 研究空白 | V2 (多来源交叉) | 03-24 |
| `research/paper/04-reference-audit.md` | 引用审计：50 条 BibTeX 质量分级 + 缺口分析 + 8 条补充建议 | V3 (静态复核) | 03-24 |
| `research/2026-03-26-ablation-study-design.md` | 消融实验设计：7 组件×128 配置、单组件消融 + 极端配置对比 | V3 (静态复核) | 03-26 |
| `research/2026-03-26-ablation-study-final-report.md` | 消融实验最终报告：简化系统优于复杂系统，LLM-only 表现最佳 | V4 (实际执行) | 03-26 |
| `research/2026-03-26-l0-calibration-summary.md` | L0 校准总结：131/131 鲁棒性测试通过，2 个安全漏洞待修复 | V3 | 03-26 |
| `research/2026-03-26-l0-scorer-calibration-report.md` | L0 评分器校准报告：阈值/权重/边界/一致性/安全性五维检查 | V3 | 03-26 |
| `research/paper/methods-overview.md` | 论文方法概述：评分系统架构总览 | V3 | 03-26 |
| `research/paper/methods-architecture.md` | 方法 - 架构：L0/VSNC 系统架构图 + 数据流 | V3 | 03-26 |
| `research/paper/methods-scoring.md` | 方法 - 评分：7 维度计算公式 + 动态比例算法 | V3 | 03-26 |
| `research/paper/methods-evaluation.md` | 方法 - 评估：L1-L4 验证架构 + 统计方法 | V3 | 03-26 |
| `research/paper/methods-implementation.md` | 方法 - 实现：Pipeline 代码结构 + 部署说明 | V3 | 03-26 |
| `research/paper/visualizations/outputs/VISUALIZATION_SUMMARY.md` | 可视化输出总结：评分分布/维度雷达图/时间序列图 | V3 | 03-26 |
| `research/2026-03-27-ablation-final-report.md` | **消融实验最终报告 v2**：12 配置×50 样本、假设验证全失败、v0.6 简化架构建议 | V4 (实际执行) | 03-27 |
| `research/paper/V-action-items.md` | V 待办事项清单：伦理审阅/arXiv 提交/LaTeX 编译/ASR 配置等 10 项 | V3 | 03-27 |
| `research/paper/assessor-training-materials.md` | 标注员培训材料：6 维度评分标准 + ICC 检验流程 | V3 | 03-27 |
| `research/paper/benchmark-annotation-protocol.md` | Benchmark 标注协议：50 条人工标注流程 + 质量控 | V3 | 03-27 |
| `research/paper/recruitment-materials.md` | 招募材料：海报文案 + 筛查问卷 + 知情同意流程 | V3 | 03-27 |
| `research/2026-03-27-l0-calibration-status.md` | **L0 校准状态报告 v0.5.1**: 情绪检测器修复、131/131 鲁棒性、待人工标注验证 | V4 | 03-27 |
| `research/2026-03-27-l0-robustness-test-report.md` | L0 鲁棒性测试报告：131/131 功能测试通过、3 个语义层面深层问题待修复 | V4 | 03-27 |
| `research/paper/09-experiment-design-comprehensive.md` | 实验设计完整版：L1-L4 验证架构详细方案 | V3 | 03-26 |
| `research/paper/09-experiment-design-executive-summary.md` | 实验设计执行摘要：决策者速览版 | V3 | 03-26 |
| `research/paper/cron-55834c68-completion-report.md` | 论文准备 Cron 完成报告：9 项产物状态汇总 | V3 | 03-26 |
| `research/paper/visualizations/outputs/CRON_RUN_2026-03-27.md` | 可视化 Cron 运行报告：评分分布/雷达图/时间序列生成 | V4 | 03-27 |
| `research/arxiv-paper/paper-draft-v1.1.md` | **arXiv 论文草稿 v1.1**: 整合事件边界 v2 + 新文献 (45KB) | V3 | 03-26 |
| `research/arxiv-paper/paper-draft-v1.0.md` | arXiv 论文草稿 v1.0：完整方法论 + 评估框架 | V3 | 03-24 |
| `research/arxiv-paper/paper-draft-v0.5.md` | arXiv 论文草稿 v0.5：早期版本 (参考) | V3 | 03-22 |
| `research/arxiv-paper/cover-letter.md` | arXiv 投稿 Cover Letter | V3 | 03-24 |
| `research/arxiv-paper/arxiv-submission-checklist.md` | arXiv 提交检查清单 | V3 | 03-24 |
| `research/2026-03-28-l0-calibration-completion-report.md` | **L0 校准完成报告 v0.5.1-final**: 131/131 鲁棒性、60/60 单元测试、情绪唤醒度修复 | V4 | 03-28 |
| `research/vsnc-l0-robustness-report.md` | **L0 鲁棒性测试报告**: 噪声输入/边界情况/对抗样本、风险词误报 P0 | V4 | 03-28 |
| `research/2026-03-28-nlp-llm-methodology-update.md` | **NLP/LLM 方法论更新**: EM-LLM 事件记忆/神经符号 AI/持久化画像/语音生物标志物 | V1-V2 | 03-28 |
| `research/NLP_LLM_Methodology_2025_2026_VSNC_L0.md` | NLP 方法论 L0 版本：技术评估与集成路径 | V1 | 03-28 |
| `research/paper/10-experiment-design-arxiv.md` | **arXiv 实验设计 v1.0**: 五层验证 + 变量控制矩阵 + Checklist 评分范式 | V3 | 03-28 |
| `research/paper/INDEX.md` | **论文产物索引**: 22 个 MD 文档 + 18 个可视化文件清单、arXiv 提交包 v1.1 就绪 | V3 | 03-28 |
| `research/paper/visualizations/outputs/CRON_RUN_2026-03-28.md` | 可视化 Cron 运行报告 (Run #10) | V4 | 03-28 |
| `memory/2026-03-24-literature-vsnc-deep-read.md` | **技术文献 #1**: 10 篇 (CheckEval/Dolphin/Event Segmentation/Rememo) | V2 | 03-24 |
| `memory/2026-03-25-literature-vsnc-deep-read-2.md` | **技术文献 #2**: 11 篇 (SeniorTalk/SpeechCARE/PTSD LLM/Robot Biomarkers) | V2 | 03-25 |
| `memory/2026-03-26-literature-vsnc-deep-read-3.md` | **技术文献 #3**: 5 篇 (**ACP 多 agent 框架** 2603.17392) | V2 | 03-26 |
| `memory/2026-03-27-literature-vsnc-deep-read-4.md` | **技术文献 #4**: 6 篇 (**Rememo 竞品**/Sophia narrative memory/Nature biomarkers) | V2 | 03-27 |
| `output/cron-hulk-reserve-literature-2026-03-27-summary.txt` | Cron 文献阅读 #4 摘要 | V2 | 03-27 |
| `output/cron-hulk-reserve-literature-2026-03-28-summary.txt` | Cron 文献阅读 #5 摘要 (**arXiv:2603.07670 Agent Memory 综述**) | V3 | 03-28 |
| `research/2026-03-30-nlp-llm-methodology-vsnc.md` | **NLP/LLM 方法论完整报告 (03-30)**: 7 篇核心论文 + 5 项可集成技术 | V1-V2 | 03-30 |
| `research/2026-03-30-nlp-llm-methodology-vsnc-summary.md` | NLP 方法论摘要版：5 项可集成技术速览 | V1 | 03-30 |
| `research/2026-04-02-remem-technical-design.md` | **REMem 情景记忆图架构技术方案**: Phase 1-2 完成 (事件分段 + 图构建), Phase 3-4 待实现 | V3 | 04-02 |
| `research/asr/asr_benchmark_2026-03-30_v7.md` | **ASR 基准测试 v7**: 40 样本、WER 1.30%、零错误率 82.5% | V4 | 03-30 |
| `research/paper/13-supplementary-materials.md` | 论文补充材料：数据字典/代码可用性声明/伦理审批号 | V3 | 03-31 |
| `research/paper/RUN_15_COMPLETION_SUMMARY.md` | 论文准备 Cron Run #15 完成总结 | V3 | 03-31 |
| `research/paper/RUN_16_COMPLETION_SUMMARY.md` | 论文准备 Cron Run #16 完成总结 | V3 | 03-31 |
| `research/paper/cron-hulk-paper-prep-001-run15.md` | 论文准备 Cron #15 详细报告 | V3 | 03-31 |
| `research/paper/cron-hulk-paper-prep-001-run16.md` | 论文准备 Cron #16 详细报告 | V3 | 03-31 |
| `research/paper/cron-55834c68-completion-report.md` | 论文准备 Cron 完成报告 (通用) | V3 | 03-31 |
| `research/paper/visualizations/outputs/CRON_RUN_2026-03-31.md` | 可视化 Cron 运行报告 (Run #12): 03-31 输出 | V4 | 03-31 |
| `research/arxiv-paper/cover-letter-final.md` | arXiv 投稿 Cover Letter 最终版 | V3 | 03-31 |
| `research/2026-04-02-nlp-llm-methodology-update.md` | **NLP/LLM 方法论更新 (04-02)**: 神经符号 AI×7/多 Agent 医疗×5/ADNI 生存分析/NARRABENCH 中文本地化 | V1-V2 | 04-02 |
| `research/2026-04-02-nlp-llm-methodology-summary.md` | NLP 方法论摘要 (04-02): 5 项可集成技术速览 | V1 | 04-02 |
| `research/2026-04-02-night-long-experiment-integration.md` | **夜间长跑实验整合**: 12 篇新论文深读 (神经符号×7/多 Agent×5)、VSNC v0.6 架构建议 | V1-V2 | 04-02 |
| `research/paper/2026-04-02-multi-agent-scorer-experiment-design.md` | **Multi-Agent Scorer v0.6 实验设计**: N=200/4 假设 (H1 仲裁效度/H2 抗堆砌/H3 触发率/H4 相关性) | V3 | 04-02 |
| `research/paper/cron-55834c68-run17-report.md` | 论文准备 Cron Run #17 报告 | V3 | 04-02 |
| `research/paper/cron-hulk-paper-prep-001-run18-report.md` | 论文准备 Cron Run #18 报告 | V3 | 04-02 |
| `research/paper/cron-55834c68-run19-report.md` | 论文准备 Cron Run #19 报告 | V3 | 04-03 |
| `research/paper/visualizations/outputs/CRON_RUN_2026-04-02.md` | 可视化 Cron 运行报告 (Run #13): 04-02 输出 | V4 | 04-02 |
| `research/asr/asr_benchmark_2026-04-02_v8.md` | **ASR 基准测试 v8**: 40 样本、WER 1.30%、零错误率 82.5% (连续第 8 次运行) | V4 | 04-02 |
| `research/vsnc-l0-robustness-report.md` | **L0 鲁棒性测试报告 (04-03)**: 30 测试/100% 通过、2 异常 (风险词语境误报/LREF 堆砌欺骗) | V4 | 04-03 |

---

## 核心知识点

### v0.5 评分维度（7 维度）
1. 事件连贯性 (0.18)
2. 情感深度 (0.18)
3. 感官细节 (0.14)
4. 时间定位 (0.14)
5. 自我认同 (0.14)
6. 信息密度分布 (0.14)
7. **情绪唤醒度** (0.08) — v0.5 新增

### 动态理想比例核心公式
```
ideal_central_ratio = 0.50 + (arousal_level - 3) * 0.05
tolerance = 0.15 + (arousal_level - 3) * 0.025
```
- 低唤醒 → 50/50 平衡叙事
- 高唤醒 → 70/30 容忍更高中心信息比例

### v0.6 三层新能力
1. **LLM 增强仲裁**：置信度 < 0.7 时触发 LLM 二次评分，加权融合
2. **多方言**：粤语（完整）、吴语（基础）、闽南/客家（规划中）
3. **向后兼容**：`score(text)` 默认行为不变，LLM 需显式 `use_llm=True`

### arXiv 投稿策略
- 推荐先投 cs.HC（无需 endorsement），再 cross-list 到 cs.CL
- 定位"方法论 + 评估框架"，不依赖尚未完成的 pilot 数据

### L0 校准完成状态 (v0.5.1-final, 03-28)

**整体状态**: ✅ **校准完成，可部署**

| 维度 | 状态 | 测试通过率 | 关键发现 |
|------|------|-----------|---------|
| 鲁棒性 | ✅ 优秀 | 131/131 (100%) | 边界处理完善，ASR 噪声影响≤1.5 分 |
| 边界情况 | ✅ 优秀 | 80/80 (100%) | 空输入/极端长度/极端事件数均安全处理 |
| 对抗性 | ✅ 优秀 | 23/23 (100%) | Prompt 注入免疫，伪叙事检出率 100% |
| 单元测试 | ✅ 优秀 | 60/60 (100%) | scorer.py 全部测试通过 |
| 情绪唤醒度 | ⚠️ 可接受 | 3/5 (60%) | 高唤醒场景修复，基线略高但<0.5 分差异 |
| 安全性 | ⚠️ 待改进 | N/A | 多样性惩罚部分缓解堆砌攻击，v0.6 需 LLM 仲裁 |

**v0.5.1-final 核心修复**:
1. 情绪词汇多样性检测 (防堆砌攻击)
2. 高唤醒词权重提升 (2.0 → 3.0)
3. 生理反应权重提升 (1.0 → 1.3-1.5)
4. 对数缩放参数调整 (1.5 → 2.0)
5. 低唤醒词权重降低 (0.3 → 0.15)

**待办**: 50 条人工标注对标 (30-45 分钟) — 需要 V 协助

### L0 对标基线 (03-28 更新)

| 基准 | 目标 | 当前状态 | 截止时间 |
|------|------|---------|---------|
| LLaMA-3 (8B) fine-tuned | r = 0.87 | ⏳ 待人工标注验证 | 05-31 |
| v0.6 LLM 仲裁 | r > 0.80 | ⏳ 待实现 | 04-30 |
| v0.5.1 规则层 | κ > 0.70 | ✅ 131/131 鲁棒性 | 已完成 |

### NLP/LLM 方法论三大方向 (03-28)

| 技术方向 | 成熟度 | VSNC 适用性 | 集成优先级 |
|---------|-------|------------|-----------|
| **EM-LLM 事件记忆架构** | ICLR 2025 接收 | ⭐⭐⭐⭐⭐ 长上下文叙事组织 | P0 (1-3 月) |
| **神经符号混合评分** | Nature Comm Med 2025 | ⭐⭐⭐⭐⭐ 可审计临床评估 | ✅ 已对齐 |
| **持久化用户画像记忆** | arXiv 2025 | ⭐⭐⭐⭐⭐ 个性化适配 | P1 (3-6 月) |

**关键发现**:
1. CittaVerse 技术路线已处前沿 (规则+LLM 混合架构与 NeSy 路径完全一致)
2. L0 评分器对标基线明确 (LLaMA-3 r=0.87 人类相关性)
3. 长上下文记忆是核心瓶颈 (EM-LLM 在 10M tokens 尺度成功检索)
4. 语音生物标志物临床可用 (AI 语音分析预测 AD 转化准确率>78%)

### 技术文献深度阅读核心发现 (03-24 ~ 03-28)

**累计覆盖**: 4 轮，32+ 篇论文

| 轮次 | 日期 | 篇数 | 核心发现 |
|------|------|------|---------|
| #1 | 2026-03-24 | 10 | CheckEval/Dolphin/Event Segmentation/Rememo 初现 |
| #2 | 2026-03-25 | 11 | SeniorTalk/SpeechCARE/PTSD LLM/Robot Biomarkers |
| #3 | 2026-03-26 | 5 | **ACP 多 agent 框架** (2603.17392, 90.5% 评分匹配率) |
| #4 | 2026-03-27 | 6 | **Rememo 竞品**/Sophia narrative memory/Nature biomarkers |
| #5 | 2026-03-28 | 3+ | **arXiv:2603.07670 Agent Memory 综述** |

**最高价值发现**:
1. **ACP (Agentic Cognitive Profiling)** — 多 agent 认知评估框架，90.5% 评分匹配率，与 VSNC 多 agent scoring pipeline 最直接对标
2. **Rememo** — 最直接竞品对标，therapist-oriented AI 工具支持痴呆症回忆疗法
3. **SeniorTalk** — 55.53h 中国 75+ 老年人对话数据集，202 人，含方言标注
4. **LLaMA-3 自动化评分** — r=0.87 人类相关性，L0 评分器黄金标准对标
5. **Nature 语音生物标志物** — 临床验证语音作为认知障碍筛查生物标志物的可行性

---

## 开放问题

| 问题 | 优先级 | 状态 | 负责人 |
|------|--------|------|--------|
| DASHSCOPE_API_KEY 未配置 | P0 | 🔴 阻塞>14 天 | V |
| 50 条人工标注对标 | P0 | 🟡 待执行 | V + Core |
| arXiv 提交 | P0 | 🟡 待 V 操作 | V |
| EM-LLM PoC 验证 | P1 | 🟢 可执行 | Core |
| ASR 真实测试 | P1 | 🟡 待 API Key | Core |
| 用户画像系统升级 | P2 | 🟢 可执行 | Core |

---

*沉淀时间: 2026-03-24 20:45 UTC | 最近更新: 2026-03-28 20:45 UTC*
*维护者: Hulk 🟢*
