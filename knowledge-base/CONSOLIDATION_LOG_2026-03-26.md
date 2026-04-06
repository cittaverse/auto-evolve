# 知识库整理日志 | Knowledge Base Consolidation Log

**日期**: 2026-03-26 20:45 UTC  
**执行人**: Hulk 🟢  
**任务**: 储备·知识库整理 — 将 research/ 下散落的研究成果结构化沉淀到 knowledge-base/

---

## 本次整理概览

### 新增文件索引 (18 个)

| 知识域 | 新增文件 | 主题 | 验证等级 |
|--------|---------|------|----------|
| **01-narrative-scorer** | `research/2026-03-26-ablation-study-design.md` | 消融实验设计：7 组件×128 配置、单组件消融 + 极端配置对比 | V3 |
| **01-narrative-scorer** | `research/2026-03-26-ablation-study-final-report.md` | 消融实验最终报告：简化系统优于复杂系统，LLM-only 表现最佳 | V4 |
| **01-narrative-scorer** | `research/2026-03-26-l0-calibration-summary.md` | L0 校准总结：131/131 鲁棒性测试通过，2 个安全漏洞待修复 | V3 |
| **01-narrative-scorer** | `research/2026-03-26-l0-scorer-calibration-report.md` | L0 评分器校准报告：阈值/权重/边界/一致性/安全性五维检查 | V3 |
| **01-narrative-scorer** | `research/paper/methods-overview.md` | 论文方法概述：评分系统架构总览 | V3 |
| **01-narrative-scorer** | `research/paper/methods-architecture.md` | 方法 - 架构：L0/VSNC 系统架构图 + 数据流 | V3 |
| **01-narrative-scorer** | `research/paper/methods-scoring.md` | 方法 - 评分：7 维度计算公式 + 动态比例算法 | V3 |
| **01-narrative-scorer** | `research/paper/methods-evaluation.md` | 方法 - 评估：L1-L4 验证架构 + 统计方法 | V3 |
| **01-narrative-scorer** | `research/paper/methods-implementation.md` | 方法 - 实现：Pipeline 代码结构 + 部署说明 | V3 |
| **01-narrative-scorer** | `research/paper/visualizations/outputs/VISUALIZATION_SUMMARY.md` | 可视化输出总结：评分分布/维度雷达图/时间序列图 | V3 |
| **03-ethics-clinical** | `research/paper/05-ethics-approval-package.md` | 伦理审批包汇总：申请表 + 知情同意书 + 数据隐私 + 风险评估整合版 | V3 |
| **03-ethics-clinical** | `research/paper/06-experiment-design-final.md` | 最终实验设计：Pilot RCT 完整方案 (N=60-80, 8 周干预，多中心) | V3 |
| **03-ethics-clinical** | `research/paper/07-experiment-timeline.md` | 实验时间线：招募→筛选→干预→评估→随访全流程 | V3 |
| **03-ethics-clinical** | `research/paper/08-variable-control-checklist.md` | 变量控制清单：受试者/干预/评估/数据四层操作化定义 | V3 |
| **04-competitive-intel** | `research/evidence/2026-03-26-competitor-evidence-update.md` | 竞品 + 证据更新：12 竞品状态确认 + 4 篇 arXiv 新论文 | V1-V2 |
| **06-infra-tools** | `research/asr/asr_benchmark_2026-03-26.md` | ASR 基准测试报告：AISHELL-1 10 样本 Mock 测试框架 + WER/CER 评估方法 | V3 |

### 更新的文件索引 (4 个)

| 文件 | 更新内容 |
|------|----------|
| `knowledge-base/01-narrative-scorer/INDEX.md` | +10 篇 (消融实验×2 + L0 校准×2 + methods 系列×5 + 可视化), 文件总数 7→17 |
| `knowledge-base/03-ethics-clinical/INDEX.md` | +9 篇 (伦理包×4 + methods 系列×5), 文件总数 14→23 |
| `knowledge-base/04-competitive-intel/INDEX.md` | +1 篇 (03-26 竞品证据更新), 文件总数 9→10 |
| `knowledge-base/06-infra-tools/INDEX.md` | +1 篇 (ASR 基准测试), 文件总数 4→5 |
| `knowledge-base/README.md` | 更新文件计数和 timestamps |

---

## 核心知识增量

### 01-narrative-scorer (叙事评分系统)

#### 消融实验核心结论 (ablation-study-final-report.md)

**Bottom Line**: 简化系统优于复杂系统。

| 配置 | 评分 | 稳定性 (std) | 仲裁率 | 等级分布 |
|------|------|-------------|--------|----------|
| Full | 56.76 | 4.22 | 100% | C:20, D:30 |
| Minimal | 61.56 | 1.36 | 0% | C:50 |
| LLM-only | 62.48 | 1.38 | 100% | C:50 |

**单组件影响排名**:
1. C4 (L0 维度): +5.61 — 6 维→3 维后评分上升，6 维有惩罚效应
2. C7 (仲裁): -3.29 — 仲裁调高分数，但也增加波动
3. C3 (LLM 事件): -1.72 — LLM 事件提取有小幅增益
4. C5 (多 Agent): -1.53 — 多 Agent 有小幅增益
5. C1 (情绪唤醒): +0.13 — **影响微弱**
6. C2 (动态比例): ±0.00 — **无影响**
7. C6 (投票加权): ±0.00 — **无影响**

**假设验证**:
- H1 (C1 对高情绪叙事重要): ❌ 未验证 (+0.13 分 vs 预期下降>15 分)
- H2 (C5 提升稳定性): ❌ 未验证 (std -0.38 vs 预期增加>50%)
- H3 (C7 仅边缘作用): ❌ 相反 (-3.29 分，100% 样本)

**建议**: v0.6 优先考虑简化架构，而非增加复杂性。

#### L0 校准核心发现 (l0-scorer-calibration-report.md)

**整体状态**: ⚠️ 需要修复

| 维度 | 状态 | 关键发现 |
|------|------|---------|
| 鲁棒性 | ✅ 优秀 | 131/131 测试通过，边界处理完善 |
| 一致性 | ✅ 良好 | ASR 噪声影响 ≤1.5 分，伪叙事检出率 100% |
| 阈值 | ⚠️ 需优化 | 分级阈值合理，但情绪唤醒度检测精度不足 |
| 权重 | ✅ 合理 | 场景化权重配置符合理论 |
| 安全性 | ❌ 有风险 | 2 个可被攻击漏洞 (情绪词堆砌、关键词堆砌) |
| 情绪检测 | ❌ 待修复 | Mock 测试 3/5 通过，高唤醒场景低估 0.57 分 |

**立即行动项**:
1. 修复情绪唤醒度检测器 (TC-01, TC-05 失败)
2. 添加情绪词汇多样性检测 (防堆砌攻击)
3. 完成 50 条人工标注对标

#### 论文 Methods 系列 (5 篇)

完整论文方法章节草稿，覆盖：
- **methods-overview**: 评分系统架构总览
- **methods-architecture**: L0/VSNC 系统架构图 + 数据流
- **methods-scoring**: 7 维度计算公式 + 动态比例算法
- **methods-evaluation**: L1-L4 验证架构 + 统计方法
- **methods-implementation**: Pipeline 代码结构 + 部署说明

### 03-ethics-clinical (伦理审批与临床试验)

#### 论文实验设计系列 (4 篇)

- **05-ethics-approval-package**: 伦理审批包汇总 (申请表 + 知情同意书 + 数据隐私 + 风险评估整合版)
- **06-experiment-design-final**: 最终实验设计 (Pilot RCT 完整方案：N=60-80, 8 周干预，多中心)
- **07-experiment-timeline**: 实验时间线 (招募→筛选→干预→评估→随访全流程)
- **08-variable-control-checklist**: 变量控制清单 (受试者/干预/评估/数据四层操作化定义)

### 04-competitive-intel (竞品与市场)

#### 03-26 竞品 + 证据更新核心发现

**工具限制应对**: web_search/ddg-search/web_fetch/browser 均受阻，改用 arXiv API (curl) 直接获取论文元数据。

**竞品层面**:
- 12 竞品无重大新信号 (基于 03-24 基线确认)
- AI 传记赛道持续拥挤 (20+ 产品)，但全部聚焦"内容生产"，无叙事评估能力
- CittaVerse 差异化依然成立：临床验证 × 叙事评分 × 中文优化 仍为唯一组合

**证据层面 (新增 4 篇)**:
1. **机器人辅助 RT fNIRS 研究** (arXiv 2405.02560): SAR-led RT 与 human-led RT 在 DLPFC 激活上无显著差异 — **支持 AI 交付 RT 的神经科学基础**
2. **XR 记忆对象研究** (arXiv 2603.21381): 物理记忆对象 vs 虚拟记忆对象 — 物理对象促进更强社交连接
3. **AI 辅助叙事创作** (arXiv 2507.xxxx): 老年移民 AI 共创汉字叙事 — AI 作为支持机制而非内容生产者
4. **RAG 虚拟考古头像** (arXiv 2603.23353): 设计空间研究 — 对 CittaVerse 的"AI 引导对话"设计有参考

**战略启示**:
- 竞品窗口仍在：03-24 识别的 20+ 竞品无一进入"评估"赛道
- 学术证据强化：新 arXiv 论文支持 AI 辅助回忆干预的可行性
- 紧迫性未减：medRxiv 上的 AI-RT 系统综述 protocol 仍在进行中，arXiv 提交应加速

### 06-infra-tools (基础设施与工具)

#### ASR 基准测试框架

**测试方法**: Mock ASR 输出模拟常见错误类型 (同音字、断句、语气词遗漏)，使用标准 WER/CER 公式计算。

**评估指标**:
- WER (Word Error Rate): `(S + D + I) / N`
- CER (Character Error Rate): 以汉字/字符为单位计算，对中文 ASR 更敏感

**测试集**: AISHELL-1, 10 样本，~30 秒总时长，单说话人 (S0724)

**状态**: 评估框架已建立，待接入真实 ASR API (讯飞/DashScope/Whisper) 进行实测。

---

## 知识库当前状态

| 知识域 | 文件数 | 最近更新 | 状态 |
|--------|--------|----------|------|
| 01-narrative-scorer | 17 | 03-26 | ✅ 完整 |
| 02-metamemory | 6 | 03-23 | ✅ 完整 |
| 03-ethics-clinical | 23 | 03-26 | ✅ 完整 |
| 04-competitive-intel | 10 | 03-26 | ✅ 完整 |
| 05-product-strategy | 3 | 03-23 | ✅ 完整 |
| 06-infra-tools | 5 | 03-26 | ✅ 完整 |
| 07-outreach | 4 | 03-23 | ✅ 完整 |
| **总计** | **68** | - | - |

---

## 待办事项 (由本次整理发现)

### P0 - 高优先级

- [ ] **L0 评分器修复**: 情绪唤醒度检测器 (TC-01, TC-05 失败)
- [ ] **L0 安全评分**: 添加情绪词汇多样性检测 (防堆砌攻击)
- [ ] **v0.6 架构决策**: 基于消融实验结论，优先简化架构 (Minimal 或 LLM-only)
- [ ] **50 条人工标注对标**: 完成 L0 评分器人工基准测试

### P1 - 中优先级

- [ ] **arXiv 提交加速**: medRxiv 上的 AI-RT 系统综述 protocol 仍在进行中
- [ ] **ASR API Key 配置**: 接入真实 ASR API 进行实测 (讯飞/DashScope/Whisper)
- [ ] **论文 methods 系列审阅**: 5 篇 methods 草稿需 V 审阅

### P2 - 低优先级

- [ ] **可视化输出完善**: 评分分布/维度雷达图/时间序列图生成脚本
- [ ] **证据扫描周更维持**: 下周关注 CHI 2026 接收论文 (Rememo 等)

---

## 方法论反思

### 本次整理策略

1. **大规模整合**: 03-26 单日新增 18 个文件索引，是此前单次整理的 6 倍
2. **论文资产归位**: 将 paper/ 目录下的 methods 系列、实验设计系列系统归入对应知识域
3. **实验结论沉淀**: 消融实验和 L0 校准的核心发现直接写入 INDEX.md，便于快速查阅
4. **验证等级标注**: 每个文件条目都标注 V0-V4 验证等级，消融实验为 V4 (实际执行)

### 改进机会

1. **跨域引用增强**: methods 系列同时涉及 01-narrative-scorer 和 03-ethics-clinical，可在 INDEX 中增加"参见"链接
2. **演进链可视化**: 消融实验→L0 校准→v0.6 架构决策的演进关系可在 INDEX 中更清晰呈现
3. **开放问题同步**: 每个知识域的"开放问题"列表可同步到 KANBAN.md 或 research-backlog.md

---

**下次整理**: 2026-04-02 (周更节奏)  
**维护者**: Hulk 🟢
