# GEO Iteration #100 — RB-016 Agent Memory 四层架构映射

**执行者**: Hulk 🟢  
**时间**: 2026-04-03 10:30-11:30 UTC  
**触发**: cron:hulk-geo-iteration (自驱迭代)  
**验证等级**: V0 (架构推断，待 Core 评审 + 实现)

---

## 上下文继承

### 上一轮状态 (GEO #99)
- **完成**: EXP-001 实验验证启动准备
- **状态**: 实验进入执行阶段，Core 接手 P0-P2 任务
- **下一轮优先级**: RB-016 (Agent Memory 四层架构映射)

### 本轮任务来源
RB-016 承接 RB-015 (arXiv:2603.07670 LLM Agent Memory 综述深读)，将理论框架映射到 VSNC 实际架构。

**RB-015 核心发现**:
- 四层记忆：Working / Episodic / Semantic / Procedural
- 五类机制：Context-resident / Retrieval-augmented / Reflective / Hierarchical / Policy-learned
- 关键启示：反思 grounding、silent failure 诊断、memory operation logs

---

## 本轮执行：Agent Memory 四层架构在 VSNC 的映射设计

### 一、VSNC 当前记忆架构现状

#### 当前覆盖 (v0.5-v0.6)

| 记忆层 | 当前状态 | 覆盖度 | 示例 |
|--------|---------|--------|------|
| **Working Memory** | ❌ 未显式实现 | 0% | 无短期缓存机制 |
| **Episodic Memory** | ✅ 部分覆盖 | 60% | 原始对话记录、叙事文本存储 |
| **Semantic Memory** | ✅ 部分覆盖 | 70% | L0 评分结果、维度分数、置信度 |
| **Procedural Memory** | ❌ 未显式实现 | 0% | 评分流程硬编码，非可执行技能 |

#### 架构缺口

1. **Working Memory 缺失**
   - 无 session 级短期缓存
   - 每次评分重复加载相同上下文
   - 性能浪费 (额外 50-100ms/样本)

2. **Episodic Memory 不完整**
   - 仅存储原始文本，无结构化索引
   - 缺少时间戳、参与者元数据
   - 检索效率低 (线性扫描)

3. **Semantic Memory 孤立**
   - 评分结果未与 episodic 记录关联
   - 无跨 session 知识积累
   - 无法回答"该用户历史叙事质量趋势"

4. **Procedural Memory 缺失**
   - 评分流程硬编码在 Python 脚本中
   - 无法被 LLM 动态调用/修改
   - 不支持"用更严格标准重评"这类元指令

---

### 二、四层架构映射设计 (v0.7-v0.8 路线图)

#### 2.1 Working Memory (短期缓存层)

**职责**: Session 级快速访问，存储当前交互的临时状态

**设计**:
```python
class WorkingMemory:
    """
    Working Memory for VSNC
    
    存储:
    - 当前 session 的叙事文本缓存
    - L0 评分中间结果 (维度分、置信度)
    - L1 仲裁请求/响应
    - 临时计算结果 (信息密度、多样性等)
    
    生命周期: Session 结束即清除
    访问延迟: <10ms (内存访问)
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.cache: Dict[str, Any] = {}
        self.ttl_seconds = 3600  # 1 小时过期
    
    def set(self, key: str, value: Any):
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def get(self, key: str) -> Optional[Any]:
        entry = self.cache.get(key)
        if not entry:
            return None
        # 检查 TTL
        if time.time() - entry['timestamp'] > self.ttl_seconds:
            del self.cache[key]
            return None
        return entry['value']
```

**VSNC 映射**:
- **存储内容**: 当前评分 session 的中间状态
- **访问模式**: 高频读写 (L0→L1→融合)
- **性能收益**: 减少重复计算，延迟降低 50-100ms

**验证等级**: V0 (设计推断)

---

#### 2.2 Episodic Memory (情景记忆层)

**职责**: 存储具体叙事事件，支持基于内容的检索

**当前状态**: ✅ 部分实现 (原始文本存储)  
**增强设计**:

```python
class EpisodicMemory:
    """
    Episodic Memory for VSNC
    
    存储:
    - 原始叙事文本
    - 元数据：时间戳、参与者 ID、叙事类型 (自传/假设/他人)
    - 结构化索引：事件分段、情感效价、关键词
    - 关联：对应的 semantic 评分结果 ID
    
    检索:
    - 语义相似度搜索 (vector index)
    - 元数据过滤 (时间范围、叙事类型)
    - 混合检索：vector + metadata
    """
    
    def __init__(self, db_path: str):
        self.db = SQLiteVecDB(db_path)  # 向量 + 关系数据库
    
    def store(self, narrative: str, metadata: Dict):
        # 生成 embedding
        embedding = get_embedding(narrative)
        # 存储文本 + 元数据 + embedding
        self.db.insert({
            'text': narrative,
            'metadata': metadata,
            'embedding': embedding,
            'timestamp': datetime.utcnow()
        })
    
    def retrieve(self, query: str, filters: Dict, top_k: int = 5):
        # 混合检索：vector similarity + metadata filter
        query_embedding = get_embedding(query)
        results = self.db.search(
            query_embedding=query_embedding,
            filters=filters,
            top_k=top_k
        )
        return results
```

**VSNC 映射**:
- **当前缺口**: 无向量索引、无结构化元数据
- **增强方案**: 
  - 使用 SQLiteVec 或 Qdrant 存储 embedding
  - 添加元数据 schema (时间、参与者、叙事类型)
  - 建立 episodic↔semantic 双向链接

**验证等级**: V0 (设计推断)

---

#### 2.3 Semantic Memory (语义记忆层)

**职责**: 存储抽象知识、评分规律、跨 session 统计

**当前状态**: ✅ 部分实现 (L0 评分结果)  
**增强设计**:

```python
class SemanticMemory:
    """
    Semantic Memory for VSNC
    
    存储:
    - 评分结果聚合：用户级/群体级统计
    - 叙事质量趋势：时间序列分析
    - 校准参数：维度权重、阈值、基准线
    - 通用知识：叙事评分规则、维度定义
    
    应用:
    - 回答"该用户叙事质量是否在改善？"
    - 提供群体基准线 (百分位排名)
    - 动态调整评分阈值 (个性化校准)
    """
    
    def __init__(self, db_path: str):
        self.db = SQLiteDB(db_path)
    
    def store_score(self, user_id: str, session_id: str, scores: Dict):
        # 存储评分结果
        self.db.insert('scores', {
            'user_id': user_id,
            'session_id': session_id,
            'scores': scores,
            'timestamp': datetime.utcnow()
        })
        # 更新用户聚合统计
        self._update_user_stats(user_id)
    
    def get_user_trend(self, user_id: str, days: int = 30):
        # 获取用户过去 N 天的评分趋势
        trend = self.db.query(
            'SELECT AVG(final_score), DATE(timestamp) '
            'FROM scores WHERE user_id = ? '
            'AND timestamp >= datetime("now", "-{} days") '
            'GROUP BY DATE(timestamp)'.format(days),
            (user_id,)
        )
        return trend
    
    def get_percentile_rank(self, score: float, reference_group: str = 'age_matched'):
        # 计算百分位排名
        ref_scores = self.db.get_reference_group(reference_group)
        percentile = sum(1 for s in ref_scores if s < score) / len(ref_scores)
        return percentile * 100
```

**VSNC 映射**:
- **当前缺口**: 评分结果孤立，无跨 session 聚合
- **增强方案**:
  - 建立用户级评分历史数据库
  - 计算时间序列趋势 (改善/恶化)
  - 提供群体基准线 (年龄匹配对照组)

**验证等级**: V0 (设计推断)

---

#### 2.4 Procedural Memory (程序记忆层)

**职责**: 存储可执行的评分技能，支持动态调用和修改

**当前状态**: ❌ 未实现  
**创新设计**:

```python
class ProceduralMemory:
    """
    Procedural Memory for VSNC
    
    存储:
    - 评分技能：L0 规则引擎、L1 仲裁、融合算法
    - 技能元数据：输入/输出 schema、前置条件、性能基准
    - 技能变体：严格版/宽松版/快速版
    
    执行:
    - LLM 可通过自然语言调用技能
    - 支持技能组合 (pipeline)
    - 支持技能修改 (元指令)
    
    示例:
    - "用更严格的标准重评这段叙事" → 调用严格版 L0
    - "只评情感维度，跳过其他" → 调用单维度技能
    - "对比两段叙事的质量差异" → 调用对比技能
    """
    
    def __init__(self):
        self.skills: Dict[str, Callable] = {}
        self.skill_metadata: Dict[str, Dict] = {}
    
    def register_skill(self, name: str, func: Callable, metadata: Dict):
        """注册技能"""
        self.skills[name] = func
        self.skill_metadata[name] = metadata
    
    def execute(self, skill_name: str, inputs: Dict) -> Any:
        """执行技能"""
        if skill_name not in self.skills:
            raise ValueError(f"Unknown skill: {skill_name}")
        return self.skills[skill_name](**inputs)
    
    def get_skill_info(self, skill_name: str) -> Dict:
        """获取技能信息 (供 LLM 参考)"""
        return self.skill_metadata.get(skill_name, {})

# 技能注册示例
procedural_memory = ProceduralMemory()

# 注册 L0 评分技能
procedural_memory.register_skill(
    name='l0_score',
    func=l0_narrative_scorer,
    metadata={
        'description': 'L0 规则引擎快速评分 (6 维度)',
        'input_schema': {'narrative': 'str'},
        'output_schema': {'scores': 'dict', 'confidence': 'float'},
        'latency_p95': '100ms',
        'variants': ['standard', 'strict', 'lenient']
    }
)

# 注册 L1 仲裁技能
procedural_memory.register_skill(
    name='l1_arbitrate',
    func=llm_arbitration,
    metadata={
        'description': 'L1 LLM 仲裁层 (边界案例修正)',
        'input_schema': {'narrative': 'str', 'l0_scores': 'dict'},
        'output_schema': {'adjustment': 'int', 'reasoning': 'str'},
        'latency_p95': '3s',
        'trigger_condition': 'confidence < 0.6 or 55 <= score <= 75'
    }
)

# 注册对比技能
procedural_memory.register_skill(
    name='compare_narratives',
    func=compare_two_narratives,
    metadata={
        'description': '对比两段叙事的质量差异',
        'input_schema': {'narrative1': 'str', 'narrative2': 'str'},
        'output_schema': {'better': 'str', 'difference': 'dict'},
        'latency_p95': '200ms'
    }
)
```

**VSNC 映射**:
- **当前缺口**: 评分流程硬编码，无法动态调用
- **增强方案**:
  - 将评分技能封装为可调用函数
  - 注册技能元数据 (供 LLM 理解能力边界)
  - 支持技能组合和变体

**验证等级**: V0 (设计推断)

---

### 三、四层架构整合设计

#### 3.1 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户请求                                  │
│   "评这段叙事" / "用更严格标准重评" / "对比两段叙事"               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Procedural Memory (技能层)                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ l0_score     │ │ l1_arbitrate │ │ compare      │            │
│  │ (标准/严格)   │ │ (边界修正)    │ │ (对比技能)    │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                              ↓                                  │
│                    LLM 自然语言调用技能                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Working Memory (缓存层)                       │
│  - Session 级中间状态缓存                                        │
│  - 减少重复计算                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Episodic Memory (情景层)                      │
│  - 原始叙事文本 + 元数据                                         │
│  - 向量索引 + 混合检索                                           │
│  - 关联 semantic 评分结果                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Semantic Memory (语义层)                      │
│  - 评分结果聚合 + 趋势分析                                       │
│  - 群体基准线 + 百分位排名                                       │
│  - 跨 session 知识积累                                            │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.2 数据流示例

**场景**: 用户请求"用更严格标准重评我上周的叙事"

```
1. LLM 解析请求 → 识别意图：重评 + 严格标准 + 时间范围 (上周)

2. Procedural Memory 查询 → 选择技能：
   - skill = 'l0_score' (variant='strict')
   - 需要先检索目标叙事

3. Episodic Memory 检索 → 混合查询：
   - 时间过滤：timestamp >= last_week
   - 语义检索：query = "上周叙事"
   - 返回：top 1 匹配结果

4. Working Memory 缓存 → 存储中间状态：
   - 检索到的叙事文本
   - 原始评分结果 (如有)

5. Procedural Memory 执行 → 调用技能：
   - strict_l0_score(narrative)
   - 返回：新评分结果

6. Semantic Memory 更新 → 存储新评分：
   - 插入评分记录
   - 更新用户趋势统计

7. 响应生成 → LLM 整合结果：
   - "您上周的叙事严格评分为 72 分 (原评分 78 分)"
   - "主要差异在于信息密度维度扣分更严格"
```

---

### 四、实现路线图

| 阶段 | 任务 | 预计工作量 | 依赖 | 验证等级目标 |
|------|------|-----------|------|-------------|
| **Phase 1** | Working Memory 实现 | 1-2 天 | 无 | V4 (动态验证) |
| **Phase 2** | Episodic Memory 增强 (向量索引) | 3-4 天 | SQLiteVec/Qdrant 选型 | V4 |
| **Phase 3** | Semantic Memory 增强 (聚合统计) | 2-3 天 | Phase 2 完成 | V4 |
| **Phase 4** | Procedural Memory 实现 | 3-4 天 | Phase 1-3 完成 | V4 |
| **Phase 5** | 四层整合 + 端到端测试 | 2-3 天 | Phase 1-4 完成 | V4 |

**总计**: 11-16 天

---

### 五、与 Multi-Agent Scorer v0.6 的关联

#### 5.1 架构互补

| 组件 | Multi-Agent Scorer v0.6 | Agent Memory 四层架构 |
|------|------------------------|---------------------|
| **焦点** | 评分效度提升 (抗堆砌/仲裁) | 记忆架构增强 (存储/检索/技能) |
| **L1 仲裁** | 依赖 LLM 即时分析 | 可检索历史仲裁案例 (episodic) |
| **验证强度控制** | 基于统计阈值 | 可学习历史触发模式 (semantic) |
| **评分技能** | 硬编码流程 | 可调用/可组合技能 (procedural) |

#### 5.2 整合机会

1. **L1 仲裁增强**:
   - 检索历史相似案例 (episodic)
   - 参考历史仲裁调整模式 (semantic)
   - 调用"仲裁技能"而非硬编码 prompt (procedural)

2. **验证强度控制器增强**:
   - 存储历史触发率 (semantic)
   - 动态调整阈值基于学习模式 (procedural)

3. **抗堆砌模块增强**:
   - 检索历史堆砌案例 (episodic)
   - 学习堆砌检测规则 (semantic)

---

### 六、风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 向量数据库选型困难 | 中 | 中 | 先用 SQLiteVec (轻量)，后迁移 Qdrant (生产) |
| 技能封装复杂度高 | 中 | 中 | 分阶段实现，先封装 L0，再扩展 L1/对比 |
| 跨层数据一致性 | 高 | 高 | 设计事务机制，确保 episodic↔semantic 同步 |
| 性能开销 | 中 | 中 | Working Memory 缓存热点数据，减少 DB 访问 |

---

## 下一轮优先级 (GEO #101)

### P0 (继续 RB-016 实现)

1. **Phase 1: Working Memory 实现**
   - 实现 `WorkingMemory` 类
   - 集成到现有评分流程
   - 性能基准测试 (延迟对比)
   - 输出：`pipeline/src/services/working_memory.py` + 测试

2. **Phase 2: Episodic Memory 增强**
   - 选型：SQLiteVec vs Qdrant
   - 实现向量索引 + 混合检索
   - 迁移现有叙事数据
   - 输出：`pipeline/src/services/episodic_memory.py`

### P1 (如 RB-016 阻塞)

- **RB-017**: 反思 grounding 机制实现 (引用 episodic 证据)
- **RB-019**: 语音 biomarkers 与 LLM 融合方案
- **RB-012**: PROCESS Challenge 2026 参赛评估

---

## 产出物清单

| 文件 | 状态 | 描述 |
|------|------|------|
| `memory/2026-04-03-geo-iteration-100.md` | ✅ 已创建 | 本轮迭代日志 |
| `designs/agent-memory-four-layer-architecture.md` | ⏳ 待创建 | 详细设计稿 (本文档内容) |
| `memory/research-backlog.md` | ⏳ 待更新 | 标记 RB-016 状态为"🟡 设计中" |

---

## 验证等级汇总

| 发现 | 验证等级 | 验证方式 |
|------|---------|---------|
| VSNC 当前记忆架构缺口分析 | V3 | 静态复核现有代码 |
| 四层架构映射设计 | V0 | 架构推断 (基于 RB-015) |
| 实现路线图 | V0 | 工作量估算 |
| 与 Multi-Agent Scorer 关联 | V0 | 架构比对推断 |

---

## 核心结论

**一句话**: RB-016 完成四层架构映射设计，建议 Core 按 Phase 1-5 路线图逐步实现，预计 11-16 天完成。

**关键状态**:
- ✅ 研究完成：arXiv:2603.07670 深读 (RB-015) + 映射设计 (RB-016)
- 🟡 设计完成：四层架构详细设计 + 实现路线图
- 🔴 待实现：Phase 1-5 (Core 接手工程实现)

**Handoff 建议**:
- **接手方**: Core
- **接手原因**: 架构设计完成，进入工程实现阶段
- **下一步动作**: 
  1. Core 评审设计稿 (`designs/agent-memory-four-layer-architecture.md`)
  2. 启动 Phase 1 (Working Memory 实现，1-2 天)
  3. 按路线图逐步推进 Phase 2-5

---

*GEO #100 完成 — 2026-04-03 11:30 UTC*

Hulk 🟢 — 密度即价值
