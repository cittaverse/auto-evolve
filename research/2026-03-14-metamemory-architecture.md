# 元记忆 (Metamemory) 策略选择器架构设计

**日期**: 2026-03-14 14:30 UTC  
**阶段**: 阶段 2 - 架构设计  
**执行者**: Hulk 🟢

---

## 1. 背景与目标

### 1.1 研究背景

基于 JMIR mHealth 2026-01《Efficacy and Safety of Mobile App–Based Metamemory Cognitive Training》：
- 元记忆训练可增强 MCI 认知训练效果
- 元认知提示能提升记忆细节 20-30%、记忆信心 1.5-2.0 分

### 1.2 阶段 1 产出

已完成引导问题库 (`config/metamemory_prompts.yaml`)：
- 4 类元认知策略：来源监控 (SM) / 信心评估 (CA) / 策略提示 (SC) / 意义反思 (MR)
- 16 个引导问题 (SM-001~003, CA-001~003, SC-001~004, MR-001~004)

### 1.3 阶段 2 目标

设计元记忆策略选择器，实现：
1. **自动策略选择**: 根据叙事特征自动选择最合适的元认知策略
2. **动态问题生成**: 结合 L0 六维认知特征生成个性化引导问题
3. **与 pipeline_v0.3 集成**: 在神经符号评分后追加元记忆引导
4. **A/B 测试支持**: 记录策略使用与效果，支持后续对照实验

---

## 2. 架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    用户叙事输入 (语音/文本)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: 神经解析 (Neuro Parse) - pipeline_v0.3.py              │
│  - LLM 事件提取                                                   │
│  - 事件图构建 (temporal/causal links)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: 符号评分 (Symbolic Score) - pipeline_v0.3.py           │
│  - Temporal Consistency                                         │
│  - Causal Density                                               │
│  - L0 六维评分 (时间/地点/人物/感官/情感/连贯性)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: 元记忆策略选择器 (Metamemory Strategy Selector) ⭐NEW   │
│  - 输入：事件图 + L0 六维评分 + 连贯性分数                         │
│  - 规则引擎：根据特征匹配策略                                     │
│  - 输出：1-3 个推荐策略 + 对应引导问题                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: 引导问题生成 (Prompt Generator)                        │
│  - 从 YAML 加载问题模板                                           │
│  - 填充叙事具体内容 (事件/人物/地点)                               │
│  - 输出个性化引导问题                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: 效果追踪 (Effect Tracker)                              │
│  - 记录使用的策略 ID                                              │
│  - 记录用户后续回应质量                                           │
│  - 为 A/B 测试积累数据                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 策略选择规则引擎

### 3.1 策略选择矩阵

| L0 维度低分 | 推荐策略 | 理由 |
|-------------|----------|------|
| 时间 (Temporal) < 3 | SM (来源监控) + SC (策略提示) | 帮助定位事件时间线 |
| 地点 (Spatial) < 3 | SM (来源监控) + SC (策略提示) | 帮助回忆场景细节 |
| 人物 (Person) < 3 | SM (来源监控) + MR (意义反思) | 帮助回忆人际互动 |
| 感官 (Sensory) < 3 | SC (策略提示) | 提示感官细节回忆 |
| 情感 (Emotional) < 3 | MR (意义反思) | 引导情感意义探索 |
| 连贯性 (Coherence) < 0.5 | SM + SC 组合 | 帮助建立事件连接 |

### 3.2 规则引擎伪代码

```python
def select_strategies(l0_scores: dict, coherence_score: float) -> List[str]:
    """
    根据 L0 评分和连贯性分数选择元记忆策略
    """
    strategies = []
    
    # 规则 1: 时间维度低分 → 来源监控 + 策略提示
    if l0_scores.get('temporal', 5) < 3:
        strategies.append('SM')  # 来源监控
        strategies.append('SC')  # 策略提示
    
    # 规则 2: 地点维度低分 → 来源监控 + 策略提示
    if l0_scores.get('spatial', 5) < 3:
        if 'SM' not in strategies:
            strategies.append('SM')
        if 'SC' not in strategies:
            strategies.append('SC')
    
    # 规则 3: 人物维度低分 → 来源监控 + 意义反思
    if l0_scores.get('person', 5) < 3:
        if 'SM' not in strategies:
            strategies.append('SM')
        if 'MR' not in strategies:
            strategies.append('MR')
    
    # 规则 4: 感官维度低分 → 策略提示
    if l0_scores.get('sensory', 5) < 3:
        if 'SC' not in strategies:
            strategies.append('SC')
    
    # 规则 5: 情感维度低分 → 意义反思
    if l0_scores.get('emotional', 5) < 3:
        if 'MR' not in strategies:
            strategies.append('MR')
    
    # 规则 6: 连贯性极低 → 组合策略
    if coherence_score < 0.5:
        if len(strategies) < 2:
            strategies.append('SM')
            strategies.append('SC')
    
    # 规则 7: 信心评估 (CA) 在所有叙事后都使用
    strategies.append('CA')
    
    # 去重并限制最多 3 个策略
    unique_strategies = list(dict.fromkeys(strategies))[:3]
    
    return unique_strategies
```

---

## 4. 引导问题生成器

### 4.1 问题模板填充

**输入**:
- 策略 ID 列表：['SM', 'SC', 'CA']
- 事件图：`{"events": [{"id": "e1", "description": "...", "estimated_time": "..."}]}`
- L0 评分：`{"temporal": 2, "spatial": 4, ...}`

**处理**:
1. 从 `config/metamemory_prompts.yaml` 加载对应策略的问题模板
2. 用事件图中的具体内容填充占位符
3. 根据 L0 低分维度优先选择针对性问题

**输出**:
```markdown
## 元记忆引导问题

### 来源监控 (SM)
- SM-001: 您提到"老面包店"，您能回忆起那是哪一年吗？当时您多大？
- SM-002: 这个记忆是您亲身经历的吗？还是听别人说的？

### 策略提示 (SC)
- SC-001: 试着回忆当时的场景：您看到了什么颜色？听到了什么声音？闻到了什么气味？
- SC-002: 如果您闭上眼睛，能想象出那个面包店的样子吗？

### 信心评估 (CA)
- CA-001: 您对这个记忆的清晰程度打几分？(1-10 分)
- CA-002: 您觉得这个记忆的细节准确吗？有没有不确定的地方？
```

---

## 5. 与 pipeline_v0.3 集成方案

### 5.1 代码结构

```
PROTOTYPES/narrative_scorer/
├── pipeline_v0.3.py              # 原有神经符号管道
├── pipeline_v0.4_metamemory.py   # 新增：集成元记忆的版本
├── metamemory_selector.py        # 新增：策略选择器
├── prompt_generator.py           # 新增：引导问题生成器
└── effect_tracker.py             # 新增：效果追踪器
```

### 5.2 pipeline_v0.4 主流程

```python
def pipeline_v0_4(transcript: str) -> dict:
    # Step 1-2: 原有神经符号评分
    graph = neuro_parse(transcript)
    scores = symbolic_score(graph)
    l0_scores = l0_quality_score(transcript)  # L0 六维评分
    
    # Step 3: 元记忆策略选择 (新增)
    strategies = select_strategies(l0_scores, scores['total_score'])
    
    # Step 4: 引导问题生成 (新增)
    prompts = generate_prompts(strategies, graph, l0_scores)
    
    # Step 5: 效果追踪初始化 (新增)
    session_id = log_strategy_usage(strategies, scores, l0_scores)
    
    return {
        'graph': graph,
        'scores': scores,
        'l0_scores': l0_scores,
        'strategies': strategies,
        'prompts': prompts,
        'session_id': session_id
    }
```

---

## 6. A/B 测试设计

### 6.1 实验组设计

| 组别 | 策略 | 样本量 | 预期效果 |
|------|------|--------|----------|
| A 组 (对照) | 无元记忆引导 | 50 人 | 基线 |
| B 组 | 固定策略 (SM+SC) | 50 人 | 细节提升 15-20% |
| C 组 | 动态策略选择 | 50 人 | 细节提升 20-30% |

### 6.2 评估指标

| 指标 | 测量方式 | 预期提升 |
|------|----------|----------|
| 叙事细节数量 | 事件计数 | +20-30% |
| L0 感官维度评分 | 自动评分 | +1.5-2.0 分 |
| L0 时间维度评分 | 自动评分 | +1.0-1.5 分 |
| 用户记忆信心 | CA 问题自评 | +1.5-2.0 分 |
| 会话时长 | 系统记录 | +10-20% |

### 6.3 数据追踪 schema

```json
{
  "session_id": "uuid",
  "timestamp": "ISO8601",
  "user_id": "anonymized",
  "group": "A|B|C",
  "strategies_used": ["SM", "SC", "CA"],
  "pre_scores": {"temporal": 2, "spatial": 4, ...},
  "post_scores": {"temporal": 3, "spatial": 5, ...},
  "prompt_ids": ["SM-001", "SC-001", "CA-001"],
  "user_response_quality": 0.85,
  "session_duration_sec": 420
}
```

---

## 7. 实施计划

### 7.1 阶段 2 时间表

| 任务 | 开始日期 | 结束日期 | 状态 |
|------|----------|----------|------|
| 架构设计 (本文档) | 2026-03-14 | 2026-03-14 | ✅ 完成 |
| 策略选择器实现 | 2026-03-15 | 2026-03-16 | 📋 待执行 |
| 引导问题生成器实现 | 2026-03-16 | 2026-03-17 | 📋 待执行 |
| pipeline_v0.4 集成 | 2026-03-17 | 2026-03-18 | 📋 待执行 |
| Mock 测试 | 2026-03-18 | 2026-03-19 | 📋 待执行 |

### 7.2 依赖项

| 依赖 | 状态 | 备注 |
|------|------|------|
| DASHSCOPE_API_KEY | ❌ 缺失 | L0 真实测试阻塞 |
| 阶段 1 引导问题库 | ✅ 完成 | config/metamemory_prompts.yaml |
| pipeline_v0.3 代码 | ✅ 可用 | PROTOTYPES/narrative_scorer/ |
| L0 质检系统 | ✅ 阶段 1 完成 | 待 API Key 配置后真实测试 |

---

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| API Key 持续缺失 | 无法真实测试 | 先用 Mock 数据验证逻辑 |
| 策略选择规则过于简单 | 推荐不准确 | 迭代优化规则，收集用户反馈 |
| 引导问题过于机械 | 用户体验差 | 加入自然语言润色，人工抽检 |
| A/B 测试样本量不足 | 统计效力低 | 延长测试周期或与学术合作联合招募 |

---

## 9. 下一步行动

### 立即执行 (不依赖 API)
1. ✅ 架构设计完成 (本文档)
2. 📋 创建 `metamemory_selector.py` 骨架代码
3. 📋 创建 `prompt_generator.py` 骨架代码
4. 📋 阅读 `config/metamemory_prompts.yaml` 确认问题模板格式

### 等待 API Key 后执行
1. ⏳ 实现完整策略选择逻辑
2. ⏳ 实现引导问题生成器
3. ⏳ pipeline_v0.4 集成测试
4. ⏳ Mock 测试 → 真实测试

---

## 10. 参考文献

1. **JMIR mHealth 2026-01**: Efficacy and Safety of Mobile App–Based Metamemory Cognitive Training
2. **MEMORY.md Section VIII**: 元记忆 (Metamemory) 整合机会
3. **config/metamemory_prompts.yaml**: 阶段 1 引导问题库
4. **PROTOTYPES/narrative_scorer/pipeline_v0.3.py**: 现有神经符号管道

---

*Architecture Design Complete. Ready for implementation (phase 2).*
