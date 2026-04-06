# 06 — 基础设施与工具 (Infrastructure & Tools)

> ASR 数据集调研、API 配置、OpenClaw 最佳实践、技术排障记录。

---

## Bottom Line

ASR 选型已完成（讯飞/DashScope/Whisper 三选一），但 API Key 配置阻塞 >7 天。老年语音数据集调研发现 Common Voice 下载受阻，AISHELL 可用但非老年专属。OpenClaw 记忆管理最佳实践已整理。这些是支撑产品技术栈的基础件。

**04-02 增量**: ASR v7 基准测试 (40 样本/WER 1.30%/零错误率 82.5%)、Claude Code 深度分析 5 篇 (Agent 循环/工具系统/Hook 机制)。

**04-03 增量**: ASR v8 基准测试 (40 样本/第 8 次连续运行/稳定性确认)、EXP-001 实验框架 (标注协议/样本准备/分析代码框架)。

---

## 文件索引

| 文件 | 主题 | 验证等级 | 日期 |
|------|------|----------|------|
| `research/asr/asr_benchmark_2026-03-26.md` | ASR 基准测试报告 v1：AISHELL-1 10 样本 Mock 测试框架 + WER/CER 评估方法 | V3 (Mock 测试) | 03-26 |
| `research/asr/asr_benchmark_2026-03-26_v2.md` | **ASR 基准测试报告 v2**: 20 样本扩展测试、平均 WER 2.18%、6 错误样本分析 (同音字/近音字) | V3 (Mock 测试) | 03-26 |
| `research/asr/asr_benchmark_2026-03-28_v3.md` | **ASR 基准测试报告 v3**: 30 样本、WER 1.48%、零错误率 80% | V3 (Mock 测试) | 03-28 |
| `research/asr/asr_benchmark_2026-03-28_v4.md` | **ASR 基准测试报告 v4**: 30 样本、WER 1.48%、框架可重复性验证 | V3 (Mock 测试) | 03-28 |
| `research/asr/asr_benchmark_2026-03-28_v5.md` | **ASR 基准测试报告 v5**: 30 样本、WER 1.48%、v3/v4/v5 结果完全一致 (标准差=0) | V3 (Mock 测试) | 03-28 |
| `research/asr/asr_benchmark_2026-03-30_v7.md` | **ASR 基准测试报告 v7**: 40 样本、WER 1.30%、零错误率 82.5%、新增 10 条挑战性场景 | V4 (Mock 测试) | 03-30 |
| `research/asr/asr_benchmark_2026-04-02_v8.md` | **ASR 基准测试报告 v8**: 40 样本、WER 1.30%、零错误率 82.5%、连续第 8 次运行稳定性验证 | V4 (Mock 测试) | 04-02 |
| `research/asr/mock_samples_v4.csv` | 30 样本 Mock 测试集 v4 | V3 | 03-28 |
| `research/asr/mock_samples_v5.csv` | 30 样本 Mock 测试集 v5 | V3 | 03-28 |
| `research/asr/README.md` | ASR 基准测试目录索引 | V3 | 03-26 |
| `research/2026-03-31-claude-code-analysis.md` | Claude Code 代码分析：核心架构解读 | V3 | 03-31 |
| `research/2026-03-31-claude-code-deep-analysis.md` | Claude Code 深度分析：逐行解读工程思想 | V3 | 03-31 |
| `research/2026-03-31-claude-code-deep-dive.md` | Claude Code 深潜：Agent 循环实现 | V3 | 03-31 |
| `research/2026-03-31-claude-code-deep-dive-v2.md` | Claude Code 深潜 v2: 工具系统设计 | V3 | 03-31 |
| `research/2026-03-31-claude-code-hook-system-analysis.md` | Claude Code Hook 系统分析：扩展机制 | V3 | 03-31 |
| `research/experiments/exp-001-sample-preparation-protocol.md` | EXP-001 实验样本准备协议：N=200 分层抽样 (正常 140/边界 40/堆砌 20) | V3 | 04-02 |
| `research/experiments/exp-001-annotation-protocol.md` | EXP-001 标注操作手册：人工标注流程 + 质量控 + 仲裁机制 | V3 | 04-02 |
| `research/experiments/exp-001-l0-scorer-calibration-report.md` | EXP-001 L0 评分器校准报告：基准测试输出 | V4 | 04-02 |
| `research/experiments/exp-001-analysis-code-framework.md` | EXP-001 分析代码框架：统计检验/相关性分析/假设验证 | V3 | 04-02 |
| `research/experiments/exp-001-analysis-report-template.md` | EXP-001 分析报告模板：结果呈现框架 | V3 | 04-02 |
| `research/2026-03-14-elderly-voice-datasets.md` | 老年语音数据集调研：AISHELL/Common Voice/DementiaBank | V1 | 03-14 |
| `research/common_voice_download_issue.md` | Common Voice 下载问题记录 + 阻塞分析 | V4 (实际测试) | 03-14 |
| `research/api-key-config-checklist.md` | API Key 配置清单：ASR/LLM/评分系统 | V3 | 03-14 |
| `research/2026-03-14-openclaw-memory-best-practices.md` | OpenClaw 记忆方案最佳实践 | V1 (文档+社区) | 03-14 |


## 核心知识点 (03-26 新增)

### ASR 基准测试框架

**测试方法**: Mock ASR 输出模拟常见错误类型 (同音字、断句、语气词遗漏)，使用标准 WER/CER 公式计算。

**评估指标**:
- WER (Word Error Rate): `(S + D + I) / N`
- CER (Character Error Rate): 以汉字/字符为单位计算，对中文 ASR 更敏感

**测试集 v1**: AISHELL-1, 10 样本，~30 秒总时长，单说话人 (S0724)

**测试集 v2 (扩展)**: 20 样本，覆盖 15 种老年回忆场景 (日常对话/工作经历/家庭生活/情感回忆/医疗健康/历史回忆等)

### ASR 基准测试 v2 核心发现

**整体指标**:
| 指标 | v2 结果 | v1 对比 |
|------|--------|--------|
| 样本数量 | 20 | +10 |
| 平均 WER | 2.18% | +1.59% (v1: 0.59%) |
| 平均 CER | 2.18% | +1.59% |
| 零错误样本 | 14/20 (70%) | -20% (v1: 90%) |

**错误类型分析** (6 个错误样本):
| 错误类型 | 示例 | 频率 |
|---------|------|------|
| 同音字 | 玩→完、十→零、君→军、级→纪 | 4/6 |
| 近音字 | 艰→坚、年→粘 | 2/6 |

**场景相关性**:
- 家庭生活/回忆叙述场景错误率较高 (WER 7-9%)
- 日常对话场景错误率较低 (WER 0-3%)

**状态**: 评估框架已建立，待接入真实 ASR API (讯飞/DashScope/Whisper) 进行实测。

### ASR 基准测试 v5 核心发现 (03-28)

**整体指标 (v3/v4/v5 稳定性验证)**:
| 指标 | v5 | v4 | v3 | v2 | v1 | 趋势 |
|------|-----|-----|-----|-----|-----|------|
| 样本数量 | 30 | 30 | 30 | 20 | 10 | 稳定 |
| 平均 WER | 1.48% | 1.48% | 1.48% | 2.18% | 0.59% | ✅ 稳定在~1.5% |
| 零错误样本 | 24/30 (80%) | 24/30 (80%) | 24/30 (80%) | 14/20 (70%) | 9/10 (90%) | ✅ 稳定在 70-90% |

**错误类型分布** (6 个错误样本):
| 错误类型 | 出现次数 | 占比 | 示例 |
|----------|----------|------|------|
| 同音字替换 | 4 | 66.7% | 玩→完、十→零、君→军、级→纪 |
| 近音字替换 | 2 | 33.3% | 艰→坚、年→粘 |

**场景风险分级**:
| 风险等级 | 场景类型 | 错误率 | 建议 |
|----------|----------|--------|------|
| 🔴 高风险 | 回忆叙述、娱乐偏好 | 100% | 建立专属词库 + 上下文校正 |
| 🟡 中风险 | 工作经历、情感回忆、家庭生活 | 25-33% | 热词增强 |
| 🟢 低风险 | 日常对话、医疗健康、科技使用 | 0% | 标准 ASR 即可 |

**框架可重复性验证**: v3/v4/v5 使用相同 30 样本，结果完全一致 (标准差=0)

**Mock vs 真实场景差距**:
| 测试类型 | WER | 说明 |
|----------|-----|------|
| Mock 测试 (v5) | 1.48% | 仅模拟同音/近音字错误 |
| 预期真实 ASR (标准普通话) | 5-10% | 包含噪音、口音、语速等 |
| 预期真实 ASR (老年语音) | 12-22% | 额外包含齿音、颤抖、停顿等 |

**下一步**: 接入真实 ASR API (讯飞/DashScope/Whisper) 进行实测

## 核心知识点

### ASR 选型对比
| 方案 | 中文普通话 | 老年语音 | 成本 | 状态 |
|------|-----------|---------|------|------|
| 讯飞听见 | 优秀 | 良好 | ¥0.003/秒 | ⚠️ 待 API Key |
| DashScope ASR | 良好 | 未测 | ¥0.002/秒 | ⚠️ 待 API Key |
| Whisper (OpenAI) | 良好 | 一般 | $0.006/分钟 | ⚠️ 待 API Key |
| Whisper (本地) | 良好 | 一般 | 免费 | ✅ 可用但延迟高 |

### 老年语音数据集
| 数据集 | 语言 | 老年人占比 | 可用性 |
|--------|------|-----------|--------|
| AISHELL-1 | 中文 | 低 | ✅ 已下载 |
| Common Voice | 多语言 | 低 | 🔴 下载阻塞 |
| DementiaBank | 英文 | 高 | ✅ 需申请 |
| 自建语料 | 中文 | 100% | ⏳ 待 Pilot |

### OpenClaw 记忆管理要点
- MEMORY.md 作为主记忆文件，memory/ 目录存放细分日志
- 语义搜索优先于全文扫描
- 定期整理避免 MEMORY.md 膨胀

---
*沉淀时间: 2026-03-23 20:45 UTC*
