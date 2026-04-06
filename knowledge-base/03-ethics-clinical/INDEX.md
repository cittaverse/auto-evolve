# 03 — 伦理审批与临床试验 (Ethics & Clinical)

> Pilot RCT + 伦理审批全套材料 + 用户研究协议。这是产品从"技术可行"到"临床可信"的桥梁。

---

## Bottom Line

已完成 Pilot RCT 方案设计（N=50，2 周干预）、伦理审批材料全套（申请表/知情同意书/数据隐私方案/风险评估）、三机构对比研究、以及 Path B 用户体验研究方案。所有材料已达 V3（文档静态复核），但实际提交伦理审批阻塞在 V 确认牵头单位（浙大心理系 / 市三医院 / 杭师大老龄研究院）。

---

## 文件索引

| 文件 | 主题 | 验证等级 | 日期 |
|------|------|----------|------|
| `research/2026-03-14-pilot-rct-protocol.md` | Pilot RCT 方案：N=50、2 周、4 次会话、MoCA 前后测 | V0 (设计) | 03-14 |
| `research/2026-03-15-rct-ethics-draft.md` | 伦理审批材料草稿（待 V 确认牵头单位） | V1 | 03-15 |
| `research/2026-03-15-ethics-committee-comparison.md` | 三机构伦理审批流程对比：浙大/市三医院/杭师大 | V1 (公开信息) | 03-15 |
| `research/2026-03-17-ethics-application-form.md` | 伦理审查申请表 v1.0 | V3 (静态复核) | 03-17 |
| `research/2026-03-17-ethics-consent-form.md` | 知情同意书 v1.0 | V3 | 03-17 |
| `research/2026-03-17-ethics-data-privacy.md` | 数据隐私保护方案 v1.0 (PIPL + GDPR) | V3 | 03-17 |
| `research/2026-03-17-ethics-risk-assessment.md` | 风险评估表 v1.0 | V3 | 03-17 |
| `research/2026-03-17-ethics-parallel-track-checklist.md` | 伦理审批并行推进检查表 | V1 | 03-17 |
| `research/2026-03-17-rct-informed-consent.md` | Pilot RCT 专用知情同意书 | V3 | 03-17 |
| `research/2026-03-17-pilot-user-study-protocol.md` | Path B 用户体验研究方案 v1.0 | V1 | 03-17 |
| `research/2026-03-17-community-partnership-checklist.md` | 社区合作执行清单（杭州 12+ 机构） | V1 | 03-17 |

## 核心知识点

### Pilot RCT 设计要点
- **N=50**（A/B 各 25），MCI 老年人（MoCA 18-25）
- **干预周期**：2 周，每周 2 次，每次 30 分钟语音会话
- **主要结局**：叙事质量评分（Scorer v0.5）前后变化
- **次要结局**：SUS 可用性、NPS 满意度、照护者反馈
- **安全协议**：情绪安全 3 级（绿/黄/红）+ 危机转介

### 三机构对比
| 机构 | 优势 | 审批周期 |
|------|------|----------|
| 浙大心理系 | 学术声望最高 | 4-6 周 |
| 杭州市三医院 | 临床资源丰富 | 3-4 周 |
| 杭师大老龄研究院 | 老龄研究专长 | 2-3 周 |

### 伦理材料完整度
- ✅ 伦理审查申请表
- ✅ 知情同意书（大字版，适老化）
- ✅ 数据隐私方案（PIPL + GDPR 合规）
- ✅ 风险评估表（4 类风险 × 3 级严重度）
- ✅ 社区合作机构清单

## 实验设计汇总 (03-24 新增)

`research/paper/02-experiment-design.md` — 三层验证架构完整设计：

### L1: 评分工具技术验证
- **已完成**: Mock 测试 60 个单元全绿 (V4)
- **待完成**: Benchmark 数据集（10-20 段手工标注叙事，2 名评估者，目标 κ>0.75, r>0.70）
- **待完成**: v0.5 vs v0.6 对比（量化事件边界检测 v2 改进）

### L2: Pilot RCT 设计
- **设计升级**: N=60-80（vs 此前 N=50），多中心、随机、对照、单盲
- **干预**: 8 周 × 每周 2 次 × 30-40 分钟 AI 引导回忆 + ASR + 六维评分 + 元记忆策略
- **对照**: 主动对照（结构化认知训练）
- **主要终点**: MoCA 变化
- **次要终点**: GDS-15/QOL-AD/SWLS/NPI-Q + 六维叙事评分
- **评估时点**: 基线/4 周/8 周/3 月随访/6 月随访

### L3: 评分标准验证
- 从 Pilot RCT 抽取 100 段叙事
- 2 名评估者独立评分 → ICC > 0.75
- 自动 vs 人工 Pearson r > 0.70 + Bland-Altman 一致性分析

### L4: A/B 测试（元记忆增强，探索性）
- 嵌套于干预组内 (n=15-20 × 2)
- 标准引导 vs 元记忆增强引导
- 多层线性模型评估改善速度差异

## 统计分析计划 (03-24 新增)

`research/paper/03-statistical-analysis-plan.md` — 独立 SAP v1.0，可直接用于预注册：

### 核心方法
- **主要分析**: 线性混合效应模型 (LMM)，组别×时间交互项
- **效力**: N=60 可检测 d=0.80 (80% power); N=80 可检测 d=0.65 (80% power)
- **多重比较**: Benjamini-Hochberg FDR (q=0.10)
- **缺失数据**: MAR 假设下 LMM 自然处理；MNAR 敏感性用模式混合模型

### 可行性指标（Pilot 核心）
| 指标 | 成功标准 |
|------|----------|
| 招募率 | ≥50% |
| 干预完成率 | ≥70% |
| 脱落率 | ≤30% |
| 数据完整率 | ≥85% |
| SUS 可用性 | ≥68 |
| NPS | ≥30 |

### 预注册计划
- 平台: ChiCTR 或 ClinicalTrials.gov
- 时机: 首例入组前
- 附件: 本 SAP

## 文件索引 (完整)

| 文件 | 主题 | 验证等级 | 日期 |
|------|------|----------|------|
| `research/2026-03-14-pilot-rct-protocol.md` | Pilot RCT 方案 v1 | V0 (设计) | 03-14 |
| `research/2026-03-15-rct-ethics-draft.md` | 伦理审批材料草稿 | V1 | 03-15 |
| `research/2026-03-15-ethics-committee-comparison.md` | 三机构伦理审批流程对比 | V1 (公开信息) | 03-15 |
| `research/2026-03-17-ethics-application-form.md` | 伦理审查申请表 v1.0 | V3 (静态复核) | 03-17 |
| `research/2026-03-17-ethics-consent-form.md` | 知情同意书 v1.0 | V3 | 03-17 |
| `research/2026-03-17-ethics-data-privacy.md` | 数据隐私保护方案 v1.0 (PIPL + GDPR) | V3 | 03-17 |
| `research/2026-03-17-ethics-risk-assessment.md` | 风险评估表 v1.0 | V3 | 03-17 |
| `research/2026-03-17-ethics-parallel-track-checklist.md` | 伦理审批并行推进检查表 | V1 | 03-17 |
| `research/2026-03-17-rct-informed-consent.md` | Pilot RCT 专用知情同意书 | V3 | 03-17 |
| `research/2026-03-17-pilot-user-study-protocol.md` | Path B 用户体验研究方案 v1.0 | V1 | 03-17 |
| `research/2026-03-17-community-partnership-checklist.md` | 社区合作执行清单（杭州 12+ 机构） | V1 | 03-17 |
| `research/paper/02-experiment-design.md` | 三层验证架构完整设计 (L1-L4) | V3 (静态复核) | 03-24 |
| `research/paper/02-experiment-design-refined.md` | 实验设计 v2.0 完善版：变量控制清单 + Checklist 范式 + 事件边界验证 | V3 (静态复核) | 03-25 |
| `research/paper/03-statistical-analysis-plan.md` | 独立 SAP v1.0，含 R 代码框架 | V2 (方法学交叉确认) | 03-24 |
| `research/paper/05-ethics-approval-package.md` | 伦理审批包汇总：申请表 + 知情同意书 + 数据隐私 + 风险评估整合版 | V3 | 03-26 |
| `research/paper/06-experiment-design-final.md` | 最终实验设计：Pilot RCT 完整方案 (N=60-80, 8 周干预，多中心) | V3 | 03-26 |
| `research/paper/07-experiment-timeline.md` | 实验时间线：招募→筛选→干预→评估→随访全流程 | V3 | 03-26 |
| `research/paper/08-variable-control-checklist.md` | 变量控制清单：受试者/干预/评估/数据四层操作化定义 | V3 | 03-26 |
| `research/paper/methods-overview.md` | 论文方法概述：评分系统架构总览 | V3 | 03-26 |
| `research/paper/methods-architecture.md` | 方法 - 架构：L0/VSNC 系统架构图 + 数据流 | V3 | 03-26 |
| `research/paper/methods-scoring.md` | 方法 - 评分：7 维度计算公式 + 动态比例算法 | V3 | 03-26 |
| `research/paper/methods-evaluation.md` | 方法 - 评估：L1-L4 验证架构 + 统计方法 | V3 | 03-26 |
| `research/paper/methods-implementation.md` | 方法 - 实现：Pipeline 代码结构 + 部署说明 | V3 | 03-26 |

## 开放问题
- [ ] **V 需确认牵头单位**（这是所有伦理材料提交的前置条件）
- [ ] Path A (正式 RCT) vs Path B (用户体验研究) 路径选择待决策
- [ ] MoCA 授权费用待确认
- [ ] **新证据建议干预周期 ≥12 周**（vs 当前设计 8 周），需 V 决策是否调整
- [ ] 预注册平台选择待确认 (ChiCTR vs ClinicalTrials.gov)
- [ ] Benchmark 标注评估者（2 名，心理学/语言学背景）待招募

---
*沉淀时间: 2026-03-25 20:45 UTC (更新)*
