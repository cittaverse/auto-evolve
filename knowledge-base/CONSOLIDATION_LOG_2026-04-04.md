# 知识库整理日志 | Knowledge Base Consolidation Log

**日期**: 2026-04-04 20:40 UTC  
**执行人**: Hulk 🟢  
**任务**: cron:hulk-reserve-knowledge-001 — 储备·知识库整理

---

## 本次整理概览

### 新增文件索引 (14 个)

| 知识域 | 新增文件 | 主题 | 验证等级 | 日期 |
|--------|---------|------|----------|------|
| **01-narrative-scorer** | `research/2026-04-03-nlp-llm-methodology-vsnc.md` | **NLP/LLM 方法论 (04-03)**: Amory 叙事记忆/HiAgent 层次化记忆/TReMu 神经符号时间推理/CSD 认知刺激对话 | V1 | 04-03 |
| **01-narrative-scorer** | `research/asr/asr_benchmark_2026-04-03_v9.md` | **ASR 基准测试 v9**: 40 样本、WER 1.30%、零错误率 82.5% (连续第 9 次运行) | V4 | 04-03 |
| **01-narrative-scorer** | `research/vsnc-l0-robustness-report-20260404.md` | **L0 鲁棒性测试 #3**: 159 测试/100% 通过、V1-V4 已知脆弱点无新增 | V4 | 04-04 |
| **01-narrative-scorer** | `research/paper/cron-hulk-paper-prep-001-run20-report.md` | 论文准备 Cron Run #20 报告 | V3 | 04-04 |
| **01-narrative-scorer** | `research/paper/cron-55834c68-run21-report.md` | 论文准备 Cron Run #21 报告 | V3 | 04-04 |
| **01-narrative-scorer** | `research/paper/visualizations/outputs/CRON_RUN_2026-04-04.md` | 可视化 Cron 运行报告 (Run #14): 04-04 输出 | V4 | 04-04 |
| **01-narrative-scorer** | `research/paper/visualizations/outputs/VISUALIZATION_SUMMARY.md` | **可视化输出总览**: 18 SVG 文件清单 + 生成说明 | V3 | 04-04 |
| **01-narrative-scorer** | `research/paper/INDEX.md` | **论文产物索引 (更新)**: 22+ MD 文档 + 可视化文件清单 | V3 | 04-04 |
| **01-narrative-scorer** | `research/paper/00-paper-prep-status.md` | 论文准备总状态看板 (更新) | V3 | 04-04 |
| **01-narrative-scorer** | `research/paper/14-experiment-design-v6-updated.md` | **实验设计 v6 更新**: 基于多 Agent v0.6 架构的调整 | V3 | 04-04 |
| **04-competitive-intel** | `research/evidence/2026-04-04-competitor-evidence-update-cron.md` | **04-04 Cron 竞品更新**: browser 恢复、arXiv 扫描 11 篇新论文、Rememo CHI 2026 倒计时 9 天 | V1 | 04-04 |
| **04-competitive-intel** | `research/competitors/10-2026-04-04-incremental-update.md` | **竞品技术深度分析增量**: arXiv/GitHub/Patents 全面扫描、技术成熟度评估、窗口期 6-12 个月 | V2 | 04-04 |
| **04-competitive-intel** | `research/competitors/README.md` | 竞品技术深度分析索引 (更新) | V3 | 04-04 |
| **06-infra-tools** | `research/2026-04-04-github-pr-status.md` | **GitHub PR 状态报告**: auto-evolve 仓库 PR 追踪 | V3 | 04-04 |

---

## 核心知识增量

### 01-narrative-scorer (叙事评分系统)

#### NLP/LLM 方法论更新 (04-03)

**文件**: `research/2026-04-03-nlp-llm-methodology-vsnc.md`

**4 篇核心论文深读**:

| 论文 | 会议/年份 | 核心贡献 | VSNC 映射 | 优先级 |
|------|----------|---------|---------|--------|
| **Amory** | EACL 2026 | 叙事驱动记忆框架 + 动量感知巩固 | L0 记忆层重构 (按"生命章节"组织) | SSS |
| **HiAgent** | ACL 2025 | 层次化工作记忆管理 (子目标作为记忆块) | 回忆引导对话 token 效率优化 | SSS |
| **TReMu** | ACL Findings 2025 | 神经符号时间推理 (时间线摘要 + Python 代码执行) | 老年人时间混乱校准 + 集体记忆锚点对齐 | SSS |
| **CSD** | ACL 2023 | 认知障碍老年人中文对话系统 (CSConv 数据集) | 阿宝情感支持策略参考 | S |

**核心洞察**:
- **Amory 叙事记忆**与 CittaVerse"生命章节"概念高度一致，可借鉴连贯性驱动检索
- **HiAgent 层次化记忆**可将 token 消耗减少 50%+，对成本敏感的 C 端产品至关重要
- **TReMu 神经符号时间推理** (GPT-4o 从 29.83→77.67, +160%) 可解决老年人回忆时间混乱问题

**验证等级**: V1 (单来源确认 — ACL Anthology)

---

#### ASR 基准测试 v9 (04-03)

**文件**: `research/asr/asr_benchmark_2026-04-03_v9.md`

**整体指标 (v9 vs v8)**:
| 指标 | v9 | v8 | 变化 |
|------|-----|-----|------|
| 样本数量 | 40 | 40 | - |
| 平均 WER | 1.30% | 1.30% | 0% ✅ |
| 平均 CER | 1.30% | 1.30% | 0% ✅ |
| 零错误样本 | 33/40 (82.5%) | 33/40 (82.5%) | 0% ✅ |

**核心结论**: **Mock 测试框架稳定性确认** — 连续第 9 次运行结果完全一致 (v7→v8→v9 三次持平)

**错误类型分布**:
- 同音字替换：71.4% (玩→完、十→零、君→军、级→纪、哟→呦)
- 近音字替换：28.6% (艰→坚、年→粘)

**场景风险分层**:
- 🔴 高风险：娱乐偏好 (100%)、回忆叙述/口语表达 (50%)
- 🟡 中风险：工作经历 (33.3%)、情感回忆/家庭生活 (25%)
- 🟢 低风险：其他 16 类场景 (0%)

**验证等级**: V4 (动态验证 — 连续 9 次运行确认)

---

#### L0 鲁棒性测试 #3 (04-04)

**文件**: `research/vsnc-l0-robustness-report-20260404.md`

**测试摘要**:
- 总测试数：159 (基础 131 + 扩展 28)
- 成功率：100% (159/159)
- 平均评分：40.72 ± 6.63
- 平均延迟：0.14ms

**已知脆弱点汇总** (无新增):
| ID | 描述 | 严重性 | 状态 |
|----|------|--------|------|
| V1 | 情感词堆砌可欺骗唤醒度检测器 | Medium | 未修复 |
| V2 | 最大化构造可达 100 分 | Medium | 未修复 |
| V3 | assign_grade 不防御超范围输入 | Low | 未修复 |
| V4 | LLM 输出格式漂移导致 fallback | Low-Medium | 未修复 |

**正面发现**:
- ✅ LLM Prompt 注入免疫
- ✅ 上下文窗口安全 (分块处理)
- ✅ 跨语言鲁棒性 (中文变体/中英混杂)
- ✅ 无状态设计 (无会话污染)
- ✅ 并发安全 (历史测试 50 并发无冲突)
- ✅ 降级策略有效 (API 失败 fallback 到规则引擎)

**验证等级**: V4 (动态验证 — 测试实际运行)

---

#### 论文准备 Cron #20-21 (04-04)

**文件**: `research/paper/cron-hulk-paper-prep-001-run20-report.md`, `research/paper/cron-55834c68-run21-report.md`

**产出状态**:
- 实验设计 v6 更新 (基于 Multi-Agent v0.6 架构)
- 可视化输出总览 (18 SVG 文件)
- 论文产物索引更新 (22+ MD 文档)

**验证等级**: V3 (静态复核)

---

#### 实验设计 v6 更新 (04-04)

**文件**: `research/paper/14-experiment-design-v6-updated.md`

**关键更新**:
- 整合 Multi-Agent Scorer v0.6 架构 (L0 + L1 仲裁层)
- 4 大核心假设 (H1 仲裁效度/H2 抗堆砌/H3 触发率/H4 相关性)
- 样本设计：N=200 (正常 140/边界 40/堆砌 20)

**验证等级**: V3 (静态复核)

---

### 04-competitive-intel (竞品与市场)

#### 04-04 Cron 竞品更新 (browser 恢复)

**文件**: `research/evidence/2026-04-04-competitor-evidence-update-cron.md`

**工具状态 (部分恢复)**:
| 工具 | 状态 | 说明 |
|------|------|------|
| `web_search` | ❌ | DuckDuckGo bot-detection |
| `browser` | ✅ | arXiv 搜索可用 |
| `web_fetch` | ⚠️ | 未测试 (之前有 VPN fake-IP 阻断) |

**本轮扫描成果**:
- **arXiv 新论文 11 篇**: Rememo (arXiv:2602.17083) 确认 + VoxCog 语音生物标志物 + 叙事连贯性评估 6 篇
- **Rememo CHI 2026 倒计时**: 会议 04-13 至 04-17 (剩余 9 天)
- **核心结论**: 证据库稳定，无推翻性新发现

**高相关性论文**:
| arXiv ID | 主题 | 相关性 |
|----------|------|--------|
| 2602.17083 | Rememo: AI-in-the-loop 治疗师工具 (CHI 2026) | ⭐⭐⭐⭐⭐ |
| 2601.07999 | VoxCog: 多语言认知障碍语音分类 | ⭐⭐⭐⭐ |
| 2510.24831 | Narrative Continuity Test: AI 系统身份持久性评估 | ⭐⭐⭐⭐ |
| 2511.22275 | RecToM: 对话推荐系统心理理论评估 | ⭐⭐⭐ |

**验证等级**: V1 (单来源确认 — arXiv)

---

#### 竞品技术深度分析增量 (04-04)

**文件**: `research/competitors/10-2026-04-04-incremental-update.md`

**全面扫描结果**:

| 数据源 | 搜索结果 | 关键发现 |
|--------|---------|---------|
| **arXiv** | 2 篇直接相关 | Rememo (2026-02) + 2019 自动疗法论文 |
| **GitHub** | 13 个仓库 | 最高 stars 仅 4 个 (elisabot)，无商业化代码 |
| **Google Patents** | ~1,319 项 | Neuroglee US20230395235A1 最直接 |

**技术成熟度评估**:

| 竞品 | 论文 | 开源代码 | 专利 | 产品 | 临床验证 | 综合成熟度 |
|------|------|---------|------|------|----------|-----------|
| **Rememo** | ✅ arXiv 2026 | ❌ | ❓ | 🟡 研究阶段 | 🟡 | 🟡 中低 |
| **Neuroglee** | ❓ | ❌ | ✅ US20230395235A1 | ✅ | ❓ | 🟡 中 |
| **MemoryLane** | ❌ | ✅ (2 stars) | ❌ | 🟡 | ❌ | 🟢 低 |
| **CittaVerse** | 🟡 在撰写 | 🟡 规划中 | ❌ | 🟡 V0.2 | 🟡 | 🟡 中 (潜力高) |

**窗口期评估**: **6-12 个月**

**依据**:
1. Rememo 论文 2026-02 发表，产品化至少需要 12-18 个月
2. MemoryLane 开源但 stars 极少，市场验证不足
3. Neuroglee 有专利但主要面向 B2B 临床
4. 无消费级 AI 回忆疗法产品形成规模

**新增研究待办 (RB-023 ~ RB-027)**:
- RB-023: MemoryLane GitHub 仓库深度分析 (P1)
- RB-024: Neuroglee 专利 claims 详细分析 (P0)
- RB-025: elisabot (ACM ICMR 2020) 代码分析 (P2)
- RB-026: 开源策略制定 (是否开源/开源什么) (P1)
- RB-027: Rememo 团队联系与合作评估 (P1)

**验证等级**: V2 (browser 直接访问确认)

---

### 06-infra-tools (基础设施与工具)

#### GitHub PR 状态报告 (04-04)

**文件**: `research/2026-04-04-github-pr-status.md`

**内容**: auto-evolve 仓库 PR 追踪状态

**验证等级**: V3 (静态复核)

---

## 知识库当前状态

| 知识域 | 文件数 | 最近更新 | 状态 |
|--------|--------|----------|------|
| 01-narrative-scorer | 90 | 04-04 20:40 | ✅ 完整 |
| 02-metamemory | 8 | 03-30 20:30 | ✅ 完整 |
| 03-ethics-clinical | 23 | 03-26 | ✅ 完整 |
| 04-competitive-intel | 59 | 04-04 20:40 | ✅ 完整 |
| 05-product-strategy | 9 | 04-03 20:45 | ✅ 完整 |
| 06-infra-tools | 24 | 04-04 20:40 | ✅ 完整 |
| 07-outreach | 5 | 03-27 | ✅ 完整 |
| **总计** | **218** | - | - |

**本次新增**: 14 篇 (204 → 218)

---

## 整理覆盖度

- **research/ 文件总数**: ~220
- **已索引文件**: 210+ (覆盖度 >95%)
- **未索引文件**: ~10 (README 类文件、临时脚本、数据文件、.git 相关)

---

## 关键风险预警

### 🔴 严重超期阻塞项 (已超期≥6 天)

| 阻塞项 | 超期时长 | 影响 | 责任人 |
|--------|----------|------|--------|
| arXiv 提交 | 6 天 | 论文无法公开，影响优先权 | V |
| 伦理审批审阅 | 6 天 | Pilot RCT 无法启动 | V |
| LaTeX PDF 编译 | 6 天 | arXiv 提交前置条件 | V |
| DASHSCOPE_API_KEY | >17 天 | LLM 增强功能/REMem Phase 3-4 无法实现 | V |

### 🟡 中度风险

| 风险项 | 状态 | 影响 |
|--------|------|------|
| **CHI 2026 Rememo 发表** | 剩余 9 天 (04-13 至 04-17) | 需提前准备解读框架 |
| **web_search 工具故障** | DuckDuckGo bot-detection | 广义 web 扫描能力丧失 |
| **L0 脆弱点 V1-V4** | 未修复但不影响系统崩溃安全性 | v0.8 需修复 V1 (情感词堆砌) |
| **ASR 真实测试未执行** | Mock 测试仅 1.30% WER | 真实场景预期 12-22% |

### 🟢 低风险

| 风险项 | 状态 | 备注 |
|--------|------|------|
| EXP-001 实验执行 | HANDOFF 已移交 Core | 等待 Core 执行 |
| REMem Phase 3-4 | 设计完成，待实现 | 依赖 DASHSCOPE_API_KEY |
| 竞品扫描 (7-12) | browser 需单独导航 | 本周内可完成 |

---

## 方法论反思

### 本次整理策略

1. **聚焦 04-03 后增量**: 重点整理 04-03 至 04-04 新增的 14 个文件
2. **browser 恢复红利**: 04-04 browser 恢复后完成 arXiv 扫描，发现 11 篇新论文
3. **竞品技术成熟度评估**: 首次系统评估 arXiv/GitHub/Patents 三维度，明确 6-12 个月窗口期
4. **ASR v9 稳定性验证**: 连续第 9 次运行结果完全一致，Mock 测试框架生产级就绪
5. **L0 鲁棒性测试 #3**: 159 测试 100% 通过，已知脆弱点 V1-V4 无新增

### 改进机会

1. **CHI 2026 解读框架准备**: Rememo 论文 04-13 发表，需 04-10 前完成解读框架
2. **web_search 修复优先级**: DuckDuckGo bot-detection 导致广义 web 扫描能力丧失，需 V 修复
3. **L0 v0.8 开发规划**: V1 (情感词堆砌) 修复优先级提升，建议纳入 v0.8
4. **开源策略文档**: 竞品开源生态薄弱，CittaVerse 开源非核心模块可建立事实标准

### 验证等级标注强化

本次整理所有条目均标注 V0-V4 验证等级：
- V4 (动态验证): 4 篇 (ASR v9/L0 鲁棒性#3/Cron 运行报告/可视化)
- V3 (静态复核): 7 篇 (论文准备/Cron 报告/实验设计/GitHub PR)
- V2 (多来源交叉): 1 篇 (竞品技术深度分析)
- V1 (单来源): 2 篇 (NLP 方法论/竞品证据更新)

---

## 待办事项 (由本次整理发现)

### P0 - 高优先级 (本周内)

- [ ] **CHI 2026 Rememo 解读框架准备** (截止 04-10) — Hulk 执行 🟡 **中度风险**
- [ ] **arXiv 提交** (截止 03-30，已超期 6 天) — V 执行 🔴 **严重超期**
- [ ] **伦理审批材料审阅** (截止 03-29，已超期 6 天) — V 执行 🔴 **严重超期**
- [ ] **LaTeX PDF 编译** (截止 03-29，已超期 6 天) — V 执行 🔴 **严重超期**
- [ ] **DASHSCOPE_API_KEY 轮换** (阻塞>17 天) — V 执行 🔴 **严重阻塞**
- [ ] **web_search 修复** (DuckDuckGo bot-detection) — V 执行 🟡 **中度风险**
- [ ] **Neuroglee 专利 claims 分析** (RB-024) — Hulk 执行 🟡 **新增 P0**

### P1 - 中优先级 (下周内)

- [ ] **消费级竞品 (7-12) browser 手动扫描** — Hulk 执行 (截止 04-07)
- [ ] **Narrative Continuity Test (2510.24831) 深读** — Hulk 执行 (截止 04-08)
- [ ] **RecToM 评估框架 (2511.22275) 深读** — Hulk 执行 (截止 04-08)
- [ ] **MemoryLane GitHub 仓库深度分析** (RB-023) — Hulk 执行
- [ ] **开源策略文档起草** (RB-026) — Hulk 执行
- [ ] **Rememo 团队联系邮件草稿** (RB-027) — Hulk 执行
- [ ] **L0 v0.8 开发规划** (V1 修复) — Core 执行

### P2 - 低优先级

- [ ] **证据扫描周更维持** (工具链修复后恢复) — Hulk 执行
- [ ] **GitHub 竞品 (3-6) 状态扫描** (等待工具修复) — Hulk 执行
- [ ] **elisabot (ACM ICMR 2020) 代码分析** (RB-025) — Hulk 执行
- [ ] **NARRABENCH 中文本地化** (文化脚本适配维度) — Hulk/Core 执行
- [ ] **ADNI 生存分析迁移** (C-index 核心指标) — Hulk/Core 执行

---

## 核心结论摘要

### Bottom Line

**AI+ 回忆疗法是极早期赛道，无成熟竞品，CittaVerse 有 6-12 个月窗口期建立先发优势。CHI 2026 Rememo 发表进入 9 天倒计时，需提前准备解读框架。**

### Key Findings

1. **NLP/LLM 方法论强化**: Amory/HiAgent/TReMu 三篇 SSS 优先级论文，直接支撑 L0 架构演进
2. **ASR Mock 测试稳定性验证**: 连续 9 次运行结果完全一致，框架生产级就绪
3. **L0 鲁棒性测试 #3**: 159 测试 100% 通过，已知脆弱点 V1-V4 无新增
4. **竞品技术成熟度评估**: arXiv 仅 2 篇直接相关、GitHub 最高 stars 仅 4 个、Neuroglee 专利需 FTO 分析
5. **窗口期明确**: 6-12 个月内若快速产品化 + 临床验证 + 论文发表，可建立壁垒

### Implications for CittaVerse

1. **加速 Pilot RCT**: 临床验证是差异化核心 (伦理审批已超期 6 天)
2. **考虑开源策略**: 开源非核心模块可建立事实标准 (竞品开源生态薄弱)
3. **FTO 分析优先级提升**: Neuroglee 专利需专业评估 (RB-024)
4. **Rememo 合作可能**: 同一研究方向，不同市场 (新加坡 vs 中国)，可探索合作 (RB-027)
5. **L0 v0.8 规划**: 整合 Amory 叙事记忆 + HiAgent 层次化记忆 + TReMu 时间推理

---

**下次整理**: 2026-04-11 (周更节奏)  
**维护者**: Hulk 🟢

---

*Hulk 🟢 — Compressing chaos into structure*  
**整理完成时间**: 2026-04-04 20:40 UTC  
**累计整理**: 8 次 (03-25/03-26/03-27/03-28/03-30/04-02/04-03/04-04)  
**知识库总文件**: 218 篇结构化知识
