# narrative-scorer v0.7.0 Release Checklist

**Version**: v0.7.0
**Release Date**: 2026-04-08 (target)
**Release Manager**: Hulk
**Status**: 🟡 Pre-release (pending DASHSCOPE_API_KEY validation)

---

## Release Overview

**Theme**: Hybrid Scoring (Rule-based + LLM Enhancement)

**Key Features**:
- ✅ LLM feature extractor for implicit emotion/causality/event detection
- ✅ Hybrid scoring: 60% rule-based + 40% LLM weights
- ✅ Graceful fallback: LLM API failure → rule-only mode
- ✅ Cost tracking: ~¥0.00084 per narrative (qwen-plus)
- ✅ Metadata tracking: LLM usage, confidence, latency, cost

**Breaking Changes**: None (backward compatible with v0.6.x)

---

## Pre-release Validation

### Code Quality

- [ ] **All unit tests passing**
  ```bash
  cd narrative-scorer
  pytest tests/ -v --tb=short
  ```
  - Expected: 50+ tests pass
  - Coverage: >85%

- [ ] **Integration tests passing (mocked LLM)**
  ```bash
  pytest tests/test_integration_v07.py -v
  ```
  - Expected: 11 tests pass (no API key needed)

- [ ] **Extended benchmark tests passing (mocked)**
  ```bash
  pytest tests/test_benchmark_v07_extended.py -v
  ```
  - Expected: 25 samples validated (no API key needed)

- [ ] **Live LLM validation** (requires DASHSCOPE_API_KEY)
  ```bash
  DASHSCOPE_API_KEY=xxx pytest tests/test_benchmark_v07.py -v
  python -c "from tests.test_benchmark_v07 import manual_integration_test; manual_integration_test()"
  ```
  - Expected: 5 live samples scored correctly
  - Validation: LLM detects implicit emotions where rule-only fails

### Documentation

- [ ] **README.md updated**
  - [ ] v0.7.0 features documented
  - [ ] Installation instructions include LLM dependencies
  - [ ] Usage examples show `use_llm=True/False`
  - [ ] API reference updated

- [ ] **CHANGELOG.md entry created**
  ```markdown
  ## [0.7.0] - 2026-04-08
  
  ### Added
  - LLM feature extractor for implicit emotion/causality/event detection
  - Hybrid scoring: 60% rule-based + 40% LLM weights
  - Graceful fallback on LLM API failure
  - Cost tracking and metadata logging
  
  ### Changed
  - score_narrative() now accepts `use_llm` parameter (default: True)
  - score_narrative() now accepts `api_key` parameter (optional)
  
  ### Fixed
  - Event segmentation over-segmentation in rule-only mode
  
  ### Deprecated
  - None
  
  ### Removed
  - None
  ```

- [ ] **API documentation** (`docs/api.md`)
  - [ ] `score_narrative()` signature updated
  - [ ] `LLMFeatureExtractor` class documented
  - [ ] `LLMConfig` options documented

- [ ] **Integration guide** (`docs/v07-llm-integration-guide.md`)
  - [ ] Installation steps
  - [ ] Configuration (API key, fallback behavior)
  - [ ] Cost estimation examples
  - [ ] Migration from v0.6.x

### Performance

- [ ] **Latency benchmark**
  ```bash
  # Rule-only mode
  python -c "import time; from scorer import score_narrative; start=time.time(); score_narrative('text'*100, use_llm=False); print(time.time()-start)"
  
  # LLM mode (requires API key)
  python -c "import time; from scorer import score_narrative; start=time.time(); score_narrative('text'*100, use_llm=True); print(time.time()-start)"
  ```
  - Expected: Rule-only <100ms, LLM <2000ms (depends on API latency)

- [ ] **Memory usage check**
  ```bash
  /usr/bin/time -v python -c "from scorer import score_narrative; score_narrative('text'*1000)"
  ```
  - Expected: <50MB RAM

### Security

- [ ] **API key handling**
  - [ ] API key never logged in plaintext
  - [ ] API key falls back to env var (not hardcoded)
  - [ ] `.env` file in `.gitignore`

- [ ] **Dependency audit**
  ```bash
  pip install pip-audit
  pip-audit -r requirements.txt
  ```
  - Expected: No critical vulnerabilities

---

## PyPI Release

### Pre-publish Checklist

- [ ] **Version bump**
  ```bash
  # Update setup.py or pyproject.toml
  version = "0.7.0"
  ```

- [ ] **Build distribution**
  ```bash
  pip install build
  python -m build
  ```
  - Expected: `dist/narrative_scorer-0.7.0-py3-none-any.whl` and `.tar.gz`

- [ ] **TestPyPI upload** (dry run)
  ```bash
  pip install twine
  twine upload --repository testpypi dist/*
  ```

- [ ] **TestPyPI install test**
  ```bash
  pip install --index-url https://test.pypi.org/simple/ narrative-scorer==0.7.0
  python -c "from narrative_scorer import score_narrative; print(score_narrative('test'))"
  ```

### Publish

- [ ] **PyPI upload**
  ```bash
  twine upload dist/*
  ```
  - Verify: https://pypi.org/project/narrative-scorer/0.7.0/

- [ ] **GitHub Release**
  ```bash
  gh release create v0.7.0 --title "v0.7.0: Hybrid Scoring (Rule + LLM)" --notes-file RELEASE_NOTES.md
  ```

---

## Post-release

### Announcement

- [ ] **GitHub Issues/PRs**
  - [ ] Comment on PR #11 (ACE-Bench integration): "v0.7.0 released with LLM enhancement"
  - [ ] Update PR #11 description to reference v0.7.0

- [ ] **Social Media** (optional)
  - [ ] Twitter/X: "Released narrative-scorer v0.7.0 with LLM-enhanced scoring for Chinese autobiographical narratives"
  - [ ] LinkedIn: Same as Twitter
  - [ ] WeChat Moments (V's network): Brief announcement

### Integration Tracking

- [ ] **core migration** (Phase 1 starts 2026-03-31)
  - [ ] Track in `core/docs/scorer-migration-phase1.md`
  - [ ] Monitor: `pip install narrative-scorer>=0.7.0,<0.8.0` in core/requirements.txt

- [ ] **Pipeline integration**
  - [ ] Update `pipeline/requirements.txt` to use v0.7.0
  - [ ] Run pipeline end-to-end test with LLM scoring

- [ ] **nlg-metricverse plugin** (PR #11)
  - [ ] Update plugin to support v0.7.0 API
  - [ ] Test plugin with LLM scoring

### Monitoring

- [ ] **PyPI download stats** (first week)
  - Track: https://pypistats.org/packages/narrative-scorer
  - Baseline: v0.6.4 downloads/week

- [ ] **GitHub issues/PRs**
  - Monitor for bug reports
  - Respond within 48 hours

- [ ] **LLM API usage** (if telemetry enabled)
  - Track: Number of LLM calls/day
  - Track: Average cost/narrative
  - Track: Fallback rate (LLM failure → rule-only)

---

## Rollback Plan

If critical issues discovered post-release:

1. **Immediate**: Yank v0.7.0 from PyPI
   ```bash
   # PyPI does not support deletion, but can yank
   # Users with unpinned deps will get v0.6.4
   ```

2. **Hotfix**: Release v0.7.1 with fix
   ```bash
   # Bump version to 0.7.1
   # Fix issue, re-run validation
   # Publish v0.7.1
   ```

3. **Communicate**: Update GitHub release notes with known issues

---

## Timeline

| Date | Milestone |
|------|-----------|
| 2026-03-28 | GEO #74: Extended benchmark + Phase 1 prep |
| 2026-03-31 | DASHSCOPE_API_KEY deadline (reminder sent) |
| 2026-04-01 | Live LLM validation (if API key received) |
| 2026-04-02 | Documentation finalization |
| 2026-04-04 | TestPyPI upload + testing |
| 2026-04-07 | Final validation + sign-off |
| **2026-04-08** | **PyPI release + GitHub release** |
| 2026-04-09 | Announcement + integration tracking |
| 2026-04-15 | Post-release monitoring report |

---

## Success Criteria

Release is successful when:

- [ ] ✅ PyPI package installs cleanly (`pip install narrative-scorer==0.7.0`)
- [ ] ✅ All tests pass (unit + integration + benchmark)
- [ ] ✅ Documentation complete and accurate
- [ ] ✅ No critical bugs reported in first 48 hours
- [ ] ✅ core migration Phase 1 starts on schedule (2026-03-31)
- [ ] ✅ PR #11 updated with v0.7.0 reference

---

## Contacts

- **Release Manager**: Hulk (via GEO iterations)
- **API Key Owner**: V (DASHSCOPE_API_KEY)
- **Core Integration**: Core team (starts 2026-03-31)
- **Pipeline Integration**: Hulk (ongoing)

---

*Release checklist created for GEO #74. Target release: 2026-04-08.*
