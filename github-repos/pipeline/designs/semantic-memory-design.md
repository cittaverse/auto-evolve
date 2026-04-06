# Semantic Memory Design for VSNC

**Status**: Design Complete, Implementation Ready  
**Author**: Hulk 🟢 (GEO #104)  
**Created**: 2026-04-04  
**Related**: RB-016 Phase 3, Four-Layer Memory Architecture  

---

## Executive Summary

Semantic Memory stores abstract knowledge, scoring patterns, and cross-session statistics for VSNC. Unlike Episodic Memory (which stores raw narrative events), Semantic Memory aggregates knowledge across users and sessions to enable:

- **User-level trends**: "Is this user's narrative quality improving over time?"
- **Population baselines**: "How does this score compare to similar users?"
- **Calibration**: Dynamic threshold adjustment based on historical patterns
- **Knowledge accumulation**: Cross-session learning and pattern recognition

**Implementation**: `src/services/semantic_memory.py` (~400 lines)  
**Tests**: `tests/test_semantic_memory.py` (~20 tests)  
**Validation Target**: V4 (dynamic verification via pytest)

---

## 1. Purpose and Scope

### 1.1 What Semantic Memory Stores

| Category | Examples | Use Case |
|----------|----------|----------|
| **Score Aggregation** | User-level averages, population distributions | Trend analysis, percentile ranking |
| **Time-Series Trends** | Daily/weekly/monthly score trajectories | Progress tracking, intervention timing |
| **Calibration Parameters** | Dimension weights, thresholds, baselines | Personalized scoring, adaptive criteria |
| **General Knowledge** | Scoring rules, dimension definitions, quality heuristics | LLM reference, skill documentation |
| **Statistical Models** | Regression coefficients, clustering centers | Predictive analytics, anomaly detection |

### 1.2 What Semantic Memory Does NOT Store

- ❌ Raw narrative text (→ Episodic Memory)
- ❌ Session-level intermediate states (→ Working Memory)
- ❌ Executable skills (→ Procedural Memory)
- ❌ PII (personally identifiable information) without consent

---

## 2. Architecture

### 2.1 Data Model

```
┌─────────────────────────────────────────────────────────────────┐
│                     SemanticMemory                              │
├─────────────────────────────────────────────────────────────────┤
│  Tables:                                                         │
│  - user_stats: Per-user aggregated statistics                   │
│  - score_history: Raw score records (for time-series)           │
│  - population_baselines: Reference group distributions          │
│  - calibration_params: User-specific calibration                │
│  - knowledge_base: General scoring knowledge                    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Database Schema

```sql
-- User-level aggregated statistics
CREATE TABLE user_stats (
    user_id TEXT PRIMARY KEY,
    total_sessions INTEGER DEFAULT 0,
    avg_final_score REAL,
    avg_confidence REAL,
    best_score REAL,
    worst_score REAL,
    score_std REAL,
    last_session_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual score records (for time-series analysis)
CREATE TABLE score_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    narrative_id TEXT,
    final_score REAL NOT NULL,
    coherence REAL,
    emotional_richness REAL,
    narrative_depth REAL,
    linguistic_complexity REAL,
    authenticity REAL,
    temporal_structure REAL,
    confidence REAL,
    l1_adjustment INTEGER DEFAULT 0,
    l1_reasoning TEXT,
    metadata JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_stats(user_id)
);

-- Population baselines (reference groups)
CREATE TABLE population_baselines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_group TEXT NOT NULL,  -- e.g., 'all_users', 'age_60_70', 'high_education'
    metric TEXT NOT NULL,            -- e.g., 'final_score', 'coherence'
    mean REAL NOT NULL,
    std REAL NOT NULL,
    p25 REAL,
    p50 REAL,
    p75 REAL,
    p90 REAL,
    sample_size INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(reference_group, metric)
);

-- User-specific calibration parameters
CREATE TABLE calibration_params (
    user_id TEXT PRIMARY KEY,
    dimension_weights JSON,  -- Override default weights
    personal_baseline REAL,  -- User's historical average
    sensitivity_factor REAL DEFAULT 1.0,  -- Amplify/reduce score changes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_stats(user_id)
);

-- General knowledge base (scoring rules, heuristics)
CREATE TABLE knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,  -- e.g., 'scoring_rules', 'dimension_defs', 'quality_heuristics'
    key TEXT NOT NULL,
    value JSON NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category, key)
);

-- Indexes for performance
CREATE INDEX idx_score_history_user ON score_history(user_id);
CREATE INDEX idx_score_history_timestamp ON score_history(timestamp);
CREATE INDEX idx_score_history_user_timestamp ON score_history(user_id, timestamp);
CREATE INDEX idx_population_baselines_group ON population_baselines(reference_group);
```

---

## 3. API Design

### 3.1 Class Interface

```python
class SemanticMemory:
    """
    Semantic Memory for VSNC
    
    Stores and retrieves cross-session knowledge:
    - User-level score aggregation and trends
    - Population baselines and percentile ranking
    - Calibration parameters for personalized scoring
    - General knowledge base (scoring rules, definitions)
    """
    
    def __init__(self, db_path: str = "semantic_memory.db"):
        """Initialize semantic memory database"""
        pass
    
    # === Score Storage & Aggregation ===
    
    def store_score(self, user_id: str, session_id: str, scores: Dict, 
                    metadata: Optional[Dict] = None) -> None:
        """Store a score record and update user stats"""
        pass
    
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """Get aggregated statistics for a user"""
        pass
    
    def get_user_trend(self, user_id: str, days: int = 30, 
                       granularity: str = 'day') -> List[Dict]:
        """Get time-series trend for a user"""
        pass
    
    # === Population Baselines ===
    
    def update_population_baselines(self, reference_group: str = 'all_users') -> Dict:
        """Recalculate population baselines from score_history"""
        pass
    
    def get_percentile_rank(self, score: float, user_id: Optional[str] = None,
                           reference_group: str = 'all_users',
                           metric: str = 'final_score') -> float:
        """Calculate percentile rank for a score"""
        pass
    
    def get_baseline_stats(self, reference_group: str = 'all_users',
                          metric: str = 'final_score') -> Optional[Dict]:
        """Get baseline statistics for a reference group"""
        pass
    
    # === Calibration ===
    
    def set_calibration_params(self, user_id: str, 
                               dimension_weights: Optional[Dict] = None,
                               sensitivity_factor: float = 1.0) -> None:
        """Set user-specific calibration parameters"""
        pass
    
    def get_calibration_params(self, user_id: str) -> Optional[Dict]:
        """Get user-specific calibration parameters"""
        pass
    
    def apply_calibration(self, user_id: str, raw_scores: Dict) -> Dict:
        """Apply calibration to raw scores"""
        pass
    
    # === Knowledge Base ===
    
    def store_knowledge(self, category: str, key: str, value: Any,
                       version: int = 1) -> None:
        """Store a piece of general knowledge"""
        pass
    
    def get_knowledge(self, category: str, key: str, 
                     version: Optional[int] = None) -> Optional[Any]:
        """Retrieve knowledge by category and key"""
        pass
    
    def list_knowledge(self, category: str) -> List[Dict]:
        """List all knowledge entries in a category"""
        pass
    
    # === Analytics ===
    
    def get_score_distribution(self, reference_group: str = 'all_users',
                              metric: str = 'final_score',
                              bins: int = 10) -> Dict:
        """Get score distribution for analysis"""
        pass
    
    def detect_anomalies(self, user_id: str, window_days: int = 7,
                        z_threshold: float = 2.0) -> List[Dict]:
        """Detect anomalous scores for a user"""
        pass
    
    def get_cohort_analysis(self, cohort_field: str, 
                           metric: str = 'final_score') -> Dict:
        """Analyze scores by cohort (e.g., age group, education level)"""
        pass
    
    # === Maintenance ===
    
    def get_stats(self) -> Dict:
        """Get semantic memory statistics"""
        pass
    
    def export_user_data(self, user_id: str) -> Dict:
        """Export all data for a user (GDPR compliance)"""
        pass
    
    def delete_user_data(self, user_id: str) -> None:
        """Delete all data for a user (GDPR compliance)"""
        pass
```

### 3.2 Usage Examples

#### Example 1: Store and Retrieve Scores

```python
from src.services.semantic_memory import SemanticMemory

sm = SemanticMemory("semantic_memory.db")

# Store a score
sm.store_score(
    user_id="user_123",
    session_id="sess_456",
    scores={
        "final_score": 78,
        "coherence": 0.85,
        "emotional_richness": 0.72,
        "narrative_depth": 0.68,
        "linguistic_complexity": 0.81,
        "authenticity": 0.90,
        "temporal_structure": 0.75,
        "confidence": 0.82
    },
    metadata={"narrative_type": "life_story", "language": "zh-CN"}
)

# Get user stats
stats = sm.get_user_stats("user_123")
# {
#   "user_id": "user_123",
#   "total_sessions": 15,
#   "avg_final_score": 76.5,
#   "avg_confidence": 0.79,
#   "best_score": 88,
#   "worst_score": 62,
#   "score_std": 7.2,
#   "last_session_at": "2026-04-04T10:00:00Z"
# }

# Get trend (last 30 days, daily granularity)
trend = sm.get_user_trend("user_123", days=30, granularity='day')
# [
#   {"date": "2026-03-06", "avg_score": 74.2, "session_count": 2},
#   {"date": "2026-03-07", "avg_score": 75.8, "session_count": 1},
#   ...
# ]
```

#### Example 2: Percentile Ranking

```python
# Calculate percentile rank
percentile = sm.get_percentile_rank(
    score=78,
    user_id="user_123",
    reference_group="age_60_70",
    metric="final_score"
)
# 72.5  (score of 78 is better than 72.5% of reference group)

# Get baseline stats
baseline = sm.get_baseline_stats("age_60_70", "final_score")
# {
#   "reference_group": "age_60_70",
#   "metric": "final_score",
#   "mean": 71.3,
#   "std": 8.5,
#   "p25": 65.0,
#   "p50": 72.0,
#   "p75": 78.0,
#   "p90": 82.0,
#   "sample_size": 1250
# }
```

#### Example 3: Calibration

```python
# Set custom dimension weights for a user
sm.set_calibration_params(
    user_id="user_123",
    dimension_weights={
        "coherence": 0.25,         # Increase weight (default: 0.20)
        "emotional_richness": 0.15,  # Decrease weight (default: 0.20)
        "narrative_depth": 0.20,
        "linguistic_complexity": 0.15,
        "authenticity": 0.15,
        "temporal_structure": 0.10
    },
    sensitivity_factor=1.2  # Amplify score changes by 20%
)

# Apply calibration to raw scores
raw_scores = {"final_score": 75, "coherence": 0.80, ...}
calibrated_scores = sm.apply_calibration("user_123", raw_scores)
# {"final_score": 77.4, ...}  # Adjusted based on weights + sensitivity
```

#### Example 4: Knowledge Base

```python
# Store scoring rule
sm.store_knowledge(
    category="scoring_rules",
    key="l1_trigger_conditions",
    value={
        "confidence_threshold": 0.6,
        "score_range": [55, 75],
        "edge_case_keywords": ["metaphor", "poetry", "dialect"]
    }
)

# Retrieve scoring rule
rules = sm.get_knowledge("scoring_rules", "l1_trigger_conditions")
```

#### Example 5: Anomaly Detection

```python
# Detect anomalous scores (z-score > 2.0)
anomalies = sm.detect_anomalies("user_123", window_days=7, z_threshold=2.0)
# [
#   {
#     "session_id": "sess_789",
#     "score": 45,
#     "z_score": -2.8,
#     "timestamp": "2026-04-03T14:00:00Z",
#     "reason": "Score significantly below user's 7-day average"
#   }
# ]
```

---

## 4. Implementation Plan

### 4.1 File Structure

```
pipeline/
├── src/
│   └── services/
│       ├── semantic_memory.py          # ~400 lines (main implementation)
│       └── __init__.py                 # Export SemanticMemory
├── tests/
│   └── test_semantic_memory.py         # ~20 tests
├── benchmarks/
│   └── semantic_memory_benchmark.py    # Performance benchmarks
└── designs/
    └── semantic-memory-design.md       # This document
```

### 4.2 Implementation Phases

#### Phase 3.1: Core Storage & Retrieval (2-3 hours)
- Database schema creation
- `store_score()`, `get_user_stats()`, `get_user_trend()`
- Basic unit tests (8-10 tests)

#### Phase 3.2: Population Baselines (1-2 hours)
- `update_population_baselines()`, `get_percentile_rank()`, `get_baseline_stats()`
- Unit tests (4-5 tests)

#### Phase 3.3: Calibration System (1-2 hours)
- `set_calibration_params()`, `get_calibration_params()`, `apply_calibration()`
- Unit tests (4-5 tests)

#### Phase 3.4: Knowledge Base (1 hour)
- `store_knowledge()`, `get_knowledge()`, `list_knowledge()`
- Unit tests (3-4 tests)

#### Phase 3.5: Analytics & Maintenance (1-2 hours)
- `get_score_distribution()`, `detect_anomalies()`, `get_stats()`
- `export_user_data()`, `delete_user_data()` (GDPR compliance)
- Unit tests (4-5 tests)

**Total Estimated Effort**: 6-10 hours

---

## 5. Integration with Existing Components

### 5.1 Integration with NarrativeScorerService

```python
# In narrative_scorer_wrapper.py
from src.services.semantic_memory import SemanticMemory
from src.services.episodic_memory import EpisodicMemory
from src.services.working_memory import WorkingMemory

class NarrativeScorerService:
    def __init__(self, use_llm=False, session_id=None, enable_cache=True,
                 enable_semantic=True, enable_episodic=True):
        self.wm = WorkingMemory(session_id=session_id) if enable_cache else None
        self.em = EpisodicMemory() if enable_episodic else None
        self.sm = SemanticMemory() if enable_semantic else None
    
    def score(self, narrative: str, user_id: str = None, 
              metadata: Dict = None) -> Dict:
        # Check working memory cache
        if self.wm:
            cached = self.wm.get(f"score:{hash(narrative)}")
            if cached:
                return cached
        
        # Compute score
        result = self._compute_score(narrative)
        
        # Store in episodic memory (raw event)
        if self.em and user_id:
            self.em.add_event(
                event_id=f"evt_{uuid4()}",
                narrative_text=narrative,
                embedding=result['embedding'],
                metadata={**metadata, "scores": result['scores']}
            )
        
        # Store in semantic memory (aggregated knowledge)
        if self.sm and user_id:
            self.sm.store_score(
                user_id=user_id,
                session_id=self.wm.session_id if self.wm else "anon",
                scores=result['scores'],
                metadata=metadata
            )
        
        # Cache in working memory
        if self.wm:
            self.wm.set(f"score:{hash(narrative)}", result)
        
        return result
```

### 5.2 Integration with REMem (REMEMemoryGraph)

```python
# REMem stores rich episodic graphs
# Semantic Memory stores aggregated statistics
# Link via user_id and session_id

# In remem_memory_graph.py
class REMEMemoryGraph:
    def store_narrative(self, user_id: str, narrative: str, 
                       segmentation: Dict) -> str:
        session_id = self._create_session(user_id, narrative)
        
        # Store rich episodic graph
        graph = self._build_graph(segmentation)
        self.graph_store.store(session_id, graph)
        
        # Update semantic memory with aggregated stats
        if self.semantic_memory:
            self.semantic_memory.increment_session_count(user_id)
        
        return session_id
```

---

## 6. Performance Targets

| Operation | Target Latency | Notes |
|-----------|---------------|-------|
| `store_score()` | <10ms | INSERT + UPDATE user_stats |
| `get_user_stats()` | <5ms | Single SELECT by user_id |
| `get_user_trend(30 days)` | <20ms | GROUP BY date, indexed |
| `get_percentile_rank()` | <10ms | Pre-computed baselines |
| `apply_calibration()` | <1ms | In-memory calculation |
| `detect_anomalies()` | <50ms | Window aggregation + z-score |

**Storage Estimates**:
- score_history: ~500 bytes/record × 10K records = ~5MB
- user_stats: ~200 bytes/user × 1K users = ~200KB
- population_baselines: ~100 bytes/row × 100 rows = ~10KB
- calibration_params: ~200 bytes/user × 100 users = ~20KB
- knowledge_base: ~500 bytes/entry × 50 entries = ~25KB
- **Total (1K users, 10K scores)**: ~5.2MB

---

## 7. Validation Criteria

### 7.1 Unit Tests (V4)

- [ ] Database initialization and schema creation
- [ ] Score storage and retrieval
- [ ] User stats aggregation (correct averages, counts)
- [ ] Time-series trend calculation (correct grouping)
- [ ] Percentile rank calculation (correct statistics)
- [ ] Calibration parameter storage and application
- [ ] Knowledge base CRUD operations
- [ ] Anomaly detection (correct z-score calculation)
- [ ] GDPR export/delete (complete data removal)
- [ ] Concurrent access (thread safety)

### 7.2 Integration Tests (V4)

- [ ] NarrativeScorerService integration (end-to-end scoring flow)
- [ ] WorkingMemory + EpisodicMemory + SemanticMemory coordination
- [ ] Population baseline updates (batch processing)

### 7.3 Performance Benchmarks (V4)

- [ ] Latency targets met for all operations
- [ ] Storage efficiency within estimates
- [ ] Scalability test (10K scores, 1K users)

---

## 8. Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Database lock contention | Medium | Medium | Use WAL mode, batch writes |
| Privacy concerns (user data) | High | High | Anonymization, GDPR export/delete |
| Baseline calculation cost | Medium | Low | Incremental updates, scheduled jobs |
| Calibration complexity | Low | Medium | Start with simple weights, iterate |

---

## 9. Future Enhancements

### 9.1 Advanced Analytics (Post-MVP)

- **Predictive modeling**: Forecast future score trajectories
- **Clustering**: Identify user segments with similar patterns
- **Causal inference**: Estimate intervention effects

### 9.2 Real-Time Features

- **Streaming updates**: Real-time baseline recalculation
- **WebSocket notifications**: Alert on anomalies/milestones
- **Dashboard integration**: Live trend visualization

### 9.3 Multi-Modal Extensions

- **Voice biomarkers integration**: Store acoustic features alongside scores
- **Cross-modal correlation**: Link voice patterns to narrative quality

---

## 10. Files and Artifacts

| File | Status | Description |
|------|--------|-------------|
| `designs/semantic-memory-design.md` | ✅ This document | Comprehensive design specification |
| `src/services/semantic_memory.py` | ⏳ Pending | Main implementation (~400 lines) |
| `tests/test_semantic_memory.py` | ⏳ Pending | Unit tests (~20 tests) |
| `benchmarks/semantic_memory_benchmark.py` | ⏳ Pending | Performance benchmarks |
| `memory/2026-04-04-geo-iteration-104.md` | ⏳ To be created | GEO #104 iteration log |

---

## 11. Handoff Notes

**For Core** (Engineering Implementation):

- ✅ Design complete, ready for implementation
- Follow implementation plan in Section 4.2
- Priority: Phase 3.1 (Core Storage) first, then expand
- Integration point: `narrative_scorer_wrapper.py`

**For V** (Decision Points):

- Reference group definitions: What cohorts matter? (age, education, region?)
- Privacy policy: What data can be stored? What requires consent?
- Baseline update frequency: Real-time, daily, or weekly?

---

*Document Version: 1.0*  
*Created: 2026-04-04*  
*Author: Hulk 🟢*
