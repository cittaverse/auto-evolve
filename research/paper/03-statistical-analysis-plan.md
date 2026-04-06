# 统计分析计划 (SAP) — CittaVerse Pilot RCT

**版本**: v1.0 (独立文档)  
**日期**: 2026-03-24  
**作者**: Hulk 🟢  
**来源**: 从 `research/2026-03-14-pilot-rct-protocol.md` 提取并扩展  
**验证等级**: V2 (方法学基于多来源交叉确认，未实际执行)

---

## 1. 分析目标

### 1.1 主要假设

- **H0**: CittaVerse 干预组与主动对照组在 8 周 MoCA 变化上无差异
- **H1**: CittaVerse 干预组的 MoCA 改善显著优于对照组

### 1.2 次要假设

| 终点 | 假设方向 |
|------|----------|
| GDS-15 (抑郁) | 干预组抑郁评分下降更多 |
| QOL-AD (生活质量) | 干预组生活质量提升更多 |
| SWLS (生活满意度) | 干预组满意度提升更多 |
| NPI-Q (行为症状) | 干预组行为症状改善更多 |
| 六维叙事评分 | 干预组叙事质量提升更多 |

---

## 2. 分析人群

| 分析集 | 定义 | 用途 |
|--------|------|------|
| **ITT** (意向性治疗) | 所有已随机化的受试者 | **主要分析** |
| **mITT** (修正 ITT) | 至少完成 1 次干预的受试者 | 辅助分析 |
| **PP** (符合方案) | 完成 ≥80% 干预会话 (≥13/16 次) | 敏感性分析 |
| **Safety** (安全性) | 至少接受 1 次干预的受试者 | 不良事件分析 |

---

## 3. 主要终点分析

### 3.1 模型选择: 线性混合效应模型 (LMM)

**理由**:
- 处理重复测量的受试者内相关性
- 自然处理缺失数据 (MAR 假设下)
- 可纳入多中心效应

### 3.2 模型规格

```
MoCA_ij ~ β0 + β1·Group_i + β2·Time_j + β3·(Group×Time)_ij 
         + β4·Center_i + β5·Baseline_MoCA_i 
         + u_i + ε_ij

其中:
  i = 受试者, j = 时点
  β0 = 截距
  β1 = 组别效应 (干预=1, 对照=0)
  β2 = 时间效应 (基线=0, 8周=1)
  β3 = 组别×时间交互 ← 主要关注项
  β4 = 中心效应
  β5 = 基线 MoCA 协变量
  u_i ~ N(0, σ²_u) = 受试者随机截距
  ε_ij ~ N(0, σ²_ε) = 残差
```

### 3.3 主要检验

- **检验统计量**: β3 的 t 检验 (Satterthwaite 自由度)
- **显著性**: α = 0.05 (双尾)
- **效应量**: Cohen's d = β3 / pooled SD
- **95% CI**: β3 的 95% 置信区间

### 3.4 效力分析

| 样本量 | 可检测效应量 (d) | 检验效能 |
|--------|-----------------|----------|
| N=60 (30/组) | 0.80 | 80% |
| N=60 (30/组) | 0.65 | 60% |
| N=80 (40/组) | 0.65 | 80% |
| N=80 (40/组) | 0.50 | 60% |

**注**: Pilot 主要评估可行性，疗效为探索性。

---

## 4. 次要终点分析

### 4.1 连续变量 (GDS-15, QOL-AD, SWLS, NPI-Q)

**方法**: 同主要终点 (LMM)

**多重比较校正**: Benjamini-Hochberg FDR (q = 0.10)

**理由**: Pilot 中次要终点为探索性，使用较宽松的 FDR 控制以保留检出力

### 4.2 分类变量

| 变量 | 分析方法 | 定义 |
|------|----------|------|
| 应答率 | χ² 检验 / Fisher 精确 | MoCA 改善 ≥2 分 |
| 临床显著改善 | χ² 检验 / Fisher 精确 | MoCA 改善 ≥3 分 (MCID) |
| 脱落率 | χ² 检验 | 组间差异 |

### 4.3 时间至事件

- **脱落时间**: Kaplan-Meier 曲线 + log-rank 检验
- **Cox 回归**: HR (hazard ratio) + 95% CI, 调整基线协变量

---

## 5. 探索性分析

### 5.1 六维叙事评分分析

**纵向模型** (多次测量: 基线、4 周、8 周):
```
Narrative_Score_ijk ~ β0 + β1·Group_i + β2·Time_j + β3·(Group×Time)_ij
                    + β4·Dimension_k + β5·(Group×Time×Dimension)_ijk
                    + u_i + v_ik + ε_ijk

其中:
  k = 维度 (1-6)
  β5 = 三阶交互 (不同维度是否有差异化改善?)
  v_ik = 受试者×维度随机效应
```

**目的**: 
- 哪些维度改善最大？
- 元记忆策略对特定维度是否有针对性效果？

### 5.2 叙事评分与认知的关联

```
MoCA_change ~ β0 + β1·Narrative_score_change + β2·Baseline_MoCA 
            + β3·Age + β4·Education + ε
```

**目的**: 叙事质量改善是否预测认知改善？

### 5.3 A/B 测试 (元记忆增强)

**嵌套于干预组内** (n=30-40):

```
Narrative_Score_ij ~ β0 + β1·Condition_i + β2·Session_j 
                   + β3·(Condition×Session)_ij + u_i + ε_ij

其中:
  Condition: 标准引导=0, 元记忆增强=1
  Session: 1-16 (会话编号)
  β3 = 改善速度差异 ← 主要关注
```

### 5.4 亚组分析

| 亚组 | 分组 | 假设 |
|------|------|------|
| 年龄 | <75 vs ≥75 | 年轻组效果更佳 |
| 基线认知 | MoCA 18-21 vs 22-25 | 较轻 MCI 效果更佳 |
| 教育水平 | ≤初中 vs ≥高中 | 教育水平调节效果 |
| 干预依从性 | ≥80% vs <80% | 高依从效果更佳 |

**注**: 亚组分析为纯探索性，不做多重比较校正，结果仅用于指导后续 RCT 设计。

---

## 6. 缺失数据处理

### 6.1 策略

| 情况 | 方法 | 假设 |
|------|------|------|
| **基线缺失** (<5%) | 多重插补 (m=20, PMM) | MAR |
| **随访缺失** (<20%) | LMM 自���处理 | MAR |
| **随访缺失** (20-30%) | 敏感性: 模式混合模型 (PMM) | MNAR 检验 |
| **随访缺失** (>30%) | Worst-case 分析 + 明确报告局限 | MNAR |

### 6.2 MAR 假设检验

- Little's MCAR test: 检验是否完全随机缺失
- 缺失模式分析: 比较完成者 vs 未完成者的基线特征
- 敏感性分析: δ-adjustment (假设缺失者比完成者差 0.5 SD)

---

## 7. 可行性指标 (Pilot 核心)

**Pilot 的主要目的是评估可行性，以下指标优先于疗效**:

| 指标 | 计算方式 | 成功标准 |
|------|----------|----------|
| **招募率** | 入组人数 / 筛查人数 | ≥50% |
| **随机化接受率** | 接受随机化 / 符合条件人数 | ≥80% |
| **干预完成率** | 完成 ≥80% 会话 / 入组人数 | ≥70% |
| **脱落率** | 脱落人数 / 入组人数 | ≤30% |
| **数据完整率** | 完整数据点 / 应收集数据点 | ≥85% |
| **会话时长** | 平均 ± SD | 25-45 分钟 |
| **技术故障率** | 故障会话 / 总会话数 | ≤5% |
| **满意度** | SUS 评分 (0-100) | ≥68 (above average) |
| **NPS** | Net Promoter Score | ≥30 |

---

## 8. 效应量估计 (为后续确证性 RCT 提供参数)

**核心产出**: 为后续大规模 RCT 的样本量计算提供：
- MoCA 变化的组间差异均值
- MoCA 变化的 pooled SD
- 效应量 d 的点估计 + 95% CI
- 组内相关系数 (ICC, 用于多中心设计)

**样本量规划公式 (后续 RCT)**:
```
N_per_group = (z_α/2 + z_β)² × 2 × σ² / δ²

其中:
  δ = Pilot 估计的组间差异
  σ = Pilot 估计的 pooled SD
  z_α/2 = 1.96 (α=0.05, 双尾)
  z_β = 0.84 (β=0.20, 80% power)
```

---

## 9. 统计软件

| 用途 | 工具 | 版本 |
|------|------|------|
| 主要分析 | R (lme4, lmerTest) | ≥ 4.3 |
| 多重插补 | R (mice) | ≥ 3.16 |
| 描述统计 | R (tableone) | ≥ 0.13 |
| 图表 | R (ggplot2) | ≥ 3.4 |
| 效力计算 | G*Power 或 R (pwr) | ≥ 3.1 |
| 数据管理 | REDCap → R (REDCapR) | — |

---

## 10. 报告标准

- **CONSORT 2010**: RCT 报告遵循 CONSORT 声明
- **SPIRIT 2013**: 方案遵循 SPIRIT 清单
- **STROBE**: 观察性分析 (如亚组) 遵循 STROBE
- **效应量**: 所有比较报告 d + 95% CI, 不仅报告 p 值

---

## 11. 分析时间线

| 阶段 | 时间 | 产出 |
|------|------|------|
| 数据锁定 | 最后一人完成 8 周后 2 周 | 锁定数据库 |
| 描述统计 | 数据锁定后 1 周 | Table 1 (基线特征) |
| 主要分析 | 数据锁定后 2 周 | LMM 结果 + 效应量 |
| 次要分析 | 数据锁定后 3 周 | 所有次要终点 |
| 探索性分析 | 数据锁定后 4 周 | 叙事评分 + 亚组 + A/B |
| SAP 偏差报告 | 论文提交时 | 记录所有与 SAP 的偏差 |

---

## 12. 预注册计划

**平台**: Chinese Clinical Trial Registry (ChiCTR) 或 ClinicalTrials.gov

**预注册内容**:
- 研究设计 + 主要假设
- 样本量 + 纳入排除
- 主要终点 + 分析模型
- SAP 关键要素

**时机**: 首例受试者入组前

**注**: 本 SAP 将作为预注册附件提交，确保分析透明。

---

## 13. R 代码框架 (预备)

```r
# ========================================
# CittaVerse Pilot RCT — SAP Implementation
# ========================================

library(lme4)
library(lmerTest)
library(mice)
library(tableone)
library(ggplot2)

# --- 1. 数据读入 ---
data <- read.csv("cittaverse_pilot_data.csv")

# --- 2. Table 1: 基线特征 ---
vars <- c("age", "sex", "education", "baseline_moca", "baseline_gds", "center")
tab1 <- CreateTableOne(vars = vars, strata = "group", data = data)
print(tab1, smd = TRUE)

# --- 3. 主要分析: LMM ---
model_primary <- lmer(
  moca ~ group * time + center + baseline_moca + (1 | subject_id),
  data = data_long
)
summary(model_primary)
confint(model_primary)  # 95% CI

# 效应量
library(effectsize)
cohens_d(model_primary, type = "d")

# --- 4. 次要分析 (示例: GDS-15) ---
model_gds <- lmer(
  gds15 ~ group * time + center + baseline_gds + (1 | subject_id),
  data = data_long
)

# FDR 校正
p_values <- c(p_moca, p_gds, p_qolad, p_swls, p_npiq)
p_adjusted <- p.adjust(p_values, method = "BH")

# --- 5. 叙事评分纵向分析 ---
model_narrative <- lmer(
  narrative_score ~ group * session_num * dimension + (1 | subject_id),
  data = narrative_data
)

# --- 6. 缺失数据: 多重插补 ---
imp <- mice(data, m = 20, method = "pmm", seed = 42)
fit_imp <- with(imp, lmer(
  moca ~ group * time + center + baseline_moca + (1 | subject_id)
))
pool(fit_imp)

# --- 7. 可行性指标 ---
feasibility <- data.frame(
  metric = c("recruitment_rate", "completion_rate", "dropout_rate", 
             "data_completeness", "mean_session_min", "tech_failure_rate",
             "sus_score", "nps"),
  value = c(
    nrow(data) / n_screened,
    sum(data$sessions_completed >= 13) / nrow(data),
    sum(data$dropped_out) / nrow(data),
    sum(!is.na(data_long$moca)) / nrow(data_long),
    mean(data$avg_session_minutes),
    sum(data$tech_failures) / sum(data$total_sessions),
    mean(data$sus_score),
    # NPS calculation
    (sum(data$recommend >= 9) - sum(data$recommend <= 6)) / nrow(data) * 100
  )
)
```

---

**文档状态**: v1.0 草案 — 独立 SAP，可直接用于预注册附件  
**验证等级**: V2 (方法学交叉确认)  
**盲点**: 
- 具体样本量取决于实际招募情况
- LMM 的协方差结构假设需要在实际数据上检验
- 亚组分析的检验效力可能不足

---

*Hulk 🟢 — 2026-03-24*
