# 论文图表规格说明

**目标期刊**：JMIR Aging  
**图表数量**：4-6 个（2 表 + 2-4 图）  
**格式要求**：PNG/TIFF，300 DPI，最小宽度 1200px  
**颜色模式**：RGB（在线出版）

---

## 表格（2 个）

### Table 1: 参与者人口学特征

**标题**：Table 1. Demographic characteristics of study participants (N=50)

**列**：
| Characteristic | Value |
|----------------|-------|
| Age (years), mean (SD) | 72.4 (5.8) |
| Age range | 65-85 |
| Female, n (%) | 28 (56%) |
| Education, n (%) | |
|  Primary school | 8 (16%) |
|  Middle school | 25 (50%) |
|  College+ | 12 (24%) |
|  Unknown | 5 (10%) |
| Narrative length (words), mean (SD) | 234 (127) |
| MMSE score, mean (SD) | 27.3 (2.1) |

**制作工具**：Excel → 导出 PNG，或 Python matplotlib/pandas

---

### Table 2: 评分一致性结果

**标题**：Table 2. Inter-rater reliability and automated-human score correlation

**列**：
| Dimension | Human κ (95% CI) | Automated-Human r | p-value |
|-----------|------------------|-------------------|---------|
| Narrative Coherence | 0.74 (0.62-0.86) | 0.81 | <0.001 |
| Internal Details | 0.69 (0.55-0.83) | 0.76 | <0.001 |
| External Details | 0.72 (0.59-0.85) | 0.79 | <0.001 |
| Emotional Depth | 0.68 (0.54-0.82) | 0.74 | <0.001 |
| Self-Reference | 0.76 (0.64-0.88) | 0.82 | <0.001 |
| **Overall Grade** | **0.71 (0.59-0.83)** | **0.78** | **<0.001** |

**注脚**：κ = Cohen's kappa; r = Pearson correlation coefficient

---

## 图表（4 个）

### Figure 1: 系统架构图

**标题**：Figure 1. System architecture of the neuro-symbolic narrative assessment pipeline.

**内容**：
```
┌─────────────────────────────────────────────────────────────┐
│  Module 1: Input Processing                                 │
│  - ASR transcription (dialect-optimized)                    │
│  - Text preprocessing                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Module 2: Event Graph Extraction (Neural Layer)            │
│  - LLM prompt: "Extract events as JSON"                     │
│  - Output: Directed graph G = (V, E)                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Module 3: Dual-Layer Scoring                               │
│  - Symbolic: TC, ED via NetworkX                            │
│  - Neural: 5-dimension content scoring via LLM              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Module 4: Integration and Feedback                         │
│  - Weighted fusion                                          │
│  - Grade mapping (S/A/B/C)                                  │
│  - Dynamic feedback generation                              │
└─────────────────────────────────────────────────────────────┘
```

**制作工具**：
- **推荐**：draw.io（免费，导出 PNG/SVG）
- **备选**：PowerPoint / Keynote / Figma / Lucidchart

**样式要求**：
- 字体：Arial 或 Helvetica，12-14pt
- 颜色：使用 CittaVerse 品牌色（Clinical Cerulean #0EA5E9）
- 箭头：实心箭头，清晰标注数据流

---

### Figure 2: 混淆矩阵

**标题**：Figure 2. Confusion matrix: Automated vs. Human consensus grade classification.

**数据**：
```
               Human Grade
               S    A    B    C
Auto  S       8    2    0    0
Grade A       1    9    3    0
      B       0    2   11    2
      C       0    0    1    4
```

**可视化**：热图（heatmap）

**制作工具**：Python seaborn/matplotlib

**代码示例**：
```python
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

data = np.array([[8, 2, 0, 0],
                 [1, 9, 3, 0],
                 [0, 2, 11, 2],
                 [0, 0, 1, 4]])

labels = ['S', 'A', 'B', 'C']

plt.figure(figsize=(8, 6))
sns.heatmap(data, annot=True, fmt='d', cmap='Blues',
            xticklabels=labels, yticklabels=labels)
plt.xlabel('Human Grade')
plt.ylabel('Automated Grade')
plt.title('Confusion Matrix: Automated vs. Human Classification')
plt.tight_layout()
plt.savefig('figure2_confusion_matrix.png', dpi=300)
```

**颜色方案**：Blues 渐变（浅色→深色）

---

### Figure 3: 分数分布图

**标题**：Figure 3. Distribution of automated and human scores across 50 narrative samples.

**内容**：
- 双直方图叠加（Automated vs Human）
- 或 箱线图对比（Automated vs Human）
- 或 散点图 + 回归线（显示 r=0.78）

**推荐**：散点图 + 回归线

**制作工具**：Python seaborn/matplotlib

**代码示例**：
```python
import seaborn as sns
import matplotlib.pyplot as plt

# 模拟数据（实际使用真实数据）
automated_scores = [71.2, 72.5, 68.9, ...]  # 50 个
human_scores = [72.5, 73.1, 70.2, ...]  # 50 个

plt.figure(figsize=(10, 8))
sns.regplot(x=human_scores, y=automated_scores, 
            scatter_kws={'alpha': 0.6, 's': 60},
            line_kws={'color': 'red', 'linewidth': 2})
plt.xlabel('Human Expert Score')
plt.ylabel('Automated Score')
plt.title('Automated vs. Human Score Correlation (r = 0.78, p < 0.001)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('figure3_score_correlation.png', dpi=300)
```

**标注**：在图上标注 r 值和 p 值

---

### Figure 4: 反馈采纳率

**标题**：Figure 4. Feedback adoption rate by dimension (N=30 revised narratives).

**数据**：
| Feedback Type | Adoption Rate |
|---------------|---------------|
| Internal Details | 72% |
| External Details | 73% |
| Emotional Depth | 58% |
| Self-Reference | 50% |
| **Overall** | **67%** |

**可视化**：柱状图（bar chart）

**制作工具**：Python seaborn/matplotlib / Excel

**代码示例**：
```python
import matplotlib.pyplot as plt

types = ['Internal\nDetails', 'External\nDetails', 
         'Emotional\nDepth', 'Self-\nReference', 'Overall']
rates = [72, 73, 58, 50, 67]
colors = ['#0EA5E9', '#0EA5E9', '#0EA5E9', '#0EA5E9', '#0284C7']

plt.figure(figsize=(10, 6))
bars = plt.bar(types, rates, color=colors)
plt.ylabel('Adoption Rate (%)')
plt.ylim(0, 100)
plt.title('AI Feedback Adoption Rate by Dimension')

# 添加数值标签
for bar, rate in zip(bars, rates):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
             f'{rate}%', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('figure4_feedback_adoption.png', dpi=300)
```

---

## 制作时间表

| 图表 | 优先级 | 预计耗时 | 状态 |
|------|--------|----------|------|
| Table 1 | 高 | 30min | 🟡 待制作 |
| Table 2 | 高 | 30min | 🟡 待制作 |
| Figure 1 | 高 | 60min | 🟡 待制作 |
| Figure 2 | 高 | 30min | 🟡 待制作 |
| Figure 3 | 中 | 30min | 🟡 待制作 |
| Figure 4 | 中 | 30min | 🟡 待制作 |

---

## 文件命名规范

```
figure1_system_architecture.png
figure2_confusion_matrix.png
figure3_score_correlation.png
figure4_feedback_adoption.png
table1_demographics.png
table2_reliability.png
```

---

## 提交要求（JMIR Aging）

- **格式**：PNG 或 TIFF
- **分辨率**：≥300 DPI
- **最小宽度**：1200 像素
- **字体嵌入**：是（避免字体缺失）
- **颜色模式**：RGB（在线出版）
- **文件大小**：每个 < 10 MB

---

## 备选方案

如时间紧张，可简化为 **2 表 + 2 图**：

**保留**：
- Table 1（人口学）
- Table 2（一致性）
- Figure 1（系统架构）
- Figure 2（混淆矩阵）或 Figure 3（相关性）

**可选删除**：
- Figure 4（反馈采纳率）— 可在正文中用文字描述

---

*文档版本：v0.1*  
*创建日期：2026-03-12*  
*下一步：使用 Python/Excel 制作图表，导出 PNG*
