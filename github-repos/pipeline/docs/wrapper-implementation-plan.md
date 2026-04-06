# Wrapper Layer Implementation Plan

**Created**: 2026-03-28 (GEO #76)
**Status**: Phase 1 Partial — REMem Event Segmentation Complete, LLM Integration Blocked
**Parent**: [scorer-migration-phase1.md](../core/docs/scorer-migration-phase1.md)
**Last Updated**: 2026-04-02 (GEO #96)

---

## Overview

This document tracks the implementation of the `narrative_scorer_wrapper.py` layer for the pipeline service.

**Purpose**:
- Provide stable API for pipeline services
- Absorb breaking changes in narrative-scorer library
- Enable graceful degradation (LLM → rule-only fallback)
- Support batch scoring, caching, and monitoring

---

## Current State (2026-04-02)

### Completed

- [x] `src/services/` directory created
- [x] `src/services/__init__.py` created
- [x] `src/services/narrative_scorer_wrapper.py` skeleton written
  - `score_narrative()` function stub
  - `NarrativeScorerService` class stub
  - `score_batch()` method stub
  - TODO checklist for Phase 1
- [x] **`src/services/remem_event_segmenter.py`** (GEO #96, 2026-04-02)
  - `EventSegmenter` class with rule-based boundary detection
  - `segment_narrative()` convenience function
  - Temporal anchor extraction
  - Emotional valence scoring per segment
  - People/place/theme extraction
  - Tested with sample narrative (3 events detected)
  - Ready for LLM integration (pending DASHSCOPE_API_KEY)

### Pending (Blocked by DASHSCOPE_API_KEY)

**Blocker Update (GEO #96, 2026-04-02)**:
- DASHSCOPE_API_KEY present in environment but returns **401 Authentication Error**
- Duration: >636 hours (~26.5 days)
- Impact: LLM-enhanced features unavailable; rule-based fallback working

**Completed Without LLM**:
- [x] REMem event segmentation (rule-based mode)
- [x] Temporal anchor extraction
- [x] Emotional valence scoring (keyword-based)

**Still Blocked**:
- [ ] Integrate narrative-scorer v0.7.0 from PyPI (requires API key for testing)
- [ ] Implement fallback to local `narrative_scorer_v0.4.py`
- [ ] LLM-based event segmentation (higher accuracy)
- [ ] Add async batch scoring support
- [ ] Add caching layer (Redis/memory)
- [ ] Add monitoring hooks (latency, error rate, cost)
- [ ] Write unit tests (mocked LLM)
- [ ] Write integration tests (live LLM)

**Workaround**: Development can proceed with rule-based mode. Production LLM features require valid API key.

---

## Implementation Phases

### Phase 1: Library Integration (2026-03-31 to 2026-04-07)

**Prerequisites**:
- narrative-scorer v0.7.0 published to PyPI
- DASHSCOPE_API_KEY available for validation

**Tasks**:
1. Update `requirements.txt`: `narrative-scorer>=0.7.0,<0.8.0`
2. Implement library import with error handling
3. Test basic scoring (mocked + live)
4. Document usage in README

**Deliverable**: Working wrapper with library integration

### Phase 2: Fallback Layer (2026-04-08 to 2026-04-14)

**Goal**: Enable offline/development usage without PyPI dependency

**Tasks**:
1. Import local `narrative_scorer_v0.4.py` as fallback
2. Implement feature parity check (v0.4 vs v0.7)
3. Add configuration flag: `SCORER_SOURCE=library|local`
4. Test both modes

**Deliverable**: Dual-mode wrapper (library + local fallback)

### Phase 3: Performance Optimization (2026-04-15 to 2026-04-21)

**Goal**: Production-ready performance

**Tasks**:
1. Add async batch scoring (`asyncio.gather`)
2. Implement memory caching (LRU cache for repeated narratives)
3. Add Redis caching option (for distributed deployment)
4. Benchmark: latency, throughput, memory

**Deliverable**: Optimized wrapper with caching

### Phase 4: Monitoring & Observability (2026-04-22 to 2026-04-28)

**Goal**: Production monitoring ready

**Tasks**:
1. Add latency tracking (p50, p95, p99)
2. Add error rate monitoring
3. Add cost tracking (token count × pricing)
4. Integrate with pipeline observability stack

**Deliverable**: Instrumented wrapper with metrics

---

## API Reference (Planned)

### Function: `score_narrative()`

```python
from pipeline.services import score_narrative

result = score_narrative(
    text="今天天气很好，我和家人一起去了公园...",
    use_llm=True,
    api_key=None,  # Falls back to DASHSCOPE_API_KEY env var
)

print(result['composite_score'])  # 0-100
print(result['emotional_depth'])  # 0-100
```

### Class: `NarrativeScorerService`

```python
from pipeline.services import NarrativeScorerService

scorer = NarrativeScorerService(
    use_llm=True,
    fallback_to_rule_only=True,
)

# Single narrative
result = scorer.score("今天天气很好...")

# Batch scoring
results = scorer.score_batch([
    "叙事 1...",
    "叙事 2...",
    "叙事 3...",
])
```

---

## Testing Strategy

### Unit Tests (Mocked LLM)

```python
# tests/test_narrative_scorer_wrapper.py
import pytest
from unittest.mock import patch, MagicMock
from pipeline.services import NarrativeScorerService

@patch('pipeline.services.narrative_scorer_wrapper._score_narrative')
def test_score_narrative(mock_score):
    mock_score.return_value = {'composite_score': 75.0, ...}
    scorer = NarrativeScorerService(use_llm=False)
    result = scorer.score("test narrative")
    assert result['composite_score'] == 75.0
```

### Integration Tests (Live LLM)

```python
# tests/test_integration_live.py
import os
import pytest
from pipeline.services import NarrativeScorerService

@pytest.mark.skipif(not os.getenv('DASHSCOPE_API_KEY'), reason="No API key")
def test_live_llm_scoring():
    scorer = NarrativeScorerService(use_llm=True)
    result = scorer.score("今天天气很好...")
    assert 0 <= result['composite_score'] <= 100
```

---

## Migration Path from v0.4

**Current**: `src/narrative_scorer_v0.4.py` (embedded, v0.4 rule-only)

**Target**: `narrative-scorer>=0.7.0` (PyPI, v0.7 hybrid rule+LLM)

**Migration Steps**:
1. Keep `narrative_scorer_v0.4.py` for backward compatibility
2. New code uses wrapper (which prefers library, falls back to local)
3. Gradually migrate callers to wrapper API
4. Deprecate direct `narrative_scorer_v0.4.py` imports (v0.8+)
5. Remove `narrative_scorer_v0.4.py` (v0.9+)

---

## Dependencies

| Dependency | Version | Purpose | Status |
|------------|---------|---------|--------|
| narrative-scorer | >=0.7.0,<0.8.0 | Primary scoring library | ⏳ Pending PyPI release |
| dashscope | >=1.14.0 | LLM API (Qwen) | ⏳ Pending API key |
| redis | >=4.0.0 | Optional caching | ⚪ Not started |
| asyncio | stdlib | Async batch scoring | ✅ Available |

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| DASHSCOPE_API_KEY delayed | High | Fallback to v0.4 rule-only mode |
| narrative-scorer PyPI release delayed | Medium | Use local install from git |
| LLM latency too high for production | Medium | Conditional LLM invocation (60-80% savings) |
| Breaking API changes in v0.7+ | Low | Wrapper layer absorbs changes |

---

## Next Steps

1. **Immediate** (GEO #77+):
   - Await DASHSCOPE_API_KEY from V
   - Monitor narrative-scorer v0.7.0 release

2. **Phase 1 Start** (2026-03-31):
   - Install narrative-scorer from PyPI
   - Run unit tests (mocked)
   - Run integration tests (live, pending API key)

3. **Phase 2-4** (2026-04-01 to 2026-04-28):
   - Implement fallback, caching, monitoring
   - Document usage in pipeline README

---

*This plan is a living document. Update as implementation progresses.*
