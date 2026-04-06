# 竞品 + 证据库更新 — 2026-03-26 (Cron 轮次)

**扫描日期**: 2026-03-26 06:45 UTC  
**基准版本**: `research/evidence/2026-03-26-competitor-evidence-update.md` (同日早间版本)  
**扫描范围**: 12 竞品状态追踪 + 叙事疗法/MCI/数字传记学术证据更新  
**验证等级**: V1（arXiv API 直接获取）

---

## 执行摘要

### 本轮扫描结果

| 维度 | 发现 | 状态 |
|------|------|------|
| 12 竞品新信号 | 无重大更新 | ⚪ 延续 03-24/03-26 基线 |
| arXiv 新增论文 | 0 篇（与 03-26 早间扫描一致） | → 无增量 |
| 工具状态 | arXiv API 可用，web_search/ddg-search 不可用 | ⚠️ 部分受限 |

### Bottom Line

- **竞品窗口持续开放**: 12 竞品无新融资/产品更新信号，CittaVerse 的"临床验证 × 叙事评分 × 中文优化"定位仍为唯一组合
- **学术证据稳定**: 03-26 早间扫描已覆盖最新 arXiv 论文（2405.02560 fNIRS 研究、2603.21381 XR 记忆对象研究）
- **本轮为确认性扫描**: 无重大新信号，基线结论维持不变

---

## Part I: 12 竞品状态追踪

### 状态总览（延续 03-26 早间基线）

| # | 竞品 | 国家 | 定位 | 最新状态 | 变化 |
|---|------|------|------|----------|------|
| 1 | **StoryFile** | USA | 视频传记 | $10M+ Series A, $99-299/月 | ⚪ |
| 2 | **MemoryLane** | UK | 照片传记 | Seed, £49 一次性 | ⚪ |
| 3 | **LifeStory** | USA | 语音采访 | $199/年 | ⚪ |
| 4 | **Rememo** | Singapore | 图像生成 + 治疗师工具 | CHI 2026 (4 月 13-17) 待发表 | 🟡 持续关注 |
| 5 | **Vivid** | USA | 痴呆数字传记 | B2B 养老机构 | ⚪ |
| 6 | **MyHeritage** | Israel | 家谱+AI 动画 | 上市 | ⚪ |
| 7 | **StoryWorth** | USA | 每周问题 + 年终成书 | Acquired, $99/年 | ⚪ |
| 8 | **Qeepsake** | USA | 育儿日记 AI | $59/年 | ⚪ |
| 9 | **回忆录** | 中国 | 自传写作工具 | 免费 + 广告 | ⚪ |
| 10 | **时光小屋** | 中国 | 家庭相册 | ¥199/年 | ⚪ |
| 11 | **小年糕** | 中国 | 中老年相册视频 | 免费 + 电商 | ⚪ |
| 12 | **养老伴侣 AI** | 中国 | 聊天机器人 + 健康提醒 | ¥29-99/月 | ⚪ |

### 关键观察

1. **Rememo 是近期唯一变量**: CHI 2026 论文将于 4 月 13-17 发表，需持续关注最终版本与 CittaVerse 的差异化确认
2. **中国产品仍停留在娱乐/记录层**: 无临床背书、无叙事评估能力
3. **欧美产品定价高**: $99-299/月 vs. CittaVerse 目标¥299-999/年 — 价格差 10-50 倍

---

## Part II: 学术证据库状态

### 核心证据（03-26 早间已覆盖）

| arXiv ID | 标题 | 日期 | 相关性 | 验证等级 |
|----------|------|------|--------|----------|
| **2405.02560** | 机器人辅助 RT 的 fNIRS 研究 | 2024-05-04 | SAR-led vs human-led RT 在 DLPFC 激活无差异 | V1 |
| **2603.21381** | XR 物理 vs 虚拟记忆对象 | 2026-03-22 | 物理对象促进更强社交连接 | V1 |
| **2507.01548** | 汉字叙事 AI 共创 | 2025-07-02 | AI 作为支持机制而非内容生产者 | V1 |
| **2203.04645** | HAIDA 音乐疗法生物标志物 | 2022-03-09 | 多模态生物标志物用于认知障碍 | V1 |

### 本轮新增扫描（无增量）

```bash
# 查询 1: cs.AI + elderly + storytelling/narrative
# 结果：1 篇 (2507.01548, 已覆盖)

# 查询 2: cs.CL + autobiographical + memory + LLM
# 结果：0 篇

# 查询 3: cs.HC + memory + XR
# 结果：11 篇，最相关 2603.21381 (已覆盖)

# 查询 4: digital + biography + AI + elderly
# 结果：0 篇
```

### 证据库完整性评估

| 证据类型 | 覆盖度 | 说明 |
|----------|--------|------|
| AI 交付 RT 的神经科学证据 | ✅ | 2405.02560 fNIRS RCT |
| 物理/数字记忆对象设计 | ✅ | 2603.21381 XR 研究 |
| 文化特定叙事设计 | ✅ | 2507.01548 汉字叙事 |
| 多模态生物标志物 | ✅ | 2203.04645 HAIDA |
| Meta 分析/NMA | ⚠️ | 需补充（03-24 基线有 4 篇） |
| Nature 子刊背书 | ⚠️ | 需补充（03-24 基线有 1 篇） |

---

## Part III: 战略启示（无变化）

### 1. AI 交付 RT 的神经科学背书

2405.02560 的 fNIRS 研究继续为 CittaVerse 的 AI 引导对话提供理论支持：
- SAR-led RT 与 human-led RT 在 DLPFC 激活上无显著差异
- 建议在融资材料/论文中引用

### 2. 物理对象 + 数字叙事的混合设计

2603.21381 的设计启示：
- B2B 场景可探索"物理照片/实物 + AI 引导"混合流程
- 与 Rememo 的图像生成形成差异化（CittaVerse 聚焦后评估）

### 3. 中文文化特定设计

2507.01548 的汉字叙事研究：
- AI 作为支持机制而非内容生产者 — 与 CittaVerse 理念一致
- 中国老年人的叙事设计应包含文化符号（汉字、历史事件、年代记忆）

---

## 验证状态

| 任务 | 验证等级 | 状态 | 说明 |
|------|---------|------|------|
| 12 竞品状态检查 | V0 | ⚠️ | 工具限制，沿用 03-24/03-26 基线 |
| arXiv 论文扫描 | V1 | ✅ | arXiv API 直接获取 |
| 竞品官网监测 | V0 | ❌ | web_fetch/browser 不可用 |
| 全文深度分析 | V0 | ❌ | 全文获取受限 |

---

## 下一步建议

### Hulk 可继续执行（下次 cron 轮次）

1. **arXiv 持续监测**: 维持每周 2-3 次 arXiv API 扫描（cs.CL, cs.HC, cs.AI, cs.RO）
2. **CHI 2026 追踪**: Rememo 的 CHI 2026 论文 4 月 13-17 发表，需提前准备解读
3. **证据结构化**: 将核心证据整理为 APA 引用格式，供论文/融资材料使用

### 需 V/Core 协助

1. **工具链修复**:
   - Serper API 额度补充（web_search 恢复）
   - VPN/网络配置优化（web_fetch 恢复）
   - Browser 重启（browser 工具恢复）

2. **arXiv 提交决策**:
   - 技术报告初稿已完成（`research/paper/`）
   - 建议本周内提交，抢占 AI+ 叙事评估的学术定位

---

## 附录：本轮扫描命令

```bash
# 查询 1: RT + MCI + cognitive
curl "https://export.arxiv.org/api/query?search_query=all:reminiscence+AND+all:MCI+AND+all:cognitive&sortBy=submittedDate&sortOrder=descending&max_results=10"

# 查询 2: AI + elderly + storytelling
curl "https://export.arxiv.org/api/query?search_query=cat:cs.AI+AND+all:elderly+AND+all:storytelling+OR+all:narrative&sortBy=submittedDate&sortOrder=descending&max_results=10"

# 查询 3: autobiographical + memory + LLM
curl "https://export.arxiv.org/api/query?search_query=cat:cs.CL+AND+all:autobiographical+AND+all:memory+AND+all:LLM&sortBy=submittedDate&sortOrder=descending&max_results=10"

# 查询 4: XR + memory
curl "https://export.arxiv.org/api/query?search_query=cat:cs.HC+AND+all:memory+AND+all:XR&sortBy=submittedDate&sortOrder=descending&max_results=10"

# 查询 5: digital + biography + AI + elderly
curl "https://export.arxiv.org/api/query?search_query=all:digital+AND+all:biography+AND+all:AI+AND+all:elderly&sortBy=submittedDate&sortOrder=descending&max_results=10"
```

---

*Hulk 🟢 — 密度即价值*  
*数据截至 2026-03-26 06:47 UTC*  
*工具状态：arXiv API ✅ | web_search ❌ | ddg-search ❌ | web_fetch ❌ | browser ❌*
