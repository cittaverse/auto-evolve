# Agent Memory 四层架构在 VSNC 的映射设计

**版本**: v0.1-draft  
**创建日期**: 2026-04-03  
**作者**: Hulk 🟢 (GEO #100)  
**状态**: 设计稿 (待 Core 评审 + 实现)  
**验证等级**: V0 (架构推断，需实现验证)  
**关联任务**: RB-016 (承接 RB-015 arXiv:2603.07670 深读)

---

## 概述

本设计稿将 arXiv:2603.07670《LLM Agent Memory 架构综述》提出的四层记忆框架映射到 VSNC 系统，目标：

1. **补全记忆架构缺口**: Working Memory + Procedural Memory
2. **增强现有层次**: Episodic Memory (向量索引) + Semantic Memory (跨 session 聚合)
3. **支持自然语言技能调用**: LLM 可通过 prompt 动态调用评分技能
4. **提升性能**: Working Memory 缓存减少重复计算 (延迟降低 50-100ms)

---

## 一、VSNC 当前记忆架构现状

### 当前覆盖 (v0.5-v0.6)

| 记忆层 | 当前状态 | 覆盖度 | 示例 |
|--------|---------|--------|------|
| **Working Memory** | ❌ 未显式实现 | 0% | 无短期缓存机制 |
| **Episodic Memory** | ✅ 部分覆盖 | 60% | 原始对话记录、叙事文本存储 |
| **Semantic Memory** | ✅ 部分覆盖 | 70% | L0 评分结果、维度分数、置信度 |
| **Procedural Memory** | ❌ 未显式实现 | 0% | 评分流程硬编码，非可执行技能 |

### 架构缺口分析

#### 1. Working Memory 缺失

**问题**:
- 无 session 级短期缓存
- 每次评分重复加载相同上下文
- L0→L1→融合流程中，中间结果未复用

**性能影响**:
- 重复计算导致额外 50-100ms/样本延迟
- 数据库查询次数增加 2-3 倍

#### 2. Episodic Memory 不完整

**问题**:
- 仅存储原始文本，无结构化索引
- 缺少时间戳、参与者 ID、叙事类型元数据
- 检索效率低 (线性扫描，O(n))

**功能限制**:
- 无法回答"找出该用户所有高分叙事"
- 无法按叙事类型过滤检索
- 无法进行语义相似度搜索

#### 3. Semantic Memory 孤立

**问题**:
- 评分结果未与 episodic 记录关联
- 无跨 session 知识积累
- 无用户级/群体级统计

**功能限制**:
- 无法回答"该用户叙事质量是否在改善？"
- 无法提供百分位排名 (vs. 同龄人)
- 无法动态校准评分阈值

#### 4. Procedural Memory 缺失

**问题**:
- 评分流程硬编码在 Python 脚本中
- 无法被 LLM 动态调用/修改
- 不支持技能组合/变体

**功能限制**:
- 无法响应"用更严格标准重评"
- 无法响应"只评情感维度"
- 无法响应"对比两段叙事"

---

## 二、四层架构详细设计

### 2.1 Working Memory (短期缓存层)

#### 职责

- 存储 session 级临时状态
- 提供 <10ms 延迟的快速访问
- 自动过期 (TTL 机制)

#### 数据结构

```python
@dataclass
class WorkingMemoryEntry:
    value: Any
    timestamp: float
    ttl_seconds: int = 3600  # 1 小时
    
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl_seconds
```

#### API 设计

```python
class WorkingMemory:
    def __init__(self, session_id: str, ttl_seconds: int = 3600):
        self.session_id = session_id
        self.cache: Dict[str, WorkingMemoryEntry] = {}
        self.ttl_seconds = ttl_seconds
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """设置缓存项"""
        self.cache[key] = WorkingMemoryEntry(
            value=value,
            timestamp=time.time(),
            ttl_seconds=ttl_seconds or self.ttl_seconds
        )
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存项 (过期自动删除)"""
        entry = self.cache.get(key)
        if not entry:
            return None
        if entry.is_expired():
            del self.cache[key]
            return None
        return entry.value
    
    def delete(self, key: str):
        """删除缓存项"""
        self.cache.pop(key, None)
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
    
    def cleanup_expired(self):
        """清理所有过期项"""
        now = time.time()
        expired_keys = [
            k for k, v in self.cache.items()
            if now - v.timestamp > v.ttl_seconds
        ]
        for key in expired_keys:
            del self.cache[key]
```

#### VSNC 集成点

```python
# 在评分流程中使用 Working Memory
async def score_narrative_with_cache(narrative: str, session_id: str):
    wm = WorkingMemory(session_id)
    
    # 检查缓存
    cached_result = wm.get(f"score:{hash(narrative)}")
    if cached_result:
        return cached_result
    
    # L0 评分
    l0_scores = await l0_scorer.score(narrative)
    wm.set("l0_scores", l0_scores)
    
    # 检查是否触发 L1
    if should_trigger_l1(l0_scores):
        # L1 仲裁可访问 L0 结果 (无需重新计算)
        l0_for_arbitration = wm.get("l0_scores")
        l1_result = await l1_arbitrator.arbitrate(narrative, l0_for_arbitration)
        wm.set("l1_result", l1_result)
        
        # 融合
        final = fuse_scores(l0_scores, l1_result)
    else:
        final = l0_scores
    
    # 缓存最终结果
    wm.set(f"score:{hash(narrative)}", final)
    return final
```

#### 性能基准 (预期)

| 指标 | 当前 (无缓存) | 目标 (有缓存) | 改善 |
|------|-------------|-------------|------|
| 平均延迟 | 150ms | 80ms | -47% |
| p95 延迟 | 250ms | 120ms | -52% |
| DB 查询次数 | 3-4 次/样本 | 1-2 次/样本 | -50% |

**验证等级**: V0 (设计推断)

---

### 2.2 Episodic Memory (情景记忆层)

#### 职责

- 存储原始叙事文本 + 元数据
- 支持语义相似度检索
- 支持元数据过滤
- 关联 semantic 评分结果

#### 数据结构

```python
@dataclass
class EpisodicRecord:
    id: str
    narrative_text: str
    embedding: List[float]  # 768 维向量
    metadata: Dict
    # 元数据字段
    user_id: str
    session_id: str
    timestamp: datetime
    narrative_type: str  # 'autobiographical' | 'hypothetical' | 'other'
    word_count: int
    language: str  # 'zh-CN' | 'en-US' | ...
    # 关联
    semantic_score_id: Optional[str]  # 关联的评分结果 ID
```

#### 数据库选型

**选项 1: SQLiteVec (轻量级，推荐用于开发/测试)**

优势:
- 单一文件，无需独立服务
- 支持向量相似度搜索
- 与现有 SQLite 代码兼容

劣势:
- 性能不如专用向量数据库
- 不支持分布式

**选项 2: Qdrant (生产级，推荐用于部署)**

优势:
- 高性能向量检索
- 支持过滤 + 向量混合查询
- 支持分布式/集群

劣势:
- 需要独立服务
- 运维复杂度增加

**推荐路径**:
- Phase 1-2: SQLiteVec (快速验证)
- Phase 3+: 迁移 Qdrant (生产优化)

#### API 设计

```python
class EpisodicMemory:
    def __init__(self, db_path: str, use_qdrant: bool = False):
        if use_qdrant:
            self.backend = QdrantBackend(db_path)
        else:
            self.backend = SQLiteVecBackend(db_path)
    
    async def store(self, narrative: str, metadata: Dict) -> str:
        """存储叙事记录"""
        # 生成 embedding
        embedding = await get_embedding(narrative)
        
        # 创建记录
        record = EpisodicRecord(
            id=str(uuid.uuid4()),
            narrative_text=narrative,
            embedding=embedding,
            metadata=metadata,
            user_id=metadata['user_id'],
            session_id=metadata['session_id'],
            timestamp=datetime.utcnow(),
            narrative_type=metadata.get('narrative_type', 'autobiographical'),
            word_count=len(narrative.split()),
            language=metadata.get('language', 'zh-CN'),
            semantic_score_id=None  # 初始为空，评分后更新
        )
        
        # 存储
        await self.backend.insert(record)
        return record.id
    
    async def retrieve_by_similarity(
        self,
        query: str,
        filters: Dict,
        top_k: int = 5
    ) -> List[EpisodicRecord]:
        """基于语义相似度检索"""
        query_embedding = await get_embedding(query)
        results = await self.backend.search(
            query_embedding=query_embedding,
            filters=filters,  # e.g., {'user_id': 'xxx', 'narrative_type': 'autobiographical'}
            top_k=top_k
        )
        return results
    
    async def retrieve_by_id(self, record_id: str) -> Optional[EpisodicRecord]:
        """按 ID 检索"""
        return await self.backend.get_by_id(record_id)
    
    async def link_semantic_score(self, record_id: str, score_id: str):
        """关联评分结果"""
        await self.backend.update(record_id, {'semantic_score_id': score_id})
```

#### 混合检索示例

```python
# 场景：找出用户 A 过去 30 天的自传体叙事，按相似度排序
results = await episodic_memory.retrieve_by_similarity(
    query="关于家庭的温暖回忆",
    filters={
        'user_id': 'user_A',
        'narrative_type': 'autobiographical',
        'timestamp_gte': datetime.utcnow() - timedelta(days=30)
    },
    top_k=5
)
```

**验证等级**: V0 (设计推断)

---

### 2.3 Semantic Memory (语义记忆层)

#### 职责

- 存储评分结果聚合统计
- 计算用户叙事质量趋势
- 提供群体基准线 (百分位排名)
- 存储校准参数

#### 数据结构

```python
@dataclass
class SemanticScoreRecord:
    id: str
    episodic_record_id: str  # 关联的情景记忆 ID
    user_id: str
    session_id: str
    timestamp: datetime
    # 维度评分
    c1_internal_details: float
    c2_external_details: float
    c3_coherence: float
    c4_emotional_valence: float
    c5_information_density: float
    c6_linguistic_fluency: float
    # 综合评分
    final_score: float
    confidence: float
    # L1 仲裁结果 (如有)
    l1_adjustment: Optional[float]
    l1_reasoning: Optional[str]
```

```python
@dataclass
class UserStats:
    user_id: str
    total_scores: int
    avg_final_score: float
    score_trend_7d: float  # 7 天趋势 (斜率)
    score_trend_30d: float
    best_score: float
    worst_score: float
    last_updated: datetime
```

#### API 设计

```python
class SemanticMemory:
    def __init__(self, db_path: str):
        self.db = SQLiteDB(db_path)
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据库表"""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id TEXT PRIMARY KEY,
                episodic_record_id TEXT,
                user_id TEXT,
                session_id TEXT,
                timestamp DATETIME,
                c1 REAL, c2 REAL, c3 REAL, c4 REAL, c5 REAL, c6 REAL,
                final_score REAL,
                confidence REAL,
                l1_adjustment REAL,
                l1_reasoning TEXT,
                FOREIGN KEY (episodic_record_id) REFERENCES episodic_records(id)
            )
        ''')
        
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id TEXT PRIMARY KEY,
                total_scores INTEGER,
                avg_final_score REAL,
                score_trend_7d REAL,
                score_trend_30d REAL,
                best_score REAL,
                worst_score REAL,
                last_updated DATETIME
            )
        ''')
    
    async def store_score(self, score: SemanticScoreRecord):
        """存储评分结果"""
        await self.db.insert('scores', score.to_dict())
        # 更新用户统计
        await self._update_user_stats(score.user_id)
    
    async def get_user_trend(self, user_id: str, days: int = 30) -> List[Dict]:
        """获取用户评分趋势"""
        trend = await self.db.query('''
            SELECT AVG(final_score) as avg_score, DATE(timestamp) as date
            FROM scores
            WHERE user_id = ? AND timestamp >= datetime("now", "-{} days")
            GROUP BY DATE(timestamp)
            ORDER BY date
        '''.format(days), (user_id,))
        return trend
    
    async def get_percentile_rank(
        self,
        score: float,
        reference_group: str = 'age_matched',
        age: Optional[int] = None
    ) -> float:
        """计算百分位排名"""
        if reference_group == 'age_matched' and age:
            # 获取年龄匹配对照组的评分分布
            ref_scores = await self._get_age_matched_reference(age)
        else:
            # 获取全体对照组
            ref_scores = await self._get_general_reference()
        
        # 计算百分位
        percentile = sum(1 for s in ref_scores if s < score) / len(ref_scores)
        return percentile * 100
    
    async def _update_user_stats(self, user_id: str):
        """更新用户统计 (内部方法)"""
        stats = await self.db.query('''
            SELECT
                COUNT(*) as total_scores,
                AVG(final_score) as avg_final_score,
                MAX(final_score) as best_score,
                MIN(final_score) as worst_score
            FROM scores
            WHERE user_id = ?
        ''', (user_id,))
        
        # 计算趋势 (简化版，实际应使用线性回归)
        trend_7d = await self._calculate_trend(user_id, days=7)
        trend_30d = await self._calculate_trend(user_id, days=30)
        
        await self.db.upsert('user_stats', {
            'user_id': user_id,
            'total_scores': stats[0]['total_scores'],
            'avg_final_score': stats[0]['avg_final_score'],
            'score_trend_7d': trend_7d,
            'score_trend_30d': trend_30d,
            'best_score': stats[0]['best_score'],
            'worst_score': stats[0]['worst_score'],
            'last_updated': datetime.utcnow()
        })
```

#### 群体基准线设计

```python
# 对照组定义
REFERENCE_GROUPS = {
    'general': '全体用户',
    'age_20_30': '20-30 岁',
    'age_31_40': '31-40 岁',
    'age_41_50': '41-50 岁',
    'age_51_60': '51-60 岁',
    'age_61_plus': '61 岁+',
    'mci': 'MCI 患者',
    'healthy_elder': '健康老年人'
}

# 示例：用户查询自己的百分位排名
# "我的叙事质量在同龄人中处于什么水平？"
percentile = await semantic_memory.get_percentile_rank(
    score=75.5,
    reference_group='age_61_plus',
    age=65
)
# 输出：percentile = 68.0 (超过 68% 的同龄人)
```

**验证等级**: V0 (设计推断)

---

### 2.4 Procedural Memory (程序记忆层)

#### 职责

- 封装评分技能为可调用函数
- 注册技能元数据 (供 LLM 理解)
- 支持技能组合 (pipeline)
- 支持技能变体 (严格/宽松/快速)

#### 技能注册系统

```python
@dataclass
class SkillMetadata:
    name: str
    description: str
    input_schema: Dict[str, str]  # {param_name: type}
    output_schema: Dict[str, str]  # {field_name: type}
    latency_p95_ms: int
    variants: List[str]  # ['standard', 'strict', 'lenient']
    prerequisites: List[str]  # 前置技能
    examples: List[Dict]  # 使用示例

class ProceduralMemory:
    def __init__(self):
        self.skills: Dict[str, Callable] = {}
        self.metadata: Dict[str, SkillMetadata] = {}
    
    def register(self, name: str, func: Callable, meta: SkillMetadata):
        """注册技能"""
        self.skills[name] = func
        self.metadata[name] = meta
    
    def execute(self, skill_name: str, **kwargs) -> Any:
        """执行技能"""
        if skill_name not in self.skills:
            raise ValueError(f"Unknown skill: {skill_name}")
        return self.skills[skill_name](**kwargs)
    
    def get_skill_info(self, skill_name: str) -> Optional[SkillMetadata]:
        """获取技能信息 (供 LLM 参考)"""
        return self.metadata.get(skill_name)
    
    def list_skills(self) -> List[str]:
        """列出所有技能"""
        return list(self.skills.keys())
```

#### 预置技能库

```python
# 初始化 Procedural Memory
procedural_memory = ProceduralMemory()

# === 技能 1: L0 评分 ===
def l0_score_standard(narrative: str) -> Dict:
    """L0 规则引擎标准版评分"""
    return l0_narrative_scorer.score(narrative, variant='standard')

def l0_score_strict(narrative: str) -> Dict:
    """L0 规则引擎严格版评分"""
    return l0_narrative_scorer.score(narrative, variant='strict')

def l0_score_lenient(narrative: str) -> Dict:
    """L0 规则引擎宽松版评分"""
    return l0_narrative_scorer.score(narrative, variant='lenient')

procedural_memory.register(
    name='l0_score',
    func=l0_score_standard,
    meta=SkillMetadata(
        name='l0_score',
        description='L0 规则引擎快速评分 (6 维度)',
        input_schema={'narrative': 'str'},
        output_schema={
            'c1': 'float', 'c2': 'float', 'c3': 'float',
            'c4': 'float', 'c5': 'float', 'c6': 'float',
            'final': 'float', 'confidence': 'float'
        },
        latency_p95_ms=100,
        variants=['standard', 'strict', 'lenient'],
        prerequisites=[],
        examples=[
            {'input': {'narrative': '今天天气很好...'}, 'output': {'final': 75.5}}
        ]
    )
)

# === 技能 2: L1 仲裁 ===
async def l1_arbitrate(narrative: str, l0_scores: Dict) -> Dict:
    """L1 LLM 仲裁层"""
    return await llm_arbitrator.arbitrate(narrative, l0_scores)

procedural_memory.register(
    name='l1_arbitrate',
    func=l1_arbitrate,
    meta=SkillMetadata(
        name='l1_arbitrate',
        description='L1 LLM 仲裁层 (边界案例修正)',
        input_schema={'narrative': 'str', 'l0_scores': 'dict'},
        output_schema={
            'adjustment': 'float',
            'reasoning': 'str',
            'dimension_adjustments': 'dict'
        },
        latency_p95_ms=3000,
        variants=['standard'],
        prerequisites=['l0_score'],
        examples=[
            {
                'input': {'narrative': '...', 'l0_scores': {...}},
                'output': {'adjustment': -3.2, 'reasoning': '...'}
            }
        ]
    )
)

# === 技能 3: 对比两段叙事 ===
def compare_narratives(narrative1: str, narrative2: str) -> Dict:
    """对比两段叙事的质量差异"""
    score1 = l0_narrative_scorer.score(narrative1)
    score2 = l0_narrative_scorer.score(narrative2)
    
    return {
        'narrative1_score': score1['final'],
        'narrative2_score': score2['final'],
        'better': 'narrative1' if score1['final'] > score2['final'] else 'narrative2',
        'difference': {
            'c1': score1['c1'] - score2['c1'],
            'c2': score1['c2'] - score2['c2'],
            # ...
        }
    }

procedural_memory.register(
    name='compare_narratives',
    func=compare_narratives,
    meta=SkillMetadata(
        name='compare_narratives',
        description='对比两段叙事的质量差异',
        input_schema={'narrative1': 'str', 'narrative2': 'str'},
        output_schema={
            'narrative1_score': 'float',
            'narrative2_score': 'float',
            'better': 'str',
            'difference': 'dict'
        },
        latency_p95_ms=200,
        variants=[],
        prerequisites=[],
        examples=[
            {
                'input': {'narrative1': '...', 'narrative2': '...'},
                'output': {'better': 'narrative1', 'difference': {...}}
            }
        ]
    )
)

# === 技能 4: 获取用户趋势 ===
async def get_user_trend(user_id: str, days: int = 30) -> List[Dict]:
    """获取用户评分趋势"""
    return await semantic_memory.get_user_trend(user_id, days)

procedural_memory.register(
    name='get_user_trend',
    func=get_user_trend,
    meta=SkillMetadata(
        name='get_user_trend',
        description='获取用户过去 N 天的评分趋势',
        input_schema={'user_id': 'str', 'days': 'int'},
        output_schema={'trend': 'list[dict]'},  # [{date, avg_score}, ...]
        latency_p95_ms=50,
        variants=[],
        prerequisites=[],
        examples=[
            {
                'input': {'user_id': 'user_A', 'days': 30},
                'output': {'trend': [...]}
            }
        ]
    )
)
```

#### LLM 自然语言调用

```python
# LLM System Prompt 模板
PROCEDURAL_MEMORY_PROMPT = """
你可以调用以下技能来帮助用户：

{skills_description}

调用格式：
- 技能名：参数 1=值 1, 参数 2=值 2

示例：
- l0_score: narrative="今天天气很好，我去公园散步了。"
- compare_narratives: narrative1="...", narrative2="..."
- get_user_trend: user_id="user_A", days=30

当用户请求时，识别意图并调用相应技能。
"""

# 技能描述生成
def generate_skills_description():
    skills = []
    for name, meta in procedural_memory.metadata.items():
        skills.append(f"- {name}: {meta.description}")
        skills.append(f"  输入：{meta.input_schema}")
        skills.append(f"  输出：{meta.output_schema}")
    return '\n'.join(skills)

# LLM 调用解析
def parse_llm_skill_call(llm_output: str):
    """解析 LLM 输出的技能调用"""
    # 示例输入："l0_score: narrative=\"今天天气很好\""
    match = re.match(r'(\w+):\s*(.+)', llm_output)
    if not match:
        return None
    
    skill_name = match.group(1)
    args_str = match.group(2)
    
    # 解析参数
    args = {}
    for arg_match in re.finditer(r'(\w+)="([^"]+)"', args_str):
        args[arg_match.group(1)] = arg_match.group(2)
    
    return {'skill': skill_name, 'args': args}

# 执行技能调用
def execute_skill_call(skill_name: str, args: Dict):
    """执行技能调用并返回结果"""
    result = procedural_memory.execute(skill_name, **args)
    return result
```

#### 使用示例

```
用户： "用更严格标准重评我上周的叙事"

LLM 思考:
1. 识别意图：重评 + 严格标准 + 时间范围 (上周)
2. 选择技能：
   - 先检索：retrieve_by_similarity: query="上周叙事", filters={user_id=xxx}
   - 后评分：l0_score_strict: narrative=检索结果
3. 生成调用

执行:
1. episodic_result = retrieve_by_similarity(query="上周叙事", filters={...})
2. narrative = episodic_result[0].text
3. score = l0_score_strict(narrative=narrative)
4. 返回结果

响应:
"您上周的叙事严格评分为 72 分 (原标准版评分 78 分)。
主要差异在于信息密度维度扣分更严格。"
```

**验证等级**: V0 (设计推断)

---

## 三、四层架构整合

### 3.1 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户请求                                  │
│   "评这段叙事" / "用更严格标准重评" / "对比两段叙事"               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              LLM 自然语言理解 + 技能路由                         │
│   (识别意图 → 选择技能 → 解析参数)                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Procedural Memory (技能层)                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ l0_score     │ │ l1_arbitrate │ │ compare      │            │
│  │ (标准/严格)   │ │ (边界修正)    │ │ (对比技能)    │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                              ↓                                  │
│                    技能执行 + 结果返回                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Working Memory (缓存层)                       │
│  - Session 级中间状态缓存                                        │
│  - 减少重复计算 (延迟降低 50-100ms)                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Episodic Memory (情景层)                      │
│  - 原始叙事文本 + 元数据                                         │
│  - 向量索引 + 混合检索 (语义 + 元数据过滤)                        │
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

### 3.2 端到端数据流

**场景**: "用更严格标准重评我上周的叙事"

```
Step 1: LLM 意图识别
  输入："用更严格标准重评我上周的叙事"
  输出：{
    'intent': 're_score',
    'variant': 'strict',
    'time_range': 'last_week',
    'user_id': 'user_A'
  }

Step 2: Episodic Memory 检索
  调用：retrieve_by_similarity(
    query="上周叙事",
    filters={'user_id': 'user_A', 'timestamp_gte': now - 7 days},
    top_k=1
  )
  输出：[EpisodicRecord(id='xxx', text='...', ...)]

Step 3: Working Memory 缓存
  调用：wm.set('retrieved_narrative', narrative_text)
  目的：避免重复检索

Step 4: Procedural Memory 技能调用
  调用：l0_score_strict(narrative=narrative_text)
  输出：{c1: ..., c2: ..., final: 72.0, ...}

Step 5: Semantic Memory 查询历史
  调用：get_user_trend(user_id='user_A', days=7)
  输出：[{date: '2026-03-27', avg_score: 78.0}, ...]

Step 6: 结果整合
  对比：新评分 72 分 vs. 历史平均 78 分
  差异分析：信息密度维度扣分更严格

Step 7: 响应生成
  LLM 生成："您上周的叙事严格评分为 72 分 (原标准版评分 78 分)。
             主要差异在于信息密度维度扣分更严格 (-5 分)。"
```

---

## 四、实现路线图

| 阶段 | 任务 | 预计工作量 | 依赖 | 产出物 |
|------|------|-----------|------|--------|
| **Phase 1** | Working Memory 实现 | 1-2 天 | 无 | `pipeline/src/services/working_memory.py` + 测试 |
| **Phase 2** | Episodic Memory 增强 | 3-4 天 | SQLiteVec 选型 | `pipeline/src/services/episodic_memory.py` + 迁移脚本 |
| **Phase 3** | Semantic Memory 增强 | 2-3 天 | Phase 2 完成 | `pipeline/src/services/semantic_memory.py` + 统计函数 |
| **Phase 4** | Procedural Memory 实现 | 3-4 天 | Phase 1-3 完成 | `pipeline/src/services/procedural_memory.py` + 技能库 |
| **Phase 5** | 四层整合 + 端到端测试 | 2-3 天 | Phase 1-4 完成 | 整合测试 + 性能基准报告 |

**总计**: 11-16 天

---

## 五、与 Multi-Agent Scorer v0.6 的关联

### 5.1 架构互补

| 维度 | Multi-Agent Scorer v0.6 | Agent Memory 四层架构 |
|------|------------------------|---------------------|
| **焦点** | 评分效度提升 (抗堆砌/仲裁) | 记忆架构增强 (存储/检索/技能) |
| **L0 评分** | 6 维度规则引擎 | → 封装为 Procedural Memory 技能 |
| **L1 仲裁** | LLM 即时分析 | → 可检索历史案例 (Episodic) |
| **验证强度控制** | 统计阈值 | → 学习历史模式 (Semantic) |
| **性能** | L0 <100ms, L1 <3s | → Working Memory 缓存优化 |

### 5.2 整合机会

#### 1. L1 仲裁增强

```python
# 当前：LLM 即时分析
l1_result = await llm_arbitrate(narrative, l0_scores)

# 增强：检索历史相似案例
similar_cases = await episodic_memory.retrieve_by_similarity(
    query=narrative,
    filters={'has_l1_arbitration': True},
    top_k=3
)

# 参考历史仲裁模式
historical_patterns = [case.l1_result for case in similar_cases]

# LLM 结合历史模式进行仲裁
l1_result = await llm_arbitrate(narrative, l0_scores, historical_patterns)
```

#### 2. 验证强度控制器增强

```python
# 当前：固定阈值
trigger_l1 = confidence < 0.6

# 增强：基于历史触发率动态调整
historical_trigger_rate = await semantic_memory.get_trigger_rate(window=1000)
target_rate = 0.2

if historical_trigger_rate > target_rate + 0.05:
    # 触发率过高，提高阈值
    threshold = 0.55
elif historical_trigger_rate < target_rate - 0.05:
    # 触发率过低，降低阈值
    threshold = 0.65
else:
    threshold = 0.6

trigger_l1 = confidence < threshold
```

#### 3. 抗堆砌模块增强

```python
# 当前：规则检测
stuffing_detected = detect_keyword_stuffing(text, keywords)

# 增强：检索历史堆砌案例
historical_stuffing_cases = await episodic_memory.retrieve_by_metadata(
    filters={'is_reward_hacking': True}
)

# 学习堆砌模式
stuffing_patterns = learn_patterns(historical_stuffing_cases)

# 结合规则 + 学习模式检测
stuffing_detected = (
    detect_keyword_stuffing(text, keywords) or
    matches_learned_patterns(text, stuffing_patterns)
)
```

---

## 六、风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 向量数据库选型困难 | 中 | 中 | 先用 SQLiteVec (轻量)，后迁移 Qdrant (生产) |
| 技能封装复杂度高 | 中 | 中 | 分阶段实现，先封装 L0，再扩展 L1/对比 |
| 跨层数据一致性 | 高 | 高 | 设计事务机制，确保 episodic↔semantic 同步 |
| 性能开销 | 中 | 中 | Working Memory 缓存热点数据，减少 DB 访问 |
| LLM 技能调用解析错误 | 中 | 中 | 添加语法验证 + 错误恢复机制 |

---

## 七、验收标准

- [ ] Working Memory 实现 + 测试覆盖 >80%
- [ ] Episodic Memory 向量检索延迟 <100ms (p95)
- [ ] Semantic Memory 趋势查询延迟 <50ms (p95)
- [ ] Procedural Memory 技能调用成功率 >95%
- [ ] 端到端延迟降低 >30% (vs. 当前架构)
- [ ] 支持自然语言技能调用 (LLM 解析准确率 >90%)

---

## 附录：文件结构

```
pipeline/
  src/
    services/
      working_memory.py        # Phase 1
      episodic_memory.py       # Phase 2
      semantic_memory.py       # Phase 3
      procedural_memory.py     # Phase 4
      __init__.py              # 导出公共接口
  tests/
    test_working_memory.py
    test_episodic_memory.py
    test_semantic_memory.py
    test_procedural_memory.py
    test_integration.py        # Phase 5 端到端测试
docs/
  agent-memory-architecture.md  # 本文档
```

---

*设计稿完成 — 2026-04-03 11:30 UTC*

Hulk 🟢 — 密度即价值
