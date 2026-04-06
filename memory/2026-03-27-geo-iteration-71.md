# GEO #71 — Core Repo Differentiation + PR #11 Status + v0.7 Benchmark Skeleton

**Date**: 2026-03-27 05:30 UTC (2026-03-27 13:30 CST)
**Theme**: Core vs narrative-scorer boundary doc + PR #11 check + v0.7 benchmark tests
**Status**: ✅ Complete

---

## Executive Summary

**Scheduled**: 2026-03-28 10:00 UTC (per #70) — **Executed Early** (2026-03-27 05:30 UTC)
**Executed**: 2026-03-27 05:20-05:45 UTC
**Duration**: ~25 minutes

**Key Deliverables**:
1. ✅ **Core Repo Differentiation Doc** (core/docs/repo-differentiation.md)
2. ✅ **PR #11 Status Check** (OPEN, 0 comments, updated 03-25)
3. ✅ **v0.7 Benchmark Test Skeleton** (narrative-scorer/tests/test_benchmark_v07.py)
4. ✅ **DASHSCOPE_API_KEY Reminder** (pipeline/docs/DASHSCOPE_API_KEY-reminder.md)
5. ✅ **3 repos pushed**: core, narrative-scorer, pipeline

---

## Deliverable 1: Core Repo Differentiation Documentation

**File**: `core/docs/repo-differentiation.md` (8.6KB, 273 lines)

### Repository Purposes

**core**:
- Product logic, API services, user interaction, business orchestration
- User authentication, WeChat integration, voice pipeline, photo upload
- Multi-agent empathy kernel, safety layer (CST protocol)
- Data persistence, analytics dashboards, subscription billing

**narrative-scorer**:
- Narrative quality assessment algorithm, benchmark suite
- Rule-based + LLM-based feature extraction
- Six-dimension scoring, letter grades, feedback generation
- Standalone Python library (pip-installable)

### Boundary Matrix

| Function | core | narrative-scorer | Notes |
|----------|------|------------------|-------|
| User login/session | ✅ | ❌ | core owns user state |
| Voice ASR/TTS | ✅ | ❌ | core handles audio pipeline |
| Narrative scoring | ⚠️ Consumer | ✅ Owner | core calls scorer API |
| Emotion detection | ⚠️ Consumer | ✅ Owner | scorer provides features |
| Benchmark tests | ❌ | ✅ | scorer owns test suite |
| Dashboard analytics | ✅ | ❌ | core aggregates over time |

### Integration Patterns

**Pattern 1: Library Import** (Recommended for v0.7):
```python
from narrative_scorer.scorer import score_narrative
from narrative_scorer.llm_feature_extractor import LLMFeatureExtractor
```

**Pattern 2: Microservice API** (Optional future):
```python
async with httpx.AsyncClient() as client:
    response = await client.post(f"{SCORER_API_URL}/score", json={"text": text})
```

**Pattern 3: Embedded Module** (Current v0.6 — Deprecated):
- ❌ Code duplication, sync drift, maintenance burden
- → Migrate to Pattern 1 by v0.7 GA

### Version Compatibility

| core Version | narrative-scorer Version | Integration Method | Status |
|--------------|--------------------------|--------------------|--------|
| v1.x | v0.5.x | Embedded copy | Deprecated |
| v2.0 | v0.6.x | Embedded copy | Current (to migrate) |
| v2.1 | v0.7.x | Library import (Pattern 1) | Target |
| v2.2+ | v0.7.x+ | Microservice (Pattern 2) | Optional |

**验证等级**: V3 (静态复核 — 文档已写入)

---

## Deliverable 2: PR #11 Status Check

**Repo**: disi-unibo-nlp/nlg-metricverse (94 stars)
**PR**: #11 — "feat: Add narrative_score metric — Six-dimensional Chinese narrative quality assessment"

**Status** (via `gh pr view 11`):
- **State**: OPEN
- **Comments**: 0
- **Last Updated**: 2026-03-25T11:02:49Z
- **Age**: 9 days (since 2026-03-18)

**7-day threshold**: 2026-03-25 (passed)
**Follow-up window**: 2026-03-31 (4 days from now)

**Action**: Continue observing. Follow-up comment ready for 03-31 if no response.

**Follow-up Comment Draft** (ready for 03-31):
> Hi @disi-unibo-nlp team! 👋 Just wanted to gently bump this PR. The narrative_score metric adds support for Chinese autobiographical narrative quality assessment (6 dimensions: event richness, temporal/causal coherence, emotional depth, identity integration, information density). It's already integrated into our clinical study pipeline. Happy to address any feedback or make adjustments. Thanks!

**验证等级**: V3 (静态复核 — gh CLI 确认状态)

---

## Deliverable 3: v0.7 Benchmark Test Skeleton

**File**: `narrative-scorer/tests/test_benchmark_v07.py` (14.4KB, 366 lines)

### Test Samples (5 total)

| ID | Label | Focus |
|----|-------|-------|
| v07-001 | Implicit emotion (no explicit emotion words) | LLM detects sadness/nostalgia where rule-only gets 0 |
| v07-002 | Implicit causality (no causal markers) | LLM infers causality without 因为/所以 |
| v07-003 | Event boundary (semantic transition) | LLM segments by events, not sentences |
| v07-004 | Mixed explicit and implicit emotions | LLM detects both 高兴 + anxiety/uncertainty |
| v07-005 | Complex causal chain | LLM extracts 5-step causal chain |

### Test Classes

**TestV07HybridVsRuleOnly** (5 tests):
- test_implicit_emotion_detection
- test_implicit_causality_detection
- test_event_segmentation_accuracy
- test_mixed_emotion_detection
- test_causal_chain_extraction

**TestV07FallbackBehavior** (2 tests):
- test_fallback_on_api_failure (mocked)
- test_extract_with_fallback_graceful_degradation

**TestV07CostTracking** (1 test):
- test_cost_estimation_per_narrative (¥0.00084/narrative)

### Manual Integration Test

```python
python -c "from tests.test_benchmark_v07 import manual_integration_test; manual_integration_test()"
```

**Blocks**: DASHSCOPE_API_KEY required for live testing (V4 validation)

**验证等级**: V3 (静态复核 — 测试代码已写入)

---

## Deliverable 4: DASHSCOPE_API_KEY Reminder

**File**: `pipeline/docs/DASHSCOPE_API_KEY-reminder.md` (2.5KB, 91 lines)

### Summary

**Blocked Since**: 2026-03-16 (>10 days / 258 hours)
**Impact**: v0.7 LLM hybrid development blocked

**Completed (V3)**:
- ✅ 3 prompt templates
- ✅ LLM feature extractor (500+ lines)
- ✅ Unit tests (25+)
- ✅ v0.7 benchmark tests (5 samples)
- ✅ Integration guide
- ✅ Configuration template

**Blocked (V4)**:
- ❌ Live LLM API testing
- ❌ Implicit emotion detection validation
- ❌ Event segmentation accuracy testing
- ❌ Causality detection validation
- ❌ Hybrid scoring benchmark

### Cost Estimate

| Scenario | Narratives | Est. Cost (¥) |
|----------|------------|---------------|
| Per narrative | 1 | ¥0.00084 |
| Benchmark validation | 5 | ¥0.004 |
| Full test suite | 25 | ¥0.02 |
| Pilot RCT | 150 | ¥0.13 |
| Large-scale study | 1500 | ¥1.26 |

**Total validation cost**: <¥1 CNY

**验证等级**: V3 (静态复核 — 提醒文档已写入)

---

## Git Commits & Push

### core (1 commit)
```
commit 11ce701
GEO #71: Add repo differentiation doc (core vs narrative-scorer)

- docs/repo-differentiation.md: Clarify responsibilities boundary
- Core: Product logic, API services, user interaction
- narrative-scorer: Scoring algorithm, benchmark, standalone library
- Integration patterns: Library import (Pattern 1), Microservice (Pattern 2)
- Version compatibility matrix: v2.0→v2.1 migration path
- Data flow diagram for v0.7+ LLM integration

Prepares for v0.7 library import migration (away from embedded copy).
```
**Push**: ✅ `main → main`

### narrative-scorer (1 commit)
```
commit d9b3303
GEO #71: Add v0.7 benchmark test skeleton (hybrid rule + LLM)

- tests/test_benchmark_v07.py: 5 LLM-enhanced benchmark samples
- Tests: implicit emotion, causality, event segmentation
- Comparison: v0.7 hybrid vs v0.6 rule-only baseline
- Fallback behavior tests (graceful degradation)
- Cost tracking tests (¥0.00084/narrative)
- Manual integration test function

Status: V3 (code written, awaiting API key for V4 validation)
Blocks: DASHSCOPE_API_KEY required for live testing
```
**Push**: ✅ `main → main`

### pipeline (1 commit)
```
commit bcc5548
GEO #71: Add DASHSCOPE_API_KEY reminder doc

- docs/DASHSCOPE_API_KEY-reminder.md: Blocked status summary
- Blocked since: 2026-03-16 (>10 days / 258 hours)
- Impact: v0.7 LLM live testing and validation blocked
- Completed: 3 prompts + extractor + tests + integration guide (V3)
- Blocked: Live API testing, benchmark validation (V4)
- Cost estimate: <¥1 for full validation
- Request: Provide API key to unblock v0.7 beta release
```
**Push**: ✅ `main → main`

### awesome-digital-therapy
- No changes (v0.7 is implementation phase, no version update yet)

---

## Blocked Items (Updated)

| Blocker | Owner | Duration | Impact |
|---------|-------|----------|--------|
| arXiv 提交执行 | V | >240h | 论文不可引用 |
| **DASHSCOPE_API_KEY** | V | **>264h** | **v0.7 LLM 混合开发受限** |
| Path B 招募执行 | V | >216h | Pilot 未启动 |
| web_search API | — | >164h | 搜索受限 (DDG fallback) |

---

## 71 轮迭代总览 (Recent)

| 轮次 | 日期 | 主题 | 核心产出 | 状态 |
|------|------|------|----------|------|
| #67 | 03-26 | 方言焦虑词 + 跨仓库同步 | v0.6.3 patch: 82 词 + CHANGELOG sync + 4 仓库 push | ✅ |
| #68 | 03-26 | 情感词终版 + Benchmark 扩展 | v0.6.4: 90 词 + 18 样本 + 108/108 准确率 | ✅ |
| #69 | 03-26 | v0.7 路线图 + LLM 实现计划 | ROADMAP-v0.7.md + 实现规范文档 | ✅ |
| #70 | 03-27 | LLM 特征提取器 + Prompt 模板 | 3 prompts + llm_feature_extractor.py + 测试 + 集成指南 | ✅ |
| **#71** | **03-27** | **Core 仓库边界 + PR #11 检查 + v0.7 Benchmark** | **differentiation.md + PR 状态 + 5 样本 benchmark + API key 提醒** | ✅ |

---

## 下一轮优先级 (GEO #72)

**日期**: 2026-03-28 10:00 UTC (2026-03-28 18:00 CST)
**主题**: Async API Calls Research + Core Migration Plan

### 待执行

**1. Async API Calls Exploration (中优先级 — 调研)**
- 调研 DashScope async API 支持
- 评估性能提升潜力 (目标：4x throughput)
- 为 v0.7.1 做准备
- 输出：async_api_research.md

**2. Core Migration Plan (高优先级)**
- 制定 core 从 embedded scorer 迁移到 library import 的计划
- 更新 core/requirements.txt 添加 narrative-scorer 依赖
- 创建 migration checklist
- 输出：core/docs/scorer-migration-plan.md

**3. PR #11 Follow-up Prep (条件性 — 03-31)**
- 当前：03-27，PR open 9 天，0 评论
- 03-31 (4 天后) 如无回复 → 发送 follow-up 评论
- 评论草稿已准备 (见 Deliverable 2)

**4. DASHSCOPE_API_KEY Follow-up (中优先级)**
- 如 V 未提供 API key → 考虑发送简短提醒邮件
- 或通过其他渠道提醒 (微信/钉钉)
- 目标：解锁 v0.7 live testing

**5. awesome-digital-therapy Update (低优先级)**
- 更新资源列表，添加 narrative-scorer v0.6.4 更新
- 添加 v0.7 LLM integration 链接

---

*GEO #71 完成于 05:45 UTC (13:45 CST, March 27). 3/4 仓库操作成功.*
*Core differentiation doc 完成 — 明确 core vs narrative-scorer 职责边界.*
*v0.7 benchmark skeleton 完成 — 5 LLM-enhanced samples + fallback tests.*
*DASHSCOPE_API_KEY reminder 完成 — blocked >264h，成本估算 <¥1.*
*PR #11: OPEN 9 天，0 评论，03-25 最后更新，03-31 准备 follow-up.*

---

*Hulk 🟢 — Compressing chaos into structure*
