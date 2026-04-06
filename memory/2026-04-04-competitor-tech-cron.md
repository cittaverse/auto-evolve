# 竞品技术深度分析 — 2026-04-04 (Cron Run)

**执行时间**: 2026-04-04 05:45 UTC  
**触发**: cron `hulk-📚-储备 - 竞品技术`  
**状态**: ✅ 完成  
**验证等级**: V2 (browser 直接访问确认)

---

## 执行摘要

本轮通过 browser 直接访问 arXiv、GitHub、Google Patents，完成全面竞品扫描：

### 核心发现

1. **arXiv 仅 2 篇直接相关论文** — Rememo (2026-02) 是唯一近期高质量研究
2. **GitHub 13 个仓库，生态极度薄弱** — 最高 stars 仅 4 个，无商业化代码
3. **Google Patents ~1,319 项** — Neuroglee US20230395235A1 是最直接竞品专利
4. **窗口期 6-12 个月** — 无成熟竞品，CittaVerse 有机会建立先发优势

### 输出文件

- `research/competitors/10-2026-04-04-incremental-update.md` (9.5KB 详细报告)
- `research/competitors/README.md` (更新研究待办 + 最新洞察)

### 新增研究待办

| ID | 主题 | 优先级 |
|----|------|--------|
| RB-023 | MemoryLane GitHub 仓库深度分析 | P1 |
| RB-024 | Neuroglee 专利 claims 详细分析 | P0 |
| RB-025 | elisabot (ACM ICMR 2020) 代码分析 | P2 |
| RB-026 | 开源策略制定 | P1 |
| RB-027 | Rememo 团队联系与合作评估 | P1 |

---

## 关键数据

### arXiv 搜索结果

| arXiv ID | 标题 | 日期 | 相关性 |
|----------|------|------|--------|
| 2602.17083 | Rememo: AI-in-the-loop Therapist's Tool | 2026-02-19 | ⭐⭐⭐ |
| 1910.11949 | Automatic Reminiscence Therapy (MSc thesis) | 2019-10-25 | ⭐⭐ |

### GitHub Top 仓库

| 仓库 | Stars | 最后更新 | 技术栈 |
|------|-------|----------|--------|
| marionacaros/elisabot | 4 | 2023-09-22 | Python |
| NathaliaCespedesG/ReminiscenceSAR | 3 | 2023-02-08 | Python + Pepper |
| aroramrinaal/memorylane | 2 | 2024-09-30 | TypeScript |
| andreihar/memory-lane | 2 | 2024-08-26 | Java (Android) |

### 最相关专利

| 专利号 | 申请人 | 优先级 | 相关性 |
|--------|--------|--------|--------|
| US20230395235A1 | Neuroglee Science Pte. Ltd. | 2020-10-23 | ⭐⭐⭐ |
| US10706971B2 | Elements of Genius, Inc. | 2017-08-02 | ⭐⭐ |

---

## 下一步行动

| 行动 | 负责人 | 截止日期 |
|------|--------|----------|
| 获取 Rememo 论文 PDF (绕过 VPN 限制) | Hulk | 2026-04-05 |
| MemoryLane GitHub 仓库深度分析 | Hulk | 2026-04-06 |
| Neuroglee 专利 claims 分析 | Hulk | 2026-04-08 |
| 起草开源策略文档 | Hulk | 2026-04-10 |
| 委托专业机构做 FTO 分析 | V | 2026-04-15 |

---

## 技术限制

**遇到的问题**:
- `web_search` — DuckDuckGo bot-detection
- `web_fetch` / `pdf` — Blocked: private/internal IP (VPN/Clash fake-IP 模式)
- `browser` — 可用，但需要手动导航 + snapshot

**解决策略**:
- 使用 browser 直接访问目标网站
- 通过 snapshot 提取结构化信息
- 无法直接下载 PDF，需寻找替代方案

---

*Hulk 🟢 - Compressing chaos into structure*
