# OpenClaw 技能按 5 个设计模式分类

**审查日期**: 2026-03-20  
**审查标准**: Google Cloud 5 Agent Skill Design Patterns  
**技能总数**: 120+ 核心技能（排除 vendor 批量生成）  
**作者**: Hulk 🟢

---

## 模式 1：Tool Wrapper（工具封装器）⭐⭐⭐

**定义**：让 Agent 快速成为某个库/框架/平台的专家，监听特定关键词，动态加载内部文档。

**核心特征**：
- 有明确的触发条件（关键词/场景）
- 封装特定工具/平台/API 的能力
- 有最佳实践文档或参考资料

### 1.1 高质量匹配（⭐⭐⭐⭐⭐）

| 技能 | 封装对象 | 触发条件 | 参考资料 | 匹配度 |
|------|---------|---------|---------|--------|
| **abao-photo-recall** | 多模态照片分析 | 用户发送照片 | 锚点类型定义 | ⭐⭐⭐⭐⭐ |
| **abao-anchor-matcher** | 集体记忆匹配 | birth_year + hometown + 年代线索 | references/年代文件 | ⭐⭐⭐⭐⭐ |
| **agent-reach** | Web/平台 Reach | 网络搜索/平台交互 | 优先级规则 | ⭐⭐⭐⭐ |

### 1.2 中等匹配（⭐⭐⭐）

| 技能 | 封装对象 | 触发条件 | 缺失 | 匹配度 |
|------|---------|---------|------|--------|
| **nano-banana-pro** | Gemini 图像生成 | 图像生成需求 | 无最佳实践文档 | ⭐⭐⭐ |
| **nano-pdf** | PDF 编辑 | PDF 操作需求 | 无场景说明 | ⭐⭐⭐ |
| **video-frames** | 视频帧提取 | 视频处理需求 | 无错误处理 | ⭐⭐⭐ |
| **tmux** | tmux 会话管理 | 远程 CLI 需求 | 无场景说明 | ⭐⭐⭐ |
| **discord** | Discord API | Discord 消息/频道操作 | 无最佳实践 | ⭐⭐⭐ |
| **slack** | Slack API | Slack 消息操作 | 无最佳实践 | ⭐⭐⭐ |
| **notion** | Notion API | Notion 页面/数据库操作 | 无场景说明 | ⭐⭐⭐ |

### 1.3 低质量匹配（⭐⭐）

| 技能 | 封装对象 | 问题 | 匹配度 |
|------|---------|------|--------|
| **google-search** | Google Search API | 仅有 API 调用，无场景说明 | ⭐⭐ |
| **ddg-search** | DuckDuckGo Search | 仅有 CLI 封装 | ⭐⭐ |
| **github** | GitHub CLI | 仅有命令列表 | ⭐⭐ |
| **gws-*** (20 个) | Google Workspace API | 批量生成，无场景说明 | ⭐⭐ |
| **canvas** | Canvas API | 仅有基础说明 | ⭐⭐ |
| **citta-engine** | Citta 引擎 | 描述模糊 | ⭐⭐ |

### 1.4 优化建议

| 行动 | 影响技能 | 工作量 |
|------|---------|--------|
| **补充最佳实践文档** | nano-banana-pro, nano-pdf, video-frames | 2h |
| **补充场景说明** | discord, slack, notion, github | 2h |
| **外置参考资料** | abao-anchor-matcher (年代文件) | 1h |

---

## 模式 2：Generator（生成器）⭐⭐⭐⭐

**定义**：生成结构一致的文档，有模板文件 + 风格指南，协调填充流程。

**核心特征**：
- 有 `assets/` 模板文件
- 有 `references/` 风格指南
- 有明确的生成流程（Step 1→2→3→4）

### 2.1 高质量匹配（⭐⭐⭐⭐⭐）

| 技能 | 生成内容 | 模板 | 风格指南 | 流程 | 匹配度 |
|------|---------|------|---------|------|--------|
| **abao-story-biographer** | 微传记故事 | ✅ (内嵌) | ✅ (写作风格) | ✅ (6 步) | ⭐⭐⭐⭐⭐ |
| **research-citta** | 科研情报周报 | ✅ (内嵌) | ✅ (输出规则) | ✅ (8 步) | ⭐⭐⭐⭐⭐ |

### 2.2 中等匹配（⭐⭐⭐）

| 技能 | 生成内容 | 模板 | 风格指南 | 流程 | 匹配度 |
|------|---------|------|---------|------|--------|
| **gstack-document-release** | 发布文档 | ⚠️ (内嵌) | ❌ | ⚠️ (不完整) | ⭐⭐⭐ |
| **gws-workflow-standup-report** | 站会报告 | ❌ | ❌ | ⚠️ (简单) | ⭐⭐⭐ |
| **gws-workflow-weekly-digest** | 周报 | ❌ | ❌ | ⚠️ (简单) | ⭐⭐⭐ |
| **gws-workflow-meeting-prep** | 会议准备 | ❌ | ❌ | ⚠️ (简单) | ⭐⭐⭐ |
| **gws-workflow-email-to-task** | 任务转换 | ❌ | ❌ | ⚠️ (简单) | ⭐⭐⭐ |
| **gws-workflow-file-announce** | 文件通知 | ❌ | ❌ | ⚠️ (简单) | ⭐⭐⭐ |
| **session-logs** | 会话日志 | ❌ | ❌ | ⚠️ (简单) | ⭐⭐⭐ |

### 2.3 低质量匹配（⭐⭐）

| 技能 | 生成内容 | 问题 | 匹配度 |
|------|---------|------|--------|
| **summarize** | 摘要 | 无模板/流程 | ⭐⭐ |
| **gws-docs-write** | 文档写入 | 仅有 API 调用 | ⭐⭐ |
| **gws-sheets-append** | 表格追加 | 仅有 API 调用 | ⭐⭐ |

### 2.4 优化建议

| 行动 | 影响技能 | 工作量 |
|------|---------|--------|
| **外置模板文件** | abao-story-biographer, research-citta | 2h |
| **补充风格指南** | gstack-document-release | 1h |
| **补充生成流程** | gws-workflow-* (6 个) | 2h |

---

## 模式 3：Reviewer（审查器）⭐⭐⭐⭐

**定义**：根据检查清单评分，按严重性分组发现问题，可复用同一套基础设施。

**核心特征**：
- 有 `references/review-checklist.md` 检查清单
- 按严重性分组（Critical/Major/Minor）
- 有评分标准

### 3.1 高质量匹配（⭐⭐⭐⭐⭐）

| 技能 | 审查对象 | 检查清单 | 严重性分组 | 评分标准 | 匹配度 |
|------|---------|---------|-----------|---------|--------|
| **abao-emotional-safety** | 情绪升级信号 | ✅ (5 条红线) | ✅ (立即/降级/红线) | ✅ | ⭐⭐⭐⭐⭐ |
| **gstack-review** | PR 代码审查 | ✅ (内嵌) | ✅ (SQL/LLM/条件) | ✅ | ⭐⭐⭐⭐⭐ |
| **gstack-qa** | Web 应用测试 | ✅ (内嵌) | ✅ (Quick/Standard/Exhaustive) | ✅ | ⭐⭐⭐⭐⭐ |
| **healthcheck** | 主机安全审计 | ✅ (内嵌) | ✅ (风险等级) | ✅ | ⭐⭐⭐⭐⭐ |

### 3.2 中等匹配（⭐⭐⭐）

| 技能 | 审查对象 | 检查清单 | 严重性分组 | 评分标准 | 匹配度 |
|------|---------|---------|-----------|---------|--------|
| **gstack-skill-vetter** | 技能审查 | ⚠️ (不完整) | ❌ | ⚠️ (简单) | ⭐⭐⭐ |
| **gstack-design-review** | 设计审查 | ⚠️ (不完整) | ❌ | ⚠️ (简单) | ⭐⭐⭐ |
| **cross-agent-audit** | 跨 Agent 消息审计 | ⚠️ (字段定义) | ❌ | ❌ | ⭐⭐⭐ |
| **gws-modelarmor** | 内容安全审查 | ⚠️ (API 调用) | ❌ | ❌ | ⭐⭐⭐ |

### 3.3 低质量匹配（⭐⭐）

| 技能 | 审查对象 | 问题 | 匹配度 |
|------|---------|------|--------|
| **gh-issues** | GitHub Issue 管理 | 无检查清单 | ⭐⭐ |
| **gws-modelarmor-sanitize-prompt** | Prompt 净化 | 仅有 API 调用 | ⭐⭐ |
| **gws-modelarmor-sanitize-response** | Response 净化 | 仅有 API 调用 | ⭐⭐ |

### 3.4 优化建议

| 行动 | 影响技能 | 工作量 |
|------|---------|--------|
| **外置检查清单** | abao-emotional-safety, gstack-review, gstack-qa | 2h |
| **补充严重性分组** | gstack-skill-vetter, gstack-design-review | 1h |
| **补充评分标准** | cross-agent-audit | 1h |

---

## 模式 4：Inversion（逆向访谈）⭐⭐⭐⭐⭐

**定义**：Agent 先采访用户，再行动。不直接执行任务，先问一组结构化问题，根据答案定制方案。

**核心特征**：
- 有采访问题模板（`assets/interview-questions.md`）
- 有采访流程（Step 1→2→3）
- 根据答案定制方案

### 4.1 高质量匹配（⭐⭐⭐⭐⭐）

| 技能 | 采访主题 | 问题模板 | 采访流程 | 定制方案 | 匹配度 |
|------|---------|---------|---------|---------|--------|
| **abao-profile-collector** | 用户画像收集 | ✅ (话术示例) | ✅ (字段优先级) | ✅ | ⭐⭐⭐⭐⭐ |
| **abao-recall-miner** | 回忆深挖 | ✅ (LREF 框架) | ✅ (4 维度) | ✅ (集体记忆匹配) | ⭐⭐⭐⭐⭐ |
| **gstack-plan-ceo-review** | 产品规划审查 | ✅ (4 模式) | ✅ (SCOPE 流程) | ✅ | ⭐⭐⭐⭐⭐ |

### 4.2 中等匹配（⭐⭐⭐）

| 技能 | 采访主题 | 问题模板 | 采访流程 | 定制方案 | 匹配度 |
|------|---------|---------|---------|---------|--------|
| **gstack-plan-design-review** | 设计审查 | ⚠️ (不完整) | ⚠️ (简单) | ⚠️ | ⭐⭐⭐ |
| **gstack-plan-eng-review** | 工程审查 | ⚠️ (不完整) | ⚠️ (简单) | ⚠️ | ⭐⭐⭐ |
| **gstack-design-consultation** | 设计咨询 | ⚠️ (不完整) | ⚠️ (简单) | ⚠️ | ⭐⭐⭐ |
| **best-later-years-topics** | 研究选题 | ⚠️ (不完整) | ⚠️ (简单) | ⚠️ | ⭐⭐⭐ |

### 4.3 低质量匹配（⭐⭐）

| 技能 | 采访主题 | 问题 | 匹配度 |
|------|---------|------|--------|
| **proactive-agent** | 主动触发 | 无采访流程 | ⭐⭐ |
| **self-improving-agent** | 学习记录 | 无采访流程 | ⭐⭐ |
| **skill-creator** | 技能创建 | 无采访流程 | ⭐⭐ |

### 4.4 优化建议

| 行动 | 影响技能 | 工作量 |
|------|---------|--------|
| **外置采访问题模板** | abao-profile-collector, abao-recall-miner | 2h |
| **补充采访流程** | gstack-plan-* (3 个) | 1h |

---

## 模式 5：Pipeline（流水线）⭐⭐⭐

**定义**：强制执行多步骤工作流，带检查点。定义严格顺序（Step 1→2→3→4），每步有检查点（不通过则停止）。

**核心特征**：
- 有明确的步骤定义（Step 1→2→3→4）
- 每步有检查点（验收标准）
- 有失败处理流程（停止/回滚/跳过）

### 5.1 高质量匹配（⭐⭐⭐⭐⭐）

| 技能 | 工作流 | 步骤定义 | 检查点 | 失败处理 | 匹配度 |
|------|-------|---------|-------|---------|--------|
| **abao-story-biographer** | 故事生成 | ✅ (素材→草稿→预览→保存) | ✅ (用户确认) | ✅ (修改循环) | ⭐⭐⭐⭐⭐ |
| **research-citta** | 科研情报 | ✅ (8 步流程) | ✅ (相关性评分) | ✅ (归档失败处理) | ⭐⭐⭐⭐⭐ |

### 5.2 中等匹配（⭐⭐⭐）

| 技能 | 工作流 | 步骤定义 | 检查点 | 失败处理 | 匹配度 |
|------|-------|---------|-------|---------|--------|
| **gstack-ship** | 发布流程 | ✅ (detect→merge→test→review→bump→commit→push→PR) | ❌ | ❌ | ⭐⭐⭐ |
| **gstack-qa** | QA 测试 | ✅ (Quick/Standard/Exhaustive) | ⚠️ (不完整) | ⚠️ (不完整) | ⭐⭐⭐ |
| **gstack-retro** | 回顾流程 | ⚠️ (不完整) | ❌ | ❌ | ⭐⭐⭐ |
| **notebooklm-workbench** | NotebookLM 工作流 | ⚠️ (不完整) | ❌ | ❌ | ⭐⭐⭐ |
| **gh-issues** | Issue 管理 | ⚠️ (不完整) | ❌ | ❌ | ⭐⭐⭐ |

### 5.3 低质量匹配（⭐⭐）

| 技能 | 工作流 | 问题 | 匹配度 |
|------|-------|------|--------|
| **automation-workflows** | 自动化工作流 | 无步骤定义 | ⭐⭐ |
| **gws-workflow** | Google 工作流 | 仅有 API 调用 | ⭐⭐ |
| **gws-workflow-* (6 个)** | 各种工作流 | 步骤不完整 | ⭐⭐ |
| **video-frames** | 视频处理 | 无检查点 | ⭐⭐ |
| **tmux** | tmux 会话 | 无检查点 | ⭐⭐ |

### 5.4 优化建议

| 行动 | 影响技能 | 工作量 |
|------|---------|--------|
| **补充检查点** | gstack-ship, gstack-qa, gstack-retro | 2h |
| **补充失败处理** | gstack-ship, notebooklm-workbench | 2h |
| **定义步骤流程** | automation-workflows, gws-workflow-* | 2h |

---

## 综合评估

### 5 个模式覆盖情况

| 模式 | 高质量 (⭐⭐⭐⭐⭐) | 中等 (⭐⭐⭐) | 低质量 (⭐⭐) | 总计 | 平均匹配度 |
|------|---------------|-----------|-----------|------|-----------|
| **Tool Wrapper** | 3 | 7 | 25+ | 35+ | ⭐⭐⭐ |
| **Generator** | 2 | 7 | 3 | 12 | ⭐⭐⭐⭐ |
| **Reviewer** | 4 | 4 | 3 | 11 | ⭐⭐⭐⭐ |
| **Inversion** | 3 | 4 | 3 | 10 | ⭐⭐⭐⭐⭐ |
| **Pipeline** | 2 | 5 | 10+ | 17+ | ⭐⭐⭐ |

### 关键洞察

1. **Inversion 模式最强** — abao 技能组 3 个高质量匹配，平均匹配度最高
2. **Generator/Reviewer 模式较强** — gstack 和 abao 都有高质量实现
3. **Pipeline 模式最弱** — 没有技能明确定义检查点和失败处理流程
4. **Tool Wrapper 模式最分散** — 数量最多但质量参差不齐

### 与 24h Agent Team 的关联

| 需求 | 匹配模式 | 现有技能 | 缺口 |
|------|---------|---------|------|
| **任务分发** | Pipeline | ❌ 无 | 需新增 orchestrator |
| **L0 评分分析** | Reviewer + Inversion | abao-recall-miner | 需新增 l0-analyzer |
| **预警处理** | Pipeline + Reviewer | abao-emotional-safety | 需新增 alert-handler |
| **报告生成** | Generator | abao-story-biographer, research-citta | ✅ 可复用 |
| **家属沟通** | Inversion | abao-profile-collector | 需新增 family-communicator |

---

## 优化优先级

### P0（立即行动，Day 1-2）

| 行动 | 影响模式 | 影响技能 | 工作量 |
|------|---------|---------|--------|
| **补充 Pipeline 检查点** | Pipeline | gstack-ship, gstack-qa, gstack-retro | 2h |
| **补充 Pipeline 失败处理** | Pipeline | gstack-ship, notebooklm-workbench | 2h |
| **外置 Tool Wrapper 参考资料** | Tool Wrapper | abao-anchor-matcher, nano-banana-pro | 2h |

### P1（中期行动，Day 3-5）

| 行动 | 影响模式 | 影响技能 | 工作量 |
|------|---------|---------|--------|
| **外置 Generator 模板** | Generator | abao-story-biographer, research-citta | 2h |
| **外置 Reviewer 检查清单** | Reviewer | abao-emotional-safety, gstack-review, gstack-qa | 2h |
| **外置 Inversion 采访模板** | Inversion | abao-profile-collector, abao-recall-miner | 2h |

### P2（长期行动，Week 2+）

| 行动 | 影响范围 | 工作量 |
|------|---------|--------|
| **新增 orchestrator 技能** | Pipeline | 4h |
| **新增 l0-analyzer 技能** | Reviewer + Inversion | 4h |
| **新增 alert-handler 技能** | Pipeline + Reviewer | 3h |
| **建立技能模板库** | 所有模式 | 8h |

---

## 总结

### 现状评分

| 模式 | 得分 | 说明 |
|------|------|------|
| **Tool Wrapper** | 65/100 | ⭐⭐⭐ 数量多但质量参差不齐 |
| **Generator** | 75/100 | ⭐⭐⭐⭐ abao-story-biographer 和 research-citta 是标杆 |
| **Reviewer** | 78/100 | ⭐⭐⭐⭐ abao-emotional-safety 和 gstack-review 是标杆 |
| **Inversion** | 85/100 | ⭐⭐⭐⭐⭐ abao 技能组是标杆 |
| **Pipeline** | 55/100 | ⭐⭐⭐ 最弱，缺检查点和失败处理 |

**综合得分**: 71/100（比初版 69 分提升 2 分）

---

*Hulk 🟢 — 2026-03-20*  
*审查范围：120+ 核心技能*  
*审查标准：Google Cloud 5 Agent Skill Design Patterns*  
*综合得分：71/100*
