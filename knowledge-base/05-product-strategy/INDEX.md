# 05 — 产品策略 (Product Strategy)

> 版本历史、产品路线图、研究周报。连接研究结论与产品决策。

---

## Bottom Line

CittaVerse 处于 MVP 验证阶段（v0.2 → v0.3）。核心假设"AI 辅助叙事评分可提升回忆治疗效果"尚未被真实用户数据证实。当前最大阻塞：ASR API Key + 用户界面 + Pilot 用户招募，三者均需 V 推动。最快验证路径是"纯手动方案 C"（V 面对面引导 → 手动转写 → Scorer 评分）。

---

## 文件索引

| 文件 | 主题 | 验证等级 | 日期 |
|------|------|----------|------|
| `research/2026-03-15-cittaverse-product-release-history.md` | 产品线版本发布历史 (03-08 ~ 03-15) | V3 (静态复核) | 03-15 |
| `research/product-roadmap-mvp-to-v2.md` | MVP → v1.0 → v2.0 路线图 + 阻塞分析 | V1 (推导) | 03-22 |
| `research/weekly_report_2026-03-20.md` | 研究周报 W12 (03-14 ~ 03-20) | V1 | 03-20 |
| `research/weekly_report_2026-03-27.md` | **研究周报 W13 (03-20 ~ 03-27)**: GEO 26 轮 + 消融实验 + L0 校准 + 论文进展 | V1 | 03-27 |
| `research/paper/00-paper-prep-status.md` | 论文准备总状态 (03-31 更新): 阻塞项更新 (arXiv 提交超期) | V3 | 03-31 |
| `research/paper/V-action-items.md` | V 待办事项清单 (03-31 更新): arXiv 提交/伦理审批/人工标注 | V3 | 03-31 |
| `research/weekly_report_2026-04-03.md` | **研究周报 W14 (03-28 ~ 04-03)**: GEO 8 轮 (#74-99) + REMem 实现 + Multi-Agent v0.6 设计 + EXP-001 实验启动 | V1 | 04-03 |

## 核心知识点

### 产品阶段定义
| 阶段 | 目标 | 核心指标 | 时间 |
|------|------|----------|------|
| **MVP (v0.3)** | 1 个真实用户完成完整闭环 | 首个完整用户循环 | 2026 Q1-Q2 |
| **v1.0** | 50 个用户、可重复的付费路径 | MAU/NPS/首单转化 | 2026 Q3 |
| **v2.0** | B2B2C 规模化 | 合作机构数/ARR | 2027 |

### MVP 最小可行路径
```
方案 C (最快，纯手动):
V 面对面引导 → 录音 → 讯飞听见转写 → Scorer 评分 → V 反馈

优势: 零技术阻塞，1 周内可执行
风险: 不可规模化，但足以验证核心假设
```

### 当前阻塞项
1. 🔴 ASR API Key (>7 天未解决)
2. 🔴 用户界面 (未开始)
3. 🔴 Pilot 用户招募 (V 未执行)
4. 🟡 反馈报告可视化 (模板完成，渲染未实现)

### 研究周报 W13 核心摘要 (03-20~03-27)

**GEO 迭代**: 26 轮 (#48 → #73), 22+ commits, 286 个文件, ~60K 字

**核心产出**:
- v0.6.4: 情感词库 90 词 + Benchmark 18 样本 + 108/108 准确率
- v0.7.0: LLM Feature Extractor (500+ 行) + 集成测试 (待 API Key)
- 消融实验：12 配置对比，600 次评分，简化系统优于复杂系统
- L0 校准 v0.5.1-final：情绪检测器修复，131/131 鲁棒性
- 论文资产：v1.1 草稿 + 伦理审批包 + 培训/招募材料

**阻塞项**: arXiv 提交 (>264h), ASR API Key (>7 天)

### 论文准备状态 (03-31 更新)

**已完成产物**:
- ✅ 文献综述 (01-literature-review.md)
- ✅ 实验设计 (12-experiment-design-arxiv-final.md)
- ✅ 方法系列 (methods-*.md)
- ✅ 可视化 (18 个 SVG)
- ✅ 伦理审批包 (05-ethics-approval-package.md)
- ✅ 培训/招募材料
- ✅ 补充材料 (13-supplementary-materials.md)
- ✅ Cover Letter (cover-letter-final.md)

**阻塞项 (V 执行)**:
| 阻塞项 | 超期时长 | 影响 |
|--------|----------|------|
| LaTeX PDF 编译 | 4 天 | arXiv 提交前置条件 |
| arXiv 提交 | 3 天 | 论文无法公开，影响优先权 |
| 伦理审批审阅 | 4 天 | Pilot RCT 无法启动 |
| 机构盖章流程 | 2 天 | 伦理审批前置条件 |
| DASHSCOPE_API_KEY | >14 天 | LLM 增强功能无法实现 |
| ASR API Key | >7 天 | 真实 ASR 测试无法执行 |

---
*沉淀时间：2026-03-28 20:30 UTC (更新) | 04-02 06:00 UTC (论文状态更新)*
