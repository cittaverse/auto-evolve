# LLM-as-Judge Architecture for Narrative Scoring

**Date**: 2026-03-25  
**Status**: Research & Design Phase  
**Context**: GEO #64 — Exploring hybrid rule-based + LLM evaluation

---

## Motivation

Current narrative-scorer v0.6.3 uses **pure rule-based scoring**:
- ✅ Fast, deterministic, transparent
- ✅ No API costs, works offline
- ❌ Limited semantic understanding (e.g., can't detect implicit emotions)
- ❌ Rigid marker-based detection (misses paraphrased causality)
- ❌ No holistic narrative quality judgment

**LLM-as-Judge** can complement rule-based scoring by:
1. Detecting implicit emotional depth (e.g., "心里空落落的" → sadness without explicit emotion word)
2. Evaluating narrative coherence beyond marker counting
3. Assessing overall "story quality" that rules can't capture

---

## Key Research Papers

### 1. G-Eval (Liu et al., 2023)
**Paper**: "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment"  
**arXiv**: 2303.16634

**Key Ideas**:
- Uses GPT-4 as evaluator with chain-of-thought prompting
- Defines evaluation criteria in natural language
- Asks LLM to score 1-5 with reasoning
- Shows higher correlation with human judgment than BLEU/ROUGE

**Relevance to CittaVerse**:
- Could define 6-dimension criteria in natural language
- LLM provides holistic judgment + reasoning
- Hybrid: rule-based for objective metrics (time markers), LLM for subjective (emotional depth)

### 2. FActScore (Min et al., 2023)
**Paper**: "FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation"

**Key Ideas**:
- Breaks text into atomic facts
- LLM judges each fact independently
- Aggregates into overall factuality score

**Relevance**:
- Event extraction could be validated by LLM
- Central vs peripheral classification could use LLM judgment
- "Does this sentence contain a specific, verifiable event?" → LLM binary classifier

### 3. Prometheus (Kim et al., 2023)
**Paper**: "Prometheus: Inducing Fine-grained Evaluation Capability in Language Models"

**Key Ideas**:
- Fine-tunes open-source LLM (Llama) as evaluator
- Uses rubric-based prompting
- Achieves GPT-4-level evaluation at lower cost

**Relevance**:
- Could fine-tune Qwen/GLM on narrative evaluation
- Lower cost than GPT-4 API
- Aligns with CittaVerse's China-first deployment strategy

---

## Proposed Hybrid Architecture

### Option A: Rule-Based Primary, LLM Validation
```
Input Text
    ↓
Rule-Based Scorer (v0.6.2)
    ↓
6-Dimension Scores (0-100)
    ↓
LLM Validator (optional)
    ↓
Adjusted Scores + Reasoning
```

**Pros**:
- Fast baseline (rule-based)
- LLM only for edge cases or quality assurance
- Low API cost

**Cons**:
- LLM doesn't improve most scores
- Limited value-add

---

### Option B: Parallel Scoring + Ensemble
```
Input Text
    ↓
    ├─→ Rule-Based Scorer → R_scores
    └─→ LLM Scorer → L_scores
         ↓
    Ensemble (weighted average)
         ↓
    Final Scores + Confidence
```

**Pros**:
- Combines strengths of both
- Can weight by confidence (e.g., rule-based for temporal, LLM for emotional)
- Provides reasoning from LLM

**Cons**:
- Higher API cost (every narrative scored twice)
- Requires calibration of ensemble weights

---

### Option C: LLM-Enhanced Feature Extraction
```
Input Text
    ↓
LLM Feature Extractor
    ├─→ Implicit emotions detected
    ├─→ Paraphrased causal links
    └─→ Semantic event boundaries
         ↓
Rule-Based Scorer (enhanced features)
         ↓
6-Dimension Scores
```

**Pros**:
- LLM augments rule-based pipeline
- Single scoring pass (rule-based)
- Transparent final scores

**Cons**:
- Still requires LLM API call per narrative
- Feature extraction prompt engineering needed

---

## Recommended Approach (Phase 1)

**Start with Option C** — LLM-Enhanced Feature Extraction:

1. **Implicit Emotion Detection**
   - Prompt: "List all emotions expressed in this text, including implicit ones. Format: [emotion, explicit/implicit]"
   - Augment `count_emotion_words()` with LLM-detected implicit emotions

2. **Semantic Event Boundary Detection**
   - Prompt: "Split this narrative into distinct events. Each event should be a coherent episode."
   - Compare with rule-based `extract_events()` → use LLM when rule-based produces <3 events

3. **Causal Link Detection**
   - Prompt: "Identify all cause-effect relationships, even if not marked by explicit causal words."
   - Augment `count_causal_markers()` with LLM-detected implicit causality

**Why Phase 1**:
- Minimal architecture change (still rule-based scoring)
- Clear value-add (detects what rules miss)
- Easy to A/B test (compare v0.6.2 vs v0.7-LLM-enhanced)

---

## Implementation Roadmap

### v0.7.0 (LLM-Enhanced Features)
- [ ] Add `llm_feature_extractor.py` module
- [ ] Qwen API integration (DASHSCOPE_API_KEY)
- [ ] Prompt templates for 3 feature types
- [ ] Fallback to rule-based if API fails
- [ ] A/B test on benchmark samples

### v0.8.0 (Hybrid Scoring)
- [ ] Add `llm_scorer.py` for direct LLM scoring
- [ ] Ensemble logic (weighted average)
- [ ] Confidence intervals
- [ ] Cost tracking (API calls per narrative)

### v0.9.0 (Fine-Tuned Evaluator)
- [ ] Collect human-annotated narrative scores (100+ samples)
- [ ] Fine-tune Qwen-7B on narrative evaluation task
- [ ] Deploy fine-tuned model (local inference, no API cost)

---

## Open Questions

1. **Which LLM to use?**
   - Qwen (Alibaba) — China deployment, DASHSCOPE_API_KEY available
   - GLM (Zhipu) — Alternative China option
   - GPT-4 — Best quality, but high cost + China access issues

2. **Prompt language?**
   - Chinese prompts for Chinese narratives?
   - Or English prompts (better LLM instruction-following)?

3. **Cost threshold?**
   - What's acceptable cost per narrative? (target: <¥0.01/narrative)

4. **Validation strategy?**
   - How to validate LLM-enhanced scores vs pure rule-based?
   - Need human-annotated gold standard (currently only 5 samples)

---

## Next Steps (GEO #65)

1. **If DASHSCOPE_API_KEY available**:
   - Implement `llm_feature_extractor.py` prototype
   - Test on 5 benchmark samples
   - Compare v0.6.2 vs v0.7-LLM scores

2. **If API key not available**:
   - Document architecture for future implementation
   - Focus on expanding benchmark samples (5 → 20)
   - Prepare prompt templates for when API access is ready

---

*Research by Hulk 🟢 for CittaVerse GEO #64*
