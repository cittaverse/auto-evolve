# 叙事评分算法 v0.4 设计文档

**版本**: v0.4  
**日期**: 2026-03-16  
**依据**: LLM-Based Scoring of Narrative Memories (ResearchGate, Mar 14, 2026)  
**状态**: 设计稿 → 待实现

---

## 📊 变更概览

### v0.3 → v0.4 核心变更

| 维度 | v0.3 | v0.4 | 变更理由 |
|------|------|------|----------|
| **评分维度** | 5 维度 | 6 维度 | 新增"信息密度分布" |
| **中心/外围信息** | ❌ 未区分 | ✅ 显式建模 | 情绪唤醒增强中心信息但牺牲外围信息 |
| **事件分段** | LLM 提取 | LLM 提取 + 密度校验 | 防止过度分段或分段不足 |
| **权重配置** | 固定权重 | 可配置权重 | 支持 A/B 测试不同权重策略 |

---

## 🧠 理论依据

### 核心发现 (LLM 叙事评分研究, Mar 14, 2026)

> **Emotional arousal enhances central information at the expense of peripheral information**

**解读**:
- 情绪唤醒时，人们更倾向于回忆"中心信息"（核心事件、关键动作、主要人物）
- 但同时会牺牲"外围信息"（环境细节、时间背景、感官体验）
- 这导致叙事呈现"高中心密度 + 低外围密度"的分布特征

**产品启示**:
1. 高质量叙事应平衡中心信息与外围信息
2. AI 引导策略应针对性补充缺失的信息类型
3. 评分算法需显式建模这一分布特征

---

## 📐 新评分维度：信息密度分布 (Information Density Distribution)

### 定义

| 信息类型 | 定义 | 示例 |
|----------|------|------|
| **中心信息 (Central)** | 事件核心、关键动作、主要人物、因果关系 | "我和老伴去了西湖"、"我们结婚了"、"孩子出生了" |
| **外围信息 (Peripheral)** | 环境细节、感官体验、时间背景、情绪感受 | "那天阳光很好"、"湖面有薄雾"、"我穿了一件蓝色旗袍"、"心里很紧张" |

### 计算逻辑

```python
# 伪代码
def calculate_information_density(events):
    """
    输入：LLM 提取的事件列表（每个事件包含 type 字段）
    输出：中心/外围信息比例 + 分布评分
    """
    central_count = sum(1 for e in events if e.type == "central")
    peripheral_count = sum(1 for e in events if e.type == "peripheral")
    
    total = central_count + peripheral_count
    if total == 0:
        return {"ratio": 0, "score": 0, "balance": "unknown"}
    
    central_ratio = central_count / total
    peripheral_ratio = peripheral_count / total
    
    # 理想比例：中心 60% ± 15%, 外围 40% ± 15%
    # 基于叙事疗法文献：高质量自传体记忆应平衡事件核心与情境细节
    ideal_central = 0.6
    ideal_peripheral = 0.4
    
    # 计算偏离度（0-1，1 表示完美平衡）
    central_deviation = abs(central_ratio - ideal_central)
    peripheral_deviation = abs(peripheral_ratio - ideal_peripheral)
    balance_score = 1 - (central_deviation + peripheral_deviation) / 2
    
    # 判定分布类型
    if central_ratio > 0.75:
        distribution_type = "central_dominant"  # 中心主导（可能缺乏细节）
    elif peripheral_ratio > 0.55:
        distribution_type = "peripheral_dominant"  # 外围主导（可能缺乏主线）
    else:
        distribution_type = "balanced"  # 平衡
    
    return {
        "central_count": central_count,
        "peripheral_count": peripheral_count,
        "central_ratio": round(central_ratio, 2),
        "peripheral_ratio": round(peripheral_ratio, 2),
        "balance_score": round(balance_score, 2),
        "distribution_type": distribution_type
    }
```

### 评分映射

| 分布类型 | 中心比例 | 外围比例 | 分布评分 | 引导策略 |
|----------|---------|---------|---------|---------|
| 中心主导 | >75% | <25% | 0.4-0.6 | 补充感官细节、环境背景、情绪感受 |
| 平衡 | 45-75% | 25-55% | 0.8-1.0 | 保持当前引导策略 |
| 外围主导 | <45% | >55% | 0.4-0.6 | 补充事件主线、因果关系、核心动作 |

---

## 🔧 v0.4 架构设计

### 整体流程

```
输入（口述文本）
    ↓
[LLM 事件提取] → 事件列表（含 type 标注）
    ↓
[结构计分] → 图论指标（节点数、边数、连通性）
    ↓
[内容评分] → 6 维度评分
    ├─ 事件丰富度 (0-100)
    ├─ 时间连贯性 (0-100)
    ├─ 因果连贯性 (0-100)
    ├─ 情感深度 (0-100)
    ├─ 自我认同整合 (0-100)
    └─ 信息密度分布 (0-100) ← 新增
    ↓
[加权综合] → 综合分数 (0-100)
    ↓
输出（分数 + 分级 + 引导建议）
```

### 事件提取 Prompt 更新

**v0.3 Prompt** (部分):
```
请从以下口述文本中提取独立事件。每个事件应包含：
- 事件描述
- 时间信息（如有）
- 涉及人物（如有）
```

**v0.4 Prompt** (新增 type 标注):
```
请从以下口述文本中提取独立事件。每个事件应包含：
- 事件描述
- 时间信息（如有）
- 涉及人物（如有）
- 信息类型：central 或 peripheral

**中心信息 (central)**：事件核心、关键动作、主要人物、因果关系
  示例："我和老伴去了西湖"、"我们结婚了"、"孩子出生了"

**外围信息 (peripheral)**：环境细节、感官体验、时间背景、情绪感受
  示例："那天阳光很好"、"湖面有薄雾"、"我穿了一件蓝色旗袍"、"心里很紧张"

请按以下 JSON 格式输出：
{
  "events": [
    {
      "description": "...",
      "time": "...",
      "people": ["..."],
      "type": "central|peripheral"
    }
  ]
}
```

---

## ⚖️ 权重配置

### 默认权重 (v0.4)

| 维度 | 权重 | 理由 |
|------|------|------|
| 事件丰富度 | 15% | 基础指标 |
| 时间连贯性 | 15% | 叙事骨架 |
| 因果连贯性 | 15% | 叙事逻辑 |
| 情感深度 | 20% | 情感是记忆的核心 |
| 自我认同整合 | 15% | 叙事疗法核心目标 |
| 信息密度分布 | 20% | ← 新增，平衡中心/外围信息 |

### 可配置策略

```yaml
# config/narrative_scorer_weights.yaml
strategies:
  default:
    event_richness: 0.15
    temporal_coherence: 0.15
    causal_coherence: 0.15
    emotional_depth: 0.20
    identity_integration: 0.15
    information_density: 0.20
  
  emc_phase:  # 早期记忆采集阶段，鼓励外围细节
    event_richness: 0.10
    temporal_coherence: 0.10
    causal_coherence: 0.10
    emotional_depth: 0.20
    identity_integration: 0.10
    information_density: 0.40  # 更高权重鼓励外围信息
  
  therapy_phase:  # 治疗阶段，平衡中心/外围
    event_richness: 0.15
    temporal_coherence: 0.15
    causal_coherence: 0.15
    emotional_depth: 0.20
    identity_integration: 0.15
    information_density: 0.20
  
  mci_screening:  # MCI 筛查，重视连贯性
    event_richness: 0.10
    temporal_coherence: 0.25
    causal_coherence: 0.25
    emotional_depth: 0.15
    identity_integration: 0.10
    information_density: 0.15
```

---

## 📈 引导策略映射

### 基于信息密度分布的引导

| 分布类型 | 识别特征 | 引导策略 | 示例问题 |
|----------|---------|---------|---------|
| 中心主导 | 中心>75%, 外围<25% | 补充感官细节、环境背景 | "那天的天气怎么样？""您当时穿的是什么衣服？""周围有什么声音或气味吗？" |
| 平衡 | 中心 45-75%, 外围 25-55% | 保持当前策略 | 继续使用标准引导问题库 |
| 外围主导 | 中心<45%, 外围>55% | 补充事件主线、因果关系 | "这件事是怎么开始的？""后来发生了什么？""这对您有什么影响？" |

### 与元记忆策略的整合

```python
def select_guidance_strategy(narrative_score, distribution_type, metamemory_profile):
    """
    综合叙事评分 + 信息密度分布 + 元记忆画像，选择引导策略
    """
    if distribution_type == "central_dominant":
        # 中心主导 → 补充外围信息
        return {
            "strategy": "sensory_enhancement",
            "prompt_template": "sensory_details_prompt",
            "metamemory_hint": "您当时是如何注意到这些细节的？"
        }
    elif distribution_type == "peripheral_dominant":
        # 外围主导 → 补充中心信息
        return {
            "strategy": "event_structure_enhancement",
            "prompt_template": "causal_chain_prompt",
            "metamemory_hint": "这件事对您意味着什么？"
        }
    else:
        # 平衡 → 标准策略
        return {
            "strategy": "standard",
            "prompt_template": "standard_prompt",
            "metamemory_hint": None
        }
```

---

## 🧪 测试计划

### Mock 数据测试

| 测试用例 | 输入特征 | 预期分布类型 | 预期评分 |
|----------|---------|-------------|---------|
| TC-01 | 纯中心信息（10 条中心，0 条外围） | central_dominant | 分布评分 0.4 |
| TC-02 | 纯外围信息（0 条中心，10 条外围） | peripheral_dominant | 分布评分 0.4 |
| TC-03 | 平衡分布（6 条中心，4 条外围） | balanced | 分布评分 0.9-1.0 |
| TC-04 | 轻微中心偏向（7 条中心，3 条外围） | balanced | 分布评分 0.8-0.9 |
| TC-05 | 轻微外围偏向（5 条中心，5 条外围） | balanced | 分布评分 0.8-0.9 |

### 真实数据验证

**数据来源**: AISHELL 23 说话人（8541 wav，待转录）

**验证步骤**:
1. 抽取 20-30 条口述样本
2. 人工标注中心/外围信息
3. 运行 v0.4 算法
4. 计算算法与人工标注的一致性（Kappa 系数）
5. 目标：Kappa ≥ 0.75

---

## 📅 实现计划

| 阶段 | 任务 | 预计耗时 | 依赖 | 状态 |
|------|------|---------|------|------|
| 1 | 更新事件提取 Prompt | 30 min | 无 | ⏳ 待执行 |
| 2 | 实现信息密度计算函数 | 60 min | 无 | ⏳ 待执行 |
| 3 | 更新权重配置系统 | 30 min | 无 | ⏳ 待执行 |
| 4 | 更新引导策略映射 | 60 min | 阶段 1-3 | ⏳ 待执行 |
| 5 | Mock 数据测试 | 30 min | 阶段 1-4 | ⏳ 待执行 |
| 6 | 真实数据验证 | 120 min | AISHELL 转录完成 | ⏳ 阻塞 (API Keys) |

**预计完成**: 2026-03-17 (不依赖 API Keys 的部分)

---

## 📚 参考文献

1. **LLM-Based Scoring of Narrative Memories** (ResearchGate, Mar 14, 2026)
   - 核心发现：情绪唤醒增强中心信息但牺牲外围信息
   - 产品启示：需显式建模中心/外围信息分布

2. **Reminiscence Therapy Meta-analysis** (PMC, Jan 2026)
   - 核心发现：RT 对 MCI 有效但证据不足（仅 3 项研究）
   - 产品启示：需自建临床数据集

3. **Narrative Scorer Pipeline v0.3** (内部文档, 2026-03-10)
   - 现有架构：5 维度评分 + 神经符号范式
   - 升级路径：增加第 6 维度（信息密度分布）

---

**创建时间**: 2026-03-16 03:44 UTC  
**创建人**: Hulk 🟢  
**下次更新**: 实现完成后更新状态
