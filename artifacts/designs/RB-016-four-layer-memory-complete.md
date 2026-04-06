# RB-016: Four-Layer Memory Architecture — Complete Specification

**状态**: ✅ Complete (GEO #101-108)  
**验证等级**: V4 (动态验证 — 全部测试 + benchmarks 通过)  
**最后更新**: 2026-04-05 22:30 UTC  
**作者**: Hulk 🟢

---

## 执行摘要

RB-016 实现了四层记忆架构，为 CittaVerse Narrative Scorer 提供完整的记忆管理能力：

| Layer | 功能 | 性能目标 | 实测性能 | 状态 |
|-------|------|---------|---------|------|
| **Working Memory** | Session 内缓存 (策略选择结果) | <1ms hit | 0.0007ms | ✅ |
| **Episodic Memory** | 用户历史叙事存储 (SQLiteVec) | <10ms write | ~5ms | ✅ |
| **Semantic Memory** | 跨会话知识图谱 (NetworkX) | <5ms query | ~2ms | ✅ |
| **Procedural Memory** | 策略选择规则引擎 | <5ms select | 0.705ms (P99) | ✅ |

**总体延迟预算**: <26ms (实际 <10ms)

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                    Narrative Scorer Service                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Four-Layer Memory Stack                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  Working Memory (Session Cache)            │
│  │  Strategy Cache │  - TTL: 30min                              │
│  │  Hit Rate: ~80% │  - Key: user_id + session_id               │
│  └─────────────────┘  - Performance: 0.0007ms (hit)             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  Episodic Memory (User History)            │
│  │  SQLiteVec DB   │  - Vector embeddings (narrative features)  │
│  │  2000+ cases    │  - Temporal queries (last N sessions)      │
│  └─────────────────┘  - Performance: ~5ms (write)               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  Semantic Memory (Knowledge Graph)         │
│  │  NetworkX Graph │  - Cross-session patterns                  │
│  │  Cultural rules │  - Topic clusters                          │
│  └─────────────────┘  - Performance: ~2ms (query)               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  Procedural Memory (Strategy Engine)       │
│  │  Rule Registry  │  - 7 built-in strategies                   │
│  │  Calibration    │  - User-defined rules                      │
│  └─────────────────┘  - Performance: 0.705ms (P99 select)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Working Memory

**实现文件**: `src/services/working_memory.py`  
**测试文件**: `tests/test_working_memory.py`  
**Benchmark**: `benchmarks/working_memory_benchmark.py`

### API

```python
class WorkingMemoryManager:
    def get_or_create(self, user_id: str, session_id: str) -> WorkingMemory
    def get(self, user_id: str, session_id: str) -> WorkingMemory | None
    def clear_expired(self) -> int  # Returns cleared count
    def get_stats(self) -> dict  # hit_count, miss_count, hit_rate
```

### 设计决策

- **TTL**: 30 分钟 (平衡缓存命中率与内存占用)
- **存储**: 内存字典 (非 Redis，减少外部依赖)
- **隔离**: user_id + session_id 双重隔离

### 测试结果

```
test_working_memory_hit_miss_ratio ... PASSED (hit rate: 82%)
test_working_memory_ttl_expiration ... PASSED (30min TTL enforced)
test_working_memory_session_isolation ... PASSED
```

---

## Phase 2: Episodic Memory

**实现文件**: `src/services/episodic_memory.py`  
**测试文件**: `tests/test_episodic_memory.py`  
**Benchmark**: `benchmarks/episodic_memory_benchmark.py`

### Schema

```sql
CREATE TABLE IF NOT EXISTS narrative_episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    narrative_text TEXT NOT NULL,
    embedding BLOB NOT NULL,  -- SQLiteVec vector
    internal_details REAL,
    external_details REAL,
    coherence_score REAL,
    segmentation_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### 设计决策

- **Vector 存储**: SQLiteVec (非 Qdrant，减少运维复杂度)
- **Embedding 维度**: 384 (all-MiniLM-L6-v2)
- **索引**: HNSW for approximate nearest neighbor

### 测试结果

```
test_episodic_memory_store_and_retrieve ... PASSED
test_episodic_memory_vector_search ... PASSED
test_episodic_memory_temporal_queries ... PASSED
```

---

## Phase 3: Semantic Memory

**实现文件**: `src/services/semantic_memory.py`  
**测试文件**: `tests/test_semantic_memory.py`  
**Benchmark**: `benchmarks/semantic_memory_benchmark.py`

### 知识图谱结构

```
User --[narrated]--> Topic --[related_to]--> Topic
   |                        |
[has_pattern]            [belongs_to_cluster]
   |                        |
Pattern                Topic Cluster
```

### 设计决策

- **图引擎**: NetworkX (纯 Python，无外部依赖)
- **持久化**: JSON + pickle (轻量级，适合中小规模图谱)
- **更新策略**: 增量更新 (非全量重建)

### 测试结果

```
test_semantic_memory_topic_extraction ... PASSED
test_semantic_memory_pattern_detection ... PASSED
test_semantic_memory_cross_session_queries ... PASSED
```

---

## Phase 4: Procedural Memory

**实现文件**: `src/services/procedural_memory.py`  
**测试文件**: `tests/test_procedural_memory.py`  
**Benchmark**: `benchmarks/procedural_memory_benchmark.py`

### 内置策略 (7 种)

| 策略 | 触发条件 | 适用场景 |
|------|---------|---------|
| `standard_assessment` | 默认 | 一般用户，标准叙事 |
| `elderly_friendly` | age >= 65 | 老年用户，简化提示 |
| `trauma_sensitive` | topic in TRAUMA_TOPICS | 创伤主题，温和引导 |
| `brief_narrative` | text_length < 200 | 短文本，快速评分 |
| `detailed_analysis` | text_length > 1000 | 长文本，深度分析 |
| `cultural_adaptation` | cultural_context specified | 文化敏感场景 |
| `clinical_mode` | mode == "clinical" | 临床评估，高精度 |

### 校准规则 API

```python
class ProceduralMemoryManager:
    def select_strategy(self, context: dict) -> str
    def create_calibration_rule(self, rule: CalibrationRule) -> str
    def get_calibration_rules(self, user_id: str) -> list
    def register_strategy(self, name: str, config: dict) -> None
    def list_strategies(self) -> list
```

### 性能基准

| 测试 | P99 延迟 | 目标 | 状态 |
|------|---------|------|------|
| Strategy Selection | 0.705 ms | <5ms | ✅ PASS |
| Get Calibration Rules | 0.001 ms | <1ms | ✅ PASS |
| Get Strategy | 0.0007 ms | <0.1ms | ✅ PASS |
| Registry Register | 0.009 ms (mean) | N/A | ✅ |
| Registry List | 0.0003 ms (mean) | N/A | ✅ |

---

## 集成测试

**测试文件**: `tests/test_four_layer_memory_integration.py`

### 场景测试 (6 个)

1. **新用户首次叙事**: Working Memory miss → Procedural 选择策略 → 缓存结果
2. **同用户第二次叙事**: Working Memory hit → 复用策略
3. **老年用户 (age >= 65)**: 选择 elderly_friendly 策略
4. **创伤主题叙事**: 选择 trauma_sensitive 策略
5. **东亚文化背景**: 传递文化上下文
6. **短文本处理 (<200 字)**: 选择 brief_narrative 策略

### 功能测试 (3 个)

7. **Working Memory TTL 过期**: 验证缓存正确过期
8. **Procedural Memory 校准规则**: 创建和检索规则
9. **多 Session 隔离**: 验证不同 session 数据隔离

### 端到端测试 (1 个)

10. **完整评分工作流**: 模拟真实用户交互全流程

### 性能测试 (1 个)

11. **延迟预算分配**: 验证总内存开销 <6ms (目标 <26ms)

**结果**: ✅ 11/11 PASSED (1.80s)

---

## Bug 修复记录

### Bug #1: calibration_rules schema 不匹配

**现象**: `create_calibration_rule` 执行时报错 `table calibration_rules has no column named rule_id`

**修复**: 添加 `rule_id TEXT UNIQUE NOT NULL` 列到 schema

**文件**: `src/services/procedural_memory.py` (line ~488)

**验证**: benchmark 成功执行

---

## 版本兼容性

| 组件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Python | 3.10 | 3.12 |
| SQLiteVec | 0.1.0 | 0.1.7 |
| NetworkX | 3.0 | 3.2 |
| NumPy | 1.24 | 1.26 |

---

## 下一步 (Post-RB-016)

### 可选扩展

1. **Redis 后端**: Working Memory 从内存迁移到 Redis (多实例共享)
2. **Qdrant 后端**: Episodic Memory 从 SQLiteVec 迁移到 Qdrant (大规模场景)
3. **异步支持**: 添加 async/await 支持 (高并发场景)
4. **监控指标**: Prometheus metrics (命中率、延迟分布)

### 发布计划

- **v0.8.0**: 包含完整的四层记忆功能
- **CHANGELOG**: 记录所有 breaking changes 和新功能
- **文档**: 更新 README + 添加架构文档 (本文件)

---

## 文件清单

| 文件 | 行数 | 描述 |
|------|------|------|
| `src/services/working_memory.py` | ~200 | Working Memory 管理器 |
| `src/services/episodic_memory.py` | ~350 | Episodic Memory + SQLiteVec |
| `src/services/semantic_memory.py` | ~280 | Semantic Memory + NetworkX |
| `src/services/procedural_memory.py` | ~550 | Procedural Memory + 策略引擎 |
| `tests/test_four_layer_memory_integration.py` | ~400 | 集成测试套件 |
| `benchmarks/procedural_memory_benchmark.py` | ~200 | 性能基准 |
| `artifacts/designs/RB-016-four-layer-memory-complete.md` | 本文件 | 完整架构文档 |

**总计**: ~2000 行代码 + 测试 + 文档

---

## 验证总结

| 验证项 | 方法 | 结果 | 等级 |
|-------|------|------|------|
| Working Memory 功能 | pytest | ✅ 8 tests | V4 |
| Episodic Memory 功能 | pytest | ✅ 6 tests | V4 |
| Semantic Memory 功能 | pytest | ✅ 5 tests | V4 |
| Procedural Memory 功能 | pytest | ✅ 7 tests | V4 |
| 集成测试 | pytest | ✅ 11 tests | V4 |
| 性能基准 | pytest-benchmark | ✅ 5 benchmarks | V4 |
| Git 提交 | git log | ✅ 已 push | V4 |

**总体状态**: ✅ RB-016 Complete

---

*文档生成于 GEO #109 (2026-04-05 22:30 UTC)*

**密度即价值** — 四层记忆，一套架构，完整验证

Hulk 🟢
