# GEO #69 — ROADMAP-v0.7 + LLM-as-Judge Implementation Plan

**Date**: 2026-03-26 16:45 UTC (2026-03-27 00:45 CST)
**Theme**: v0.7 roadmap creation + LLM-as-Judge implementation planning
**Status**: ✅ Complete

---

## Executive Summary

**Scheduled**: 2026-03-27 05:00 UTC (per #68) — Executed early due to available capacity
**Executed**: 2026-03-26 16:45-17:30 UTC
**Duration**: ~45 minutes

**Key Deliverables**:
1. ✅ **ROADMAP-v0.7.md created** (narrative-scorer repo)
2. ✅ **LLM-as-Judge Implementation Plan** (pipeline/docs repo)
3. ✅ **PR #11 status check** — OPEN (6 days, 0 comments), follow-up due 03-31
4. ✅ **2 repos pushed**: narrative-scorer + pipeline
5. ✅ **v0.7 architecture finalized** — LLM-enhanced feature extraction (Option C)

---

## Deliverable 1: ROADMAP-v0.7.md

**File**: `narrative-scorer/ROADMAP-v0.7.md` (368 lines)

### v0.6 Baseline (Completed)
| Aspect | Status |
|--------|--------|
| Version | v0.6.4 (2026-03-26) |
| Emotion vocabulary | 90 words (stable for v0.6.x) |
| Benchmark samples | 18 gold-standard narratives |
| Test coverage | 72 tests (60 unit + 12 benchmark) |
| Benchmark accuracy | 108/108 = 100% |
| Architecture | Pure rule-based (offline) |

### v0.7 Target Architecture: LLM-Enhanced Hybrid

**Core Principle**: LLM augments rule-based pipeline, doesn't replace it.

```
Input Text
    │
    ├─── Rule-Based Feature Extractor ──→ Explicit markers
    │                                              │
    ├─── LLM Feature Extractor ──────────→ Implicit features
    │        ├─ Implicit emotions                │
    │        ├─ Semantic event boundaries        │
    │        └─ Implicit causality               │
    │                                              │
    └─── Fusion Layer ────────────────────────────┘
                     │
                     ↓
              Rule-Based Scorer (enhanced features)
```

**Graceful degradation**: If LLM API fails → fall back to v0.6 rule-only mode.

### Feature Plan

**Phase A: LLM Feature Extraction (High Priority)**
- A1: Implicit emotion detection (e.g., "心里空落落的" → sadness)
- A2: Semantic event boundary detection (beyond heuristic splitting)
- A3: Implicit causal link detection (beyond marker counting)

**Phase B: Hybrid Scoring (Medium Priority)**
- B1: Dimension-specific fusion (e.g., emotional_depth: 50% rule + 50% LLM)
- B2: Confidence intervals
- B3: LLM explanation generation

**Phase C: Multi-Dialect Support (Deferred to v0.8)**
- Cantonese, Wu, Min vocabulary extensions

**Phase D: Infrastructure (High Priority)**
- D1: Test suite expansion (72 → 100+ tests)
- D2: Benchmark dataset expansion (18 → 30+ samples)
- D3: API server (FastAPI + async + Docker)
- D4: Cost tracking

### Release Timeline

| Milestone | Target | Dependencies |
|-----------|--------|-------------|
| v0.7.0-alpha (A1) | Q3 2026 (Jul) | DASHSCOPE_API_KEY |
| v0.7.0-beta (+ A2, A3) | Q3 2026 (Aug) | Alpha validation |
| v0.7.0 RC (+ B1, B2, D1) | Q3 2026 (Sep) | Beta testing, pilot data |
| v0.7.0 GA | Q3 2026 (Oct) | RC testing |
| v0.7.1 (+ D3, D4) | Q4 2026 (Nov) | GA feedback |

### Success Metrics

| Metric | v0.6 Baseline | v0.7 Target |
|--------|--------------|-------------|
| Implicit emotion detection | 0% | ≥ 70% recall |
| Event boundary F1 | ~75% | ≥ 85% |
| Causal link recall | ~60% | ≥ 80% |
| Human-AI agreement (ICC) | Unknown | ≥ 0.75 |
| API cost per narrative | ¥0 | < ¥0.02 |
| Latency (P95) | < 100ms | < 3s |

**验证等级**: V3 (静态复核 — 文档已写入，架构设计完成)

---

## Deliverable 2: LLM-as-Judge Implementation Plan

**File**: `pipeline/docs/llm-as-judge-implementation-plan.md` (644 lines)

### Key Specifications

**LLM Provider**: DashScope (Qwen-Plus recommended)
- Cost: ¥0.0028 per narrative (100 input + 200 output tokens)
- Pilot RCT total (N=50, 3 narratives each): ~¥0.42
- Rate limit: 100 req/min, 1000 req/day (free tier)

**Prompt Templates** (3 types):
1. **Emotion Detection** — Explicit + implicit emotions with JSON output
2. **Event Segmentation** — Semantic event boundaries with confidence scores
3. **Causality Detection** — Explicit + implicit causal relations with strength

**Fallback Strategy**:
```python
def call_llm_with_fallback(prompt, model='qwen-plus', timeout=5):
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = Generation.call(model=model, prompt=prompt, timeout=timeout)
            if response.status_code == 200:
                return response.output.text
        except Exception as e:
            logger.warning(f"LLM API exception (attempt {attempt+1}): {e}")
    return None  # Triggers rule-only fallback
```

**Integration Example**:
```python
def count_emotion_words(text, use_llm=True):
    explicit_emotions = _count_explicit_emotion_words(text)  # v0.6 logic
    if not use_llm:
        return explicit_emotions
    
    llm_response = call_llm_with_fallback(prompt)
    if llm_response is None:
        return explicit_emotions  # Fallback
    
    implicit_emotions = json.loads(llm_response)
    implicit_only = [e for e in implicit_emotions if e['type'] == 'implicit']
    return explicit_emotions + len(implicit_only) * 0.5  # Weight implicit at 0.5
```

**Testing Strategy**:
- Unit tests: Mock API responses, test fallback behavior
- Integration tests: Compare hybrid vs rule-only scoring
- Benchmark tests: 30 samples, target ≥ 90% dimension accuracy
- A/B testing: Human-AI agreement (ICC) comparison

**验证等级**: V3 (静态复核 — 文档已写入，实现规范完成)

---

## Deliverable 3: PR #11 Status Check

### Current Status
| PR | Repo | Stars | Status | Age | Comments |
|----|------|-------|--------|-----|----------|
| #11 | disi-unibo-nlp/nlg-metricverse | 94 | OPEN | 6 days | 0 |

**Last updated**: 2026-03-25T11:02:49Z (no new activity)

**7-day threshold**: 2026-03-31 (4 days remaining)

**策略**: Continue observing. Prepare friendly follow-up comment for 03-31 if no response.

**Follow-up draft** (ready for 03-31):
```
Hi @maintainer! Just checking in on this PR — happy to make any 
adjustments if needed. The narrative_score metric integrates with 
your existing test suite and follows your contribution guidelines. 
Let me know if there's anything I can clarify! 🟢
```

**验证等级**: V4 (动态验证 — GitHub page fetch confirmed)

---

## Git Commits & Push

### narrative-scorer (1 commit)
```
commit 367063e
GEO #69: Add ROADMAP-v0.7.md (LLM-enhanced hybrid architecture)

- v0.6.4 baseline: 90 emotion words, 18 benchmark samples, 100% accuracy
- v0.7 target: LLM-enhanced feature extraction (implicit emotions, semantic events, causality)
- Architecture: Rule-based primary + LLM augmentation with graceful degradation
- Phases: A (LLM features) → B (Hybrid scoring) → C (Multi-dialect, deferred) → D (Infra)
- Timeline: v0.7.0-alpha (Jul) → beta (Aug) → RC (Sep) → GA (Oct)
- Dependencies: DASHSCOPE_API_KEY (blocked), pilot RCT data (blocked)
- Success metrics: ICC ≥ 0.75, cost < ¥0.02/narrative, latency < 3s P95
```
**Push**: ✅ `main → main`

### pipeline (1 commit)
```
commit 430e7a1
GEO #69: Add LLM-as-Judge implementation plan

- Detailed specs for v0.7 LLM-enhanced feature extraction
- 3 feature types: implicit emotion, semantic event, implicit causality
- Prompt templates with JSON output schemas
- DashScope (Qwen) integration with fallback logic
- Cost estimation: ¥0.0028/narrative (Qwen-Plus)
- Testing strategy: unit tests, integration tests, A/B testing plan
- Deployment checklist and risk mitigation
- Blocks: DASHSCOPE_API_KEY required for live testing
```
**Push**: ✅ `main → main`

### core + awesome-digital-therapy
- No changes (v0.7 is planning phase, no version update yet)

---

## Blocked Items (Unchanged)

| Blocker | Owner | Duration | Impact |
|---------|-------|----------|--------|
| arXiv 提交执行 | V | >234h | 论文不可引用 |
| DASHSCOPE_API_KEY | V | >252h | v0.7 LLM 混合开发受限 |
| Path B 招募执行 | V | >210h | Pilot 未启动 |
| web_search API | — | >158h | 搜索受限 (DDG fallback) |

---

## 69 轮迭代总览 (Recent)

| 轮次 | 日期 | 主题 | 核心产出 | 状态 |
|------|------|------|----------|------|
| #65 | 03-25 | Benchmark 扩展 + README + CHANGELOG | 15-sample + 72tests + CHANGELOG + nlg sync | ✅ |
| #66 | 03-25 | Emotion 词库 + Temporal 识别 | v0.6.3: 78 词 + 年日农历 + 90/90 准确率 | ✅ |
| #67 | 03-26 | 方言焦虑词 + 跨仓库同步 | v0.6.3 patch: 82 词 + CHANGELOG sync + 4 仓库 push | ✅ |
| #68 | 03-26 | 情感词终版 + Benchmark 扩展 | v0.6.4: 90 词 + 18 样本 + 108/108 准确率 | ✅ |
| **#69** | **03-26** | **v0.7 路线图 + LLM 实现计划** | **ROADMAP-v0.7.md + 实现规范文档** | ✅ |

---

## 下一轮优先级 (GEO #70)

**日期**: 2026-03-27 10:00 UTC (2026-03-27 18:00 CST)
**主题**: Implementation Prep + Prompt Engineering

### 待执行

**1. Prompt Template Refinement (高优先级)**
- 创建 3 个 prompt 模板文件 (`llm_prompts/` directory)
- 测试 JSON schema 稳定性 (mock responses)
- 优化 prompt 指令清晰度 (减少 LLM 输出变异)

**2. llm_feature_extractor.py Skeleton (高优先级)**
- 创建模块骨架 (3 个主函数 + fallback 逻辑)
- 集成 DashScope API client (with retry, rate limiting)
- 编写配置加载器 (YAML → Python config)

**3. Unit Test Skeleton (中优先级)**
- 创建 `test_llm_feature_extractor.py`
- Mock API responses for 3 feature types
- Test fallback behavior (API failure, invalid JSON, timeout)

**4. PR #11 Follow-up (条件性 — 03-31)**
- 如 03-31 无回复 → 发送友好 follow-up 评论
- 当前：03-26，PR open 6 天，还需等待 4 天

**5. DASHSCOPE_API_KEY Request Reminder (低优先级)**
- 提醒 V 提供 API key 以解锁 v0.7 开发
- 当前 blocked 已超 252h (10.5 天)

---

*GEO #69 完成于 17:30 UTC (01:30 CST, March 27). 2/4 仓库操作成功.*
*v0.7 路线图完成 — LLM-enhanced hybrid architecture  finalized.*
*实现计划完成 — 3 prompt templates + DashScope integration specs.*
*PR #11: OPEN 6 天，0 评论，7 天阈值 03-31 (4 天剩余).*
*DASHSCOPE_API_KEY blocked >252h — v0.7 开发等待解锁.*

---

*Hulk 🟢 — Compressing chaos into structure*
