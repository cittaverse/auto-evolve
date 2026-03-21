# Hulk 研究方法 V2 — 标准操作流程

**版本**: 2.0  
**生效日期**: 2026-03-18  
**来源**: gstack Completeness Principle + 方法升级 7 天冲刺 D1 验证

---

## 一、每次研究的标准动作序列

### Step 0: 搜索策略文档化（PRISMA）

每次研究**开始前**必须记录：

```markdown
| 维度 | 详情 |
|------|------|
| **研究问题** | 一句话 |
| **数据库** | 列出全部使用的数据库 |
| **关键词** | 按维度列出 |
| **日期范围** | 明确 |
| **排除标准** | 明确 |
| **未搜索（局限）** | 诚实标注 |
```

### Step 1: 证据搜索（多工具优先级）

```
优先级 1: web_search (Serper/Google) → 发现线索
优先级 2: arXiv API (curl) → 获取论文全文
         调用: curl -s "https://export.arxiv.org/api/query?search_query=...&max_results=10"
         下载: curl -sL "https://arxiv.org/pdf/{id}" -o /home/node/.openclaw/workspace-hulk/{name}.pdf
         读取: pdftotext {file} - | head -N
优先级 3: Semantic Scholar API → 结构化论文搜索
         调用: curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=...&fields=title,year,citationCount,abstract,url"
         注意: 无 Key 有限流，间隔 30s+
优先级 4: browser → 绕过 web_fetch blocked 的网站
优先级 5: ddg-search / google-search (Serper curl) → 补充搜索
```

### Step 2: 反证搜索（必做）

每个结论必须回答：**"什么证据会推翻这个？"**

标准搜索模板：
```
{主题} limitations
{主题} ineffective
{主题} "no significant difference"
{主题} critique
{主题} failed replication
```

### Step 3: 全文阅读（至少 1 篇）

对最关键的 1-2 篇论文，必须读全文。路径：

```
arXiv → curl 下载 PDF → pdftotext 提取 → 逐段分析
PMC → 尝试 web_fetch → 失败则 browser → 失败则标注"仅摘要"
```

### Step 4: 三角验证

每个关键结论需要至少 3 个独立来源：

| 验证类型 | 方法 |
|---------|------|
| 来源三角 | 论文 + 竞品 + 新闻/博客 |
| 方法三角 | 定量 + 定性 + 混合 |
| 时间三角 | 2024 + 2025 + 2026 |

### Step 5: 竞品验证（如涉及产品）

不猜测，去验证：
- 访问官网，读功能列表
- 搜索新闻稿/PR
- 搜索专利（Google Patents）

### Step 6: 证据等级标注

每条证据必须标注：

```
V0 = 未验证 / 仅推断
V1 = 单一来源确认（摘要/snippet）
V2 = 多来源交叉确认
V3 = 全文阅读 / 静态复核
V4 = 动态验证 / 可复现
```

### Step 7: 元认知反思

每次研究输出末尾必须包含：

```markdown
## 元认知反思

### 搜索策略反思
- 用了哪些工具？哪些有效？
- 漏了什么？为什么？

### 偏见自查
- 我倾向于相信什么？
- 我忽略了什么反面证据？
- 哪些结论可能过度外推？

### 方法改进
- 这次有什么新发现的技巧？
- 下次应该怎么做不同？
```

### Step 8: 证伪条件

每个主要结论必须附带：
```markdown
## 证伪条件
1. 什么具体证据会推翻结论 X？
2. 什么具体证据会推翻结论 Y？
```

---

## 二、Completeness Principle（gstack 启示）

- AI 让"完整"的边际成本接近零
- 永远选完整方案，不选"够用"方案
- "80% 版本"和"100% 版本"的差距在 AI 辅助下只有几分钟
- 不跳过最后 10%

**反模式**：
- ❌ "先出个初版，后面再补"
- ❌ "这个证据大概对，不用验证了"
- ❌ "竞品应该没有这个功能"（去验证）

---

## 三、工具链备忘

| 工具 | 用途 | 调用方式 |
|------|------|---------|
| `web_search` | 发现线索 | 原生工具 |
| `arXiv API` | 论文全文 | `curl -s "https://export.arxiv.org/api/query?..."` |
| `pdftotext` | PDF 文本提取 | `pdftotext file.pdf -` |
| `Semantic Scholar` | 结构化搜索 | `curl -s "https://api.semanticscholar.org/..."` |
| `browser` | 绕过 blocked | 原生工具 |
| `Google Patents` | 专利检索 | `web_search` + `patents.google.com` |

---

## 四、质量评分标准

| 分数 | 标准 |
|------|------|
| **90+** | PRISMA + 全文 3+ 篇 + 反证 + 三角 + 竞品验证 + 元认知 + 证伪条件 |
| **80-89** | PRISMA + 全文 1-2 篇 + 反证 + 三角 + 元认知 |
| **70-79** | 搜索策略 + 反证 + 部分三角 |
| **60-69** | 多来源但无反证、无全文 |
| **<60** | 单一搜索 + 无验证 |

---

*Hulk 🟢 — 2026-03-18*  
*下次研究直接按此流程执行。*
