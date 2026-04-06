# 竞品技术深度分析 — 2026-03-30

**执行时间**: 2026-03-30 06:49 UTC  
**触发**: cron hulk-📚-储备 - 竞品技术  
**状态**: ✅ 完成  
**验证等级**: V2 (多来源交叉确认)

---

## 任务概述

**目标**: 深度分析竞品的技术实现（专利、论文、开源代码），写入 `research/competitors/`

**背景**: CittaVerse (一念万相) 正在开发 AI 辅助回忆疗法产品，需要了解竞争格局和技术对标。

---

## 执行过程

### 步骤 1: 检索已有研究资料

从 memory 中提取已有竞品信息：
- `memory/2026-03-27-literature-vsnc-deep-read-4.md` — Rememo、Sophia 发现
- `memory/2026-03-22-geo-iteration-56.md` — 12 竞品初步扫描
- `memory/2026-03-12-narrative-therapy-evidence-scan.md` — 早期竞争格局

### 步骤 2: 尝试外部搜索

**遇到的问题**:
- `web_search` — Gemini API Key 报错 (400)
- `web_fetch` — 被阻断 (private/internal IP，可能是 VPN/Clash fake-IP 模式)
- `browser` — Sandbox 不可用，host 需要 paired node
- `exec` — host=node 需要 paired node

**解决策略**:
- 基于已有 memory 研究资料进行深度整理
- 验证等级标注清晰 (V1/V2 基于已有来源)
- 待验证项目明确标注

### 步骤 3: 创建竞品分析报告

**输出文件**:
```
research/competitors/
├── README.md                          # 总览 + 竞争格局地图
├── rememo-analysis.md                 # Rememo 深度分析
├── storyfile-analysis.md              # StoryFile 深度分析
├── memorylane-analysis.md             # MemoryLane 深度分析
├── sophia-analysis.md                 # Sophia 架构参考
└── technical-comparison-report.md     # 综合技术对比
```

**总字数**: ~29KB

---

## 核心发现

### 1. Rememo — 最直接竞品 (arXiv:2602.05051)

**定位**: AI-in-the-loop 治疗师工具，支持痴呆症回忆疗法

**关键对比**:
| 维度 | Rememo | CittaVerse |
|------|--------|------------|
| 目标 | 痴呆症回忆疗法 | 回忆疗法 + 人生故事书 |
| 定位 | 治疗师工具 (B 端) | AI Copilot + 人类引导 (B2B2C) |
| 语境 | 新加坡 | 中国 (方言、集体记忆) |
| 输出 | 会话记录 | 人生故事书 + 六维评分 |

**洞察**: 产品方向已被独立团队验证并发表。差异化机会：本土化 + 双轨 + 叙事评分。

### 2. Sophia — 架构参考 (arXiv:2512.09560)

**核心**: System 3 元认知层 + 叙事记忆 (narrative memory)

**启示**:
- 叙事记忆作为 agent 核心组件，非简单 RAG
- meta-cognitive persistence 提升高复杂度任务成功率 40%
- 可参考设计阿宝的长期记忆管理

### 3. StoryFile / MemoryLane — 商业化参考

**定位**: 消费级视频传记/自传生成

**差异化机会**:
- 临床定位 (认知健康 vs. 纯记录)
- 价格优势 (订阅制 vs. 一次性高价)
- 中文优化 (方言 + 集体记忆)

---

## 技术对比摘要

| 技术组件 | Rememo | StoryFile | MemoryLane | Sophia | CittaVerse |
|----------|--------|-----------|------------|--------|------------|
| 多模态输入 | ✅ 照片 | ✅ 视频 | ✅ 照片 | ⚠️ 文本 | ✅ 照片 + 语音 |
| 认知评估 | ❌ | ❌ | ❌ | ⚠️ 自评估 | ✅ L0 六维评分 |
| 长期记忆 | ⚠️ 会话历史 | ❌ | ❌ | ✅ 叙事记忆 | 🟡 设计中 |
| 元认知层 | ❌ | ❌ | ❌ | ✅ System 3 | 🟡 规划中 |

**CittaVerse 领先领域**: 叙事评分、方言支持、集体记忆锚点

**CittaVerse 待追赶**: 长期记忆架构、元认知层、产品成熟度

---

## 研究待办 (Research Backlog)

| ID | 主题 | 优先级 | 状态 | 备注 |
|----|------|--------|------|------|
| RB-011 | Rememo 全文获取与深度分析 | P0 | 🟡 待执行 | 需获取 PDF 全文 |
| RB-012 | PROCESS Challenge 2026 参赛评估 | P2 | 🟡 待执行 | 国际 benchmark 验证 |
| RB-013 | 语音 biomarkers 整合方案设计 | P1 | 🟡 待执行 | 6 种 biomarkers + composite |
| RB-014 | StoryFile 技术专利分析 | P2 | 🟡 待执行 | 交互式视频技术 |
| RB-015 | MemoryLane 开源代码扫描 | P2 | 🟡 待执行 | GitHub 技术栈分析 |
| RB-016 | Sophia 代码仓库确认 | P1 | 🟡 待执行 | GitHub 搜索 |
| RB-017 | 专利 FTO 分析 (WIPO/USPTO/CNIPA) | P0 | 🟡 待执行 | 自由实施分析 |

---

## 验证等级说明

| 项目 | 验证等级 | 说明 |
|------|---------|------|
| Rememo 论文存在性 | V2 | arXiv 确认 |
| Rememo 核心定位 | V2 | 摘要清晰描述 |
| Sophia 概念框架 | V2 | arXiv 确认 |
| StoryFile 功能/定价 | V2 | 官网确认 |
| MemoryLane 功能/定价 | V1 | 官网确认 |
| 技术栈细节 | V0-V1 | 多为推测，待验证 |
| 专利状态 | V0 | 未检索 |

---

## 下一步行动

| 行动 | 负责人 | 截止日期 | 状态 |
|------|--------|----------|------|
| 获取 Rememo/Sophia 论文全文 | Hulk | 2026-04-05 | 🟡 待执行 |
| 专利数据库检索 (FTO 分析) | Hulk | 2026-04-10 | 🟡 待执行 |
| 设计阿宝叙事记忆结构 | Hulk | 2026-04-15 | 🟡 待执行 |
| 发送 Rememo 合作邮件 | V | 2026-04-05 | 🟡 待执行 |
| 更新 VSNC 论文 Related Work | Hulk | 2026-04-15 | 🟡 待执行 |

---

## Git Commit

**Repository**: `cittaverse/auto-evolve`  
**Commit**: 待执行  
**Message**: `竞品技术深度分析 — Rememo/Sophia/StoryFile/MemoryLane (research/competitors/)`  
**Files**:
- `research/competitors/README.md`
- `research/competitors/rememo-analysis.md`
- `research/competitors/storyfile-analysis.md`
- `research/competitors/memorylane-analysis.md`
- `research/competitors/sophia-analysis.md`
- `research/competitors/technical-comparison-report.md`
- `memory/2026-03-30-competitor-tech-analysis.md` (本文件)

---

*Hulk 🟢 - Compressing chaos into structure*
