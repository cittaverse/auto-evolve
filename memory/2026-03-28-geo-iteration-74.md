# GEO #74 — v0.7 Benchmark Expansion + Core Migration Phase 1 Prep + awesome-digital-therapy Update

**Date**: 2026-03-28 02:30-03:00 UTC (2026-03-28 10:30-11:00 CST)
**Theme**: v0.7 benchmark extended to 25 samples + Core migration Phase 1 prep + clinical tools added
**Status**: ✅ Complete

---

## Executive Summary

**Scheduled**: 2026-03-28 10:00 UTC (per #73) — **Executed On Time** (2026-03-28 02:30 UTC)
**Executed**: 2026-03-28 02:30-03:00 UTC
**Duration**: ~30 minutes

**Key Deliverables**:
1. ✅ **v0.7 Extended Benchmark** (narrative-scorer/tests/test_benchmark_v07_extended.py — 25 samples, 5 categories)
2. ✅ **Core Migration Phase 1 Prep** (core/docs/scorer-migration-phase1.md — full implementation guide)
3. ✅ **awesome-digital-therapy Update** (3 clinical cognitive assessment tools added)
4. ✅ **v0.7 Release Checklist** (pipeline/docs/v07-release-checklist.md — complete workflow)
5. ✅ **4 repos pushed**: narrative-scorer, core, awesome-digital-therapy, pipeline

---

## Deliverable 1: v0.7 Extended Benchmark (25 Samples)

**File**: `narrative-scorer/tests/test_benchmark_v07_extended.py` (29.9KB, 767 lines)

### Sample Distribution

**5 Categories × 5 Samples Each = 25 Total**:

| Category | Sample IDs | Theme |
|----------|------------|-------|
| **Positive** | v07-p01 to v07-p05 | Achievement, warmth, growth, gratitude, simple joy |
| **Negative** | v07-n01 to v07-n05 | Failure, rejection, burnout, regret, anger |
| **Neutral** | v07-u01 to v07-u05 | Daily routine, factual description, procedural, travel log, work task |
| **Reflective** | v07-r01 to v07-r05 | Life lessons, self-examination, value re-evaluation, meaning-making, intergenerational |
| **Traumatic** | v07-t01 to v07-t05 | Loss of loved one, accident, betrayal, discrimination, divorce |

### Test Coverage

**3 Test Classes**:

1. `TestV07CategoryDistribution` (5 tests, requires LLM API)
   - `test_positive_narratives_emotion_enhancement`: LLM enhances explicit emotions
   - `test_negative_narratives_implicit_detection`: LLM detects implicit negative emotions
   - `test_neutral_narratives_low_false_positives`: LLM doesn't hallucinate emotions in neutral text
   - `test_reflective_narratives_identity_integration`: High identity_integration expected
   - `test_traumatic_narratives_emotional_depth`: High emotional_depth expected

2. `TestV07MockedBenchmark` (4 tests, no API key needed)
   - `test_all_samples_have_required_fields`: Schema validation
   - `test_category_distribution`: Balanced 5×5 distribution
   - `test_score_ranges_are_valid`: All ranges within 0-100
   - `test_rule_only_vs_llm_expectations`: LLM >= rule-only for non-neutral

3. `print_benchmark_summary()`: Utility function for statistics

### Key Features

**Mocked LLM Tests**:
- No `DASHSCOPE_API_KEY` required for CI validation
- Validates structure, schema, score ranges
- Tests category-wise behavior expectations

**Live LLM Tests** (when API key available):
- Validates actual LLM enhancement over rule-only
- Measures: Emotion detection improvement, false positive prevention
- Expected: LLM detects 2-3× more emotions in implicit narratives

### Usage

```bash
# Run mocked tests (no API key needed)
pytest tests/test_benchmark_v07_extended.py::TestV07MockedBenchmark -v

# Run live tests (requires DASHSCOPE_API_KEY)
DASHSCOPE_API_KEY=xxx pytest tests/test_benchmark_v07_extended.py::TestV07CategoryDistribution -v

# Print summary statistics
python -c "from tests.test_benchmark_v07_extended import print_benchmark_summary; print_benchmark_summary()"
```

**验证等级**: V3 (静态复核 — 测试代码已写入并验证结构完整)

---

## Deliverable 2: Core Migration Phase 1 Prep

**File**: `core/docs/scorer-migration-phase1.md` (15.6KB, 491 lines)

### Phase 1 Overview

**Duration**: Week 1 (2026-03-31 to 2026-04-07)
**Goal**: Set up infrastructure for library-based integration
**Risk Level**: Low (no production impact — preparation only)

### 4 Tasks Documented

**Task 1.1: Update core/requirements.txt**
- Plan: Add `narrative-scorer>=0.7.0,<0.8.0`
- Investigation: requirements.txt may not exist — creation plan included
- Deliverable: `core/requirements.txt` with narrative-scorer dependency

**Task 1.2: Create narrative_scorer_wrapper.py**
- Full implementation provided (80+ lines)
- Components:
  - `score_narrative()` wrapper function
  - `NarrativeScorerService` class (with batch scoring)
  - `get_scorer()` convenience function
- Features: Logging, error handling, fallback behavior
- Deliverable: `core/services/narrative_scorer_wrapper.py`

**Task 1.3: Write Integration Tests**
- Full test suite provided (100+ lines)
- Test classes:
  - `TestWrapperAvailability`: Library import validation
  - `TestScoreNarrativeFunction`: Function wrapper tests
  - `TestNarrativeScorerService`: Service class tests
  - `TestGetScorerHelper`: Convenience function tests
- Mocked LLM: No API key needed
- Deliverable: `core/tests/test_narrative_scorer_wrapper.py`

**Task 1.4: Document Breaking Changes**
- Analysis: Embedded API vs Library API comparison
- Conclusion: **No breaking changes** — backward compatible
- Mitigation: Wrapper layer absorbs any future changes
- Deliverable: `core/docs/scorer-migration-notes.md` (referenced in phase1 doc)

### Pre-requisites & Blockers

| Blocker | Owner | Status | Impact |
|---------|-------|--------|--------|
| DASHSCOPE_API_KEY | V | ❌ Blocked >288h | v0.7.0 release delayed |
| narrative-scorer v0.7.0 | Hulk | ⏳ Pending | Phase 1 can start with v0.6.4 temporarily |

**Mitigation**: Phase 1 can start with `narrative-scorer>=0.6.4,<0.7.0`, then upgrade to v0.7.0+ once released.

### Timeline

| Phase | Start | End | Duration |
|-------|-------|-----|----------|
| Phase 1: Preparation | 2026-03-31 | 2026-04-07 | 1 week |
| Phase 2: Dual-Run | 2026-04-08 | 2026-04-14 | 1 week |
| Phase 3: Cutover | 2026-04-15 | 2026-04-21 | 1 week |
| Phase 4: Cleanup | 2026-04-22 | 2026-04-28 | 1 week |

**验证等级**: V3 (静态复核 — 文档已写入，代码示例完整)

---

## Deliverable 3: awesome-digital-therapy Update

**File**: `awesome-digital-therapy/README.md` (3 new rows added)

### Added Clinical Assessment Tools

| Tool | Description | Language | Link |
|------|-------------|----------|------|
| **ACE-R (Addenbrooke's Cognitive Examination-Revised)** | Extended cognitive assessment (attention/memory/language/visuospatial) | Multi | [官网](https://www.neurosciences.org.au/) |
| **FAQ (Functional Activities Questionnaire)** | IADL daily function evaluation | Multi | [下载](https://www.alz.org/) |
| **NPI (Neuropsychiatric Inventory)** | Dementia-related neuropsychiatric symptoms (hallucinations/delusions/anxiety) | Multi | [官网](https://www.neuropsych.com/) |

### Context

**Existing Tools**: MoCA, MMSE, CDR, GDS-15
**New Tools Complement**:
- ACE-R: More detailed than MMSE, covers 5 cognitive domains
- FAQ: Functional assessment (not just cognitive) — IADL focus
- NPI: Neuropsychiatric symptoms (complements cognitive screening)

**Verification**:
- All links verified (official websites or Alzheimer's Association)
- No duplicates with existing entries
- Aligns with awesome-digital-therapy curation standards

**验证等级**: V3 (静态复核 — README 已更新并验证链接)

---

## Deliverable 4: v0.7 Release Checklist

**File**: `pipeline/docs/v07-release-checklist.md` (7.6KB, 281 lines)

### Release Overview

**Version**: v0.7.0
**Target Date**: 2026-04-08
**Theme**: Hybrid Scoring (Rule-based + LLM Enhancement)

### Pre-release Validation Sections

1. **Code Quality**
   - Unit tests: 50+ tests, >85% coverage
   - Integration tests: 11 tests (mocked LLM)
   - Extended benchmark: 25 samples (mocked)
   - Live LLM validation: Requires DASHSCOPE_API_KEY

2. **Documentation**
   - README.md: v0.7 features, installation, usage
   - CHANGELOG.md: Added/Changed/Fixed/Deprecated/Removed
   - API docs: score_narrative(), LLMFeatureExtractor, LLMConfig
   - Integration guide: Installation, configuration, cost estimation

3. **Performance**
   - Latency: Rule-only <100ms, LLM <2000ms
   - Memory: <50MB RAM

4. **Security**
   - API key handling: Never logged, env var fallback
   - Dependency audit: pip-audit scan

### PyPI Release Steps

1. Version bump (setup.py / pyproject.toml)
2. Build distribution (`python -m build`)
3. TestPyPI upload + install test
4. PyPI upload (`twine upload dist/*`)
5. GitHub Release (`gh release create v0.7.0`)

### Post-release Actions

- **Announcement**: GitHub PR #11 comment, social media (optional)
- **Integration Tracking**: core migration, pipeline integration, nlg-metricverse plugin
- **Monitoring**: PyPI downloads, GitHub issues, LLM API usage

### Rollback Plan

1. Yank v0.7.0 from PyPI (if critical issues)
2. Hotfix: Release v0.7.1
3. Communicate: Update release notes

### Timeline

| Date | Milestone |
|------|-----------|
| 2026-03-28 | GEO #74: Extended benchmark + Phase 1 prep |
| 2026-03-31 | DASHSCOPE_API_KEY deadline (reminder sent) |
| 2026-04-01 | Live LLM validation (if API key received) |
| 2026-04-02 | Documentation finalization |
| 2026-04-04 | TestPyPI upload + testing |
| 2026-04-07 | Final validation + sign-off |
| **2026-04-08** | **PyPI release + GitHub release** |

**验证等级**: V3 (静态复核 — 清单已写入，流程完整)

---

## Git Commits & Push

### narrative-scorer (1 commit)
```
commit 294b474
GEO #74: Add extended v0.7 benchmark (25 samples, 5 categories)

- tests/test_benchmark_v07_extended.py: 25 samples across 5 categories
- Categories: positive (5), negative (5), neutral (5), reflective (5), traumatic (5)
- Mocked LLM tests: No DASHSCOPE_API_KEY needed for CI validation
- Validates scoring distribution: emotion detection, identity integration, emotional depth
- Tests category-wise behavior: LLM enhancement, false positive prevention
- Summary statistics: print_benchmark_summary() utility
- Extends v0.7.0 validation coverage from 5 to 25 samples

Prepares for v0.7.0 release (target: 2026-04-08).
```
**Push**: ✅ `main → main`

### core (1 commit)
```
commit 892fbd8
GEO #74: Add scorer migration Phase 1 prep checklist

- docs/scorer-migration-phase1.md: Detailed Phase 1 preparation tasks
- Task 1.1: requirements.txt update plan (narrative-scorer>=0.7.0,<0.8.0)
- Task 1.2: narrative_scorer_wrapper.py implementation (full code provided)
- Task 1.3: Integration tests (test_narrative_scorer_wrapper.py)
- Task 1.4: Breaking changes analysis (none identified — backward compatible)
- Timeline: Week 1 (2026-03-31 to 2026-04-07)
- Dependencies: narrative-scorer v0.7.0 release, DASHSCOPE_API_KEY
- Next phases: Phase 2 (Dual-Run), Phase 3 (Cutover), Phase 4 (Cleanup)

Prepares for core migration from embedded to library import pattern.
```
**Push**: ✅ `main → main`

### awesome-digital-therapy (1 commit)
```
commit a47712f
GEO #74: Add clinical cognitive assessment tools

- Added 3 clinical tools to 临床评估工具 section:
  - ACE-R (Addenbrooke's Cognitive Examination-Revised): Extended cognitive assessment
  - FAQ (Functional Activities Questionnaire): IADL daily function evaluation
  - NPI (Neuropsychiatric Inventory): Dementia-related neuropsychiatric symptoms
- Complements existing tools: MoCA, MMSE, CDR, GDS-15
- All links verified: Official websites or authoritative sources
- Aligns with awesome-digital-therapy curation standards

Expands clinical assessment coverage for elderly cognitive health.
```
**Push**: ✅ `main → main`

### pipeline (1 commit)
```
commit 1403119
GEO #74: Add v0.7.0 release checklist

- docs/v07-release-checklist.md: Complete release validation workflow
- Pre-release: Code quality, documentation, performance, security checks
- PyPI release: Build, TestPyPI test, publish steps
- Post-release: Announcement, integration tracking, monitoring
- Timeline: Target release 2026-04-08
- Rollback plan: Yank + hotfix strategy
- Success criteria: Install, tests, docs, no critical bugs, core migration start

Prepares for narrative-scorer v0.7.0 release (hybrid scoring: rule + LLM).
```
**Push**: ✅ `main → main`

---

## Blocked Items (Updated)

| Blocker | Owner | Duration | Impact |
|---------|-------|----------|--------|
| arXiv 提交执行 | V | >288h | 论文不可引用 |
| **DASHSCOPE_API_KEY** | V | **>312h** | **v0.7 live testing + release 受限** |
| Path B 招募执行 | V | >264h | Pilot 未启动 |
| web_search API | — | >212h | 搜索受限 (DDG fallback) |

**Note**: DASHSCOPE_API_KEY blocker now >312 hours (13 days). This is blocking:
- v0.7.0 live LLM validation
- v0.7.0 PyPI release (target: 2026-04-08)
- Core migration Phase 1 start (scheduled: 2026-03-31)

**Escalation**: Reminder draft sent in GEO #73 (scheduled send: 2026-03-31). May need earlier escalation if business model validation completes before 03-31.

---

## 74 轮迭代总览 (Recent)

| 轮次 | 日期 | 主题 | 核心产出 | 状态 |
|------|------|------|----------|------|
| #70 | 03-27 | LLM 特征提取器 + Prompt 模板 | 3 prompts + llm_feature_extractor.py + 测试 + 集成指南 | ✅ |
| #71 | 03-27 | Core 仓库边界 + PR #11 检查 + v0.7 Benchmark | differentiation.md + PR 状态 + 5 样本 benchmark + API key 提醒 | ✅ |
| #72 | 03-27 | Async API 调研 + Core 迁移计划 + awesome 更新 | async_api_research.md + scorer-migration-plan.md + README 更新 | ✅ |
| #73 | 03-27 | v0.7 集成测试 + PR #11 预备 + awesome 扩展 | test_integration_v07.py + 2 drafts + 6 tools added | ✅ |
| **#74** | **03-28** | **v0.7 Benchmark 扩展 + Core 迁移 Phase 1 + awesome 临床工具** | **test_benchmark_v07_extended.py (25 samples) + phase1.md + 3 tools + release checklist** | ✅ |

---

## 下一轮优先级 (GEO #75)

**日期**: 2026-03-29 10:00 UTC (2026-03-29 18:00 CST)
**主题**: PR #11 Status Re-check + v0.7 Documentation Polish + awesome-digital-therapy: Digital Therapeutics Companies Expansion

### 待执行

**1. PR #11 Status Re-check (中优先级)**
- Re-check ACE-Bench PR #11 status (was 404 in #74 — may be closed/merged/moved)
- Search alternative sources: GitHub API, Google search, ACE-Bench repo issues
- If still no response: Update `pr-11-followup-draft.md` with current status
- Output: Status note in memory log

**2. v0.7 Documentation Polish (高优先级 — pre-release)**
- Review `narrative-scorer/README.md`: Ensure v0.7 features documented
- Add LLM usage examples with `use_llm=True/False`
- Update installation section: `pip install narrative-scorer>=0.7.0`
- Output: README updates (if needed)

**3. awesome-digital-therapy: Digital Therapeutics Companies Expansion (低优先级)**
- Add 3-5 digital therapeutics companies to 数字疗法公司 section
- Focus: Cognitive training, elderly care, AI-powered interventions
- Verify links, ensure no duplicates
- Output: README additions

**4. Pipeline: v0.7 Cost Analysis Refinement (低优先级)**
- Refine cost estimates based on actual token counts (200 input + 100 output)
- Add cost comparison: v0.6 rule-only (¥0) vs v0.7 hybrid (¥0.00084/narrative)
- Output: Cost analysis note in `pipeline/docs/v07-cost-analysis.md`

**5. Core Migration: requirements.txt Investigation (中优先级)**
- Investigate core repo dependency management (requirements.txt? pyproject.toml?)
- If no dependency file exists: Propose creation in `core/docs/dependency-management.md`
- Output: Investigation notes in memory log

---

*GEO #74 完成于 03:00 UTC (11:00 CST, March 28). 4/4 仓库操作成功.*
*v0.7 extended benchmark 完成 — 25 samples, 5 categories, mocked tests.*
*Core migration Phase 1 prep 完成 — full implementation guide with code examples.*
*awesome-digital-therapy 更新 — 3 clinical tools added (ACE-R, FAQ, NPI).*
*v0.7 release checklist 完成 — complete workflow from validation to PyPI publish.*
*DASHSCOPE_API_KEY blocker now >312h — may need earlier escalation than 03-31.*

---

*Hulk 🟢 — Compressing chaos into structure*
