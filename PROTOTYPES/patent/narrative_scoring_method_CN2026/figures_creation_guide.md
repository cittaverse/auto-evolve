# 图表制作指南（无 Python 依赖）

**目标**：制作 JMIR Aging 论文所需的 6 个图表（2 表 +4 图）  
**工具**：在线工具或常用软件（无需编程）  
**输出要求**：PNG/TIFF，300 DPI，最小宽度 1200px

---

## 方案 A：使用在线工具（推荐，最快）

### 工具 1：Canva（免费 + 模板丰富）

**网址**：https://www.canva.com/

**适用图表**：
- Figure 1: 系统架构图 ✅
- Figure 4: 反馈采纳率柱状图 ✅
- Table 1-2: 表格（可导出 PNG）✅

**操作步骤**：
1. 注册/登录 Canva
2. 搜索"Flowchart"或"Bar Chart"模板
3. 替换文字和数据
4. 下载 → 选择 PNG → 300 DPI

**优点**：模板多，操作简单，导出质量高  
**缺点**：部分高级功能需付费

---

### 工具 2：ChartGo（免费在线图表）

**网址**：https://www.chartgo.com/

**适用图表**：
- Figure 2: 混淆矩阵（Heatmap）✅
- Figure 3: 散点图 + 回归线 ✅
- Figure 4: 柱状图 ✅

**操作步骤**（以 Figure 4 为例）：
1. 访问 https://www.chartgo.com/
2. 选择"Bar Chart"
3. 输入数据：
   ```
   Internal Details,72
   External Details,73
   Emotional Depth,58
   Self-Reference,50
   Overall,67
   ```
4. 自定义颜色（#0EA5E9）
5. 下载 PNG（300 DPI）

**优点**：完全免费，支持多种图表  
**缺点**：界面较简单，需手动调整

---

### 工具 3：Draw.io（流程图专用）

**网址**：https://app.diagrams.net/

**适用图表**：
- Figure 1: 系统架构图 ✅（强烈推荐）

**操作步骤**：
1. 访问 https://app.diagrams.net/
2. 选择"Create New Diagram"
3. 拖拽矩形框，输入模块内容
4. 添加箭头连接
5. File → Export As → PNG → 300 DPI

**优点**：专业流程图工具，完全免费  
**缺点**：仅适合流程图，不适合数据图表

---

### 工具 4：Google Sheets（表格 + 简单图表）

**网址**：https://sheets.google.com/

**适用图表**：
- Table 1-2: 表格 ✅
- Figure 3: 散点图 ✅
- Figure 4: 柱状图 ✅

**操作步骤**（以 Table 1 为例）：
1. 创建新表格
2. 输入两列数据（Characteristic, Value）
3. 格式化表格（加粗标题，调整列宽）
4. File → Download → PNG（或截图后 PS 处理）

**优点**：熟悉度高，协作方便  
**缺点**：导出 PNG 质量一般，需后期处理

---

## 方案 B：使用本地软件

### PowerPoint / Keynote

**适用图表**：全部 6 个图表 ✅

**操作步骤**（以 Figure 2 混淆矩阵为例）：
1. 插入表格（4×4）
2. 填入数据
3. 设置条件格式（颜色深浅）
4. 另存为图片 → 选择 PNG → 设置 DPI（300）

**优点**：本地软件，可控性强  
**缺点**：导出高分辨率需设置

### Excel

**适用图表**：
- Table 1-2: 表格 ✅
- Figure 3: 散点图 ✅
- Figure 4: 柱状图 ✅

**操作步骤**：
1. 输入数据
2. 插入图表（散点图/柱状图）
3. 格式化（颜色、字体、标题）
4. 右键图表 → 另存为图片 → PNG

---

## 方案 C：使用 Python（如环境允许）

**前提**：安装 matplotlib, seaborn, numpy

```bash
pip install matplotlib seaborn numpy
```

**执行**：
```bash
cd /Users/moondy/.openclaw/workspace-hulk/PROTOTYPES/patent/narrative_scoring_method_CN2026
python3 generate_figures.py
```

**输出**：6 个 PNG 文件自动生成到 `figures/` 目录

---

## 各图表制作详解

### Table 1: 人口学特征

**数据**：
| Characteristic | Value |
|----------------|-------|
| Age (years), mean (SD) | 72.4 (5.8) |
| Age range | 65-85 |
| Female, n (%) | 28 (56%) |
| Education: Primary school | 8 (16%) |
| Education: Middle school | 25 (50%) |
| Education: College+ | 12 (24%) |
| Narrative length (words) | 234 (127) |
| MMSE score | 27.3 (2.1) |

**推荐工具**：Canva 或 Google Sheets  
**预计耗时**：15 分钟

---

### Table 2: 一致性结果

**数据**：
| Dimension | Human κ | r | p-value |
|-----------|---------|---|---------|
| Narrative Coherence | 0.74 | 0.81 | <0.001 |
| Internal Details | 0.69 | 0.76 | <0.001 |
| External Details | 0.72 | 0.79 | <0.001 |
| Emotional Depth | 0.68 | 0.74 | <0.001 |
| Self-Reference | 0.76 | 0.82 | <0.001 |
| **Overall** | **0.71** | **0.78** | **<0.001** |

**推荐工具**：Canva 或 Excel  
**预计耗时**：15 分钟

---

### Figure 1: 系统架构图

**内容**：4 个模块垂直排列，箭头连接

**模块文本**：
1. Module 1: Input Processing (ASR + Preprocessing)
2. Module 2: Event Graph Extraction (LLM)
3. Module 3: Dual-Layer Scoring (Symbolic + Neural)
4. Module 4: Integration and Feedback

**推荐工具**：Draw.io（最佳）或 Canva  
**预计耗时**：30 分钟

---

### Figure 2: 混淆矩阵

**数据**（热图）：
```
       Human
       S  A  B  C
Auto S  8  2  0  0
     A  1  9  3  0
     B  0  2 11  2
     C  0  0  1  4
```

**推荐工具**：ChartGo（Heatmap）或 Excel  
**预计耗时**：20 分钟

---

### Figure 3: 分数相关性散点图

**数据**：50 个样本的 Human Score vs Automated Score  
**关键标注**：r = 0.78, p < 0.001

**推荐工具**：ChartGo（Scatter Plot）或 Excel  
**预计耗时**：20 分钟

---

### Figure 4: 反馈采纳率柱状图

**数据**：
| Type | Rate |
|------|------|
| Internal Details | 72% |
| External Details | 73% |
| Emotional Depth | 58% |
| Self-Reference | 50% |
| Overall | 67% |

**推荐工具**：Canva 或 ChartGo  
**预计耗时**：15 分钟

---

## 文件命名规范

```
table1_demographics.png
table2_reliability.png
figure1_system_architecture.png
figure2_confusion_matrix.png
figure3_score_correlation.png
figure4_feedback_adoption.png
```

---

## 质量检查清单

制作完成后检查：

- [ ] 所有文字清晰可读（无模糊）
- [ ] 图片宽度 ≥ 1200px
- [ ] 分辨率 ≥ 300 DPI
- [ ] 颜色使用 CittaVerse 品牌色（#0EA5E9）
- [ ] 标题和坐标轴标签完整
- [ ] 数据准确无误
- [ ] 文件格式为 PNG 或 TIFF

---

## 快速制作路径（最省时）

**总耗时**：约 2 小时

| 图表 | 工具 | 耗时 |
|------|------|------|
| Table 1 | Canva | 15min |
| Table 2 | Canva | 15min |
| Figure 1 | Draw.io | 30min |
| Figure 2 | ChartGo | 20min |
| Figure 3 | ChartGo | 20min |
| Figure 4 | Canva | 15min |
| **合计** | | **115min** |

---

## 备用方案

如时间紧急，可简化为 **2 表 + 2 图**：

**保留**：
- Table 1（人口学）
- Table 2（一致性）
- Figure 1（系统架构）
- Figure 3（相关性）— 最重要的结果图

**可删除**：
- Figure 2（混淆矩阵）— 可在正文用文字描述
- Figure 4（反馈采纳率）— 可在正文用文字描述

---

*文档版本：v1.0*  
*创建日期：2026-03-12*  
*下一步：选择工具，开始制作图表*
