# Multi-Agent Scorer v0.6 设计稿

**版本**: v0.6-draft  
**创建日期**: 2026-04-02  
**作者**: Hulk 🟢 (GEO #98)  
**状态**: 设计稿 (待 Core 评审 + 实现)  
**验证等级**: V0 (架构推断，需实验验证)

---

## 概述

本设计稿描述 VSNC 评分器 v0.6 的多 Agent 架构，核心目标：
1. **抗 Reward Hacking**: 防止通过关键词堆砌/模板化叙述欺骗评分
2. **抗 Over-Verification**: 动态调整验证强度，平衡性能与效度
3. **分层仲裁**: L0 规则引擎快速评分 + L1 LLM 仲裁边界案例 + L2 人工复核高价值样本

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                      输入：叙事文本                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    L0 规则引擎 (现有 L0 评分器)                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ C1: 内部细节  │ │ C2: 外部细节  │ │ C3: 事件连贯性│            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ C4: 情感效价  │ │ C5: 信息密度  │ │ C6: 语言流畅度│            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                              ↓                                  │
│                    置信度计算 (维度间一致性)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │ 置信度 < 0.6?    │
                    └─────────────────┘
                      ↓           ↓
                    是            否
                      ↓           ↓
        ┌──────────────────┐      │
        │  L1 LLM 仲裁层     │      │
        │  (新增模块)       │      │
        └──────────────────┘      │
                      ↓           │
        ┌──────────────────┐      │
        │ 维度级修正建议    │      │
        │ (+/- 5 分区间)    │      │
        └──────────────────┘      │
                      ↓           ↓
        ┌─────────────────────────────────────────┐
        │          加权融合 → 最终评分              │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │   L2 人工复核 (仅高价值样本，可选)        │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │   输出：评分 + 置信度 + 解释              │
        └─────────────────────────────────────────┘
```

---

## 组件详细设计

### 1. L0 规则引擎 (现有)

**状态**: ✅ 已实现 (v0.5)  
**职责**: 6 维度快速评分 + 置信度计算  
**性能目标**: <100ms/样本，80% 样本不进入 L1

**置信度计算公式**:
```python
def calculate_confidence(dimensions):
    """
    基于维度间一致性计算置信度
    
    参数:
        dimensions: dict {C1: score, C2: score, ..., C6: score}
    
    返回:
        confidence: float [0, 1]
    """
    scores = list(dimensions.values())
    mean_score = sum(scores) / len(scores)
    std_dev = statistics.stdev(scores)
    
    # 标准差越小，维度间越一致，置信度越高
    # 标准差 > 15 → 置信度 < 0.5
    # 标准差 < 5 → 置信度 > 0.9
    confidence = 1.0 - min(std_dev / 20.0, 0.8)
    
    return confidence
```

**L1 触发条件**:
```python
should_trigger_L1 = (
    confidence < 0.6 or  # 低置信度
    (55 <= final_score <= 75)  # 边界案例
)
```

---

### 2. L1 LLM 仲裁层 (新增)

**状态**: ⏳ 待实现 (v0.6 核心)  
**依赖**: DASHSCOPE_API_KEY (已就绪)  
**预计工作量**: 4-6 天

#### 2.1 仲裁维度

| 维度 | 检测目标 | Prompt 关键词 | 输出格式 |
|------|---------|-------------|---------|
| **情感 - 事件一致性** | 情感词是否与事件效价匹配 | "情感词", "事件效价", "一致性" | consistent: bool, reason: str |
| **内部一致性** | 前后叙述是否矛盾 | "矛盾", "不一致", "前后冲突" | contradictions: list[str] |
| **代际语言特征** | 识别老年人特有词汇/句式 | "老年人", "代际", "词汇特征" | elderly_markers: list[str] |
| **Lexical Fidelity** | 方言词/时代特征词检测 | "方言", "时代特征", "保真度" | dialect_words: list[str], era_markers: list[str] |
| **Persona Tone** | 叙述者语气识别 | "语气", "温和", "急躁", "犹豫" | tone: str, confidence: float |

#### 2.2 仲裁 Prompt 模板

```python
ARBITRATION_PROMPT = """
你是一位叙事质量评估专家。请对以下叙事文本进行深度分析：

【叙事文本】
{narrative_text}

【L0 规则引擎初评结果】
- C1 内部细节：{c1_score}
- C2 外部细节：{c2_score}
- C3 事件连贯性：{c3_score}
- C4 情感效价：{c4_score}
- C5 信息密度：{c5_score}
- C6 语言流畅度：{c6_score}
- 置信度：{confidence}

【仲裁任务】
请逐项分析以下维度，输出 JSON 格式结果：

1. 情感 - 事件一致性：情感词是否与叙述事件的效价匹配？
2. 内部一致性：叙述前后是否存在矛盾或不一致？
3. 代际语言特征：是否包含老年人特有的词汇或句式？
4. 语言风格保真度：是否包含方言词或时代特征词？
5. 叙述者语气：语气是温和、急躁、犹豫还是其他？

【输出格式】
{{
  "emotional_consistency": {{
    "consistent": true/false,
    "reason": "..."
  }},
  "internal_consistency": {{
    "contradictions": ["...", "..."],
    "score_adjustment": -5 to +5
  }},
  "generational_markers": {{
    "elderly_words": ["...", "..."],
    "score_adjustment": -5 to +5
  }},
  "lexical_fidelity": {{
    "dialect_words": ["...", "..."],
    "era_markers": ["...", "..."],
    "score_adjustment": -5 to +5
  }},
  "persona_tone": {{
    "tone": "温和/急躁/犹豫/中性",
    "confidence": 0.0-1.0,
    "score_adjustment": -5 to +5
  }},
  "overall_adjustment": -10 to +10,
  "reasoning": "..."
}}
"""
```

#### 2.3 加权融合算法

```python
def fuse_scores(l0_scores, l1_arbitration):
    """
    融合 L0 初评和 L1 仲裁结果
    
    参数:
        l0_scores: dict {C1: score, ..., C6: score, final: score}
        l1_arbitration: dict (LLM 仲裁输出)
    
    返回:
        final_scores: dict (融合后评分)
    """
    l0_final = l0_scores['final']
    l1_adjustment = l1_arbitration['overall_adjustment']
    
    # 动态权重：L0 置信度越高，L0 权重越大
    l0_weight = l0_scores['confidence']
    l1_weight = 1.0 - l0_weight
    
    # 融合公式：L0 基础分 + L1 调整 * L1 权重
    adjustment_factor = l1_adjustment * l1_weight
    final_score = l0_final + adjustment_factor
    
    # 限制在 0-100 区间
    final_score = max(0, min(100, final_score))
    
    return {
        **l0_scores,
        'final': final_score,
        'l1_adjustment': l1_adjustment,
        'final_confidence': calculate_final_confidence(l0_scores, l1_arbitration)
    }
```

---

### 3. L2 人工复核接口 (新增)

**状态**: ⏳ 待实现 (v0.7 规划)  
**触发条件**:
- 样本标记为"高价值" (临床研究/论文数据)
- L0+L1 置信度仍 < 0.5
- 用户主动申请人工复核

**输出格式**:
```json
{
  "sample_id": "...",
  "l0_score": 72.5,
  "l1_adjustment": -3.2,
  "l2_manual_score": 70.0,
  "l2_reason": "叙述中存在轻微矛盾，但不影响整体质量",
  "final_score": 70.0,
  "reviewer_id": "...",
  "review_timestamp": "2026-04-02T19:00:00Z"
}
```

---

### 4. 抗 Reward Hacking 模块 (新增)

**状态**: ⏳ 待实现 (v0.6 核心)  
**检测维度**:

#### 4.1 信息密度检测

```python
def calculate_information_density(text, external_details):
    """
    计算信息密度：单位字数的有效信息量
    
    参数:
        text: 叙事文本
        external_details: L0 检测到的外部细节数量
    
    返回:
        density: float (0-1)
    """
    char_count = len(text)
    if char_count == 0:
        return 0.0
    
    # 信息密度 = 外部细节数 / 字数 (归一化到 0-1)
    # 期望：每 100 字包含 1-3 个外部细节
    expected_density = external_details / (char_count / 100.0)
    
    # 归一化：0.5-2.0 倍期望密度 → 1.0，过低或过高 → 降低
    if 0.5 <= expected_density <= 2.0:
        density = 1.0
    elif expected_density < 0.5:
        density = expected_density / 0.5
    else:  # expected_density > 2.0
        density = 1.0 - (expected_density - 2.0) / 3.0
    
    return max(0.0, min(1.0, density))
```

#### 4.2 叙事多样性检测

```python
def calculate_narrative_diversity(text):
    """
    计算叙事多样性：句式/词汇/结构变化
    
    参数:
        text: 叙事文本
    
    返回:
        diversity: float (0-1)
    """
    sentences = text.split('。')
    if len(sentences) < 2:
        return 0.5  # 样本太小，无法评估
    
    # 句式多样性：句子长度标准差
    sentence_lengths = [len(s) for s in sentences if s.strip()]
    length_std = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
    
    # 词汇多样性：独特词比例
    words = text.split()
    unique_words = set(words)
    vocab_diversity = len(unique_words) / len(words) if words else 0
    
    # 综合多样性 (简单加权)
    diversity = 0.5 * (length_std / 50.0) + 0.5 * vocab_diversity
    
    return max(0.0, min(1.0, diversity))
```

#### 4.3 关键词堆砌识别

```python
def detect_keyword_stuffing(text, dimension_keywords):
    """
    检测关键词堆砌
    
    参数:
        text: 叙事文本
        dimension_keywords: dict {dimension: [keywords]}
    
    返回:
        stuffing_detected: bool
        stuffed_dimensions: list[str]
    """
    stuffed_dimensions = []
    
    for dim, keywords in dimension_keywords.items():
        keyword_count = sum(text.count(kw) for kw in keywords)
        # 如果某维度关键词出现频率 > 期望值 3 倍，标记为堆砌
        expected_count = len(text) / 500  # 期望每 500 字出现 1 次
        if keyword_count > expected_count * 3:
            stuffed_dimensions.append(dim)
    
    return len(stuffed_dimensions) > 0, stuffed_dimensions
```

---

### 5. 验证强度控制器 (新增)

**状态**: ⏳ 待实现 (v0.6 核心)  
**职责**: 动态调整 L1 触发阈值，监控性能 - 效度平衡

**配置参数**:
```yaml
validation_controller:
  # L1 触发阈值
  confidence_threshold: 0.6  # 置信度 < 此值 → 触发 L1
  boundary_score_range: [55, 75]  # 评分在此区间 → 触发 L1
  
  # 性能目标
  target_l1_trigger_rate: 0.2  # 目标 20% 样本进入 L1
  target_l0_latency_ms: 100  # L0 延迟 < 100ms
  target_l1_latency_ms: 3000  # L1 延迟 < 3s
  
  # 动态调整
  auto_adjust_threshold: true  # 根据实际触发率动态调整阈值
  adjustment_window: 1000  # 每 1000 样本调整一次
  max_threshold_change: 0.1  # 单次调整最大幅度
```

**动态调整算法**:
```python
def adjust_threshold(current_trigger_rate, target_rate, current_threshold):
    """
    根据实际触发率动态调整 L1 触发阈值
    
    参数:
        current_trigger_rate: 实际 L1 触发率 (0-1)
        target_rate: 目标触发率 (默认 0.2)
        current_threshold: 当前置信度阈值
    
    返回:
        new_threshold: 调整后的阈值
    """
    error = current_trigger_rate - target_rate
    
    # 触发率过高 → 提高阈值 (减少 L1 触发)
    # 触发率过低 → 降低阈值 (增加 L1 触发)
    adjustment = -error * 0.1  # 学习率 0.1
    new_threshold = current_threshold + adjustment
    
    # 限制在 [0.4, 0.8] 区间
    new_threshold = max(0.4, min(0.8, new_threshold))
    
    return new_threshold
```

---

## 性能基准

| 指标 | 目标值 | 测量方式 |
|------|--------|---------|
| L0 延迟 | <100ms | p95 延迟 |
| L1 延迟 | <3s | p95 延迟 |
| L1 触发率 | 20% ± 5% | 滑动窗口 1000 样本 |
| 评分效度 (vs. 人工) | r > 0.75 | Pearson 相关系数 |
| 抗堆砌效度 | 堆砌样本评分下降 >10 分 | 对照实验 |

---

## 实现路线图

| 阶段 | 任务 | 预计工作量 | 依赖 |
|------|------|-----------|------|
| **Phase 1** | L1 LLM 仲裁层基础实现 | 2-3 天 | DASHSCOPE_API_KEY |
| **Phase 2** | 抗 Reward Hacking 模块 | 1-2 天 | Phase 1 完成 |
| **Phase 3** | 验证强度控制器 | 1 天 | Phase 1 完成 |
| **Phase 4** | 端到端测试 + 效度验证 | 2-3 天 | 50 条人工标注数据 |
| **Phase 5** | 性能优化 + 部署 | 1-2 天 | Phase 4 通过 |

**总计**: 7-11 天

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| L1 延迟超标 | 中 | 高 | 异步处理 + 缓存机制 |
| LLM 仲裁不一致 | 中 | 中 | 多次采样 + 一致性检验 |
| 人工标注数据不足 | 高 | 高 | V 协调标注人员 (04-07 前完成) |
| DASHSCOPE_API_KEY 失效 | 低 | 高 | 监控 + 自动告警 + V 快速刷新 |

---

## 验收标准

- [ ] L0 规则引擎 80% 样本 <100ms
- [ ] L1 仲裁层触发率 20% ± 5%
- [ ] 评分效度 r > 0.75 (vs. 50 条人工标注)
- [ ] 堆砌样本评分下降 >10 分
- [ ] 端到端延迟 p95 < 500ms

---

## 附录：与夜间长跑实验的关联

本设计稿承接 `research/2026-04-02-night-long-experiment-integration.md` 的以下建议：

1. **TwinVoice 映射**: Lexical Fidelity + Persona Tone 集成到 L1 仲裁层
2. **AD-CARE 迁移**: 多队列评估设计 → 叙事类型分层校准
3. **Reward Hacking 防御**: 抗堆砌模块设计
4. **Over-Verification 规避**: 验证强度控制器动态调整

---

*设计稿完成 — 2026-04-02 19:30 UTC*

Hulk 🟢 — 密度即价值
