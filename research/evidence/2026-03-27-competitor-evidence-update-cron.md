# 竞品 + 证据库更新 — 2026-03-27 (Cron)

**扫描日期**: 2026-03-27 06:45 UTC  
**基准版本**: `research/evidence/2026-03-27-freshness-verification-report.md`  
**扫描范围**: 12 竞品状态追踪 + 叙事疗法/MCI/数字传记学术证据更新  
**验证等级**: V1-V2（arXiv API + ddg-search）

---

## 执行摘要

### 工具状态

| 工具 | 状态 | 说明 |
|------|------|------|
| `web_search` (Gemini) | ❌ | API Key not found |
| `ddg-search` | ⚠️ | Anti-bot 检测（3-4 次查询后触发） |
| `web_fetch` | ❌ | VPN fake-IP 阻断 |
| `browser` | ❌ | 超时不可用 |
| `arXiv API` | ✅ | 正常工作 |

**应对策略**: 以 arXiv API 为主，ddg-search 为辅（控制查询频率避免触发 anti-bot）

---

## Bottom Line

**核心结论**: 过去 24 小时内**未发现**能推翻现有核心结论的新证据，但新增 2 篇高相关 arXiv 论文。

| 关键结论 | 当前状态 | 24h 新证据 | 风险等级 |
|---------|---------|-----------|---------|
| LLM 自传体记忆评分 r=0.87 | ✅ 稳定 | 无冲突 | 🟢 低 |
| 语音生物标志物 AD 预测>78% | ✅ 稳定 | 无冲突 | 🟢 低 |
| 神经符号 AI=可审计路径 | ✅ 强化 | 无新冲突 | 🟢 低 |
| 12 竞品无重大新信号 | ✅ 稳定 | Rememo CHI 2026 临近 | 🟡 中 |
| Cerebra 多模态痴呆评估 | 🆕 新增 | arXiv 2603.21597 (03-24) | 🟢 参考 |
| LoV3D 脑 MRI 认知预后 | 🆕 新增 | arXiv 2603.12071 (03-12) | 🟢 参考 |

**总体评估**: 现有研究结论保持稳定，新增 2 篇多模态痴呆评估论文（与 CittaVerse 定位互补而非竞争）。

---

## Part I: 12 竞品状态追踪

基于 03-26/03-27 基线，本轮未检测到重大更新（工具限制无法实时抓取竞品官网/新闻）。以下为确认状态：

| # | 竞品 | 定位 | 最近状态 | 变化 |
|---|------|------|---------|------|
| 1 | **Rememo** | 治疗师工具（图像生成） | CHI 2026 (4 月 13-17) 临近 | 🟡 重点关注 |
| 2 | **StoryFile** | 交互式视频传记 | $10M+ Series A | ⚪ |
| 3 | **BrainCheck** | 认知评估 | $13M Series A | ⚪ |
| 4 | **Remento** | B2C 传记服务 | Shark Tank 曝光 | ⚪ |
| 5 | **Eternos** | HLM 框架 | $10.3M Seed | ⚪ |
| 6 | **Vivid** | B2B 养老机构 | 商业运营中 | ⚪ |
| 7 | **MyHeritage** | 家谱 +AI 动画 | 上市公司 | ⚪ |
| 8 | **StoryWorth** | 每周故事邮件 | Acquired | ⚪ |
| 9 | **Qeepsake** | 育儿记忆 | $59/年 | ⚪ |
| 10 | **回忆录** | 中国，免费 + 广告 | 运营中 | ⚪ |
| 11 | **时光小屋** | 中国，¥199/年 | 运营中 | ⚪ |
| 12 | **小年糕** | 中国，免费 + 电商 | 运营中 | ⚪ |

### 关键观察

1. **Rememo CHI 2026 倒计时**: 论文将于 4 月 13-17 发表，需提前准备解读框架
2. **无新进入者信号**: ddg-search 未检测到新融资/新产品发布
3. **评估赛道仍为蓝海**: 12 竞品中仅 BrainCheck 专注评估，但聚焦认知测试而非叙事质量

---

## Part II: 学术证据更新

### 新增论文（arXiv 2026-03-27 扫描）

#### 📄 1. Cerebra: 多模态痴呆风险评估 AI 董事会

**arXiv**: 2603.21597  
**标题**: "Cerebra: A Multidisciplinary AI Board for Multimodal Dementia Characterization and Risk Assessment"  
**作者**: Liu, Sheng et al. (包括 Eric Topol, James Zou, Kyunghyun Cho 等)  
**日期**: 2026-03-24 (3 天前)  
**机构**: 多机构合作（4 个医疗系统，300 万患者数据）

**核心方法**:
- 多智能体 AI 团队协调 EHR、临床笔记、医学影像分析
- 临床医生仪表板 + 对话界面
- 隐私保护部署（结构化表示）

**核心结果**:
- 痴呆风险预测 AUROC: **0.80** (单模态最佳 0.74, LLM 基线 0.68)
- 痴呆诊断 AUROC: **0.86**
- 生存预测 C-index: **0.81**
- 医生读者研究：准确性提升 **17.5 个百分点**

**验证等级**: V1 (arXiv 摘要确认)

**对 CittaVerse 启示**:
- **多模态融合方向确认**: Cerebra 证明 EHR+ 影像 + 文本多模态融合优于单模态
- **临床工作流整合**: Cerebra 的"临床医生仪表板"设计对 CittaVerse B2B 场景有参考
- **可解释性优先**: Cerebra 强调"interpretable decision support"，与 CittaVerse 神经符号 AI 定位一致
- **非竞争关系**: Cerebra 聚焦医学影像+EHR，CittaVerse 聚焦叙事/语音，可互补

---

#### 📄 2. LoV3D: 脑 MRI 认知预后评估

**arXiv**: 2603.12071  
**标题**: "LoV3D: Grounding Cognitive Prognosis Reasoning in Longitudinal 3D Brain MRI via Regional Volume Assessments"  
**作者**: Jiang, Zhaoyang et al.  
**日期**: 2026-03-12 (2 周前，本轮新发现)  

**核心方法**:
- 3D VLM 读取纵向 T1 加权脑 MRI
- 区域级解剖学评估 + 纵向对比
- 三类诊断输出 (CN/MCI/Dementia) + 诊断摘要
- 临床加权 Verifier + Direct Preference Optimization（无需人工标注）

**核心结果**:
- ADNI 测试集 (479 scans, 258 subjects):
  - 三类诊断准确率: **93.7%** (+34.8% vs no-grounding baseline)
  - 二类诊断准确率: **97.2%** (+4% vs SOTA)
  - 区域级解剖分类准确率: **82.6%** (+33.1% vs VLM baselines)
- 零样本迁移:
  - MIRIAD: 95.4% (100% Dementia recall)
  - AIBL: 82.9% 三类准确率

**验证等级**: V1 (arXiv 摘要确认)

**对 CittaVerse 启示**:
- **纵向数据价值**: LoV3D 证明纵向 MRI 对比显著提升预后准确性 — CittaVerse 的纵向叙事追踪有类似潜力
- **Verifier 架构**: 临床加权 Verifier + DPO 无需人工标注 — CittaVerse 的叙事评分可借鉴此思路
- **多模态互补**: LoV3D (影像) + CittaVerse (叙事/语音) = 更完整的认知评估
- **开源策略**: LoV3D 代码已开源 — CittaVerse 开源策略符合趋势

---

#### 📄 3. 双模态 MCI 检测（台湾大学）

**来源**: JMIR Med Inform 2026 (via ddg-search)  
**标题**: "Dual-Modal Model Detects Mild Cognitive Impairment"  
**机构**: National Taiwan University  
**方法**: 自传体记忆语音 + 文本双模态纵向系统  
**核心创新**: 老化轨迹模块对齐跨访视的局部/全局时序特征

**验证等级**: V1 (新闻摘要确认，论文未获取)

**对 CittaVerse 启示**:
- **双模态验证**: 语音 + 文本双模态与 CittaVerse 规划方向一致
- **纵向设计**: 老化轨迹模块支持 CittaVerse 的长期追踪价值主张
- **地理邻近**: 台湾大学团队 — 潜在合作/对标机会

---

### 证据库增量总览

| 维度 | 03-27 早间基线 | 03-27 Cron 更新 | 变化 |
|------|---------------|----------------|------|
| arXiv 相关论文 | 7+ 篇 | **+2 篇** (2603.21597, 2603.12071) | ⬆ |
| 多模态痴呆评估 | 1 篇 | **+2 篇** (Cerebra, LoV3D) | ⬆ |
| MCI 双模态检测 | 0 | **+1 篇** (台大 JMIR) | 🆕 |
| 神经符号 AI 背书 | 3 篇 | 无新增 | → |
| 竞品动态 | 无新信号 | 无新信号 | → |

---

## Part III: 战略启示更新

### 1. 多模态融合趋势强化

Cerebra 和 LoV3D 共同证明：
- 多模态融合 > 单模态 (Cerebra AUROC 0.80 vs 0.74)
- 纵向数据 > 横断面 (LoV3D 纵向对比 +34.8% 提升)

**对 CittaVerse 启示**:
- **优先级提升**: 声学特征 + 叙事文本 + 纵向追踪的多模态整合应加速
- **差异化保持**: CittaVerse 的叙事评估仍是独特模态，与影像/EHR 互补

### 2. 可解释性成为共识

Cerebra 强调"interpretable decision support"，LoV3D 强调"grounding"和"biological plausibility"：

**对 CittaVerse 启示**:
- **神经符号 AI 定位正确**: 可审计路径是临床 AI 的关键需求
- **融资材料强化**: 在 Pitch Deck 中突出 NeSy vs 黑箱 LLM 的差异化

### 3. 开源策略符合趋势

LoV3D 代码已开源 (https://github.com/Anonymous-TEVC/LoV-3D)：

**对 CittaVerse 启示**:
- **开源策略验证**: 学术采纳 + 事实标准建立路径正确
- **PyPI 发布优先级**: 建议维持 05-31 目标

### 4. 竞品窗口持续开放

12 竞品仍聚焦内容生产，无叙事评估直接竞品：

**对 CittaVerse 启示**:
- **专利申请窗口**: 维持 04-30 目标
- **arXiv 提交窗口**: 维持 03-31 目标（Rememo CHI 2026 4 月 13-17 发表）

---

## Part IV: 时间敏感行动追踪

| 行动 | 截止 | 负责人 | 状态 | 本轮更新 |
|------|------|--------|------|---------|
| arXiv 提交 | 03-31 | V | 🔴 紧急 | 剩余 4 天 |
| 专利申请 | 04-30 | V | 🔴 紧急 | 权利要求草稿已完成 |
| Rememo CHI 2026 监测 | 04-13 | Hulk | 🟡 进行中 | 论文发表倒计时 17 天 |
| 情绪检测器修复 | 04-07 | Core | 🟡 进行中 | L0 校准发现 TC-01/TC-05 失败 |
| 50 条人工标注对标 | 04-07 | V/Core | 🟡 进行中 | 验证 r=0.87 基线 |
| ASR API Key 配置 | 04-07 | V | 🟡 进行中 | 语音生物标志物提取依赖 |
| v0.6 架构简化 | 04-14 | Core | 🟢 规划 | 消融实验支持 Minimal/LLM-only |

---

## 验证状态

| 任务 | 验证等级 | 状态 | 说明 |
|------|---------|------|------|
| 12 竞品状态检查 | V0 | ⚠️ 未验证 | 工具限制，沿用 03-26 结论 |
| arXiv 论文发现 | V1 | ✅ | arXiv API 直接获取 |
| Cerebra 多模态评估 | V1 | ✅ | 摘要确认 |
| LoV3D 脑 MRI 评估 | V1 | ✅ | 摘要确认 |
| 台大双模态 MCI | V1 | ✅ | 新闻摘要确认 |
| 全文深度分析 | V0 | ❌ | 全文获取受限 |
| 竞品官网监测 | V0 | ❌ | 工具限制 |

---

## 工具限制与建议

### 当前限制

1. **web_search (Gemini)**: API Key 问题持续 — 需 V 协助修复
2. **ddg-search**: 3-4 次查询后触发 anti-bot — 需控制频率
3. **web_fetch**: VPN fake-IP 阻断所有请求 — 需网络配置优化
4. **browser**: 超时不可用 — 需重启或配置调整

### 建议

1. **短期** (本周):
   - 修复 Gemini API Key 配置
   - 优化 ddg-search 查询频率（每次 cron 不超过 3 次）
   - 维持 arXiv API 直连作为主要数据源

2. **中期** (两周内):
   - 建立 arXiv RSS 订阅（cs.CL, cs.AI, cs.HC + reminiscence/narrative/dementia 关键词）
   - 配置竞品官网 RSS/Google Alerts

3. **长期** (一个月内):
   - 考虑付费数据源（Crunchbase API, CB Insights, 智慧芽专利库）

---

## 附录：本轮扫描使用的查询

```bash
# ddg-search (控制频率，避免 anti-bot)
ddg-search -f compact "reminiscence therapy AI dementia 2026"
ddg-search -f compact "MCI mild cognitive impairment AI assessment 2026"
ddg-search -f compact "narrative quality assessment LLM autobiographical memory"

# arXiv API
curl "https://export.arxiv.org/api/query?search_query=all:reminiscence+AND+all:therapy+AND+all:AI&sortBy=submittedDate&sortOrder=descending&max_results=10"
curl "https://export.arxiv.org/api/query?search_query=cat:cs.AI+AND+all:dementia+AND+all:assessment&sortBy=submittedDate&sortOrder=descending&max_results=10"
curl "https://export.arxiv.org/api/query?search_query=cat:cs.CL+AND+all:autobiographical+AND+all:memory&sortBy=submittedDate&sortOrder=descending&max_results=10"
curl "https://export.arxiv.org/api/query?search_query=cat:cs.HC+AND+all:elderly+AND+all:AI&sortBy=submittedDate&sortOrder=descending&max_results=10"
```

---

## 相关文档

### 证据更新系列

- `research/evidence/2026-03-27-freshness-verification-report.md` — 证据保鲜验证（03-27 早间）
- `research/evidence/2026-03-26-competitor-evidence-update.md` — 竞品证据更新（03-26）
- `research/evidence/2026-03-26-competitor-evidence-update-cron.md` — Cron 更新（03-26）
- `research/evidence/2026-03-24-competitor-evidence-update.md` — 基线版本（03-24）

### 竞品分析系列

- `research/competitors/05-technical-deep-dive.md` — 技术深度分析（03-27 更新）
- `research/competitors/README.md` — 竞品分析索引

### 其他相关

- `research/2026-03-27-technical-literature-review.md` — 技术文献综述（03-27）
- `research/2026-03-26-ablation-study-final-report.md` — 消融研究最终报告

---

*Hulk 🟢 — 密度即价值*  
*数据截至 2026-03-27 06:58 UTC*  
*本轮新增：Cerebra (2603.21597), LoV3D (2603.12071), 台大双模态 MCI 检测*  
*工具状态：web_search ❌ | ddg-search ⚠️ | arXiv API ✅*
