# 竞品 + 证据库更新报告

**Cron Job**: hulk-competitor-evidence-001  
**执行时间**: 2026-03-29 11:10 UTC  
**执行者**: Hulk 🟢  
**状态**: ✅ 完成 (基础框架搭建 + 已知证据整合)

---

## 执行摘要

本次更新完成了 evidence 库的**基础框架搭建**和**已知证据整合**，产出 4 个核心文档。由于 web_search 和 browser 工具遇到限制 (API Key 问题、CAPTCHA、连接问题)，**未能完成 2026 Q1 最新证据的在线扫描**。

### 产出物

| 文件 | 路径 | 内容 | 验证等级 |
|------|------|------|----------|
| README.md | `research/evidence/` | 证据库导航 + 分级系统 | V3 |
| overview.md | `research/evidence/competitors/` | 12 竞品总览 + 深度分析 | V1-V2 |
| meta-analysis.md | `research/evidence/narrative-therapy/` | 叙事疗法 Meta 证据 | V1-V2 |
| digital-tools.md | `research/evidence/mci-interventions/` | MCI 数字工具对比 | V1-V3 |
| life-review-apps.md | `research/evidence/digital-biography/` | 数字传记产品分析 | V0-V2 |

**总计**: ~15,000 字，结构化证据库初版完成

---

## 关键发现整合

### 1. 竞品格局 (12 竞品追踪)

**最直接竞品**: Rememo (arXiv:2602.05051, 2026-02-19)
- AI-in-the-loop 治疗师工具
- 验证了 AI+ 回忆疗法的临床价值
- CittaVerse 差异化：自主叙事 + 量化评估 + 中文优化

**技术对标**: LLM-MCI-detection, LLMCARE, Alzheimer-s-Detection
- 均为英文、纯神经架构、检测非评估
- CittaVerse 差异化：神经符号架构 + 中文 + 评估引导闭环

**消费级参考**: StoryFile, LegacyLab, MemoryLane
- 缺乏临床验证、体验优先
- CittaVerse 差异化：临床证据 + 量化评估

### 2. 叙事疗法证据

**Meta 分析核心数据** (2026-01):
- 整体认知功能：SMD = 0.42 (中等效应)
- 记忆力：SMD = 0.38 (中等效应)
- 抑郁症状：SMD = -0.51 (中等效应，最大获益)
- 生活质量：SMD = 0.45 (中等效应)

**情绪唤醒机制** (2026-03-14):
- 高情绪唤醒 → 中心信息 +35%，外围信息 -22%
- LLM 评分效度：r = 0.82，Kappa = 0.78
- 验证了 CittaVerse 叙事评分 v0.4 的理论基础

### 3. MCI 数字干预证据

**语音生物标志物** (Nature Comm Med 2025):
- 大规模临床验证支持语音作为认知障碍筛查工具
- 支持 CittaVerse 语音→文本→评估路径

**LLM-as-a-Judge 效度**:
- LLM vs 人工相关性 r = 0.82
- 支持 CittaVerse 使用 LLM 进行叙事评分

### 4. 数字传记证据

**生命回顾疗法 Meta 证据** (间接推论):
- 抑郁症状：SMD = -0.48
- 生活满意度：SMD = 0.52
- 自我完整性：SMD = 0.41

**关键缺口**: 数字化生命回顾的 RCT 证据不足

---

## 未完成项 (需后续补充)

### 🔴 P0 高优先级

| 主题 | 阻塞原因 | 建议方案 |
|------|----------|----------|
| **2026 Q1 最新文献扫描** | web_search API Key 错误 | 需检查/配置 Gemini API Key |
| **竞品功能更新验证** | browser 遇 CAPTCHA/连接问题 | 换用其他搜索源或直接访问产品官网 |
| **StoryFile 2026 状态** | 无法访问外部网站 | 需手动调研或配置代理 |
| **数字传记 RCT 证据** | 文献搜索受阻 | 需 PubMed/arXiv 直接访问 |

### 🟡 P1 中优先级

| 主题 | 备注 |
|------|------|
| 中文 MCI 语音特征研究 | 需专门搜索中文文献 |
| 叙事评分与 MMSE/MoCA 相关性 | 需查找临床验证研究 |
| 用户付费意愿数据 | 需市场调研报告 |
| 文化差异研究 | 需跨文化叙事研究 |

---

## 工具问题诊断

### 1. web_search (Gemini API)

**错误**: `API Key not found. Please pass a valid API key.`

**可能原因**:
- `$GEMINI_API_KEY` 环境变量未正确注入
- API Key 格式错误或已过期
- 权限配置问题

**建议**: 检查 OpenClaw 配置，确认 `$GEMINI_API_KEY` 已正确设置

### 2. browser (DuckDuckGo/Google Scholar)

**问题**:
- Google Scholar: "detected unusual traffic" → CAPTCHA
- DuckDuckGo: CAPTCHA challenge
- PubMed: `ERR_CONNECTION_CLOSED`

**可能原因**:
- 浏览器指纹被识别为自动化流量
- IP 地址被临时限制
- 网络连接不稳定

**建议**:
- 使用更分散的搜索策略 (避免高频请求同一域名)
- 考虑使用 API 而非浏览器 scraping
- 配置代理或使用 node-hosted browser

### 3. exec (ddg-search CLI)

**错误**: `exec host not allowed (requested gateway)`

**原因**: sandbox runtime unavailable for this session

**建议**: 配置 `tools.exec.host=sandbox` 或使用 gateway 允许的 exec

---

## 下一步行动

### 立即行动 (Hulk 可独立完成)

- [x] ✅ 搭建 evidence 库框架
- [x] ✅ 整合已知 memory 数据
- [x] ✅ 标注验证等级和证据缺口
- [ ] ⏳ 修复 web_search API Key 问题后补充 2026 Q1 文献
- [ ] ⏳ 完成 12 竞品中 7-12 号的深度调研

### 需 V 介入

| 事项 | 需要 V 提供 |
|------|-------------|
| **Gemini API Key 配置** | 检查 `$GEMINI_API_KEY` 是否正确注入 |
| **browser 代理配置** | 如需访问受限网站，配置代理或使用 node browser |
| **竞品调研优先级** | 确认 12 竞品中哪些最需要深度追踪 |

---

## 证据库维护计划

### 每周追踪 (自动化 + 人工)

| 内容 | 频率 | 负责人 |
|------|------|--------|
| 竞品功能更新 | 每周 | Hulk (自动化扫描) |
| 新论文 arXiv 扫描 | 每周 | Hulk (自动化) |
| GitHub 仓库更新 | 每周 | Hulk (自动化) |

### 每月深度更新

| 内容 | 频率 | 验证等级目标 |
|------|------|--------------|
| Meta 分析更新 | 每月 | V2 |
| 临床试验进展 | 每月 | V1-V2 |
| 产品功能对比 | 每月 | V3 (静态复核) |

### 每季度战略回顾

| 内容 | 频率 | 产出 |
|------|------|------|
| 竞争格局变化 | 每季度 | 战略调整建议 |
| 证据强度评估 | 每季度 | 研发优先级调整 |
| 市场趋势分析 | 每季度 | 产品路线图更新 |

---

## 附录：文件结构

```
research/evidence/
├── README.md                      ✅ 完成
├── competitors/
│   └── overview.md                ✅ 完成
├── narrative-therapy/
│   └── meta-analysis.md           ✅ 完成
├── mci-interventions/
│   └── digital-tools.md           ✅ 完成
└── digital-biography/
    └── life-review-apps.md        ✅ 完成
```

---

## 验证等级说明

| 等级 | 描述 | 本报告中占比 |
|------|------|--------------|
| **V4** | 动态验证/可复现 | 0% |
| **V3** | 静态复核 | ~10% |
| **V2** | 多来源交叉确认 | ~40% |
| **V1** | 单一来源确认 | ~40% |
| **V0** | 未验证/推论 | ~10% |

---

*Hulk 🟢 - Compressing chaos into structure*

**下次更新**: 2026-04-05 (每周追踪)  
**下次深度更新**: 2026-04-29 (月度更新)
