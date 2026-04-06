# LLM-as-Judge Implementation Plan

**Date**: 2026-03-26  
**Status**: Design Phase  
**Context**: GEO #69 — Detailed implementation plan for v0.7 LLM-enhanced features  
**Author**: Hulk 🟢

---

## Overview

This document provides detailed implementation specifications for integrating LLM feature extraction into the narrative-scorer pipeline (v0.7.0).

### Goals
1. **Implicit emotion detection** — Capture emotions not expressed via explicit vocabulary
2. **Semantic event boundary detection** — Improve event segmentation beyond heuristic splitting
3. **Implicit causal link detection** — Detect cause-effect relationships without explicit markers

### Design Constraints
- **Graceful degradation**: If LLM API fails, fall back to v0.6 rule-only behavior
- **Cost control**: Target < ¥0.02 per narrative
- **Latency**: Target < 3s P95 for single narrative scoring
- **China deployment**: Use DashScope (Qwen) as primary LLM provider

---

## Architecture

### Module Structure

```
narrative_scorer/
├── scorer.py                    # Main scoring logic (v0.6)
├── llm_feature_extractor.py     # NEW: LLM feature extraction (v0.7)
├── llm_prompts/
│   ├── emotion_detection.txt
│   ├── event_segmentation.txt
│   └── causality_detection.txt
├── config/
│   └── llm_config.yaml          # API config, rate limits, retry logic
└── tests/
    ├── test_llm_feature_extractor.py
    └── test_hybrid_scoring.py
```

### Data Flow

```
1. Input text received
       ↓
2. Rule-based feature extraction (parallel)
   - count_emotion_words() → explicit_emotions[]
   - extract_events() → rule_events[]
   - count_causal_markers() → explicit_causality[]
       ↓
3. LLM feature extraction (async, with timeout)
   - detect_implicit_emotions() → implicit_emotions[]
   - segment_events_semantic() → llm_events[]
   - detect_implicit_causality() → implicit_causality[]
       ↓
4. Feature fusion
   - all_emotions = explicit_emotions + implicit_emotions
   - all_events = llm_events (if confidence > 0.7) else rule_events
   - all_causality = explicit_causality + implicit_causality
       ↓
5. Rule-based scoring (unchanged)
   - score_event_richness(all_events)
   - score_temporal_coherence(all_events)
   - score_emotional_depth(all_emotions)
   - score_causal_coherence(all_causality)
   - ... (other dimensions)
       ↓
6. Output scores + optional LLM explanations
```

---

## LLM Provider Configuration

### Primary: DashScope (Qwen)

**API Endpoint**: `https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation`

**Model Options**:
| Model | Context | Max Output | Price (input/output) | Latency | Use Case |
|-------|---------|------------|---------------------|---------|----------|
| Qwen-Turbo | 32K | 6K | ¥0.002 / ¥0.006 per 1K tokens | ~500ms | Fast prototyping |
| Qwen-Plus | 32K | 6K | ¥0.004 / ¥0.012 per 1K tokens | ~1s | Balanced |
| Qwen-Max | 32K | 6K | ¥0.04 / ¥0.12 per 1K tokens | ~2s | Best quality |

**Recommended**: Qwen-Plus (balanced cost/quality for pilot RCT)

**Cost Estimation** (per narrative, ~200 chars):
- Input: ~100 tokens (Chinese chars → ~0.5 tokens/char)
- Output: ~200 tokens (JSON with 5-10 features)
- Cost: (100 × ¥0.004/1000) + (200 × ¥0.012/1000) = ¥0.0004 + ¥0.0024 = **¥0.0028 per narrative**
- Pilot RCT (N=50, 3 narratives/participant): 150 × ¥0.0028 = **¥0.42 total**

**Rate Limits**:
- Qwen-Plus: 100 requests/minute, 1000 requests/day (free tier)
- Upgrade available for higher limits

### Fallback Strategy

```python
import dashscope
from dashscope import Generation

def call_llm_with_fallback(prompt, model='qwen-plus', timeout=5):
    """Call LLM with retry logic and fallback to rule-only."""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = Generation.call(
                model=model,
                prompt=prompt,
                timeout=timeout,
                temperature=0.1,  # Low temperature for deterministic output
            )
            if response.status_code == 200:
                return response.output.text
            else:
                logger.warning(f"LLM API error: {response.status_code}")
        except Exception as e:
            logger.warning(f"LLM API exception (attempt {attempt+1}): {e}")
    
    # Fallback: return None to trigger rule-only behavior
    logger.info("LLM API failed, falling back to rule-only")
    return None
```

---

## Prompt Templates

### 1. Implicit Emotion Detection

**File**: `llm_prompts/emotion_detection.txt`

```
你是一位心理学研究员，擅长分析叙事文本中的情感表达。

请分析以下叙事文本中表达的所有情感，包括明确表达的和隐含的情感。

对于每个情感，请标注：
1. 情感类型（从以下类别选择：喜悦、悲伤、愤怒、恐惧、惊讶、厌恶、信任、期待、羞愧、内疚、骄傲、感激、孤独、怀念、平静、焦虑）
2. 表达方式（explicit=明确用情感词表达 / implicit=通过描述、隐喻、身体感受等隐含表达）
3. 原文依据（引用触发该情感的短语或句子，不超过 20 字）

文本：
{text}

请严格按照以下 JSON 格式输出（不要添加任何解释）：
[
  {"emotion": "悲伤", "type": "implicit", "evidence": "心里空落落的"},
  {"emotion": "喜悦", "type": "explicit", "evidence": "我很开心"}
]

如果文本中没有检测到任何情感，输出空数组：[]
```

**Expected Output Example**:
```json
[
  {"emotion": "悲伤", "type": "implicit", "evidence": "心里空落落的"},
  {"emotion": "怀念", "type": "explicit", "evidence": "我很想念奶奶"},
  {"emotion": "平静", "type": "implicit", "evidence": "整个人都静下来了"}
]
```

**Integration**:
```python
def count_emotion_words(text, use_llm=True):
    """Count emotion words with optional LLM enhancement."""
    # Rule-based: count explicit emotion words
    explicit_emotions = _count_explicit_emotion_words(text)  # v0.6 logic
    
    if not use_llm:
        return explicit_emotions
    
    # LLM-based: detect implicit emotions
    prompt = load_prompt('emotion_detection.txt', text=text)
    llm_response = call_llm_with_fallback(prompt)
    
    if llm_response is None:
        return explicit_emotions  # Fallback to rule-only
    
    try:
        implicit_emotions = json.loads(llm_response)
        # Filter to only implicit emotions
        implicit_only = [e for e in implicit_emotions if e['type'] == 'implicit']
        # Combine: explicit count + implicit bonus
        return explicit_emotions + len(implicit_only) * 0.5  # Weight implicit at 0.5
    except json.JSONDecodeError:
        logger.warning("LLM emotion detection returned invalid JSON")
        return explicit_emotions  # Fallback to rule-only
```

---

### 2. Semantic Event Segmentation

**File**: `llm_prompts/event_segmentation.txt`

```
你是一位叙事分析专家，擅长识别故事中的事件边界。

请将以下叙事文本分割成独立的事件。每个事件应该是一个连贯的片段，
描述一个具体的时间、地点、人物和发生的事。

对于每个事件，请标注：
1. 事件类型：central（核心事件，推动叙事主线）/ peripheral（边缘事件，补充细节）/ transitional（过渡事件，连接其他事件）
2. 时间标记（如有，引用原文）
3. 主要人物（如有，列出）
4. 事件摘要（一句话概括，不超过 30 字）
5. 置信度（0.0-1.0，表示你对这个事件分割的把握）

文本：
{text}

请严格按照以下 JSON 格式输出（不要添加任何解释）：
[
  {
    "type": "central",
    "temporal_marker": "那年夏天",
    "participants": ["我", "奶奶"],
    "summary": "我和奶奶一起在院子里摘桂花",
    "confidence": 0.95
  },
  {
    "type": "peripheral",
    "temporal_marker": "那天下午",
    "participants": ["我"],
    "summary": "我一个人坐在门槛上发呆",
    "confidence": 0.85
  }
]

如果文本太短或无法分割成多个事件，可以输出单个事件。
```

**Expected Output Example**:
```json
[
  {
    "type": "central",
    "temporal_marker": "那年夏天",
    "participants": ["我", "奶奶"],
    "summary": "我和奶奶一起在院子里摘桂花",
    "confidence": 0.95
  },
  {
    "type": "transitional",
    "temporal_marker": "后来",
    "participants": ["我"],
    "summary": "奶奶去世了，我再也没摘过桂花",
    "confidence": 0.90
  }
]
```

**Integration**:
```python
def extract_events(text, use_llm=True):
    """Extract events with optional LLM enhancement."""
    # Rule-based: heuristic event extraction (v0.6)
    rule_events = _extract_events_rule_based(text)
    
    if not use_llm or len(text) < 100:  # Skip LLM for very short texts
        return rule_events
    
    # LLM-based: semantic event segmentation
    prompt = load_prompt('event_segmentation.txt', text=text)
    llm_response = call_llm_with_fallback(prompt, timeout=8)  # Longer timeout
    
    if llm_response is None:
        return rule_events  # Fallback to rule-only
    
    try:
        llm_events = json.loads(llm_response)
        # Calculate average confidence
        avg_confidence = sum(e['confidence'] for e in llm_events) / len(llm_events)
        
        # Use LLM events if confidence is high enough
        if avg_confidence > 0.7:
            return llm_events
        else:
            logger.info(f"LLM event confidence too low ({avg_confidence:.2f}), using rule-based")
            return rule_events
    except json.JSONDecodeError:
        logger.warning("LLM event segmentation returned invalid JSON")
        return rule_events  # Fallback to rule-only
```

---

### 3. Implicit Causality Detection

**File**: `llm_prompts/causality_detection.txt`

```
你是一位逻辑分析专家，擅长识别文本中的因果关系。

请识别以下叙事文本中所有的因果关系，包括明确表达的和隐含的。

对于每个因果关系，请标注：
1. 原因（引用原文，不超过 20 字）
2. 结果（引用原文，不超过 20 字）
3. 表达方式：explicit（有因为/所以/因此等标记词）/ implicit（无标记词，但语义上存在因果）
4. 因果强度：strong（直接因果）/ moderate（间接因果）/ weak（相关但因果性弱）

文本：
{text}

请严格按照以下 JSON 格式输出（不要添加任何解释）：
[
  {
    "cause": "我那晚烧到 39 度",
    "effect": "父母半夜抱着我往医院跑",
    "type": "explicit",
    "strength": "strong"
  },
  {
    "cause": "奶奶去世后",
    "effect": "我再也没摘过桂花",
    "type": "implicit",
    "strength": "moderate"
  }
]

如果文本中没有检测到因果关系，输出空数组：[]
```

**Expected Output Example**:
```json
[
  {
    "cause": "我那晚烧到 39 度",
    "effect": "父母半夜抱着我往医院跑",
    "type": "explicit",
    "strength": "strong"
  },
  {
    "cause": "奶奶去世后",
    "effect": "我再也没摘过桂花",
    "type": "implicit",
    "strength": "moderate"
  }
]
```

**Integration**:
```python
def count_causal_markers(text, use_llm=True):
    """Count causal markers with optional LLM enhancement."""
    # Rule-based: count explicit causal markers
    explicit_causality = _count_explicit_causal_markers(text)  # v0.6 logic
    
    if not use_llm:
        return explicit_causality
    
    # LLM-based: detect implicit causality
    prompt = load_prompt('causality_detection.txt', text=text)
    llm_response = call_llm_with_fallback(prompt)
    
    if llm_response is None:
        return explicit_causality  # Fallback to rule-only
    
    try:
        causal_relations = json.loads(llm_response)
        # Count implicit causality with weight
        implicit_count = sum(
            1.0 if r['strength'] == 'strong' else 0.5 if r['strength'] == 'moderate' else 0.25
            for r in causal_relations if r['type'] == 'implicit'
        )
        return explicit_causality + implicit_count
    except json.JSONDecodeError:
        logger.warning("LLM causality detection returned invalid JSON")
        return explicit_causality  # Fallback to rule-only
```

---

## Configuration

### File: `config/llm_config.yaml`

```yaml
llm:
  provider: dashscope
  model: qwen-plus  # Options: qwen-turbo, qwen-plus, qwen-max
  
  # API configuration
  api_key_env: DASHSCOPE_API_KEY
  timeout_seconds: 5
  max_retries: 2
  retry_delay_seconds: 1
  
  # Rate limiting
  rate_limit:
    requests_per_minute: 50
    requests_per_day: 500
  
  # Cost tracking
  cost_tracking:
    enabled: true
    log_file: logs/llm_costs.jsonl
  
  # Feature-specific settings
  features:
    emotion_detection:
      enabled: true
      weight: 0.5  # Implicit emotions weighted at 0.5 of explicit
      min_confidence: 0.0  # No confidence threshold for emotion
    
    event_segmentation:
      enabled: true
      confidence_threshold: 0.7  # Use LLM events only if avg confidence > 0.7
      timeout_seconds: 8  # Longer timeout for event segmentation
    
    causality_detection:
      enabled: true
      weight_strategy: strength  # strong=1.0, moderate=0.5, weak=0.25
  
  # Fallback behavior
  fallback:
    on_api_failure: rule_only  # Options: rule_only, cached, error
    on_invalid_json: rule_only
    on_timeout: rule_only
  
  # Logging
  logging:
    level: INFO
    log_prompts: false  # Don't log prompts in production (privacy)
    log_responses: false  # Don't log responses in production (privacy)
    log_costs: true
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/test_llm_feature_extractor.py`

```python
import pytest
from unittest.mock import patch, MagicMock
from narrative_scorer.llm_feature_extractor import (
    detect_implicit_emotions,
    segment_events_semantic,
    detect_implicit_causality,
)

class TestImplicitEmotionDetection:
    @patch('narrative_scorer.llm_feature_extractor.call_llm_with_fallback')
    def test_detects_implicit_emotions(self, mock_llm):
        mock_llm.return_value = '[{"emotion": "悲伤", "type": "implicit", "evidence": "心里空落落的"}]'
        result = detect_implicit_emotions("那天之后，心里空落落的")
        assert len(result) == 1
        assert result[0]['emotion'] == '悲伤'
    
    @patch('narrative_scorer.llm_feature_extractor.call_llm_with_fallback')
    def test_fallback_on_api_failure(self, mock_llm):
        mock_llm.return_value = None
        result = detect_implicit_emotions("那天之后，心里空落落的")
        assert result == []  # Fallback to empty (rule-only will handle explicit)
    
    @patch('narrative_scorer.llm_feature_extractor.call_llm_with_fallback')
    def test_fallback_on_invalid_json(self, mock_llm):
        mock_llm.return_value = 'invalid json'
        result = detect_implicit_emotions("那天之后，心里空落落的")
        assert result == []  # Fallback to empty

class TestEventSegmentation:
    @patch('narrative_scorer.llm_feature_extractor.call_llm_with_fallback')
    def test_uses_llm_events_when_confident(self, mock_llm):
        mock_llm.return_value = '''
        [
          {"type": "central", "confidence": 0.95, "summary": "Event 1"},
          {"type": "peripheral", "confidence": 0.90, "summary": "Event 2"}
        ]
        '''
        result = segment_events_semantic("Long narrative text...")
        assert len(result) == 2
        assert result[0]['type'] == 'central'
    
    @patch('narrative_scorer.llm_feature_extractor.call_llm_with_fallback')
    def test_fallback_to_rule_when_low_confidence(self, mock_llm):
        mock_llm.return_value = '''
        [
          {"type": "central", "confidence": 0.5, "summary": "Event 1"}
        ]
        '''
        with patch('narrative_scorer.llm_feature_extractor._extract_events_rule_based') as mock_rule:
            mock_rule.return_value = [{'type': 'central', 'summary': 'Rule event'}]
            result = segment_events_semantic("Long narrative text...")
            assert len(result) == 1
            assert result[0]['summary'] == 'Rule event'  # Used rule-based

class TestCausalityDetection:
    @patch('narrative_scorer.llm_feature_extractor.call_llm_with_fallback')
    def test_weights_by_strength(self, mock_llm):
        mock_llm.return_value = '''
        [
          {"cause": "A", "effect": "B", "type": "implicit", "strength": "strong"},
          {"cause": "C", "effect": "D", "type": "implicit", "strength": "moderate"},
          {"cause": "E", "effect": "F", "type": "implicit", "strength": "weak"}
        ]
        '''
        result = detect_implicit_causality("Text with causality...")
        # strong=1.0, moderate=0.5, weak=0.25
        assert result == 1.75
```

### Integration Tests

**File**: `tests/test_hybrid_scoring.py`

```python
import pytest
from narrative_scorer.scorer import score_narrative

class TestHybridScoring:
    def test_hybrid_vs_rule_only_comparison(self):
        """Compare v0.7 hybrid scoring vs v0.6 rule-only on benchmark samples."""
        text = "那年夏天，奶奶还在。院子里的桂花开得正好。后来她走了，我再也没摘过桂花。"
        
        # Rule-only (v0.6 behavior)
        rule_scores = score_narrative(text, use_llm=False)
        
        # Hybrid (v0.7 behavior)
        hybrid_scores = score_narrative(text, use_llm=True)
        
        # Expect hybrid to detect more emotions (implicit sadness)
        assert hybrid_scores['emotional_depth'] >= rule_scores['emotional_depth']
        
        # Expect hybrid to detect similar event count (short text, rule-based is fine)
        assert abs(hybrid_scores['event_richness'] - rule_scores['event_richness']) < 10
```

### Benchmark Tests

**File**: `tests/test_benchmark.py` (extension)

```python
# Add 3 new benchmark samples with LLM-enhanced expected ranges

BENCHMARK_SAMPLES_LLM = [
    {
        'id': 'bench-019',
        'text': '...',  # Implicit emotion-heavy narrative
        'gold_ranges': {
            'emotional_depth': (50, 80),  # Higher than v0.6 range due to implicit detection
            # ... other dimensions
        }
    },
    # ... more samples
]

def test_llm_enhanced_benchmark_accuracy():
    """Test that LLM-enhanced scoring achieves target accuracy on benchmark."""
    # Target: ≥ 90% dimension accuracy (108/120 for 18 samples × 6 dimensions)
    pass
```

---

## A/B Testing Plan

### Goal
Compare v0.6 (rule-only) vs v0.7 (LLM-enhanced) scoring quality.

### Method
1. **Dataset**: 18 benchmark samples + 12 new samples (30 total)
2. **Human Annotation**: 2 independent raters score all 30 samples on 6 dimensions (0-100)
3. **AI Scoring**:
   - Run v0.6 (rule-only) on all 30 samples
   - Run v0.7 (LLM-enhanced) on all 30 samples
4. **Metrics**:
   - Human-AI agreement (ICC, Pearson r) per dimension
   - Improvement: v0.7 ICC - v0.6 ICC
   - Target: v0.7 ICC ≥ 0.75 (vs v0.6 baseline unknown)

### Timeline
- Week 1: Human annotation (2 raters, ~2 hours each)
- Week 2: AI scoring + statistical analysis
- Week 3: Results documentation + fusion weight tuning

---

## Deployment Checklist

### Pre-Deployment
- [ ] DASHSCOPE_API_KEY configured in environment
- [ ] Rate limits tested (100 req/min sustained)
- [ ] Fallback behavior verified (simulate API failure)
- [ ] Cost tracking enabled and logging to file
- [ ] Unit tests passing (72 + new LLM tests)
- [ ] Benchmark tests passing (18 samples, target ≥ 90% accuracy)
- [ ] A/B test completed (human-AI agreement analysis)

### Deployment
- [ ] Update version to v0.7.0 in `setup.py` and `__init__.py`
- [ ] Update CHANGELOG.md with v0.7.0 changes
- [ ] Update README.md with LLM-enhanced features
- [ ] Tag git release: `git tag v0.7.0 && git push origin v0.7.0`
- [ ] Deploy to staging environment
- [ ] Smoke test on staging
- [ ] Deploy to production

### Post-Deployment
- [ ] Monitor API costs (daily report)
- [ ] Monitor error rates (API failures, fallback triggers)
- [ ] Collect user feedback (if UI exposes LLM explanations)
- [ ] Plan v0.7.1 based on production learnings

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API cost overrun | Low | Medium | Daily cost alerts, rate limiting |
| API latency spike | Medium | Low | Timeout + fallback to rule-only |
| LLM output instability | Medium | Low | JSON schema validation, retry logic |
| Privacy concerns (sending narratives to API) | Low | High | Anonymization before API call, data retention policy |
| Model behavior change (DashScope updates) | Low | Medium | Version pinning, regression tests |

---

## Next Steps (GEO #70+)

1. **Implement `llm_feature_extractor.py`** — Core module with 3 feature detection functions
2. **Create prompt template files** — 3 prompts in `llm_prompts/` directory
3. **Write unit tests** — Mock API responses, test fallback behavior
4. **Request DASHSCOPE_API_KEY from V** — Unblock live testing
5. **Run A/B test on benchmark samples** — Compare v0.6 vs v0.7 scoring
6. **Update documentation** — README, CHANGELOG, usage examples

---

*Implementation plan by Hulk 🟢 for CittaVerse GEO #69*
