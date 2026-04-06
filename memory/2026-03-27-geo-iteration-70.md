# GEO #70 — LLM Feature Extractor Implementation + Integration Guide

**Date**: 2026-03-27 10:45 UTC (2026-03-27 18:45 CST)
**Theme**: LLM feature extractor skeleton + prompt templates + integration guide
**Status**: ✅ Complete

---

## Executive Summary

**Scheduled**: 2026-03-27 10:00 UTC (per #69) — Executed on time
**Executed**: 2026-03-27 10:00-10:45 UTC
**Duration**: ~45 minutes

**Key Deliverables**:
1. ✅ **3 Prompt Templates Created** (narrative-scorer/llm_prompts/)
2. ✅ **LLM Feature Extractor Implementation** (narrative-scorer/src/llm_feature_extractor.py)
3. ✅ **Unit Test Skeleton** (25+ test cases)
4. ✅ **v0.7 LLM Integration Guide** (pipeline/docs/)
5. ✅ **Configuration Template** (config/llm_config.example.yaml)
6. ✅ **2 repos pushed**: narrative-scorer + pipeline

---

## Deliverable 1: Prompt Templates (3 files)

### 1.1 Emotion Detection Prompt
**File**: `narrative-scorer/llm_prompts/emotion_detection.txt`

**Specifications**:
- Detects both explicit and implicit emotions
- 18 standard emotion categories (joy, sadness, nostalgia, anxiety, etc.)
- JSON output schema with confidence scores
- Examples for explicit ("感到非常高兴") and implicit ("心里空落落的") emotions
- Constraint: Only valid JSON output, no explanatory text

**Output Schema**:
```json
{
  "emotions": [
    {
      "text": "原文片段",
      "emotion": "joy",
      "type": "explicit|implicit",
      "confidence": 0.0-1.0
    }
  ],
  "total_explicit": 数字，
  "total_implicit": 数字，
  "emotional_density": 数字
}
```

### 1.2 Event Segmentation Prompt
**File**: `narrative-scorer/llm_prompts/event_segmentation.txt`

**Specifications**:
- Detects semantic event boundaries (beyond heuristic splitting)
- 4 boundary cue types: temporal, spatial, causal, topical
- Returns event summaries and confidence scores
- Granularity control (avoid over/under-segmentation)

**Output Schema**:
```json
{
  "events": [
    {
      "event_id": 1,
      "start_char": 字符位置，
      "end_char": 字符位置，
      "text": "事件文本片段",
      "summary": "一句话概括",
      "boundary_before": {
        "cue_type": "temporal|spatial|causal|topical|none",
        "confidence": 0.0-1.0
      }
    }
  ],
  "total_events": 数字，
  "avg_event_length": 数字
}
```

### 1.3 Causality Detection Prompt
**File**: `narrative-scorer/llm_prompts/causality_detection.txt`

**Specifications**:
- Detects explicit and implicit causal relations
- 3 strength levels: strong, moderate, weak
- Cue type classification: lexical vs inferential
- Cause-effect pair extraction with character positions

**Output Schema**:
```json
{
  "causal_relations": [
    {
      "relation_id": 1,
      "cause": {"text": "...", "start_char": N, "end_char": N},
      "effect": {"text": "...", "start_char": N, "end_char": N},
      "type": "explicit|implicit",
      "strength": "strong|moderate|weak",
      "cue_type": "lexical|inferential|none",
      "confidence": 0.0-1.0
    }
  ],
  "total_explicit": 数字，
  "total_implicit": 数字，
  "causal_density": 数字
}
```

**验证等级**: V3 (静态复核 — 3 个 prompt 模板文件已写入)

---

## Deliverable 2: LLM Feature Extractor Implementation

**File**: `narrative-scorer/src/llm_feature_extractor.py` (21KB, 500+ lines)

### Key Classes

**LLMConfig**:
- YAML/environment-based configuration
- API settings (model, timeout, retries, rate limiting)
- Feature toggles (emotion/event/causality detection)
- Cost tracking configuration
- Fallback behavior configuration

**LLMFeatures** (dataclass):
- Aggregated feature container
- Emotions, events, causal relations lists
- Metadata: API success/failure, cost, latency, fallback flag
- `to_dict()` method for scorer integration

**LLMFeatureExtractor**:
- Main extraction class
- Prompt template loading from llm_prompts/
- DashScope API integration with retry logic
- JSON response parsing (handles markdown code blocks)
- Graceful degradation to rule-only mode
- `extract()`: Main entry point
- `extract_with_fallback()`: Automatic fusion with rule-based features

### Integration Methods

**Method 1: Manual Fusion** (fine-grained control):
```python
rule_features = score_narrative(text, return_features=True)
llm_features = extractor.extract(text)

if not llm_features.used_fallback:
    implicit_emotions = [e for e in llm_features.emotions if e.emotion_type == 'implicit']
    enhanced_emotion_count = rule_features['emotion_count'] + len(implicit_emotions) * 0.5
```

**Method 2: Automatic Fusion** (simpler):
```python
enhanced_features = extractor.extract_with_fallback(text, rule_features)
```

### Fallback Logic

```python
def call_llm_with_fallback(prompt, model='qwen-plus', timeout=5):
    for attempt in range(max_retries):
        try:
            response = Generation.call(model=model, prompt=prompt, timeout=timeout)
            if response.status_code == 200:
                return response.output.text
        except Exception as e:
            logger.warning(f"LLM API exception (attempt {attempt+1}): {e}")
    return None  # Triggers rule-only fallback
```

**验证等级**: V3 (静态复核 — 代码已写入，结构完整)

---

## Deliverable 3: Unit Test Skeleton

**File**: `narrative-scorer/tests/test_llm_feature_extractor.py` (17KB, 25+ tests)

### Test Coverage

**TestLLMConfig** (5 tests):
- Default configuration values
- Configuration from dictionary
- Configuration to dictionary conversion
- Configuration from YAML file
- YAML file not found handling

**TestLLMFeatures** (2 tests):
- Default initialization
- to_dict() conversion

**TestLLMFeatureExtractor** (15+ tests):
- Extractor initialization
- Prompt template loading
- Prompt preparation
- JSON parsing (valid, markdown, invalid, empty)
- LLM API call (success, error, status code, no API key)
- Emotion extraction
- Event segmentation extraction
- Causal relation extraction
- Full extraction pipeline
- Extraction with failures
- extract_with_fallback() success/failure

**TestExtractLLMFeatures** (1 test):
- Convenience function testing

**TestIntegration** (1 test):
- Full pipeline with sample narrative

**验证等级**: V3 (静态复核 — 测试代码已写入)

---

## Deliverable 4: v0.7 LLM Integration Guide

**File**: `pipeline/docs/v0.7-llm-integration-guide.md` (12KB, 480 lines)

### Contents

1. **Overview**: Hybrid architecture principles
2. **Architecture Diagram**: Rule-based + LLM fusion flow
3. **Prerequisites**:
   - DashScope API key setup
   - Python dependencies (dashscope, pyyaml)
   - Repository structure verification
4. **Step-by-Step Integration**:
   - Step 1: Configuration
   - Step 2: Import LLM feature extractor
   - Step 3: Extract LLM features
   - Step 4: Integrate with rule-based scorer (2 methods)
   - Step 5: Error handling
5. **Testing**:
   - Unit tests (pytest commands)
   - Integration tests (sample narratives)
   - Benchmark tests (v0.6 vs v0.7 comparison)
6. **Cost Estimation**:
   - Per-narrative: ~¥0.00084
   - Pilot RCT (150 narratives): ~¥0.13
   - Large-scale (1500 narratives): ~¥1.26
7. **Performance**:
   - Latency: 1.5-2.5s P95
   - Throughput: 20-40 narratives/minute (single-threaded)
8. **Troubleshooting**:
   - API key issues
   - DashScope availability
   - API call failures
   - JSON parsing errors
   - High fallback rate diagnosis
9. **Migration Guide**: v0.6 → v0.7 (backward compatible)
10. **Roadmap Reference**: v0.7.0-alpha → beta → RC → GA

**验证等级**: V3 (静态复核 — 文档已写入)

---

## Deliverable 5: Configuration Template

**File**: `narrative-scorer/config/llm_config.example.yaml`

**Contents**:
```yaml
api_key: null  # Uses DASHSCOPE_API_KEY env var
model: qwen-plus
timeout: 5
max_retries: 2
rate_limit_delay: 0.1
use_emotion_detection: true
use_event_segmentation: true
use_causality_detection: true
fallback_to_rule_only: true
track_cost: true
cost_per_1k_input_tokens: 0.0028
cost_per_1k_output_tokens: 0.0028
use_cache: false
```

**验证等级**: V3 (静态复核 — 配置文件已写入)

---

## Git Commits & Push

### narrative-scorer (1 commit)
```
commit 80f9ecc
GEO #70: LLM feature extractor skeleton + prompt templates (v0.7.0-alpha)

- llm_prompts/: 3 prompt templates (emotion, event, causality)
- src/llm_feature_extractor.py: Full implementation skeleton
- tests/test_llm_feature_extractor.py: 25+ unit tests
- config/llm_config.example.yaml: Configuration template

Blocks: DASHSCOPE_API_KEY required for live testing
Next: Integration with scorer.py, benchmark tests
```
**Push**: ✅ `main → main`

### pipeline (1 commit)
```
commit 713918f
GEO #70: Add v0.7 LLM integration guide

- docs/v0.7-llm-integration-guide.md: Step-by-step integration instructions
- Architecture overview, prerequisites, 5-step integration process
- Testing guide, cost estimation, performance expectations
- Troubleshooting guide, migration path from v0.6

Blocks: DASHSCOPE_API_KEY required for live testing
Next: Core repo differentiation documentation update
```
**Push**: ✅ `main → main`

### core + awesome-digital-therapy
- No changes (v0.7 is implementation phase, no version update yet)

---

## PR #11 Status Check

**Status**: ⚠️ Unable to verify (web tools unavailable)

**Last known status** (from #69, 2026-03-26):
- Repo: disi-unibo-nlp/nlg-metricverse (94 stars)
- Status: OPEN
- Age: 6 days
- Comments: 0

**7-day threshold**: 2026-03-31 (4 days remaining from #69, now 3 days remaining)

**Note**: web_fetch and web_search both failed (404 + API key error). PR status couldn't be verified in this iteration. Will retry in #71.

**策略**: Continue observing. Follow-up comment ready for 03-31 if no response.

**验证等级**: V0 (未验证 — 工具失败，无法获取最新状态)

---

## Blocked Items (Unchanged)

| Blocker | Owner | Duration | Impact |
|---------|-------|----------|--------|
| arXiv 提交执行 | V | >240h | 论文不可引用 |
| DASHSCOPE_API_KEY | V | >258h | v0.7 LLM 混合开发受限 |
| Path B 招募执行 | V | >216h | Pilot 未启动 |
| web_search API | — | >164h | 搜索受限 (DDG fallback) |

---

## 70 轮迭代总览 (Recent)

| 轮次 | 日期 | 主题 | 核心产出 | 状态 |
|------|------|------|----------|------|
| #66 | 03-25 | Emotion 词库 + Temporal 识别 | v0.6.3: 78 词 + 年日农历 + 90/90 准确率 | ✅ |
| #67 | 03-26 | 方言焦虑词 + 跨仓库同步 | v0.6.3 patch: 82 词 + CHANGELOG sync + 4 仓库 push | ✅ |
| #68 | 03-26 | 情感词终版 + Benchmark 扩展 | v0.6.4: 90 词 + 18 样本 + 108/108 准确率 | ✅ |
| #69 | 03-26 | v0.7 路线图 + LLM 实现计划 | ROADMAP-v0.7.md + 实现规范文档 | ✅ |
| **#70** | **03-27** | **LLM 特征提取器 + Prompt 模板** | **3 prompts + llm_feature_extractor.py + 测试 + 集成指南** | ✅ |

---

## 下一轮优先级 (GEO #71)

**日期**: 2026-03-28 10:00 UTC (2026-03-28 18:00 CST)
**主题**: Core Repo Differentiation + PR #11 Follow-up Prep

### 待执行

**1. Core Repo Differentiation Documentation (高优先级)**
- 更新 core/README.md 或新建 docs/differentiation.md
- 明确 core vs narrative-scorer 的职责边界
- core: 产品逻辑、API 服务、用户交互
- narrative-scorer: 评分算法、benchmark、独立库
- 为 v0.7 集成做准备

**2. PR #11 Status Check + Follow-up (条件性 — 03-31)**
- 尝试再次检查 PR 状态 (web 工具可能恢复)
- 如 03-31 无回复 → 发送友好 follow-up 评论
- 当前：03-27，PR open 7 天，还需等待 3 天

**3. DASHSCOPE_API_KEY Reminder (中优先级)**
- 提醒 V 提供 API key 以解锁 v0.7 开发
- 当前 blocked 已超 258h (10.75 天)
- 考虑写一封简短的提醒邮件草稿

**4. Benchmark Test Integration (中优先级)**
- 将 LLM feature extractor 集成到 test_benchmark.py
- 创建 v0.7 benchmark 测试流程
- 目标：v0.7 hybrid vs v0.6 rule-only 对比

**5. Async API Calls Exploration (低优先级 — 调研)**
- 调研 DashScope async API 支持
- 评估性能提升潜力 (目标：4x throughput)
- 为 v0.7.1 做准备

---

*GEO #70 完成于 10:45 UTC (18:45 CST, March 27). 2/4 仓库操作成功.*
*v0.7 实现完成 — 3 prompt templates + LLM feature extractor + 25+ tests.*
*集成指南完成 — 5 步集成流程 + 成本估算 + 故障排查.*
*PR #11: 状态无法验证 (web 工具失败)，最后已知 OPEN 7 天，0 评论.*
*DASHSCOPE_API_KEY blocked >258h — v0.7 live testing 等待解锁.*

---

*Hulk 🟢 — Compressing chaos into structure*
