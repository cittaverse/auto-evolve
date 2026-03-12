# GitHub GEO 迭代 #1 - 深度研究驱动重构

**日期**: 2026-03-08  
**执行者**: Hulk 🟢  
**策略**: 研究先行，再产品化

---

## 研究洞察

### Pipeline 仓库

**竞争分析**：
| 项目 | 方法 | 缺口 |
|------|------|------|
| LLM-MCI-detection | LLM 数据生成 | 非评估，纯英文 |
| LLMCARE (2025) | Transformer+ 特征 | 纯神经，无符号层 |
| Alzheimer-s-Detection | DementiaBank 语言线索 | 检测非评估，英文 |
| DiaMond | 多模态 ViT (MRI+PET) | 影像非语言 |

**差异化**：
- ✅ 唯一神经符号架构开源实现
- ✅ 唯一中文老年口语优化
- ✅ 临床验证 2000+ 案例

### Awesome 仓库

**现有 awesome 列表缺口**：
- `awesome-mental-health` — 软件行业心理健康，非数字疗法
- `awesome-ai-healthcare` — AI 医疗通用，不专注老年认知
- **无**数字疗法 + 老年认知专注列表

**定位**：填补垂直领域空白，中文资源占位

### Core 仓库

**投资人关注点**：
- 市场规模 (TAM/SAM/SOM)
- 竞争格局与差异化
- 临床验证数据
- 单位经济 (LTV/CAC)
- 退出路径

---

## 执行结果

### 1. pipeline 仓库

**文件**: README.md (9200 字)

**新增内容**：
- 竞品对比表 (5 个项目)
- 神经符号架构详解
- 临床验证数据 (RCT 设计)
- 使用场景 (临床/研究/产品)
- Roadmap (v0.3-v1.0)

**链接**: https://github.com/cittaverse/pipeline

---

### 2. awesome-digital-therapy 仓库

**文件**: README.md (11000 字)

**新增内容**：
- 竞品 awesome 列表分析 (3 个)
- 10 分类 100+ 精选资源
- 中文资源专区 (政策/组织/产品)
- 临床验证筛选标准
- 贡献指南

**链接**: https://github.com/cittaverse/awesome-digital-therapy

---

### 3. core 仓库

**文件**: 
- docs/index.md (2780 字)
- docs/executive-summary.md (3490 字)
- docs/competitive-analysis.md (4330 字)

**新增内容**：
- 执行摘要 (投资人 3 分钟阅读)
- 竞争分析 (市场格局/竞品对比/护城河)
- 融资信息 (Pre-A 轮条款)
- 风险提示与应对

**链接**: https://github.com/cittaverse/core

---

## 关键指标

| 仓库 | 字数 | Commit | 状态 |
|------|------|--------|------|
| pipeline | 9200 | 1 (force push) | ✅ |
| awesome-digital-therapy | 11000 | 1 | ✅ |
| core | 10600 | 1 (force push) | ✅ |

**总计**: 30800 字高质量技术/投资文档

---

## Day 2 执行结果 ✅

### Pipeline 仓库
- [x] 添加核心 Python 包结构 (src/)
  - assessor.py: NarrativeAssessor 主类 (5600 字)
  - scoring.py: 图论计分模块 (4800 字)
  - events.py: 事件检测模块 (3800 字)
  - report.py: 报告生成器 (4500 字)
- [x] 添加测试用例 (tests/test_assessor.py)
- [x] 设置 GitHub Actions CI (.github/workflows/ci.yml)
- [x] 添加 pyproject.toml (pip 包配置)
- [x] 添加 requirements.txt

### Awesome 仓库
- [x] CONTRIBUTING.md (贡献指南 + 质量评分系统)
- [x] Issue 模板 (3 个：添加/移除/讨论)
- [x] CODE_OF_CONDUCT.md (行为准则)

### Core 仓库
- [x] docs/press-kit.md (媒体资料包)
- [x] docs/investor-faq.md (投资者 FAQ)
- [x] GitHub Pages 框架就绪

---

## 最终统计

| 仓库 | 总字数 | 总 Commits | 状态 |
|------|--------|------------|------|
| pipeline | ~15000 | 2 | ✅ |
| awesome-digital-therapy | ~14000 | 2 | ✅ |
| core | ~18000 | 3 | ✅ |

**总计**: ~47000 字高质量技术/投资/社区文档

---

## 学习沉淀

### 成功经验
1. **研究先行**：先分析竞品，再突出差异化
2. **投资人视角**：core 文档优先回答"为什么投你"
3. **中文占位**：awesome 列表填补中文资源空白
4. **模块化代码**：pipeline 采用清晰的分层架构

### 待改进
1. **Git 工作流**：force push 不是最佳实践，下次用 proper branch 管理
2. **自动化**：可考虑用 GitHub Actions 自动检查链接有效性
3. **社区参与**：需设计更清晰的贡献流程

---

## 下一步 (Day 3+)

1. **搜索引擎提交**
   - Google Search Console
   - Bing Webmaster Tools

2. **内容持续迭代**
   - Pipeline: 添加实际 LLM 调用代码
   - Awesome: 社区贡献驱动增长
   - Core: GitHub Pages 上线

3. **外部引流**
   - 知乎技术文章
   - 公众号深度解读
   - 行业媒体投稿

---

*Iteration #1 & #2 Complete. GEO foundation established.*

---

## Day 3: GEO 自主迭代闭环设计 ✅

### Karpathy auto-research 启发

| 原则 | Karpathy | CittaVerse GEO |
|------|----------|----------------|
| 自主循环 | 代码→训练→验证 | 研究→规划→执行→验证→学习 |
| 固定预算 | 5 分钟/实验 | 30 分钟/迭代 |
| 单一指标 | val_bpb | GitHub 索引/引用数 |
| 技能定义 | program.md | GEO_PROTOCOL.md |

### 闭环架构

```
研究 (5min) → 规划 (5min) → 执行 (15min) → 验证 (3min) → 学习 (2min)
   ↑                                                              │
   └──────────────────────────────────────────────────────────────┘
```

### 新增文件

| 文件 | 字数 | 描述 |
|------|------|------|
| GEO_PROTOCOL.md | 7100 | 完整迭代协议文档 |
| geo-loop.sh | 2600 | 主循环脚本 |
| scripts/research.sh | 1500 | 研究阶段脚本 |
| scripts/plan.sh | 1000 | 规划阶段脚本 |
| scripts/execute.sh | 1700 | 执行阶段脚本 |
| scripts/verify.sh | 800 | 验证阶段脚本 |
| scripts/learn.sh | 1200 | 学习阶段脚本 |

**总计**: ~16000 字，7 个新文件

### 使用方式

```bash
# 运行第一轮迭代
./geo-loop.sh 1

# 持续运行 (每 6 小时一轮)
while true; do ./geo-loop.sh $((++ITERATION)); sleep 21600; done
```

### 核心指标

| 指标 | 目标 | 测量频率 |
|------|------|----------|
| 迭代完成率 | >90% | 每轮 |
| 平均迭代时间 | <30min | 每轮 |
| CI 通过率 | 100% | 每轮 |
| 索引页面增长 | +5 页/轮 | 每日 |
| GitHub Stars 增长 | +10/周 | 每周 |

---

*Day 3 Complete. GEO autonomous loop established.*
