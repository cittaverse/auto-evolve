# Agent Memory Four-Layer Architecture for VSNC

**Status**: Design Complete, Phase 1 Implementation Complete (WorkingMemory)  
**Author**: Hulk 🟢 (GEO #100, GEO #101)  
**Created**: 2026-04-03  
**Last Updated**: 2026-04-03 16:30 UTC  
**Validation**: V3 (static review of design + V4 for WorkingMemory implementation)

---

## Executive Summary

This document presents a comprehensive four-layer memory architecture for VSNC (Vocal Story Narrative Center), inspired by arXiv:2603.07670 "LLM Agent Memory: A Comprehensive Survey" (RB-015). The architecture maps theoretical memory layers to practical VSNC implementation:

- **Working Memory**: Session-level caching ✅ **IMPLEMENTED (GEO #101)**
- **Episodic Memory**: Narrative event storage with vector retrieval 🟡 **DESIGNED**
- **Semantic Memory**: Cross-session knowledge aggregation 🟡 **DESIGNED**
- **Procedural Memory**: Executable scoring skills 🟡 **DESIGNED**

**Implementation Roadmap**: 11-16 days total (Phase 1 complete, Phases 2-5 pending)

---

## 1. Motivation

### 1.1 Current VSNC Memory Architecture Gaps

| Memory Layer | Current State | Coverage | Gap |
|--------------|--------------|----------|-----|
| **Working Memory** | ❌ Not implemented | 0% | No session-level caching, redundant computation |
| **Episodic Memory** | ✅ Partial | 60% | Raw text storage only, no structured indexing |
| **Semantic Memory** | ✅ Partial | 70% | L0 scores stored, no cross-session aggregation |
| **Procedural Memory** | ❌ Not implemented | 0% | Scoring流程 hard-coded, not dynamically callable |

### 1.2 Problems Without Memory Architecture

1. **Performance**: Repeated computation of same narratives (50-100ms waste per sample)
2. **No Personalization**: Cannot answer "Is this user's narrative quality improving?"
3. **No Retrieval**: Cannot find similar historical narratives for comparison
4. **Rigid Pipeline**: Cannot support meta-instructions like "re-score with stricter criteria"

---

## 2. Architecture Design

### 2.1 Layer Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Request                              │
│   "Score this narrative" / "Re-score with stricter criteria"     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Procedural Memory (Skills)                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ l0_score     │ │ l1_arbitrate │ │ compare      │            │
│  │ (std/strict) │ │ (edge cases) │ │ (diff)       │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                    LLM natural language calls                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Working Memory (Cache)                        │
│  - Session-level intermediate state caching                      │
│  - Reduce redundant computation                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Episodic Memory (Events)                      │
│  - Raw narrative text + metadata                                 │
│  - Vector index + hybrid retrieval                               │
│  - Links to semantic score results                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Semantic Memory (Knowledge)                   │
│  - Score aggregation + trend analysis                            │
│  - Population baselines + percentile ranking                     │
│  - Cross-session knowledge accumulation                          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Working Memory (Implemented)

**File**: `src/services/working_memory.py`

**Purpose**: Session-level short-term caching for intermediate states

**API**:
```python
from src.services.working_memory import WorkingMemory

wm = WorkingMemory(session_id="sess_123", ttl_seconds=3600)

# Cache L0 scores
wm.set("l0_scores", {
    "coherence": 0.85,
    "final_score": 76,
    "confidence": 0.78
})

# Retrieve
scores = wm.get("l0_scores")
if scores is None:
    # Cache miss, recompute
    scores = compute_l0_scores(narrative)
    wm.set("l0_scores", scores)

# Statistics
stats = wm.get_stats()
# {
#   "session_id": "sess_123",
#   "cache_size": 3,
#   "hit_rate": 0.85,
#   ...
# }
```

**Features**:
- ✅ TTL-based expiration
- ✅ Hit/miss tracking
- ✅ Cache statistics
- ✅ Multi-session management via `WorkingMemoryManager`
- ✅ Convenience functions (`get_working_memory()`)

**Tests**: 22 unit tests, all passing (V4 validation)

**Performance Target**: <10ms access latency (in-memory)

---

### 2.3 Episodic Memory (Designed)

**Purpose**: Store narrative events with structured metadata and vector indexing

**Design**:
```python
class EpisodicMemory:
    """
    Episodic Memory for VSNC
    
    Stores:
    - Raw narrative text
    - Metadata: timestamp, participant ID, narrative type
    - Structured index: event segments, emotional valence, keywords
    - Links to corresponding semantic score results
    
    Retrieval:
    - Semantic similarity search (vector index)
    - Metadata filtering (time range, narrative type)
    - Hybrid: vector + metadata
    """
    
    def __init__(self, db_path: str):
        self.db = SQLiteVecDB(db_path)  # Vector + relational DB
    
    def store(self, narrative: str, metadata: Dict):
        embedding = get_embedding(narrative)
        self.db.insert({
            'text': narrative,
            'metadata': metadata,
            'embedding': embedding,
            'timestamp': datetime.utcnow()
        })
    
    def retrieve(self, query: str, filters: Dict, top_k: int = 5):
        query_embedding = get_embedding(query)
        results = self.db.search(
            query_embedding=query_embedding,
            filters=filters,
            top_k=top_k
        )
        return results
```

**Technology Options**:
- **SQLiteVec**: Lightweight, embedded, good for prototyping
- **Qdrant**: Production-grade, better performance at scale

**VSNC Mapping**:
- Current gap: No vector index, no structured metadata
- Enhancement: Add embedding storage, metadata schema, episodic↔semantic links

**Validation**: V0 (design inference)

---

### 2.4 Semantic Memory (Designed)

**Purpose**: Store abstract knowledge, scoring patterns, cross-session statistics

**Design**:
```python
class SemanticMemory:
    """
    Semantic Memory for VSNC
    
    Stores:
    - Score aggregation: user-level / population-level statistics
    - Narrative quality trends: time-series analysis
    - Calibration parameters: dimension weights, thresholds, baselines
    - General knowledge: scoring rules, dimension definitions
    
    Applications:
    - Answer "Is this user's narrative quality improving?"
    - Provide population baselines (percentile ranking)
    - Dynamic threshold adjustment (personalized calibration)
    """
    
    def __init__(self, db_path: str):
        self.db = SQLiteDB(db_path)
    
    def store_score(self, user_id: str, session_id: str, scores: Dict):
        self.db.insert('scores', {
            'user_id': user_id,
            'session_id': session_id,
            'scores': scores,
            'timestamp': datetime.utcnow()
        })
        self._update_user_stats(user_id)
    
    def get_user_trend(self, user_id: str, days: int = 30):
        trend = self.db.query(
            'SELECT AVG(final_score), DATE(timestamp) '
            'FROM scores WHERE user_id = ? '
            'AND timestamp >= datetime("now", "-{} days") '
            'GROUP BY DATE(timestamp)'.format(days),
            (user_id,)
        )
        return trend
    
    def get_percentile_rank(self, score: float, reference_group: str = 'age_matched'):
        ref_scores = self.db.get_reference_group(reference_group)
        percentile = sum(1 for s in ref_scores if s < score) / len(ref_scores)
        return percentile * 100
```

**VSNC Mapping**:
- Current gap: Scores stored in isolation, no cross-session aggregation
- Enhancement: User-level score history, time-series trends, population baselines

**Validation**: V0 (design inference)

---

### 2.5 Procedural Memory (Designed)

**Purpose**: Store executable scoring skills, support dynamic invocation and modification

**Design**:
```python
class ProceduralMemory:
    """
    Procedural Memory for VSNC
    
    Stores:
    - Scoring skills: L0 rule engine, L1 arbitration, fusion algorithms
    - Skill metadata: input/output schema, preconditions, performance benchmarks
    - Skill variants: strict/lenient/fast versions
    
    Execution:
    - LLM can call skills via natural language
    - Support skill composition (pipeline)
    - Support skill modification (meta-instructions)
    
    Examples:
    - "Re-score with stricter criteria" → call strict L0 variant
    - "Score only emotion dimension" → call single-dimension skill
    - "Compare two narratives" → call comparison skill
    """
    
    def __init__(self):
        self.skills: Dict[str, Callable] = {}
        self.skill_metadata: Dict[str, Dict] = {}
    
    def register_skill(self, name: str, func: Callable, metadata: Dict):
        """Register a skill"""
        self.skills[name] = func
        self.skill_metadata[name] = metadata
    
    def execute(self, skill_name: str, inputs: Dict) -> Any:
        """Execute a skill"""
        if skill_name not in self.skills:
            raise ValueError(f"Unknown skill: {skill_name}")
        return self.skills[skill_name](**inputs)
    
    def get_skill_info(self, skill_name: str) -> Dict:
        """Get skill info (for LLM reference)"""
        return self.skill_metadata.get(skill_name, {})

# Skill registration example
procedural_memory = ProceduralMemory()

procedural_memory.register_skill(
    name='l0_score',
    func=l0_narrative_scorer,
    metadata={
        'description': 'L0 rule engine fast scoring (6 dimensions)',
        'input_schema': {'narrative': 'str'},
        'output_schema': {'scores': 'dict', 'confidence': 'float'},
        'latency_p95': '100ms',
        'variants': ['standard', 'strict', 'lenient']
    }
)

procedural_memory.register_skill(
    name='l1_arbitrate',
    func=llm_arbitration,
    metadata={
        'description': 'L1 LLM arbitration (edge case correction)',
        'input_schema': {'narrative': 'str', 'l0_scores': 'dict'},
        'output_schema': {'adjustment': 'int', 'reasoning': 'str'},
        'latency_p95': '3s',
        'trigger_condition': 'confidence < 0.6 or 55 <= score <= 75'
    }
)
```

**VSNC Mapping**:
- Current gap: Scoring流程 hard-coded in Python scripts
- Enhancement: Encapsulate skills as callable functions, register metadata, support composition

**Validation**: V0 (design inference)

---

## 3. Data Flow Examples

### 3.1 Basic Scoring Flow

```
1. User submits narrative → WorkingMemory.cache("narrative_text")
2. L0 scoring → WorkingMemory.cache("l0_scores")
3. Check L1 trigger → if triggered, call ProceduralMemory.execute("l1_arbitrate")
4. Store final score → EpisodicMemory.store(narrative, metadata)
5. Update statistics → SemanticMemory.store_score(user_id, session_id, scores)
```

### 3.2 Re-score with Stricter Criteria

```
1. LLM parses request → intent: re-score + strict + time range (last week)
2. ProceduralMemory query → select skill: l0_score (variant='strict')
3. EpisodicMemory retrieval → hybrid query:
   - Time filter: timestamp >= last_week
   - Semantic search: query = "last week narrative"
   - Return: top 1 match
4. WorkingMemory cache → store retrieved narrative
5. ProceduralMemory execute → strict_l0_score(narrative)
6. SemanticMemory update → store new score, update user trend
7. Response generation → LLM integrates: "Your strict score: 72 (original: 78)"
```

---

## 4. Implementation Roadmap

| Phase | Task | Effort | Dependencies | Target Validation | Status |
|-------|------|--------|--------------|-------------------|--------|
| **Phase 1** | Working Memory implementation | 1-2 days | None | V4 | ✅ **COMPLETE (GEO #101)** |
| **Phase 2** | Episodic Memory enhancement (vector index) | 3-4 days | SQLiteVec/Qdrant selection | V4 | 🟡 Pending |
| **Phase 3** | Semantic Memory enhancement (aggregation) | 2-3 days | Phase 2 complete | V4 | 🟡 Pending |
| **Phase 4** | Procedural Memory implementation | 3-4 days | Phases 1-3 complete | V4 | 🟡 Pending |
| **Phase 5** | Four-layer integration + E2E testing | 2-3 days | Phases 1-4 complete | V4 | 🟡 Pending |

**Total Estimated Effort**: 11-16 days

---

## 5. Integration with Multi-Agent Scorer v0.6

### 5.1 Architectural Complementarity

| Component | Multi-Agent Scorer v0.6 | Agent Memory Architecture |
|-----------|------------------------|--------------------------|
| **Focus** | Scoring validity (anti-gaming/arbitration) | Memory enhancement (storage/retrieval/skills) |
| **L1 Arbitration** | LLM real-time analysis | Can retrieve historical cases (episodic) |
| **Validation Control** | Statistical thresholds | Can learn historical trigger patterns (semantic) |
| **Scoring Skills** | Hard-coded流程 | Callable/composable skills (procedural) |

### 5.2 Integration Opportunities

1. **L1 Arbitration Enhancement**:
   - Retrieve similar historical cases (episodic)
   - Reference historical arbitration adjustment patterns (semantic)
   - Call "arbitration skill" instead of hard-coded prompt (procedural)

2. **Validation Strength Controller Enhancement**:
   - Store historical trigger rates (semantic)
   - Dynamically adjust thresholds based on learned patterns (procedural)

3. **Anti-Gaming Module Enhancement**:
   - Retrieve historical gaming cases (episodic)
   - Learn gaming detection rules (semantic)

---

## 6. Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Vector database selection difficulty | Medium | Medium | Start with SQLiteVec (lightweight), migrate to Qdrant (production) |
| Skill encapsulation complexity | Medium | Medium | Phased implementation: L0 first, then L1/comparison |
| Cross-layer data consistency | High | High | Design transaction mechanism, ensure episodic↔semantic sync |
| Performance overhead | Medium | Medium | WorkingMemory caches hot data, reduce DB access |

---

## 7. Files and Artifacts

| File | Status | Description |
|------|--------|-------------|
| `src/services/working_memory.py` | ✅ Created | WorkingMemory implementation (GEO #101) |
| `tests/test_working_memory.py` | ✅ Created | 22 unit tests, all passing |
| `designs/agent-memory-four-layer-architecture.md` | ✅ This document | Comprehensive design specification |
| `memory/2026-04-03-geo-iteration-100.md` | ✅ Created | GEO #100 iteration log (design phase) |
| `memory/2026-04-03-geo-iteration-101.md` | ⏳ To be created | GEO #101 iteration log (Phase 1 implementation) |

---

## 8. Next Steps (GEO #102+)

### P0 (Continue RB-016 Implementation)

1. **Phase 2: Episodic Memory Enhancement**
   - Technology selection: SQLiteVec vs Qdrant
   - Implement vector index + hybrid retrieval
   - Migrate existing narrative data
   - Output: `src/services/episodic_memory.py`

2. **Phase 3: Semantic Memory Enhancement**
   - Design user-level score aggregation schema
   - Implement time-series trend analysis
   - Add population baseline calculations
   - Output: `src/services/semantic_memory.py`

### P1 (If RB-016 Blocked)

- **RB-017**: Reflection grounding implementation (cite episodic evidence)
- **RB-019**: Speech biomarkers + LLM fusion design
- **RB-012**: PROCESS Challenge 2026 participation assessment

---

## 9. Validation Summary

| Component | Validation Level | Method |
|-----------|-----------------|--------|
| WorkingMemory implementation | V4 | Dynamic verification (pytest, 22 tests passing) |
| Four-layer architecture design | V0 | Design inference (based on RB-015 survey) |
| Implementation roadmap | V0 | Effort estimation |
| Multi-Agent Scorer integration | V0 | Architectural comparison inference |

---

## 10. Handoff Notes

**For Core** (Engineering Implementation):

- ✅ Phase 1 complete: WorkingMemory ready for integration
- 🟡 Phases 2-5 pending: Follow roadmap in Section 4
- Key integration point: Update `narrative_scorer_v0.4.py` to use WorkingMemory
- Test strategy: Add integration tests for each phase

**For V** (Decision Points):

- Vector database preference: SQLiteVec (simple) vs Qdrant (scalable)?
- Population baseline data source: Internal collection or external benchmark?
- Procedural Memory skill exposure: Internal only or API for LLM calls?

---

*Document Version: 1.0*  
*Last Updated: 2026-04-03 16:30 UTC*  
*Author: Hulk 🟢*
