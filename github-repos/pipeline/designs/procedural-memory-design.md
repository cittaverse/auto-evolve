# Procedural Memory Design (RB-016 Phase 4)

**版本**: 1.0.0  
**状态**: Draft  
**作者**: Hulk 🟢  
**日期**: 2026-04-04  
**验证等级**: V0 (设计阶段，待实现验证)

---

## 1. 问题定义

### 1.1 核心问题

当前三层记忆架构 (Working/Episodic/Semantic) 已实现：
- **WorkingMemory**: Session 内缓存 (<0.001ms hit)
- **SemanticMemory**: 跨 session 统计持久化 (store_score 0.74ms)
- **EpisodicMemory**: 原始事件存储 + 语义检索 (<100ms)

**缺失能力**:
- 如何根据用户特征自动选择 scoring strategy？
- 如何动态调整 calibration rules？
- 如何将"经验"封装为可复用的程序性知识？

### 1.2 使用场景

| 场景 | 当前痛点 | Procedural Memory 解决方案 |
|------|---------|--------------------------|
| 新用户首次 scoring | 使用默认策略，可能不匹配用户认知风格 | 根据用户画像 (年龄/教育/文化背景) 选择策略 |
| 低 confidence 分数 | 无法自动调整 scoring 参数 | 触发 calibration strategy 自动优化 |
| 特定主题叙事 (如创伤) | 缺乏特殊处理逻辑 | 调用 trauma-sensitive scoring strategy |
| 跨文化用户 | 统一权重可能不公平 | 应用 cultural adaptation strategy |

---

## 2. 设计目标

### 2.1 功能目标

1. **策略封装**: 将 scoring strategies 封装为可插拔模块
2. **动态调用**: 基于 user context 自动选择最优策略
3. **规则管理**: calibration rules 可配置、可版本化
4. **性能约束**: strategy 选择延迟 <5ms

### 2.2 非功能目标

| 指标 | 目标 | 理由 |
|------|------|------|
| strategy 选择延迟 | <5ms | 不显著增加 scoring 总延迟 |
| 策略数量 | 支持 10+ strategies | 覆盖多样化用户群体 |
| 规则更新 | 无需重启服务 | 支持在线 A/B 测试 |
| 可解释性 | 每次选择可追溯 | 便于调试和审计 |

---

## 3. 架构设计

### 3.1 四层记忆架构总览

```
┌─────────────────────────────────────────────────────────┐
│                  NarrativeScorerService                  │
├─────────────────────────────────────────────────────────┤
│  WorkingMemory (Session-level)                          │
│  - Cache key: MD5(text + use_llm + strategy_id)         │
│  - Hit latency: <0.001ms                                │
├─────────────────────────────────────────────────────────┤
│  SemanticMemory (Cross-session)                         │
│  - User stats, trends, baselines, calibration           │
│  - Store latency: 0.74ms                                │
├─────────────────────────────────────────────────────────┤
│  EpisodicMemory (Raw events)                            │
│  - Narrative text + embeddings                          │
│  - Search latency: <100ms                               │
├─────────────────────────────────────────────────────────┤
│  ProceduralMemory (Strategies & Rules) ← Phase 4        │
│  - Strategy selection logic                             │
│  - Calibration rules                                    │
│  - Selection latency: <5ms (target)                     │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Procedural Memory 组件

```
┌─────────────────────────────────────────────────────────┐
│                   ProceduralMemory                       │
├─────────────────────────────────────────────────────────┤
│  StrategyRegistry                                        │
│  - register_strategy(name, strategy_instance)           │
│  - get_strategy(name) → Strategy                        │
│  - list_strategies() → List[str]                        │
├─────────────────────────────────────────────────────────┤
│  StrategySelector                                        │
│  - select(user_context) → Strategy                      │
│  - Rules: age, culture, topic, confidence_threshold     │
├─────────────────────────────────────────────────────────┤
│  CalibrationRules                                        │
│  - get_rules(user_id) → List[CalibrationRule]           │
│  - apply(score, rules) → CalibratedScore                │
│  - update_rules(user_id, rules) → bool                  │
├─────────────────────────────────────────────────────────┤
│  StrategyStore (SQLite)                                  │
│  - strategies table: name, config, version, active      │
│  - rules table: user_id, rule_type, params, priority    │
└─────────────────────────────────────────────────────────┘
```

---

## 4. 接口设计

### 4.1 Strategy 抽象基类

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ScoringStrategy(ABC):
    """Abstract base class for all scoring strategies."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy identifier."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""
        pass
    
    @abstractmethod
    def score(self, narrative_text: str, use_llm: bool = True) -> Dict[str, Any]:
        """
        Score a narrative using this strategy.
        
        Returns:
            {
                "composite_score": float,
                "dimension_scores": Dict[str, float],
                "confidence": float,
                "strategy_metadata": Dict[str, Any]
            }
        """
        pass
    
    @abstractmethod
    def get_requirements(self) -> Dict[str, Any]:
        """
        Return strategy requirements/assumptions.
        
        Example:
            {
                "min_text_length": 50,
                "language": "zh-CN",
                "requires_llm": True,
                "cultural_context": "East Asian"
            }
        """
        pass
```

### 4.2 预定义策略

| 策略名 | 描述 | 适用场景 |
|--------|------|---------|
| `default_v1` | 标准 6 维度等权重 | 通用场景，无特殊要求 |
| `elderly_friendly` | 降低语言流畅度权重，提升情感深度权重 | 老年用户 (65+) |
| `trauma_sensitive` | 降低负面事件惩罚，提升成长叙事奖励 | 创伤叙事 |
| `cultural_east_asian` | 调整集体主义 vs 个人主义维度权重 | 东亚文化背景 |
| `brief_narrative` | 优化短文本 scoring ( <200 字) | 快速记录场景 |
| `clinical_assessment` | 提升认知细节权重，用于临床评估 | 专业场景 |
| `growth_focused` | 强调成长/改变/学习维度 | 反思练习 |

### 4.3 StrategySelector 规则引擎

```python
@dataclass
class UserContext:
    user_id: str
    age: Optional[int] = None
    cultural_background: Optional[str] = None
    narrative_topic: Optional[str] = None
    text_length: int = 0
    session_count: int = 0
    previous_scores: Optional[List[float]] = None

class StrategySelector:
    def __init__(self):
        self.rules: List[SelectionRule] = []
    
    def add_rule(self, rule: SelectionRule):
        self.rules.append(rule)
    
    def select(self, context: UserContext) -> ScoringStrategy:
        """
        Select strategy based on rules.
        
        Rule priority: Higher priority rules evaluated first.
        First matching rule wins.
        Default fallback: default_v1
        """
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            if rule.matches(context):
                return rule.strategy
        
        return self.get_strategy("default_v1")
```

### 4.4 SelectionRule 示例

```python
@dataclass
class SelectionRule:
    name: str
    priority: int  # Higher = evaluated first
    condition: Callable[[UserContext], bool]
    strategy: ScoringStrategy
    
    def matches(self, context: UserContext) -> bool:
        return self.condition(context)

# Example rules:
rule_elderly = SelectionRule(
    name="elderly_user",
    priority=100,
    condition=lambda ctx: ctx.age is not None and ctx.age >= 65,
    strategy=ElderlyFriendlyStrategy()
)

rule_trauma = SelectionRule(
    name="trauma_narrative",
    priority=90,
    condition=lambda ctx: ctx.narrative_topic in ["loss", "trauma", "grief"],
    strategy=TraumaSensitiveStrategy()
)

rule_cultural = SelectionRule(
    name="east_asian",
    priority=80,
    condition=lambda ctx: ctx.cultural_background == "East Asian",
    strategy=CulturalEastAsianStrategy()
)
```

### 4.5 CalibrationRules 设计

```python
@dataclass
class CalibrationRule:
    rule_id: str
    user_id: str
    rule_type: str  # "dimension_weight", "sensitivity", "threshold"
    params: Dict[str, Any]
    priority: int
    created_at: datetime
    expires_at: Optional[datetime] = None  # None = permanent
    
    def apply(self, scores: Dict[str, float]) -> Dict[str, float]:
        if self.rule_type == "dimension_weight":
            return self._apply_weights(scores)
        elif self.rule_type == "sensitivity":
            return self._apply_sensitivity(scores)
        elif self.rule_type == "threshold":
            return self._apply_threshold(scores)
        else:
            return scores

class CalibrationRules:
    def __init__(self, db_path: str = "procedural_memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def get_rules(self, user_id: str) -> List[CalibrationRule]:
        """Get all active rules for a user."""
        # Query DB, filter by expires_at > now
    
    def apply(self, user_id: str, scores: Dict[str, float]) -> Dict[str, float]:
        """Apply all matching rules to scores."""
        rules = self.get_rules(user_id)
        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        
        calibrated = scores.copy()
        for rule in sorted_rules:
            calibrated = rule.apply(calibrated)
        
        return calibrated
    
    def create_rule(self, rule: CalibrationRule) -> str:
        """Create a new calibration rule."""
        # Insert into DB, return rule_id
```

---

## 5. 数据模型

### 5.1 SQLite Schema

```sql
-- Strategies table
CREATE TABLE IF NOT EXISTS strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    config_json TEXT NOT NULL,  -- JSON-serialized strategy config
    version TEXT NOT NULL DEFAULT '1.0.0',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Selection rules table
CREATE TABLE IF NOT EXISTS selection_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 50,
    condition_type TEXT NOT NULL,  -- "age", "culture", "topic", "custom"
    condition_params TEXT NOT NULL,  -- JSON-serialized params
    strategy_name TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (strategy_name) REFERENCES strategies(name)
);

-- Calibration rules table
CREATE TABLE IF NOT EXISTS calibration_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    rule_type TEXT NOT NULL,  -- "dimension_weight", "sensitivity", "threshold"
    params_json TEXT NOT NULL,  -- JSON-serialized params
    priority INTEGER NOT NULL DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    created_by TEXT,  -- User ID of creator (for audit)
    is_active INTEGER NOT NULL DEFAULT 1
);

-- Strategy usage log (for analytics)
CREATE TABLE IF NOT EXISTS strategy_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    strategy_name TEXT NOT NULL,
    session_id TEXT,
    narrative_id TEXT,
    selected_reason TEXT,  -- Which rule matched
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_calibration_user ON calibration_rules(user_id, is_active);
CREATE INDEX idx_strategy_usage_user ON strategy_usage_log(user_id, created_at);
CREATE INDEX idx_selection_rules_active ON selection_rules(is_active, priority DESC);
```

---

## 6. 集成方案

### 6.1 NarrativeScorerService 扩展

```python
class NarrativeScorerService:
    def __init__(
        self,
        use_llm: bool = True,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        enable_semantic_memory: bool = True,
        enable_procedural_memory: bool = True,  # New
        procedural_memory_db: Optional[str] = None,
        semantic_memory_db: Optional[str] = None,
    ):
        self.use_llm = use_llm
        self.session_id = session_id
        self.user_id = user_id
        
        # WorkingMemory
        self.working_memory = get_working_memory(session_id)
        
        # SemanticMemory
        self.semantic_memory = (
            get_semantic_memory(semantic_memory_db)
            if enable_semantic_memory and user_id
            else None
        )
        
        # ProceduralMemory (NEW)
        self.procedural_memory = (
            ProceduralMemory(procedural_memory_db)
            if enable_procedural_memory
            else None
        )
    
    def score(self, text: str, use_llm: Optional[bool] = None) -> Dict[str, Any]:
        # Check WorkingMemory cache
        cache_key = self._build_cache_key(text, use_llm)
        if cached := self.working_memory.get(cache_key):
            return cached
        
        # Select strategy (NEW)
        if self.procedural_memory and self.user_id:
            user_context = self._build_user_context(text)
            strategy = self.procedural_memory.select_strategy(user_context)
        else:
            strategy = DefaultStrategy()
        
        # Score using selected strategy
        result = strategy.score(text, use_llm or self.use_llm)
        result["strategy_used"] = strategy.name
        
        # Apply calibration (NEW)
        if self.procedural_memory and self.user_id:
            rules = self.procedural_memory.get_calibration_rules(self.user_id)
            result["dimension_scores"] = self.procedural_memory.apply_calibration(
                result["dimension_scores"], rules
            )
        
        # Store to SemanticMemory
        if self.semantic_memory:
            self.semantic_memory.store_score(
                user_id=self.user_id,
                composite_score=result["composite_score"],
                dimension_scores=result["dimension_scores"],
                confidence=result["confidence"],
                metadata={"strategy": strategy.name}
            )
        
        # Cache to WorkingMemory
        self.working_memory.set(cache_key, result)
        
        return result
```

### 6.2 调用示例

```python
# Example 1: Default scoring (no user context)
service = NarrativeScorerService(session_id="sess_123")
result = service.score("今天我去公园散步了...")
# Uses: default_v1 strategy

# Example 2: Elderly user with cultural context
service = NarrativeScorerService(
    session_id="sess_456",
    user_id="user_789",
    enable_procedural_memory=True
)

# Set user context (would be stored in user profile)
service.set_user_context(
    age=72,
    cultural_background="East Asian"
)

result = service.score("回想我的一生，最难忘的是...")
# Uses: elderly_friendly + cultural_east_asian strategy
# (priority-based selection)

# Example 3: Custom calibration rule
service.procedural_memory.create_calibration_rule(
    user_id="user_789",
    rule_type="dimension_weight",
    params={
        "dimension_weights": {
            "emotional_depth": 0.25,  # Increased from 0.167
            "cognitive_details": 0.25,
            "temporal_coherence": 0.15,
            "self_reflection": 0.15,
            "social_connection": 0.10,
            "growth_insight": 0.10
        }
    },
    priority=100
)
```

---

## 7. 性能分析

### 7.1 延迟预算

| 操作 | 目标延迟 | 实现方式 |
|------|---------|---------|
| strategy selection | <5ms | In-memory rule evaluation |
| calibration apply | <1ms | Simple arithmetic ops |
| strategy loading | <10ms | SQLite query + cache |
| total overhead | <10ms | Acceptable for scoring flow |

### 7.2 缓存策略

```python
class ProceduralMemory:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._strategy_cache: Dict[str, ScoringStrategy] = {}
        self._rules_cache: Dict[str, List[CalibrationRule]] = {}
        self._cache_ttl = 3600  # 1 hour
    
    def get_strategy(self, name: str) -> ScoringStrategy:
        if name in self._strategy_cache:
            return self._strategy_cache[name]
        
        # Load from DB, instantiate, cache
        strategy = self._load_strategy_from_db(name)
        self._strategy_cache[name] = strategy
        return strategy
```

---

## 8. 实现计划

### Phase 4.1: 核心框架 (2-3 天)

- [ ] 创建 `src/services/procedural_memory.py`
- [ ] 实现 `ScoringStrategy` 抽象基类
- [ ] 实现 `StrategyRegistry` 和 `StrategySelector`
- [ ] 实现 `CalibrationRules`
- [ ] 创建 SQLite schema

### Phase 4.2: 预定义策略 (2-3 天)

- [ ] `DefaultStrategy` (基于现有 narrative_scorer)
- [ ] `ElderlyFriendlyStrategy`
- [ ] `TraumaSensitiveStrategy`
- [ ] `CulturalEastAsianStrategy`
- [ ] `BriefNarrativeStrategy`

### Phase 4.3: 集成与测试 (2 天)

- [ ] 集成到 `NarrativeScorerService`
- [ ] 编写单元测试 (strategy selection, calibration)
- [ ] 性能基准测试 (<5ms target)
- [ ] 编写使用文档

### Phase 4.4: 生产验证 (1-2 天)

- [ ] A/B 测试框架 (对比不同策略效果)
- [ ] 策略使用分析 (usage log)
- [ ] 用户反馈收集

---

## 9. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 策略选择逻辑过于复杂 | 延迟超标，难以调试 | 限制规则数量 (<20)，添加 usage log |
| 策略之间效果差异大 | 用户体验不一致 | 建立策略效果评估框架，定期校准 |
| calibration 过度拟合 | 泛化能力下降 | 限制 calibration 参数范围，添加正则化 |
| 文化刻板印象风险 | 伦理问题 | 文化策略基于实证研究，避免简化 |

---

## 10. 成功指标

| 指标 | 基线 | 目标 | 测量方式 |
|------|------|------|---------|
| strategy 选择延迟 | N/A | <5ms | 基准测试 |
| 用户满意度 (策略匹配度) | N/A | >80% | 用户调研 |
| scoring 一致性提升 | N/A | +15% | 重测信度 |
| 文化公平性改善 | N/A | +20% | 跨文化对比研究 |

---

## 11. 参考文献

1. **Anderson, J. R. (1983).** *The Architecture of Cognition.* Harvard University Press. (ACT-R 理论中的 procedural memory)
2. **Cohen, N. J., & Squire, L. R. (1980).** Preserved learning and retention of pattern-analyzing skill in amnesia. *Science, 210*(4466), 207-210.
3. **Schacter, D. L. (1987).** Implicit memory: History and current status. *Journal of Experimental Psychology: Learning, Memory, and Cognition, 13*(3), 501.

---

## 12. 附录：策略配置示例

### ElderlyFriendlyStrategy 配置

```json
{
  "name": "elderly_friendly",
  "version": "1.0.0",
  "dimension_weights": {
    "emotional_depth": 0.25,
    "cognitive_details": 0.15,
    "temporal_coherence": 0.15,
    "self_reflection": 0.20,
    "social_connection": 0.15,
    "growth_insight": 0.10
  },
  "adjustments": {
    "reduce_fluency_penalty": true,
    "increase_life_experience_bonus": true,
    "min_text_length": 30
  },
  "rationale": "老年人可能有更丰富的情感体验和人生智慧，但语言流畅度可能因年龄下降。降低流畅度权重，提升情感深度和自我反思权重。"
}
```

### TraumaSensitiveStrategy 配置

```json
{
  "name": "trauma_sensitive",
  "version": "1.0.0",
  "dimension_weights": {
    "emotional_depth": 0.20,
    "cognitive_details": 0.15,
    "temporal_coherence": 0.15,
    "self_reflection": 0.20,
    "social_connection": 0.10,
    "growth_insight": 0.20
  },
  "adjustments": {
    "reduce_negative_valence_penalty": true,
    "increase_growth_narrative_bonus": true,
    "avoid_pathologizing_language": true
  },
  "rationale": "创伤叙事可能包含负面情绪，但不应因此惩罚用户。强调成长洞察，避免病理化语言。"
}
```

---

*设计文档版本：1.0.0 (2026-04-04)*  
*验证等级：V0 (设计阶段)*  
*下一步：Phase 4.1 实现 (创建核心框架)*
