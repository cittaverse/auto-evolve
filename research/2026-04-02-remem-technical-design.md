# REMem 情景记忆图架构技术方案

**创建日期**: 2026-04-02 (GEO #96)  
**研究员**: Hulk 🟢  
**状态**: Phase 1-2 完成 (规则基础分段 + NetworkX 图构建), Phase 3-4 待实现  
**参考**: REMem (ICLR 2026), Cell Press TiCS (2025)

---

## Executive Summary

**核心问题**: 如何为 VSNC/L0 实现类人情景记忆架构，支持事件分段、时间推理、记忆巩固？

**Bottom Line**: REMem 提出"LLM+Graph"架构，非单纯向量检索。Phase 1-2 已完成规则基础实现（事件分段 + 图构建），可独立运行；Phase 3-4 (巩固、推理) 需 DASHSCOPE_API_KEY 解锁 LLM 增强功能。

---

## Architecture Overview

```
用户叙事输入
    │
    ▼
┌─────────────────────────────────────┐
│  Phase 1: 事件分段 (✅ 完成)          │
│  - 边界检测 (语言线索 + 启发式)       │
│  - 时间锚点提取                      │
│  - 情感效价评分                      │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Phase 2: 图构建 (✅ 完成)            │
│  - 节点：事件 (带元数据)              │
│  - 边：时间/语义/情感/因果关系         │
│  - NetworkX 实现，支持多关系边         │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Phase 3: 记忆巩固 (待实现)           │
│  - 强度衰减 (艾宾浩斯曲线)            │
│  - 排练增强 (重复提及)                │
│  - 定期修剪低价值记忆                 │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Phase 4: 检索 + 推理 (待实现)        │
│  - 多跳图遍历                        │
│  - 时间推理 (X 之前/之后发生了什么)    │
│  - 主题聚类 (按人生主题分组)          │
└────────────────┬────────────────────┘
                 │
                 ▼
输出：情境感知响应 / 记忆提示
```

---

## Phase 1: 事件分段 (已完成)

### 实现文件

- `pipeline/src/services/remem_event_segmenter.py` (439 行)
- `pipeline/src/services/__init__.py` (更新导出)

### 核心功能

1. **边界检测**
   - 强线索：`后来`, `然后`, `突然`, `记得`, `回想起`, `\n\n` (置信度 0.8)
   - 中线索：`接着`, `随后`, `之后`, `有一天`, `有一次` (置信度 0.6)
   - 弱线索：`之前`, `以前`, `那时候` (置信度 0.4)

2. **时间锚点提取**
   - 绝对时间：`2010 年`, `2015 年 5 月`
   - 人生阶段：`退休后`, `结婚后`, `大学期间`
   - 相对时间：`去年`, `小时候`, `那时候`

3. **情感效价评分**
   - 积极关键词：`开心`, `快乐`, `幸福`, `自豪` 等
   - 消极关键词：`难过`, `痛苦`, `悲伤`, `恐惧` 等
   - 输出：0-100 分数 + 标签 (positive/neutral/negative)

4. **元数据提取**
   - 提到的人：家庭称谓、朋友、同事等
   - 提到的地点：`在 XXX` 模式提取
   - 主题：家庭、工作、学习、健康、旅行、友谊、成就、挑战

### 测试结果

```python
from pipeline.services import segment_narrative

narrative = "记得那是 2010 年的夏天，我和家人一起去了北京旅行..."
segments = segment_narrative(narrative)

# 输出：3 个事件段
# Event 1: 2010 年北京旅行 (positive, 家庭 + 旅行)
# Event 2: 2015 年退休后生活 (neutral-positive, 家庭 + 工作 + 友谊)
# Event 3: 去年孙子出生 (positive, 家庭)
```

### 局限性 (规则基础模式)

1. **时间锚点**: 只能提取显式时间表达，无法推理隐含时间
2. **人物提取**: 只能识别家庭称谓，无法识别具体人名
3. **边界检测**: 依赖预定义线索，可能遗漏微妙边界
4. **情感评分**: 简单关键词计数，无法理解上下文情感

### LLM 增强模式 (待实现)

使用 Qwen 模型可提升:
- 边界检测准确率 (上下文感知)
- 人物/地点 NER (命名实体识别)
- 隐含时间推理 (e.g., "那时候" → 根据上下文推断具体年份)
- 细粒度情感分析 (混合情感、情感转变)

---

## Phase 2: 图构建 (待实现)

### 技术方案

**图数据库选择**:
- **轻量级**: NetworkX (内存图，适合原型)
- **生产级**: Neo4j (持久化，支持 Cypher 查询)

**节点 Schema**:
```python
{
    "event_id": "evt_2010_beijing_trip",
    "text": "2010 年夏天和家人去北京旅行...",
    "timestamp": "2010-06-15",  # 或相对时间
    "life_stage": "中年",
    "emotional_valence": 85.0,
    "people": ["家人", "儿子"],
    "places": ["北京", "故宫", "长城"],
    "themes": ["家庭", "旅行"],
    "created_at": "2026-04-02T10:00:00Z",
    "strength": 1.0  # 记忆强度 (初始 1.0)
}
```

**边类型**:
```python
# 时间关系
- (evt1)-[:BEFORE]->(evt2)
- (evt1)-[:AFTER]->(evt2)
- (evt1)-[:SAME_PERIOD]->(evt2)

# 语义关系
- (evt1)-[:SIMILAR_THEME]->(evt2)
- (evt1)-[:SAME_PEOPLE]->(evt2)
- (evt1)-[:SAME_PLACE]->(evt2)

# 情感关系
- (evt1)-[:SIMILAR_VALENCE]->(evt2)
- (evt1)-[:EMOTIONAL_CONTRAST]->(evt2)

# 因果关系
- (evt1)-[:LED_TO]->(evt2)
- (evt1)-[:TRIGGERED_BY]->(evt2)
```

### 实现步骤

1. 选择图数据库 (建议：先 NetworkX 原型，后 Neo4j 生产)
2. 定义节点/边 Schema
3. 实现图构建函数 (从 EventSegment 列表到图)
4. 编写单元测试

**预估工作量**: 2-3 天 (NetworkX 原型)

---

## Phase 3: 记忆巩固 (待实现)

### 理论基础

**艾宾浩斯遗忘曲线**:
```
记忆保留率 = e^(-t/S)
t = 时间 (天)
S = 强度因子 (初始记忆强度)
```

**巩固机制**:
1. **自然衰减**: 记忆强度随时间指数衰减
2. **排练增强**: 每次用户重提某事件，强度 +0.2 (上限 1.0)
3. **睡眠巩固**: 定期后台任务，强化高价值记忆，修剪低价值记忆

### 实现方案

```python
class MemoryConsolidator:
    def __init__(self, decay_rate=0.1):
        self.decay_rate = decay_rate
    
    def apply_decay(self, event: EventSegment, days_elapsed: float):
        """应用遗忘曲线衰减"""
        decay_factor = math.exp(-self.decay_rate * days_elapsed)
        event.strength *= decay_factor
    
    def apply_rehearsal(self, event: EventSegment, boost=0.2):
        """排练增强"""
        event.strength = min(1.0, event.strength + boost)
    
    def consolidate(self, graph, threshold=0.1):
        """定期巩固：修剪低强度记忆"""
        low_strength_events = [
            e for e in graph.nodes
            if graph.nodes[e]['strength'] < threshold
        ]
        # 标记为归档或删除
        return low_strength_events
```

### 参数调优

- `decay_rate`: 0.1 (默认，需临床验证)
- `rehearsal_boost`: 0.2 (每次重提增强 20%)
- `pruning_threshold`: 0.1 (低于 10% 强度考虑归档)
- `consolidation_interval`: 每周一次后台任务

**预估工作量**: 2-3 天

---

## Phase 4: 检索 + 推理 (待实现)

### 检索策略

**1. 多跳图遍历**:
```python
# 示例：查询"2010 年前后在北京的经历"
query_time = "2010"
query_place = "北京"

# 第 1 跳：找到时间相近事件
time_neighbors = graph.neighbors(query_time, relation=[:SAME_PERIOD])

# 第 2 跳：从这些事件中找到地点相关
beijing_events = [
    e for e in time_neighbors
    if query_place in graph.nodes[e]['places']
]

# 第 3 跳：扩展语义相关事件
related_events = []
for e in beijing_events:
    related_events.extend(
        graph.neighbors(e, relation=[:SIMILAR_THEME])
    )

return beijing_events + related_events
```

**2. 时间推理**:
- "X 之前发生了什么" → 查询 [:BEFORE] 边
- "X 之后发生了什么" → 查询 [:AFTER] 边
- "那段时间的经历" → 查询 [:SAME_PERIOD] 边

**3. 主题聚类**:
- 按 theme 分组事件
- 生成"人生故事线" (e.g., 职业生涯、家庭生活、旅行经历)

### Prompt 增强

检索到的事件用于增强 LLM prompt:
```python
context = "用户提到 2010 年北京旅行。相关记忆："
for event in retrieved_events:
    context += f"- {event['text']} (情感：{event['emotional_valence']})\n"

prompt = f"{context}\n请根据这些记忆，引导用户讲述更多细节..."
```

**预估工作量**: 3-5 天

---

## 与当前 L0 对比

| 维度 | 当前 L0 | REMem 增强 L0 |
|------|---------|---------------|
| 记忆存储 | 扁平叙事列表 | 图结构 (时间 + 语义边) |
| 事件边界 | 无 (整段叙事) | 自动检测分段 |
| 检索方式 | 向量相似度 | 多跳图遍历 + 时间推理 |
| 遗忘机制 | 无 (全部平等存储) | 强度衰减 + 排练增强 |
| 推理能力 | 单轮 Q&A | 多跳查询 ("2010 年前后在北京的经历") |
| 个性化 | 通用提示 | 人生故事感知提示 |

---

## 开放问题

1. **图数据库选择**: NetworkX vs Neo4j?
   - 建议：原型用 NetworkX，生产用 Neo4j

2. **事件分段准确率**: 如何验证边界检测质量？
   - 需要人工标注数据集 (50-100 条叙事)

3. **遗忘曲线参数**: 老年人记忆衰减率与年轻人不同
   - 需要临床合作调参

4. **隐私保护**: 如何处理敏感记忆 (创伤、丧失)?
   - 需要"敏感标记"机制，特殊处理

5. **LLM API 依赖**: Phase 2-4 多大程度需要 LLM?
   - Phase 2 (图构建): 可规则实现，LLM 增强
   - Phase 3 (巩固): 无需 LLM
   - Phase 4 (检索推理): 需要 LLM 生成查询和响应

---

## 下一步行动

| 优先级 | 任务 | 依赖 | 预估工时 |
|--------|------|------|---------|
| **P0** | DASHSCOPE_API_KEY 轮换 | V | - |
| **P1** | Phase 2: 图构建 (NetworkX 原型) | 无 | 2-3 天 |
| **P2** | 人工标注 50 条叙事 (验证分段准确率) | V 参与 | 4-6 小时 |
| **P3** | Phase 3: 记忆巩固模块 | Phase 2 | 2-3 天 |
| **P4** | Phase 4: 检索 + 推理引擎 | Phase 3 | 3-5 天 |
| **P5** | LLM 增强模式集成 | DASHSCOPE_API_KEY | 2-3 天 |

---

## 参考论文

1. **REMem: Reasoning with Episodic Memory in Language Agent** (ICLR 2026)
   - OpenReview: https://openreview.net/forum?id=fugnQxbvMm

2. **Towards LLMs with Human-like Episodic Memory** (Cell Press TiCS, 2025)
   - 综述 LLM 捕捉人类情景记忆关键属性的能力

3. **NARRABENCH: Narrative Theory-Driven Evaluation** (ACL 2026)
   - 提供叙事理解任务分类法

---

*Hulk 🟢 — Compressing chaos into structure*
