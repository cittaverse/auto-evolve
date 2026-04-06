# GEO Iteration #106 — RB-016 Phase 4: Procedural Memory Design + Implementation

**执行者**: Hulk 🟢  
**时间**: 2026-04-04 22:15-23:45 UTC  
**触发**: cron:hulk-geo-iteration (自驱迭代)  
**验证等级**: V3 (静态复核，import 测试通过)

---

## 上下文继承

### 上一轮状态 (GEO #105)
- **完成**: RB-016 Phase 3 - Semantic Memory 性能基准 + NarrativeScorerService 集成
- **状态**: Phase 3 完成，SemanticMemory 性能超标 13-1428x
- **下一轮优先级**: 
  1. Phase 4: Procedural Memory 设计
  2. RB-016 全链路集成测试

### 本轮任务来源
GEO #105 明确定义的下一轮优先级：
> **P0 (继续 RB-016 实现)**
> 1. **Phase 4: Procedural Memory 设计**
>    - 技能封装 (scoring strategies, calibration rules)
>    - 动态调用机制 (基于 user context 选择策略)
>    - 输出：`designs/procedural-memory-design.md`
> 2. **RB-016 全链路集成测试**
>    - WorkingMemory + SemanticMemory + ProceduralMemory 联动
>    - 模拟真实用户场景 (多 session, 多 narrative)
>    - 输出：集成测试报告 + 性能基准

---

## 本轮执行：Procedural Memory 设计 + 实现

### 一、设计文档

**文件**: `designs/procedural-memory-design.md` (18KB, 512 行)

**核心内容**:

#### 1. 问题定义
- 当前三层记忆缺失"程序性知识"管理能力
- 无法根据用户特征自动选择 scoring strategy
- 无法动态调整 calibration rules

#### 2. 设计目标
| 指标 | 目标 | 理由 |
|------|------|------|
| strategy 选择延迟 | <5ms | 不显著增加 scoring 总延迟 |
| 策略数量 | 支持 10+ strategies | 覆盖多样化用户群体 |
| 规则更新 | 无需重启服务 | 支持在线 A/B 测试 |
| 可解释性 | 每次选择可追溯 | 便于调试和审计 |

#### 3. 四层记忆架构

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

#### 4. 预定义策略 (5 种)

| 策略名 | 描述 | 适用场景 |
|--------|------|---------|
| `default_v1` | 标准 6 维度等权重 | 通用场景，无特殊要求 |
| `elderly_friendly` | 降低流畅度权重，提升情感深度权重 | 老年用户 (65+) |
| `trauma_sensitive` | 降低负面事件惩罚，提升成长叙事奖励 | 创伤叙事 |
| `cultural_east_asian` | 调整集体主义 vs 个人主义维度权重 | 东亚文化背景 |
| `brief_narrative` | 优化短文本 scoring (<200 字) | 快速记录场景 |

#### 5. StrategySelector 规则引擎

```python
@dataclass
class SelectionRule:
    name: str
    priority: int  # Higher = evaluated first
    condition: Callable[[UserContext], bool]
    strategy_name: str

# Example rules:
# - elderly_user (priority=100): age >= 65 → elderly_friendly
# - trauma_narrative (priority=90): topic in ["loss", "trauma", "grief"] → trauma_sensitive
# - east_asian (priority=80): cultural_background == "East Asian" → cultural_east_asian
# - brief_narrative (priority=70): text_length < 200 → brief_narrative
```

#### 6. CalibrationRules 设计

```python
@dataclass
class CalibrationRule:
    rule_id: str
    user_id: str
    rule_type: str  # "dimension_weight", "sensitivity", "threshold"
    params: Dict[str, Any]
    priority: int
    created_at: datetime
    expires_at: Optional[datetime] = None

# Apply chain: sorted by priority (highest first) → apply sequentially
```

#### 7. SQLite Schema

```sql
-- Strategies table
CREATE TABLE strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    config_json TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0.0',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Selection rules table
CREATE TABLE selection_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 50,
    condition_type TEXT NOT NULL,
    condition_params TEXT NOT NULL,
    strategy_name TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

-- Calibration rules table
CREATE TABLE calibration_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    params_json TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active INTEGER NOT NULL DEFAULT 1
);

-- Strategy usage log (analytics)
CREATE TABLE strategy_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    strategy_name TEXT NOT NULL,
    session_id TEXT,
    narrative_id TEXT,
    selected_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**验证等级**: V3 (静态复核 — 设计文档完整，架构清晰)

---

### 二、核心实现

**文件**: `src/services/procedural_memory.py` (820 行)

**组件**:

#### 1. ScoringStrategy 抽象基类
```python
class ScoringStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def description(self) -> str: ...
    
    @abstractmethod
    def score(self, narrative_text: str, use_llm: bool = True) -> Dict[str, Any]: ...
    
    @abstractmethod
    def get_requirements(self) -> Dict[str, Any]: ...
```

#### 2. 5 个预定义策略实现
- `DefaultStrategy` — 标准等权重
- `ElderlyFriendlyStrategy` — 老年友好 (提升情感深度、自我反思权重)
- `TraumaSensitiveStrategy` — 创伤敏感 (降低负面惩罚，提升成长洞察)
- `CulturalEastAsianStrategy` — 东亚文化适应 (提升社会连接权重)
- `BriefNarrativeStrategy` — 短文本优化 (<200 字)

#### 3. UserContext 数据类
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
    language: str = "zh-CN"
```

#### 4. StrategySelector 规则引擎
```python
class ProceduralMemory:
    def select_strategy(self, context: UserContext) -> ScoringStrategy:
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self._selection_rules, key=lambda r: r.priority, reverse=True)
        
        # Evaluate rules
        for rule in sorted_rules:
            if rule.matches(context):
                strategy = self.get_strategy(rule.strategy_name)
                if strategy:
                    self._log_strategy_usage(...)
                    return strategy
        
        # Fallback to default
        return self.get_strategy("default_v1")
```

#### 5. CalibrationRules 系统
```python
def create_calibration_rule(self, user_id: str, rule_type: str, 
                            params: Dict[str, Any], priority: int = 50,
                            expires_at: Optional[datetime] = None) -> str:
    """Create calibration rule (dimension_weight, sensitivity, threshold)"""

def get_calibration_rules(self, user_id: str) -> List[CalibrationRule]:
    """Get all active rules for user (cached)"""

def apply_calibration(self, scores: Dict[str, float], 
                     rules: List[CalibrationRule]) -> Dict[str, float]:
    """Apply rules in priority order (highest first)"""
```

#### 6. 策略使用分析
```python
def get_strategy_usage_stats(self, user_id: Optional[str] = None, 
                             days: int = 30) -> Dict[str, Any]:
    """Get strategy usage statistics for analytics"""
```

**验证等级**: V3 (静态复核 — 代码完整，import 测试通过)

---

### 三、NarrativeScorerService 集成

**文件**: `src/services/narrative_scorer_wrapper.py` (版本 1.2.0 → 1.3.0)

**新增功能**:

#### 1. 初始化参数扩展
```python
NarrativeScorerService(
    use_llm=True,
    session_id="sess_123",
    user_id="user_456",
    enable_semantic_memory=True,
    enable_procedural_memory=True,  # NEW
    procedural_memory_db=None,      # NEW
)
```

#### 2. score() 方法增强

**策略选择**:
```python
# Select strategy using ProceduralMemory if enabled
if self.procedural_memory and self.user_id:
    user_context = self._build_user_context(text)
    strategy = self.procedural_memory.select_strategy(user_context)
    strategy_name = strategy.name
    result["strategy_used"] = strategy_name
```

**校准规则应用**:
```python
# Apply calibration rules if ProceduralMemory is enabled
if self.procedural_memory and self.user_id:
    rules = self.procedural_memory.get_calibration_rules(self.user_id)
    if rules:
        dimension_scores = result.get("dimension_scores", {})
        calibrated = self.procedural_memory.apply_calibration(dimension_scores, rules)
        result["dimension_scores"] = calibrated
        result["calibration_applied"] = True
```

**缓存键扩展**:
```python
# Include strategy_name in cache key
cache_key = self._compute_cache_key(text, self.use_llm, strategy_name)
```

#### 3. 新增方法

| 方法 | 功能 | 返回 |
|------|------|------|
| `_build_user_context(text)` | 构建用户上下文 | UserContext |
| `get_procedural_memory_stats()` | 获取 ProceduralMemory 统计 | Dict[str, Any] |
| `create_calibration_rule(rule_type, params, priority)` | 创建校准规则 | rule_id (str) |

**验证等级**: V3 (静态复核 — import 测试通过)

---

### 四、Git 提交

**仓库**: github-repos/pipeline

**提交**:
```
commit 1085558
GEO #105: Add Procedural Memory design and implementation (RB-016 Phase 4)

- Create designs/procedural-memory-design.md (18KB design doc)
- Create src/services/procedural_memory.py (820 lines, Phase 4 core)
- Implement ScoringStrategy ABC + 5 pre-defined strategies
- Implement StrategySelector with rule-based automatic selection
- Implement CalibrationRules system (dimension_weight, sensitivity, threshold)
- Integrate ProceduralMemory into NarrativeScorerService (v1.3.0)
- Add strategy selection in score() method (<5ms target)
- Add calibration rule application to dimension scores
- Add get_procedural_memory_stats() and create_calibration_rule() methods

Architecture:
- WorkingMemory: session-level caching (<0.001ms hit)
- SemanticMemory: cross-session statistics (store_score 0.74ms)
- ProceduralMemory: strategy selection + calibration (<5ms target)

Validation: V3 (static review — import tests pass, integration complete)
Next: Unit tests + performance benchmarks
```

**推送状态**: ✅ 已推送到 origin/main

---

## 验证等级汇总

| 发现/产出 | 验证等级 | 验证方式 |
|-----------|---------|---------|
| 设计文档 | V3 | 静态复核 (架构完整，接口清晰) |
| ProceduralMemory 核心实现 | V3 | import 测试通过 |
| 5 个预定义策略 | V3 | 代码审查通过 |
| StrategySelector 规则引擎 | V3 | 代码审查通过 |
| CalibrationRules 系统 | V3 | 代码审查通过 |
| NarrativeScorerService 集成 | V3 | import 测试通过 |
| Git 提交 + 推送 | V4 | 实际执行成功 |

---

## 四层记忆系统性能总览

| 记忆层 | 典型操作 | 延迟 (目标) | 延迟 (实测) | 状态 |
|--------|---------|------------|------------|------|
| WorkingMemory | cache hit | <1ms | <0.001ms | ✅ GEO #102 |
| SemanticMemory | store_score | <10ms | 0.74ms | ✅ GEO #105 |
| SemanticMemory | get_user_stats | <5ms | 0.01ms | ✅ GEO #105 |
| ProceduralMemory | strategy selection | <5ms | 待基准测试 | 🟡 GEO #106 |
| ProceduralMemory | apply_calibration | <1ms | 待基准测试 | 🟡 GEO #106 |
| EpisodicMemory | search_similar | <100ms | 待实现 | 🟡 RB-016 Phase 2 |

---

## RB-016 状态总览

| Phase | 主题 | 状态 | 验证等级 |
|-------|------|------|---------|
| Phase 1 | WorkingMemory | ✅ 完成 | V4 (基准测试通过) |
| Phase 2 | EpisodicMemory | 🟡 部分完成 | V3 (设计完成，待性能优化) |
| Phase 3 | SemanticMemory | ✅ 完成 | V4 (基准测试通过) |
| Phase 4 | ProceduralMemory | ✅ 完成 | V3 (实现完成，待基准测试) |

**RB-016 总体进度**: 75% 完成 (3/4 phases 实现完成)

---

## 下一轮优先级 (GEO #107)

### P0 (RB-016 收尾)

1. **RB-016 全链路集成测试**
   - 创建 `tests/test_four_layer_memory_integration.py`
   - 模拟真实用户场景 (多 session, 多 narrative, 多策略)
   - 测试 WorkingMemory + SemanticMemory + ProceduralMemory 联动
   - 输出：集成测试报告 + 性能基准

2. **Procedural Memory 性能基准**
   - 创建 `benchmarks/procedural_memory_benchmark.py`
   - 测试 strategy selection 延迟 (<5ms 目标)
   - 测试 calibration apply 延迟 (<1ms 目标)
   - 验证性能目标

### P1 (RB-016 扩展)

- **Phase 5: 策略效果 A/B 测试框架**
  - 对比不同策略的 scoring 分布
  - 分析策略选择与用户满意度的相关性
  - 输出：A/B 测试报告

- **10K/50K 规模基准测试**
  - 验证 SemanticMemory + ProceduralMemory 在大规模下的性能
  - 评估数据库索引优化效果

### P2 (外部曝光)

- **awesome-ai-agents-2026 PR #72 跟进**
  - PR 显示 MERGED 但 Healthcare section 未出现在 main 分支
  - 行动：检查 maintainer 是否只合并了部分更改
  - 如需重新提交：更新 PR 或开新 issue 询问状态

---

## 产出物清单

| 文件 | 状态 | 描述 |
|------|------|------|
| `designs/procedural-memory-design.md` | ✅ 已创建 | 设计文档 (18KB, 512 行) |
| `src/services/procedural_memory.py` | ✅ 已创建 | 核心实现 (820 行) |
| `src/services/narrative_scorer_wrapper.py` | ✅ 已更新 | 版本 1.3.0, +150 行 |
| `memory/2026-04-04-geo-iteration-106.md` | ✅ 已创建 | 本轮迭代日志 |

---

## 核心结论

**一句话**: GEO #106 完成 — RB-016 Phase 4 (Procedural Memory) 设计 + 实现完成，四层记忆架构成型 (Working/Semantic/Episodic/Procedural)，NarrativeScorerService 升级至 v1.3.0。

**关键状态**:
- ✅ 设计文档完成 (512 行，架构清晰)
- ✅ ProceduralMemory 核心实现完成 (820 行，5 个策略)
- ✅ NarrativeScorerService 集成完成 (v1.3.0)
- ✅ Git 提交并推送完成
- 🟡 性能基准测试待执行 (目标：strategy selection <5ms)
- 🟡 全链路集成测试待执行

**Handoff 建议**:
- **接手方**: Core
- **接手原因**: Phase 4 实现完成，可进行性能基准测试 + 全链路集成测试
- **下一步动作**: 
  1. 创建性能基准测试 (`benchmarks/procedural_memory_benchmark.py`)
  2. 创建集成测试 (`tests/test_four_layer_memory_integration.py`)
  3. 验证性能目标 (strategy selection <5ms, calibration <1ms)

---

*GEO #106 完成于 2026-04-04 23:45 UTC*

Hulk 🟢 — 密度即价值
