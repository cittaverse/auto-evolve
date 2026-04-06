# V 待办事项清单 — CittaVerse 论文与 Pilot RCT 准备

**创建**: 2026-03-27 00:45 UTC  
**更新**: 2026-04-05 00:45 UTC (Run #22)  
**状态**: ⚠️ 已逾期，建议 48 小时内完成

---

## 📍 当前状态摘要 (2026-04-05 00:45 UTC)

| 任务 | 状态 | 下一步 |
|------|------|--------|
| **arXiv Methods 终稿 v5.0** | ✅ **已完成 (Run #14)** | 可直接用于论文 Section 3 |
| **实验设计 v6.0** | ✅ **已完成 (Run #21)** | 最新版参考 (整合 EXP-001 + 抗堆砌机制) |
| **arXiv 提交包** | ✅ 已就绪 | V 上传至 arXiv |
| **伦理审批包** | ✅ 已就绪 | V 填写 4 个占位符后提交 |
| **时间线** | ⚠️ **arXiv 提交已逾期 5 天，伦理审批已逾期 4 天** | **建议 48 小时内完成** |

---

## Run #14 最新进展 (2026-03-30 17:45 UTC)

✅ **arXiv Methods 终稿 v5.0 已生成**: `research/paper/12-experiment-design-arxiv-final.md` (34KB)
- **关键升级**: 整合 CONSORT 2010 + SPIRIT 2013 指南，每节标注对应章节
- **结构优化**: 按论文章节组织 (3.1-3.5)，arXiv Section 3 直接素材
- **伦理信息**: 集中 4 个占位符 (PI 姓名、职称、GCP 证书、联系方式)
- **核心内容保持**: 四层变量控制矩阵、对比组设计、评估指标操作化、五层验证体系
- **用途**: arXiv 论文 Section 3 直接素材 + 伦理审批 + 预注册 + 实验执行参考
- **推荐**: 优先使用此版本作为论文 Methods 章节基础

---

## Run #13 最新进展 (2026-03-29 17:47 UTC)

✅ **实验设计精炼版 v4.0 已生成**: `research/paper/11-experiment-design-refined.md` (19KB)
- 整合 v1.0-v3.0 设计，聚焦三大核心要素
- **变量控制**: 四层矩阵 (受试者→干预→评估→数据)，系统化管理 40+ 混淆变量
- **对比组**: 主动对照 + 嵌套 A/B + 5 种算法基线，隔离核心机制
- **评估指标**: 4 层指标 + Checklist 范式，所有指标可测量、可复现
- **用途**: 伦理审批 + 预注册 + 实验执行现场参考 + 论文 Methods 章节素材
- **推荐**: 伦理审批优先审阅此版本 (30 分钟)

---

## Run #11-12 最新进展 (2026-03-29)

✅ **Section 5 (Experimental Design) 已整合完成**: `research/arxiv-paper/paper.tex`
- 从 ~20 行扩展至 ~200 行
- 新增 5.1 Five-Layer Validation Framework (五层验证体系)
- 新增 5.2 Variable Control Matrix (四层变量控制)
- 新增 5.3 Comparison Groups (主动对照 + 嵌套 A/B + 算法基线)
- 新增 5.4 Operationalized Metrics (操作化指标表格)
- 新增 5.5 Statistical Analysis Plan (LMM/HLM + 样本量计算)
- 新增 5.6 Quality Control & Fidelity (保真度 + 评估者培训)
- **状态**: 等待 V 本地编译 LaTeX 生成 PDF

✅ **arXiv 提交包 v1.1 已就绪**: `research/arxiv-paper/arxiv-submission-v1.1.tar.gz` (23KB)
- 包含完整 LaTeX 源码 + 参考文献 + Cover Letter
- **状态**: 等待 V 上传至 arXiv (账号 cittaverse@gmail.com)

✅ **伦理审批包 v1.0 已就绪**: `research/paper/05-ethics-approval-package.md`
- 包含研究方案、知情同意书、风险评估、数据管理计划
- **待填写**: 4 个占位符 (PI 姓名、机构名称、联系方式、伦理委员会名称)
- **状态**: 等待 V 填写后提交

⏰ **时间线提醒** (当前：2026-04-05 00:45 UTC):
| 截止日期 | 任务 | 逾期时间 | 状态 |
|----------|------|----------|------|
| 2026-03-31 | arXiv 提交 | **+5 天** | 🔴 **已逾期** |
| 2026-04-01 | 伦理审批提交 | **+4 天** | 🔴 **已逾期** |
| 2026-04-12 | EXP-001 分析报告 | ~7 天 | 🟡 依赖 Core 协调 |

---

## Run #9 新增 (2026-03-28 12:21 UTC)

✅ **产物清单索引已生成**: `INDEX.md`
- 22 个 Markdown 文档完整清单
- 18 个可视化文件 (11 SVG + 7 PNG)
- 文件路径速查 + 提交前检查清单
- **推荐阅读**: 打开 `INDEX.md` 快速定位所有文件

⚠️ **占位符定位**: 伦理审批包中 4 个 `[待填写]`
- PI 姓名、职称、GCP 证书编号、联系方式
- 位置：`05-ethics-approval-package.md` (grep 可定位)

---

## Run #8 最新进展 (2026-03-28)

✅ **arXiv 提交包 v1.1 已准备**: `research/arxiv-paper/arxiv-submission-v1.1.tar.gz` (23KB)
- 包含：`paper.tex` (v1.1, 555 行), `references.bib` (668 行), `cover-letter.md`, `arxiv-submission-checklist.md`
- 所有新引用已验证存在 (11 条：checkeval2024, healthcare_llm_judge2025, llm_event_seg2025 等)

⚠️ **LaTeX 编译**: 容器环境无 TeX 权限，需 V 本地执行
- 在 macOS/本地 Linux 运行：`cd research/arxiv-paper && pdflatex paper.tex` (3 次)
- 或使用 Overleaf 等在线编辑器

---

## 高优先级 (本周内完成)

### 任务 0: 审阅实验设计 v6.0 (最新版)
- **优先级**: 🔴 高
- **预计耗时**: 45 分钟
- **原截止日期**: 2026-04-05 — ⚠️ 今日截止
- **建议完成**: 2026-04-06 (周一) 内
- **状态**: ✅ 新文档已生成，推荐优先审阅此版本
- **文件**: `research/paper/14-experiment-design-v6-updated.md` (v6.0, 25KB)
- **背景**: 整合 EXP-001 多 Agent 验证 + 抗堆砌机制，最新版设计
- **核心内容**:
  - 五层验证体系 (L1a Mock → L1b Benchmark → L1c 事件检测 → L2 Pilot RCT → L3 A/B 测试)
  - 四层变量控制矩阵 (受试者→干预→评估→数据)
  - 对比组设计 (主动对照 + 嵌套 A/B + 5 种算法基线)
  - 评估指标操作化 (4 层指标 + Checklist 范式)
  - **新增**: EXP-001 多 Agent 验证框架 (L0/L1/L2 融合评分)
  - **新增**: 抗堆砌机制 (Reward Hacking Detection: C1/C2/C4 检测规则)
  - **新增**: 验证强度控制器 (动态调整 L1 触发率至 20% ± 5%)
- **待确认**:
  - [ ] 变量控制策略是否充分
  - [ ] 对比组设计是否合理 (主动对照 vs 等待对照)
  - [ ] 评估指标是否可操作 (特别是六维评分的临床截断值)
  - [ ] 样本量计算是否合理 (N=80 是否足够)
  - [ ] EXP-001 验证框架是否清晰
  - [ ] 抗堆砌机制是否能有效识别关键词堆砌
- **操作**:
  1. 阅读 `14-experiment-design-v6-updated.md` (推荐优先，最新版)
  2. 如需更多背景，参考 `12-experiment-design-arxiv-final.md` (v5.0, CONSORT/SPIRIT 对齐)
  3. 确认后可用于伦理审批 + 预注册
- **背景**: 整合 v1.0-v3.0 设计，聚焦三大核心要素 (变量控制/对比组/评估指标)，形成可立即执行的精炼版本
- **核心内容**:
  - 变量控制矩阵 (四层：受试者→干预→评估→数据，含 40+ 混淆变量)
  - 对比组设计 (主动对照 + 嵌套 A/B + 5 种算法基线)
  - 评估指标操作化 (4 层指标 + Checklist 范式，含截断值/时点)
  - 五层验证体系 (L1a Mock → L1b Benchmark → L1c 事件检测 → L2 Pilot RCT → L3 A/B 测试)
- **待确认**:
  - [ ] 变量控制策略是否充分
  - [ ] 对比组设计是否合理 (主动对照 vs 等待对照)
  - [ ] 评估指标是否可操作 (特别是六维评分的临床截断值)
  - [ ] 样本量计算是否合理 (N=80 是否足够)
- **操作**:
  1. 阅读 `11-experiment-design-refined.md` (推荐优先，精炼版)
  2. 如需更多背景，参考 `09-experiment-design-comprehensive.md`
  3. 确认后可用于伦理审批 + 预注册

---

### 任务 1: 审阅伦理审批材料包
- **优先级**: 🔴 高
- **预计耗时**: 60 分钟
- **原截止日期**: 2026-03-29 (周日) — ⚠️ 已逾期
- **建议完成**: 2026-04-01 (周三) 前
- **文件**: `research/paper/05-ethics-approval-package.md`
- **待填写字段**:
  - [ ] PI 姓名
  - [ ] 机构名称
  - [ ] 联系方式 (电话/邮箱)
  - [ ] 研究场所 (医院/社区中心名称)
  - [ ] 伦理委员会名称
- **操作**:
  1. 阅读全文，确认内容准确
  2. 填写所有 `[待填写]` 占位符
  3. 标记需要修改的部分
  4. 确认后可提交

---

### 任务 2: 联系 PI 确认 + 机构盖章
- **优先级**: 🔴 高
- **预计耗时**: 30 分钟
- **截止日期**: 2026-03-31 (周二)
- **依赖**: 任务 1 完成
- **操作**:
  1. 联系 PI (如非本人) 审阅方案
  2. 确认机构盖章流程
  3. 准备盖章所需材料 (通常包括: 研究方案、知情同意书、研究者资质)
  4. 提交盖章申请

---

### 任务 3: 提交伦理委员会
- **优先级**: 🔴 高
- **预计耗时**: 15 分钟 (在线提交)
- **截止日期**: 2026-04-01 (周三)
- **依赖**: 任务 2 完成
- **操作**:
  1. 登录机构伦理委员会在线系统
  2. 上传材料:
     - 研究方案摘要
     - 知情同意书
     - 招募材料
     - 研究者资质
     - 机构盖章文件
  3. 填写申请表
  4. 提交并记录申请号
- **预计审批周期**: 2-4 周

---

### 任务 4: 本地编译 LaTeX PDF (v1.1)
- **优先级**: 🔴 高
- **预计耗时**: 30 分钟
- **截止日期**: 2026-03-30 (周一)
- **文件**: `research/arxiv-paper/paper.tex` (v1.1, 555 行) + `references.bib` (668 行)
- **说明**: 容器环境无 TeX 权限，需 V 本地执行
- **操作**:
  ```bash
  cd /home/node/.openclaw/workspace-hulk/research/arxiv-paper/
  pdflatex paper.tex
  bibtex paper
  pdflatex paper.tex
  pdflatex paper.tex
  ```
- **输出**: `paper.pdf` (约 150-200KB)
- **检查**:
  - [ ] PDF 无编译错误
  - [ ] 参考文献完整显示
  - [ ] 图表位置正确
  - [ ] 页码连续
- **备选**: 使用 Overleaf 上传 `paper.tex` + `references.bib` 在线编译

---

### 任务 5: arXiv 提交 (v1.1 PDF)
- **优先级**: 🔴 高
- **预计耗时**: 20 分钟
- **截止日期**: 2026-03-30 (周一)
- **依赖**: 任务 4 完成
- **账号**: cittaverse@gmail.com (已注册 arXiv)
- **提交包**: `research/arxiv-paper/arxiv-submission-v1.1.tar.gz` (已准备，23KB)
- **操作**:
  1. 登录 https://arxiv.org/user/login
  2. 点击 "Start new submission"
  3. 填写元数据:
     - **标题**: CittaVerse Narrative Scorer v0.6: Six-Dimension Assessment for Chinese Autobiographical Memory Quality with Event Boundary Detection
     - **作者**: [填写所有作者]
     - **摘要**: [使用 paper.tex 中的 abstract，含事件边界检测 v2 描述]
     - **分类**: cs.HC (primary), cs.CL (cross-list, 需 endorsement)
  4. 上传文件:
     - 解压 `arxiv-submission-v1.1.tar.gz` 后上传 `paper.pdf`
     - 或直接在 arXiv 系统上传源文件
  5. 确认并提交
- **注意**:
  - cs.CL 分类需要 endorsement (如首次提交该分类)
  - 建议先提交 cs.HC，cs.CL 可后续添加
  - arXiv 允许后续版本更新 (v1 → v2 → ...)
  - v1.1 新增内容：事件边界检测 v2 算法、CheckEval/事件分割/Rememo/Dolphin 等新文献整合

---

## 中优先级 (下周内完成)

### 任务 6: 确认 LaTeX v1.1 同步方案
- **优先级**: 🟡 中
- **预计耗时**: 10 分钟 (决策)
- **截止日期**: 2026-04-07
- **背景**: `paper-draft-v1.1.md` 已包含事件边界检测 v2 内容，但 `paper.tex` 仍为 v1.0
- **方案选择**:
  - **方案 A**: 从 Markdown 重新生成 LaTeX (工作量大，需手动调整格式)
  - **方案 B**: 增量更新 paper.tex 关键章节 (中等工作量，保留现有格式)
  - **方案 C**: 先提交 v1.0，v1.1 作为修订版本后续提交 (推荐，时间效率最高)
- **推荐**: 方案 C — arXiv 支持版本迭代，可先确保 v1.0 可引用

---

### 任务 7: 配置 DASHSCOPE_API_KEY
- **优先级**: 🟡 中
- **预计耗时**: 10 分钟
- **截止日期**: 2026-04-07
- **用途**: v0.7 LLM 混合验证 (Qwen API)
- **操作**:
  1. 登录阿里云百炼平台: https://bailian.console.aliyun.com/
  2. 创建/选择应用
  3. 获取 API Key
  4. 注入环境变量:
     ```bash
     export DASHSCOPE_API_KEY="sk-xxx"
     ```
  5. 验证:
     ```bash
     curl -X POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation \
       -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{"model":"qwen-plus","input":{"messages":[{"role":"user","content":"Hello"}]}}'
     ```
- **影响**: 不配置则无法执行 LLM 混合验证实验

---

### 任务 8: 招募海报设计确认
- **优先级**: 🟡 中
- **预计耗时**: 20 分钟
- **截止日期**: 2026-04-10
- **依赖**: 伦理批准 (任务 3)
- **文件**: `research/paper/recruitment-materials.md` (已有文案)
- **操作**:
  1. 审阅海报文案
  2. 确认设计风格 (简洁/温馨/专业)
  3. 委托设计师或使用 Canva 等工具制作
  4. 打印 A4 彩页 (建议 50-100 份)

---

### 任务 9: 研究助理招聘/确认
- **优先级**: 🟡 中
- **预计耗时**: 60 分钟
- **截止日期**: 2026-04-15
- **依赖**: 伦理批准 (任务 3)
- **职责**:
  - 受试者招募与筛查
  - 基线评估执行
  - 数据录入与质控
  - 随访提醒
- **要求**:
  - 心理学/护理学/社会工作专业本科及以上
  - 有临床研究经验者优先
  - 每周可投入 10-15 小时
- **操作**:
  1. 发布招聘信息 (机构官网/高校就业网)
  2. 筛选简历
  3. 面试 (线上/线下)
  4. 确认入职

---

### 任务 10: Benchmark 标注员培训
- **优先级**: 🟡 中
- **预计耗时**: 120 分钟 (培训 + ICC 检验)
- **截止日期**: 2026-04-20
- **依赖**: 任务 9 完成 (研究助理到位)
- **文件**: `research/paper/assessor-training-materials.md`
- **操作**:
  1. 准备培训材料 (PPT + 速查卡)
  2. 招募 3 名标注员 (心理学背景)
  3. 执行培训 (6 小时: 理论 + 练习 + ICC 检验)
  4. ICC 达标后上岗

---

## 状态追踪

| 任务 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 0. 实验设计审阅 | ⏳ 待完成 | — | 综合设计方案 (`09-experiment-design-comprehensive.md`) |
| 1. 伦理审阅 | ⏳ 待完成 | — | `05-ethics-approval-package.md` |
| 2. PI 确认 + 盖章 | ⏳ 待完成 | — | 依赖任务 1 |
| 3. 伦理提交 | ⏳ 待完成 | — | 依赖任务 2 |
| 4. LaTeX 编译 | ⏳ 待完成 | — | 需 V 本地执行 (容器无 TeX 权限) |
| 5. arXiv 提交 | 📦 包已准备 | — | `arxiv-submission-v1.1.tar.gz` (23KB) 已就绪 |
| 6. LaTeX v1.1 方案 | ✅ 已同步 | 2026-03-28 | paper.tex 已升级 v1.1 |
| 7. DASHSCOPE 配置 | ⏳ 待完成 | — | v0.7 LLM 混合验证 |
| 8. 招募海报 | ⏳ 待完成 | — | 依赖任务 3 |
| 9. 研究助理 | ⏳ 待完成 | — | 依赖任务 3 |
| 10. 标注员培训 | ⏳ 待完成 | — | 依赖任务 9 |

---

## 联系方式

如有疑问，请查阅以下文件:
- 伦理审批包: `research/paper/05-ethics-approval-package.md`
- 招募材料: `research/paper/recruitment-materials.md`
- 实验设计: `research/paper/06-experiment-design-final.md`
- 状态看板: `research/paper/00-paper-prep-status.md`

---

## Run #17 更新 (2026-04-02 09:16 UTC)

### 方法学完整性审查结论

✅ **实验设计 v5.0 方法学审查完成** (`cron-55834c68-run17-report.md`)

| 审查维度 | 状态 | 备注 |
|----------|------|------|
| 变量控制矩阵 | ✅ 完整 (v5.0 §1) | 四层控制，40+ 混淆变量 |
| 对比组设计 | ✅ 完整 (v5.0 §2) | 主动对照 + 嵌套 A/B + 5 种算法基线 |
| 评估指标操作化 | ✅ 完整 (v5.0 §3) | 4 层指标 + Checklist 范式 |
| 统计分析计划 | ✅ 完整 (v5.0 §4) | LMM/HLM + R 代码 + 样本量计算 |
| CONSORT/SPIRIT 对齐 | ✅ 完整 | 每节标注指南对应章节 |

**结论**: 当前实验设计已满足 arXiv 技术报告 + Pilot RCT 执行的方法学要求，无需额外补充即可提交。

### 逾期影响更新

| 里程碑 | 原计划 | 当前估计 (如本周提交) | 延迟 |
|--------|--------|----------------------|------|
| arXiv 提交 | 2026-03-31 | 2026-04-03 | +3 天 |
| 伦理审批收到 | 2026-04-15 | 2026-04-22 | +1 周 |
| Pilot RCT 启动 | 2026-05-01 | 2026-05-15 | +2 周 |
| 数据收集完成 | 2026-07-31 | 2026-08-15 | +2 周 |

### V 快速行动清单 (建议 48 小时内完成)

| # | 任务 | 预计耗时 | 操作 | 优先级 |
|---|------|----------|------|--------|
| 1 | **LaTeX 编译** | 30 分钟 | `cd research/arxiv-paper && pdflatex paper.tex` (3 次) | 🔴 高 |
| 2 | **arXiv 提交** | 20 分钟 | 上传 `arxiv-submission-v1.1.tar.gz` 到 arxiv.org | 🔴 高 |
| 3 | **伦理审批填写** | 30 分钟 | 填写 `05-ethics-approval-package.md` 中 4 个占位符 | 🔴 高 |
| 4 | **伦理提交** | 15 分钟 | 在线系统上传材料 | 🔴 高 |

**总耗时**: ~95 分钟 (可在一个工作单元内完成)

---

## Run #16 更新 (2026-04-02 05:42 UTC)

### 状态检查
- **V 待办事项进度**: 无变化，所有阻塞项仍等待 V 执行
- **arXiv 提交**: 已逾期 2 天 (原截止 03-31)
- **伦理审批**: 已逾期 1 天 (原截止 04-01)
- **文件修改扫描**: 无新修改 (最后修改仍为 Mar 26-31)

### 逾期影响
| 阻塞项 | 影响 | 建议 |
|--------|------|------|
| **arXiv 提交** | 论文不可引用，学术影响力延迟；EverMemOS 已有 arXiv:2601.02163 | 尽快提交，arXiv 允许后续版本更新 |
| **伦理审批** | Pilot RCT 启动延迟约 2 周 | 本周内完成提交，仍可在 2-4 周内获得审批 |

### V 快速行动清单 (建议 48 小时内完成)
| # | 任务 | 预计耗时 | 操作 |
|---|------|----------|------|
| 1 | **LaTeX 编译** | 30 分钟 | `cd research/arxiv-paper && pdflatex paper.tex` (3 次) |
| 2 | **arXiv 提交** | 20 分钟 | 上传 `arxiv-submission-v1.1.tar.gz` 到 arxiv.org |
| 3 | **伦理审批填写** | 30 分钟 | 填写 `05-ethics-approval-package.md` 中 4 个占位符 |
| 4 | **伦理提交** | 15 分钟 | 在线系统上传材料 |

**总耗时**: ~95 分钟 (可在一个工作单元内完成)

---

*Hulk 🟢 — V Action Items v1.2 (2026-04-02 05:42 UTC) — Run #16: 逾期提醒*
