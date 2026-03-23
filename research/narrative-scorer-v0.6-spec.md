# Narrative Scorer v0.6 功能规划

**版本**: v0.6 (规划稿)  
**日期**: 2026-03-23  
**状态**: 设计中  
**前置版本**: v0.5 (6 维度 + 动态理想比例 + 情绪唤醒度)  
**验证等级**: V0（规划阶段，需技术评审后实现）

---

## 一、v0.6 核心目标

在 v0.5 基础上增加三层能力：

1. **LLM 增强仲裁层** — 处理边界案例，提升评分准确性
2. **多方言支持** — 粤语、吴语词表扩展
3. **向后兼容** — v0.5 输出格式不变，v0.6 增加可选字段

**设计原则**：
- 保持零依赖核心（LLM 为可选增强）
- 保持离线可用（LLM 增强需显式启用）
- 保持可解释性（LLM 评分需提供 reasoning）

---

## 二、LLM 增强评分方案设计

### 2.1 架构概述

```
┌─────────────────────────────────────────────────────────┐
│                    Input Text (中文)                      │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Rule-Based Scorer (v0.5 核心)                │
│  - 6 维度基础评分                                         │
│  - 情绪唤醒度检测                                         │
│  - 动态理想比例计算                                       │
│  - 输出：scores_v0.5 (7 维度 + 置信度)                     │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ 置信度检查点   │
                    │ if conf < 0.7 │
                    └───────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
     ┌─────────────────┐         ┌─────────────────┐
     │ 高置信度案例     │         │ 低置信度案例     │
     │ 直接输出 v0.5    │         │ 触发 LLM 仲裁     │
     │ (无需 LLM)       │         │ (可选增强)       │
     └─────────────────┘         └─────────────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │  LLM Scorer     │
                                 │  (DashScope/    │
                                 │   GPT-4o-mini)  │
                                 └─────────────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │  仲裁逻辑        │
                                 │  - 对比 v0.5     │
                                 │  - 加权融合      │
                                 │  - 生成 reasoning│
                                 └─────────────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │  scores_v0.6    │
                                 │  (含 llm_enhanced│
                                 │   字段)          │
                                 └─────────────────┘
```

### 2.2 触发条件

LLM 仲裁层仅在以下情况触发（可配置）：

| 触发条件 | 默认阈值 | 说明 |
|----------|----------|------|
| 整体置信度 | < 0.70 | v0.5 综合置信度低于阈值 |
| 维度分歧 | > 1.5 分 | 任意两个维度评分差异过大（可能表示叙事异常） |
| 文本长度 | < 50 字 或 > 3000 字 | 过短或过长，规则可能失效 |
| 情绪唤醒度 | = 5 (极高) | 极高情绪下规则可能低估情感深度 |
| 方言标记 | 检测到粤语/吴语特征 | v0.5 普通话词表可能不适用 |
| 显式请求 | `use_llm=true` | 用户强制启用 LLM 增强 |

### 2.3 LLM Prompt 设计

**系统 Prompt**:
```
你是一位叙事心理学专家，擅长评估中文自传体记忆的质量。
请根据以下 7 个维度对叙事进行评分（1-5 分），并提供简要理由。

评分维度：
1. Event Richness (事件丰富度) - 叙述中包含多少独立事件
2. Temporal Coherence (时间连贯性) - 时间线是否清晰
3. Causal Coherence (因果连贯性) - 事件间因果逻辑
4. Emotional Depth (情感深度) - 情感表达深度
5. Identity Integration (身份整合) - 与自我身份的关联
6. Information Density (信息密度) - 信息分布是否均匀
7. Emotional Arousal (情绪唤醒度) - 情绪强度和激活水平

输出格式（JSON）：
{
  "scores": {
    "event_richness": {"score": 3, "reason": "..."},
    "temporal_coherence": {"score": 4, "reason": "..."},
    "causal_coherence": {"score": 3, "reason": "..."},
    "emotional_depth": {"score": 4, "reason": "..."},
    "identity_integration": {"score": 3, "reason": "..."},
    "information_density": {"score": 3, "reason": "..."},
    "emotional_arousal": {"score": 2, "reason": "..."}
  },
  "overall_confidence": 0.85,
  "flags": ["边界案例说明"]
}
```

**用户 Prompt**:
```
请评估以下叙事：

"""
{input_text}
"""

v0.5 规则评分结果（供参考）：
{v0.5_scores_json}

请独立评分，然后对比规则评分。如果差异较大（>1 分），请说明原因。
```

### 2.4 仲裁融合策略

当 LLM 评分与 v0.5 规则评分存在差异时：

```python
def fuse_scores(v05_scores, llm_scores, v05_confidence, llm_confidence):
    """
    加权融合策略：
    - 高置信度 v0.5 (conf > 0.85): v0.5 权重 0.7, LLM 权重 0.3
    - 中置信度 v0.5 (0.70-0.85): v0.5 权重 0.5, LLM 权重 0.5
    - 低置信度 v0.5 (< 0.70): v0.5 权重 0.3, LLM 权重 0.7
    """
    if v05_confidence > 0.85:
        v05_weight = 0.7
    elif v05_confidence > 0.70:
        v05_weight = 0.5
    else:
        v05_weight = 0.3
    
    llm_weight = 1.0 - v05_weight
    
    fused = {}
    for dim in SCORE_DIMS:
        v05_score = v05_scores[dim]
        llm_score = llm_scores[dim]['score']
        fused[dim] = v05_score * v05_weight + llm_score * llm_weight
    
    return fused
```

### 2.5 支持的后端

| 后端 | 模型 | 成本 | 延迟 | 推荐场景 |
|------|------|------|------|----------|
| DashScope | qwen-plus | ¥0.004/1K tokens | ~1s | 默认推荐，中文优化 |
| DashScope | qwen-turbo | ¥0.002/1K tokens | ~500ms | 低成本场景 |
| OpenAI | GPT-4o-mini | $0.15/1M tokens | ~1s | 已有 OpenAI 配额 |
| Local | Qwen2.5-7B-Instruct | 免费 | ~3s (CPU) | 完全离线需求 |

**默认配置**: DashScope qwen-plus（需 `DASHSCOPE_API_KEY`）

### 2.6 输出格式（v0.6）

```json
{
  "version": "0.6.0",
  "text_length": 342,
  "processing_time_ms": 1250,
  
  "scores_v05": {
    "event_richness": 3.5,
    "temporal_coherence": 4.0,
    "causal_coherence": 3.0,
    "emotional_depth": 3.5,
    "identity_integration": 3.0,
    "information_density": 3.5,
    "emotional_arousal": 2.5,
    "overall_confidence": 0.68
  },
  
  "llm_enhanced": {
    "enabled": true,
    "trigger_reason": "low_confidence",
    "backend": "dashscope/qwen-plus",
    "scores": {
      "event_richness": {"score": 4.0, "reason": "叙述包含 3 个独立事件..."},
      "temporal_coherence": {"score": 4.0, "reason": "时间标记清晰..."},
      "causal_coherence": {"score": 3.5, "reason": "因果关系基本明确..."},
      "emotional_depth": {"score": 4.0, "reason": "情感表达丰富..."},
      "identity_integration": {"score": 3.5, "reason": "有自我反思..."},
      "information_density": {"score": 3.5, "reason": "信息分布均匀..."},
      "emotional_arousal": {"score": 3.0, "reason": "中等情绪强度..."}
    },
    "overall_confidence": 0.85,
    "cost_tokens": {"prompt": 450, "completion": 320, "total": 770}
  },
  
  "scores_final": {
    "event_richness": 3.85,
    "temporal_coherence": 4.0,
    "causal_coherence": 3.35,
    "emotional_depth": 3.85,
    "identity_integration": 3.35,
    "information_density": 3.5,
    "emotional_arousal": 2.85,
    "overall_confidence": 0.80
  },
  
  "flags": [],
  "recommendations": ["叙事质量良好，建议继续练习"]
}
```

---

## 三、多方言支持路线图

### 3.1 方言挑战

| 方言 | 使用人口 | 主要挑战 | 优先级 |
|------|----------|----------|--------|
| 粤语 | ~8000 万 | 时间词/因果词差异大，书面语 vs 口语分离 | 高 |
| 吴语（上海话/苏州话） | ~8000 万 | 时间表达独特（"今朝/明朝/后朝"） | 高 |
| 闽南语 | ~5000 万 | 语法结构差异大，书面化程度低 | 中 |
| 客家话 | ~4500 万 | 词汇差异，研究数据少 | 低 |
| 西南官话（四川话等） | ~1 亿 | 与普通话接近，词表扩展即可 | 低 |

### 3.2 v0.6 方言支持范围

**粤语支持** (完整):
- 时间词表扩展：100+ 粤语特有时间词
  - 而家（现在）、听日（明天）、琴日（昨天）、前日（前天）
  - 早朝（早上）、晏昼（中午）、夜晚（晚上）
  - 寻晚（昨晚）、第日（改天）、依家（现在）
- 因果连接词：20+ 粤语特有
  - 皆因、所以话、至会、先至
- 情感词：200+ 粤语特有
  - 开心、唔开心、惊、嬲、挂住、心翳
- 语法模式识别：
  - 粤语否定结构（唔 X、未 X）
  - 粤语疑问结构（X 唔 X、X 吗）

**吴语支持** (基础):
- 时间词表扩展：50+ 吴语特有
  - 今朝（今天）、明朝（明天）、后朝（后天）
  - 早浪向（早上）、夜快（傍晚）
- 因果连接词：10+ 吴语特有
- 情感词：100+ 吴语特有

**其他方言** (规划中):
- v0.7: 闽南语支持
- v0.8: 客家话支持
- v0.9: 西南官话优化

### 3.3 方言检测与自动切换

```python
def detect_dialect(text: str) -> Tuple[str, float]:
    """
    检测文本方言，返回 (dialect, confidence)
    
    策略：
    1. 关键词匹配（粤语/吴语特有词）
    2. 语法模式匹配（粤语否定/疑问结构）
    3. 字符特征（粤语字：咗、佢、哋、唔、喺）
    """
    cantonese_chars = ['咗', '佢', '哋', '唔', '喺', '啲', '嘅', '咁', '点', '係']
    wu_chars = ['阿拉', '侬', '伊', '伐', '啥', '结棍']
    
    cantonese_score = sum(1 for c in cantonese_chars if c in text)
    wu_score = sum(1 for w in wu_chars if w in text)
    
    if cantonese_score >= 3:
        return ('cantonese', min(0.95, 0.5 + cantonese_score * 0.1))
    elif wu_score >= 2:
        return ('wu', min(0.90, 0.5 + wu_score * 0.15))
    else:
        return ('mandarin', 0.80)


def get_scorer_config(dialect: str) -> Dict:
    """根据方言加载对应词表和规则"""
    configs = {
        'mandarin': {
            'time_lexicon': 'lexicons/time_mandarin.json',
            'causal_lexicon': 'lexicons/causal_mandarin.json',
            'emotion_lexicon': 'lexicons/emotion_mandarin.json',
        },
        'cantonese': {
            'time_lexicon': 'lexicons/time_cantonese.json',
            'causal_lexicon': 'lexicons/causal_cantonese.json',
            'emotion_lexicon': 'lexicons/emotion_cantonese.json',
            'grammar_patterns': 'patterns/cantonese_grammar.json',
        },
        'wu': {
            'time_lexicon': 'lexicons/time_wu.json',
            'causal_lexicon': 'lexicons/causal_wu.json',
            'emotion_lexicon': 'lexicons/emotion_wu.json',
        },
    }
    return configs.get(dialect, configs['mandarin'])
```

### 3.4 词表文件格式

```json
// lexicons/time_cantonese.json
{
  "name": "粤语时间词表",
  "version": "0.6.0",
  "entries": [
    {
      "word": "而家",
      "normalized": "现在",
      "temporal_type": "present",
      "offset_minutes": 0
    },
    {
      "word": "听日",
      "normalized": "明天",
      "temporal_type": "future",
      "offset_days": 1
    },
    {
      "word": "琴日",
      "normalized": "昨天",
      "temporal_type": "past",
      "offset_days": -1
    }
  ]
}
```

---

## 四、与 v0.5 的兼容性设计

### 4.1 API 向后兼容

```python
# v0.5 调用方式（保持不变）
from narrative_scorer import score

result = score(text)
# 返回：Dict with scores (7 dimensions)

# v0.6 新增可选参数
result = score(
    text,
    use_llm=False,          # 默认 False，保持 v0.5 行为
    llm_backend='auto',     # 'auto' | 'dashscope' | 'openai' | 'local'
    dialect='auto',         # 'auto' | 'mandarin' | 'cantonese' | 'wu'
    return_reasoning=False, # 是否返回 LLM reasoning
)
```

### 4.2 输出字段兼容

| 字段 | v0.5 | v0.6 (use_llm=False) | v0.6 (use_llm=True) |
|------|------|----------------------|---------------------|
| version | "0.5.0" | "0.6.0" | "0.6.0" |
| scores | ✅ 7 维度 | ✅ 7 维度 | ✅ 7 维度 (final) |
| overall_confidence | ✅ | ✅ | ✅ |
| scores_v05 | ❌ | ❌ | ✅ (原始规则评分) |
| llm_enhanced | ❌ | ❌ | ✅ (LLM 评分 + reasoning) |
| scores_final | ❌ | ❌ | ✅ (融合后评分) |
| flags | ✅ | ✅ | ✅ |
| recommendations | ✅ | ✅ | ✅ |

**迁移策略**:
- 现有代码无需修改，`score(text)` 返回结构兼容
- 需要 LLM 增强的用户显式启用 `use_llm=True`
- v0.5 用户升级到 v0.6 后，默认行为不变

### 4.3 配置迁移

```yaml
# v0.5 config.yaml
scorer:
  version: "0.5"
  dimensions: 7
  language: "zh"

# v0.6 config.yaml (向后兼容)
scorer:
  version: "0.6"
  dimensions: 7
  language: "zh"
  
  # 新增配置（可选）
  llm:
    enabled: false          # 默认关闭，保持 v0.5 行为
    backend: "dashscope"
    model: "qwen-plus"
    trigger_confidence: 0.70
    api_key_env: "DASHSCOPE_API_KEY"
  
  dialect:
    auto_detect: true
    supported: ["mandarin", "cantonese", "wu"]
    default: "mandarin"
```

---

## 五、实现计划

### Phase 1: LLM 增强核心 (1-2 周)
- [ ] 设计 LLM prompt 模板
- [ ] 实现 DashScope 后端集成
- [ ] 实现仲裁融合逻辑
- [ ] 添加置信度触发机制
- [ ] 单元测试 + 集成测试

### Phase 2: 方言支持 (2-3 周)
- [ ] 粤语词表构建（300+ 条目）
- [ ] 吴语词表构建（150+ 条目）
- [ ] 方言检测算法
- [ ] 自动词表切换逻辑
- [ ] 方言测试集构建

### Phase 3: 性能优化 (1 周)
- [ ] LLM 调用缓存（相同文本不重复调用）
- [ ] 批量评分支持
- [ ] 异步评分 API
- [ ] 成本追踪与限额

### Phase 4: 文档与发布 (3-5 天)
- [ ] API 文档更新
- [ ] 方言使用指南
- [ ] LLM 增强最佳实践
- [ ] v0.5 → v0.6 迁移指南
- [ ] GitHub Release + arXiv 更新

---

## 六、风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| LLM API 成本高 | 中 | 中 | 默认关闭 + 缓存 + 仅边界案例触发 |
| 方言词表覆盖不足 | 中 | 高 | 社区贡献机制 + 持续迭代 |
| LLM 评分与规则冲突 | 低 | 中 | 加权融合 + 显式 flags 标注 |
| 延迟增加 | 中 | 高 | 异步支持 + 超时降级（LLM 失败回退 v0.5） |
| DASHSCOPE_API_KEY 缺失 | 高 | 已知阻塞 | 文档明确标注 + 提供 OpenAI/Local 备选 |

---

## 七、成功指标

| 指标 | v0.5 基线 | v0.6 目标 | 测量方式 |
|------|----------|----------|----------|
| 评分准确性（vs 人工） | r = 0.75 | r = 0.82 | 与 3 名编码员对比 |
| 边界案例处理 | 60% 准确 | 80% 准确 | 低置信度样本子集 |
| 方言覆盖率 | 普通话 only | 粤语 80% / 吴语 60% | 方言测试集 |
| 平均延迟 | <100ms | <200ms (LLM off) / <1500ms (LLM on) | 基准测试 |
| 用户满意度 | N/A | >4.0/5.0 | 试点用户反馈 |

---

## 八、与 Midas 商业化的关联

**v0.6 对商业化的价值**:

1. **LLM 增强** → 支持高端产品线（豪华版传记使用 LLM 增强评分）
2. **方言支持** → 扩大市场覆盖（粤语区/吴语区老年人）
3. **成本可控** → 默认规则评分保持零 API 成本，LLM 仅用于高价值场景

**定价策略影响**:
- 基础版（2999 RMB）：v0.5 规则评分，零 LLM 成本
- 豪华版（5999 RMB）：v0.6 LLM 增强评分 + 方言支持

---

*文档创建*: GEO #59 (2026-03-23 04:15 UTC)  
*状态*: 规划稿，需技术评审后进入实现  
*验证等级*: V0（设计推导，需实现后验证）  
*下一步*: 与 Core 讨论实现优先级，确认 DASHSCOPE_API_KEY 状态
