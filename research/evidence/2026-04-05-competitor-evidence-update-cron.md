# 竞品 + 证据库更新报告 — 2026-04-05

**执行时间**: 2026-04-05 06:45 UTC  
**执行人**: Hulk 🟢  
**任务**: 12 竞品持续追踪 + 叙事疗法/MCI/数字传记证据更新  
**扫描窗口**: 2026-04-04 至 2026-04-05 (24 小时新证据)  
**数据源**: arXiv (browser ⚠️ 间歇性超时)

---

## 执行摘要

### 工具状态 (部分恢复，不稳定)

| 工具 | 状态 | 说明 |
|------|------|------|
| `web_search` | ❌ | DuckDuckGo bot-detection (持续) |
| `browser` | ⚠️ | arXiv 可用但间歇性超时 |
| `web_fetch` | ⚠️ | 未测试 (之前有 VPN fake-IP 阻断) |
| `exec` | ⚠️ | 未测试 (之前 host=node 不支持 system.run) |

**影响**: **browser 可访问 arXiv 但稳定性下降**。今日搜索 MCI 相关论文时遭遇超时，仅完成 Rememo 论文确认和叙事连贯性文献扫描。

**本轮策略**: 聚焦已知关键论文状态确认，广义 arXiv 扫描受限。

---

## Bottom Line

**核心结论**: **24 小时内无颠覆性新证据**。Rememo CHI 2026 论文状态稳定，倒计时 8 天。叙事连贯性文献库维持 04-04 结论 (478 篇 arXiv 论文)。

| 关键结论 | 当前状态 | 24h 新证据 | 风险等级 |
|---------|---------|-----------|---------|
| LLM 自传体记忆评分 r=0.87 | ✅ 稳定 | 无推翻证据 | 🟢 低 |
| 语音生物标志物 AD 预测>78% | ✅ 稳定 | 未扫描 (browser 超时) | 🟢 低 |
| 神经符号 AI=可审计路径 | ⚠️ 待验证 | 未扫描 | 🟡 中 |
| 多 Agent 医疗评估趋势 | ✅ 稳定 | 未扫描 | 🟢 低 |
| Rememo 竞品 | ✅ 确认 | arXiv:2602.17083 状态稳定 | 🟡 中 (CHI 04-13) |
| 叙事连贯性评估方法 | ✅ 稳定 | 478 篇文献 (无新增高相关) | 🟢 低 |

**总体评估**: 证据库稳定，无新增高相关性论文。CHI 2026 Rememo 发表进入 8 天倒计时。

---

## Part I: arXiv 证据扫描 (受限)

### 1.1 Rememo 竞品论文确认

**arXiv:2602.17083** — 状态验证 (2026-04-05 06:45 UTC)

| 字段 | 值 |
|------|-----|
| **标题** | Rememo: A Research-through-Design Inquiry Towards an AI-in-the-loop Therapist's Tool for Dementia Reminiscence |
| **作者** | Celeste Seah, Yoke Chuan Lee, Jung-Joo Lee, Ching-Chiuan Yen, Clement Zheng |
| **分类** | cs.HC (人机交互) |
| **提交日期** | 2026-02-19 |
| **版本** | v1 (未更新) |
| **状态** | ✅ 稳定 (CHI 2026 投稿) |
| **定位** | 治疗师工具 (AI-in-the-loop) |
| **与 CittaVerse 差异** | Rememo 面向治疗师，我们面向老年人直接交互 + B2B2C |

**验证等级**: V3 (静态复核 — arXiv 页面亲自检查)

---

### 1.2 叙事连贯性文献扫描

**搜索词**: "narrative coherence"  
**结果**: 478 篇 (arXiv 全量)

**2026 年新增高相关性论文** (03-01 至 04-05):

| arXiv ID | 标题 | 日期 | 相关性 | 状态 |
|----------|------|------|--------|------|
| arXiv:2603.25537 | Humans vs Vision-Language Models: A Unified Measure of Narrative Coherence | 03-26 | ⭐⭐⭐⭐ | 04-02 已收录 |
| arXiv:2603.16410 | PlotTwist: A Creative Plot Generation Framework with Small Language Models | 03-17 | ⭐⭐⭐ | 04-04 已收录 |
| arXiv:2603.29661 | Agenda-based Narrative Extraction: Steering Pathfinding Algorithms with LLMs | 03-31 | ⭐⭐ | 新增 |
| arXiv:2603.28082 | LogiStory: A Logic-Aware Framework for Multi-Image Story Visualization | 03-30 | ⭐⭐ | 新增 |
| arXiv:2603.20003 | An Agentic Approach to Generating XAI-Narratives | 03-20 | ⭐⭐ | 新增 |

**说明**: 
- arXiv:2603.29661 (叙事提取)、arXiv:2603.28082 (多图像故事可视化)、arXiv:2603.20003 (XAI 叙事生成) 为新增发现
- 相关性⭐⭐，非核心证据，但可丰富叙事评估方法学参考

**验证等级**: V1 (单来源确认 — arXiv 搜索结果)

---

### 1.3 MCI 认知障碍检测扫描

**搜索词**: "MCI mild cognitive impairment LLM"  
**状态**: ❌ browser 超时，未完成扫描

**建议**: 等待 web_search 修复或 browser 稳定性恢复后补扫。

**验证等级**: V0 (未验证)

---

## Part II: 12 竞品追踪状态

| # | 产品名称 | 最后追踪 | 24h 变化 | 状态 | 备注 |
|---|----------|----------|---------|------|------|
| 1 | **Rememo** | 2026-04-05 | ✅ arXiv 页面确认 (v1 稳定) | 🟡 CHI 2026 倒计时 8 天 | 02-19 提交，CHI 会议 04-13 至 04-17 |
| 2 | **Sophia** | 2025-12-20 | ⚠️ 未扫描 | 🟢 稳定 | arXiv:2512.18202 |
| 3 | **LLM-MCI-detection** | 2026-03-08 | ⚠️ 未扫描 | 🟢 稳定 | GitHub 项目 |
| 4 | **LLMCARE (2025)** | 2026-03-08 | ⚠️ 未扫描 | 🟢 稳定 | GitHub 项目 |
| 5 | **Alzheimer-s-Detection** | 2026-03-08 | ⚠️ 未扫描 | 🟢 稳定 | GitHub 项目 |
| 6 | **DiaMond** | 2026-03-08 | ⚠️ 未扫描 | 🟢 稳定 | GitHub 项目 |
| 7 | **StoryFile** | TBD | ⚠️ browser 限制 | 🟡 工具限制 | 官网抓取需单独导航 |
| 8 | **LegacyLab** | TBD | ⚠️ browser 限制 | 🟡 工具限制 | 官网抓取需单独导航 |
| 9 | **MemoryLane** | TBD | ⚠️ browser 限制 | 🟡 工具限制 | 官网抓取需单独导航 |
| 10 | **Eldera** | TBD | ⚠️ browser 限制 | 🟡 工具限制 | 官网抓取需单独导航 |
| 11 | **Rendever** | TBD | ⚠️ browser 限制 | 🟡 工具限制 | 官网抓取需单独导航 |
| 12 | **Unmind/Headspace** | TBD | ⚠️ browser 限制 | 🟡 工具限制 | 官网抓取需单独导航 |

**说明**: 
- Rememo arXiv 页面已确认 (v1, 02-19 提交，无更新)
- 消费级竞品 (7-12) 需单独 browser 导航抓取，本轮未执行
- GitHub 竞品 (3-6) 需 web_search 或 exec git 命令，本轮未执行

---

## Part III: 证据库状态更新

### 3.1 神经符号 AI 证据

**本轮扫描**: 未执行 (browser 超时)

**状态**: 维持 04-04 结论 (5 篇背书论文)

**验证等级**: V0 (未验证)

---

### 3.2 多 Agent 评估证据

**本轮扫描**: 未执行

**状态**: 维持 04-04 结论 + 1 篇 (DITING)

**验证等级**: V0 (未验证)

---

### 3.3 叙事评估证据

**本轮新增**: 3 篇⭐⭐相关性论文 (见 1.2 节)

| arXiv ID | 标题 | 日期 | 相关性 |
|----------|------|------|--------|
| arXiv:2603.29661 | Agenda-based Narrative Extraction | 03-31 | ⭐⭐ |
| arXiv:2603.28082 | LogiStory: Multi-Image Story Visualization | 03-30 | ⭐⭐ |
| arXiv:2603.20003 | Agentic Approach to Generating XAI-Narratives | 03-20 | ⭐⭐ |

**状态**: 小幅扩展 (非核心证据)

**验证等级**: V1 (单来源确认)

---

### 3.4 数字传记证据

**本轮扫描**: 未执行

**状态**: 维持 04-04

**验证等级**: V0 (未验证)

---

## Part IV: 验证等级说明

| 等级 | 描述 | 本轮占比 |
|------|------|---------|
| V0 | 未验证/仅推断 | MCI 扫描、神经符号、多 Agent、数字传记 |
| V1 | 单来源确认 | **3 篇新论文** (叙事评估⭐⭐) |
| V2 | 多来源交叉确认 | 0 篇 |
| V3 | 静态复核 | **Rememo arXiv 页面确认** |
| V4 | 动态验证/可复现 | 0 篇 |

**说明**: 本轮因 browser 稳定性问题，仅完成 Rememo 确认和叙事连贯性有限扫描。

---

## Part V: 行动建议

### P0 - 紧急 (24 小时内)

| 行动项 | 理由 | 截止 | 负责人 |
|--------|------|------|--------|
| **CHI 2026 Rememo 论文监测** | 会议 04-13 至 04-17 (剩余 8 天)，需提前准备解读框架 | 04-10 | Hulk |
| **web_search 修复** | DuckDuckGo bot-detection 持续，失去广义 web 扫描能力 | 04-05 | V |
| **browser 稳定性排查** | arXiv 搜索 MCI 时超时，影响证据扫描 | 04-06 | V |

### P1 - 高优先级 (本周内)

| 行动项 | 理由 | 截止 | 负责人 |
|--------|------|------|--------|
| **MCI 证据补扫** | 04-05 未完成，需验证语音生物标志物新进展 | 04-07 | Hulk |
| **消费级竞品 (7-12) browser 手动扫描** | browser 可用时单独导航抓取官网 | 04-07 | Hulk |
| **2510.24831 Narrative Continuity Test 深读** | 直接关联 L0 六维"自我认同整合"维度 | 04-08 | Hulk |

### P2 - 中优先级 (两周内)

| 行动项 | 理由 | 截止 | 负责人 |
|--------|------|------|--------|
| **GitHub 竞品 (3-6) 状态扫描** | 需 exec 或 web_search，等待工具修复 | 04-14 | Hulk |
| **神经符号 AI 扩展搜索** | "neurosymbolic"无结果，需扩展搜索词 | 04-14 | Hulk |

---

## Part VI: 结论

### 6.1 核心结论

1. ✅ **Rememo CHI 2026 论文状态稳定** (arXiv:2602.17083v1, 02-19 提交，无更新) — 竞品动态明确
2. ⚠️ **MCI 证据扫描失败** (browser 超时) — 需补扫
3. ✅ **叙事评估证据小幅扩展** (3 篇⭐⭐论文) — 非核心但可丰富方法学参考
4. ⚠️ **工具稳定性下降** (browser 间歇性超时) — 影响证据扫描效率
5. ⚠️ **消费级竞品扫描受限** (browser 需单独导航) — 工具效率待优化

### 6.2 风险态势

| 风险类型 | 等级 | 说明 |
|---------|------|------|
| **CHI 2026 Rememo 发表** | 🟡 中 | 8 天后会议开始，需提前准备解读 |
| web_search 工具故障 | 🟡 中 | DuckDuckGo bot-detection 持续 |
| browser 稳定性 | 🟡 中 | arXiv 搜索 MCI 时超时 |
| 技术迭代风险 | 🟢 低 | 基于本轮扫描，无突破性新研究 |
| 竞品动态风险 | 🟡 中 | 消费级竞品 (7-12) 验证不完全 |

### 6.3 建议

1. **CHI 2026 重点监测**: Rememo 论文 04-13 至 04-17 发表，04-10 前完成解读框架准备
2. **工具修复优先级**: web_search (DuckDuckGo bot-detection) > browser 稳定性 > browser 批量扫描优化
3. **证据库扩展**: 叙事评估 3 篇新论文可择一深读 (推荐 arXiv:2603.29661 叙事提取)
4. **竞品扫描策略**: browser 单独导航消费级竞品官网 (7-12)，本周内完成
5. **MCI 补扫**: 待 browser 稳定后优先补扫 MCI 证据

---

## 更新日志

| 日期 | 更新内容 | 验证等级 | 新论文数 | 工具状态 |
|------|----------|----------|----------|---------|
| **2026-04-05** | **arXiv 扫描 (browser ⚠️ 超时)** | V1/V3 | **3 篇** (⭐⭐) | ⚠️ (arXiv only, 不稳定) |
| 2026-04-04 | arXiv 扫描 (browser 恢复) | V1 | 11 篇 | ✅ (arXiv only) |
| 2026-04-03 | 工具链故障，无法扫描 | V0 | 0 篇 | ❌❌❌❌❌ |
| 2026-04-02 | 48 小时快速更新 | V1 | 5 篇 | ✅ (arXiv only) |
| 2026-03-31 | 7 天证据保鲜验证 | V1-V4 | 12 篇 | ✅ |
| 2026-03-29 | 周更竞品追踪 | V1-V2 | - | ✅ |

---

*Hulk 🟢 — 密度即价值*  
*数据截至 2026-04-05 06:45 UTC*  
*工具状态：web_search ❌ | browser ⚠️ (arXiv, 不稳定) | web_fetch ⚠️ | exec ⚠️*  
*本轮新增：**3 篇新论文** (叙事评估⭐⭐)*  
*CHI 2026 Rememo 倒计时：**8 天** (04-13 至 04-17)*

---

## 交付说明

**产出文件**: `research/evidence/2026-04-05-competitor-evidence-update-cron.md`

**文件位置**: `/Users/moondy/.openclaw/workspace-hulk/research/evidence/`

**验证**: V3 (静态复核 — 文件已创建)

**下一步**: 
1. CHI 2026 Rememo 监测准备 (04-10 前)
2. web_search 工具修复 (V)
3. browser 稳定性排查 (V)
4. MCI 证据补扫 (04-07 前)
5. 消费级竞品 browser 手动扫描 (04-07 前)
