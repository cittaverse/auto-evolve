# 知识库整理日志 | Knowledge Base Consolidation Log

**日期**: 2026-03-25 20:45 UTC  
**执行人**: Hulk 🟢  
**任务**: 储备·知识库整理 — 将 research/ 下散落的研究成果结构化沉淀到 knowledge-base/

---

## 本次整理概览

### 新增文件索引 (3 个)

| 知识域 | 新增文件 | 主题 | 验证等级 |
|--------|---------|------|----------|
| **04-competitive-intel** | `research/evidence_scan/weekly_2026-03-25.md` | 证据扫描周报 W14: BMC Geriatrics MA (SMD=0.387) + Lancet Semaglutide + tDCS RCT | V2 |
| **04-competitive-intel** | `research/arxiv-digest-2026-03-25.md` | arXiv 前沿论文摘要：MemCollab/PERMA/MSP-Conversation/Cultural LLM 等 15 篇 | V1 |
| **03-ethics-clinical** | `research/paper/02-experiment-design-refined.md` | 实验设计 v2.0 完善版：变量控制清单 + Checklist 范式 + 事件边界验证 | V3 |

### 更新的文件索引 (2 个)

| 文件 | 更新内容 |
|------|----------|
| `knowledge-base/04-competitive-intel/INDEX.md` | +2 篇新文献 (W14 证据扫描 + arXiv 摘要), 文件总数 7→9 |
| `knowledge-base/03-ethics-clinical/INDEX.md` | +1 篇实验设计 v2.0, 文件总数 13→14 |
| `knowledge-base/README.md` | 更新文件计数和 timestamps |

---

## 核心知识增量

### 04-competitive-intel (竞品与市场)

#### W14 证据扫描核心发现 (weekly_2026-03-25.md)

1. **BMC Geriatrics MA (N=829, 15 RCTs)**: 数字健康干预 SCD/MCI 的 SMD=0.387
   - 认知功能显著改善，但情绪/生活质量无显著效果
   - 产品行动：Pilot 效应量基准设为 SMD=0.387，需同时测量认知 + 情绪验证"叙事疗法突破情绪天花板"

2. **Lancet Semaglutide evoke/evoke+**: GLP-1 RA 治疗早期 AD 的 Phase 3 RCT
   - 产品行动：如获批，阿宝应定位为"药物 + 叙事疗法联合方案"的非药物组件

3. **GeroScience tDCS RCT (N=144)**: 流体智力低者获益更大
   - 产品行动：Pilot 增加音位/语义流畅性测试，对话难度根据认知基线动态调整

4. **Remi (AAGP)**: LLM chatbot 回忆疗法，直接竞品/参照
   - 产品行动：追踪团队/方法/数据

#### arXiv 前沿论文摘要 (arxiv-digest-2026-03-25.md)

**15 篇论文覆盖 4 大方向**:
- **记忆**: MemCollab (跨 agent 记忆协作), PERMA (个人化记忆评估基准)
- **叙事**: Multiperspectivity (叙事相似性多元视角), LLM 装饰性推理检测
- **ASR**: MSR-HuBERT (多采样率自适应), MSP-Conversation (时间连续情感语料)
- **LLM**: Cultural Embeddings (文化本地化生成), SpecEyes (多模态 agent 加速)

**高优先级跟进**: MemCollab, PERMA, MSP-Conversation, Cultural LLM, Multiperspectivity

### 03-ethics-clinical (伦理审批与临床试验)

#### 实验设计 v2.0 完善版 (02-experiment-design-refined.md)

**核心改进 (v1.0 → v2.0)**:

| 维度 | v1.0 | v2.0 |
|------|------|------|
| 变量控制 | 原则性描述 | 操作化清单 (受试者/干预/评估/数据四层) |
| 对比组 | 干预组 vs 主动对照 | +A/B 嵌套设计 +5 种算法基线对比 |
| 评估指标 | 工具名称 + 时点 | 操作化定义 + 评分规范 + 截断值 + 培训要求 |
| Checklist 范式 | 未明确 | 整合 CheckEval 方法论，6 维度各 5 项二元 checklist |
| 事件边界验证 | 未独立 | 新增实验 5，F1>0.75 目标，±1 句容差处理 |
| 统计方法 | LMM 框架 | 完整 HLM 公式 + R 代码 + 效应量计算 |
| 样本量计算 | 经验估计 | 公式推导 + 参数依据 + 脱落率调整 |
| 盲法控制 | 提及 | 盲法检验程序 + 破坏处理方案 |
| 协变量 | 部分列出 | 完整列表 + 纳入理由 + 测量方式 |

**新增实验 5**: 事件边界检测独立验证 (F1>0.75 目标)

---

## 知识库当前状态

| 知识域 | 文件数 | 最近更新 | 状态 |
|--------|--------|----------|------|
| 01-narrative-scorer | 7 | 03-24 | ✅ 完整 |
| 02-metamemory | 6 | 03-23 | ✅ 完整 |
| 03-ethics-clinical | 14 | 03-25 | ✅ 完整 |
| 04-competitive-intel | 9 | 03-25 | ✅ 完整 |
| 05-product-strategy | 3 | 03-23 | ✅ 完整 |
| 06-infra-tools | 4 | 03-23 | ✅ 完整 |
| 07-outreach | 4 | 03-23 | ✅ 完整 |
| **总计** | **47** | - | - |

---

## 待办事项 (由本次整理发现)

### P0 - 高优先级

- [ ] **V 需审阅实验设计 v2.0** → 伦理审批材料准备前置条件
- [ ] **Pilot 效应量基准更新**: SMD=0.387 (来自 BMC Geriatrics MA)
- [ ] **Pilot 设计调整**: 同时测量认知 + 情绪，验证"叙事疗法突破情绪天花板"假设

### P1 - 中优先级

- [ ] **追踪 Remi 团队**: AAGP 完整摘要 + 合作/差异化可能
- [ ] **获取 Lancet evoke/evoke+ 全文**: semaglutide AD 疗效数据
- [ ] **arXiv 高优先级论文精读**: MemCollab, PERMA, MSP-Conversation, Cultural LLM
- [ ] **Pilot 评估工具扩充**: 增加音位/语义流畅性测试

### P2 - 低优先级

- [ ] **事件边界检测 Benchmark 标注**: 2 名评估者，100 段叙事
- [ ] **Checklist 范式评估者培训**: 6 维度×5 项二元 checklist
- [ ] **证据扫描周更节奏维持**: 下周关注 CHI 2026 接收论文

---

## 方法论反思

### 本次整理策略

1. **增量更新优先**: 仅处理 03-25 新增文件，避免大规模重构
2. **INDEX.md 为中心**: 每个知识域的 INDEX.md 是"压缩结论 + 文件清单"的单一事实源
3. **原始文件保留**: research/ 中的原始研究文件不动，只在 INDEX.md 中建立引用
4. **验证等级标注**: 每个文件条目都标注 V0-V4 验证等级，避免过度承诺

### 改进机会

1. **跨域交叉引用**: Rememo 相关材料同时出现在 04-competitive-intel 和 07-outreach，可在 INDEX.md 中增加"参见"链接
2. **版本演进链**: narrative-scorer v0.5→v0.6→arXiv 论文的演进关系可在 INDEX.md 中更清晰呈现
3. **开放问题追踪**: 每个知识域的"开放问题"列表可同步到 KANBAN.md 或 research-backlog.md

---

**下次整理**: 2026-04-01 (周更节奏)  
**维护者**: Hulk 🟢
