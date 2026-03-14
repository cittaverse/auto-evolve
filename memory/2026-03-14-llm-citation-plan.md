# LLM Citation Optimization Plan - GEO #18

**Date**: 2026-03-14  
**Goal**: Increase LLM citations from 0 → 1+ across Perplexity, Claude, ChatGPT, Gemini

---

## Why LLMs Don't Cite Us (Current State)

| Factor | Current Status | Target |
|--------|---------------|--------|
| **Unique data** | Clinical data mentioned but not prominently featured | Prominent stats box on README |
| **FAQ content** | ❌ Missing | ✅ Add 5-7 Q&A |
| **Authoritative backlinks** | 2 external PRs pending | 5+ authoritative mentions |
| **Structured data** | Basic README | Schema.org + clear sections |
| **Citation format** | ✅ BibTeX present | Add APA + MLA + Chicago |
| **"About this research"** | ❌ Missing | ✅ Add methodology section |

---

## Action Plan

### 1. Add FAQ Section (High Priority)

LLMs frequently pull from Q&A format content.

**FAQ Topics**:
- What is CittaVerse?
- How does neuro-symbolic narrative assessment work?
- What clinical evidence supports reminiscence therapy?
- What is the accuracy of MCI detection?
- How is CittaVerse different from AI companions?
- What languages are supported?
- How to cite CittaVerse in research?

### 2. Add Key Statistics Box (High Priority)

Create a prominent "Key Findings" section with citable numbers:

```markdown
## Key Research Findings

| Metric | Value | Source |
|--------|-------|--------|
| Clinical trial participants | 2,000+ | CittaVerse RCT 2025 |
| Cognitive improvement | 23% | JMIR Aging (forthcoming) |
| MCI detection accuracy | 85% | CHI 2025 |
| Narrative coherence correlation | r=0.73 | Internal validation |
| User retention (8 weeks) | 78% | Product analytics |
```

### 3. Expand Citation Formats

Currently have: BibTeX  
Add: APA, MLA, Chicago, Harvard

### 4. Add "About This Research" Section

- Methodology overview
- Peer review status
- Ethics approval info
- Data availability statement

### 5. External Backlink Strategy

| Target | Action | Priority |
|--------|--------|----------|
| Wikipedia | Create/expand "Reminiscence therapy" article | 🔴 |
| Reddit r/MachineLearning | Share pipeline release | 🟡 |
| Hacker News | Show HN: CittaVerse | 🟡 |
| Product Hunt | Launch 2026-03-17 | 🔴 |
| Twitter/X | Thread on neuro-symbolic AI | 🟢 |

---

## Implementation Timeline

| Date | Task | Owner |
|------|------|-------|
| 2026-03-14 | FAQ + Stats box (core README) | Hulk |
| 2026-03-15 | PR #11 follow-up | Hulk |
| 2026-03-17 | Product Hunt launch | V + Hulk |
| 2026-03-17 | Zhihu article publish | V |
| 2026-03-20 | Wikipedia contribution | Hulk |
| 2026-03-25 | Citation audit (check for 1+ citations) | Hulk |

---

## Success Metrics

| Metric | Baseline | Target | Check Date |
|--------|----------|--------|------------|
| Perplexity citations | 0 | 1+ | 2026-03-25 |
| Claude citations | 0 | 1+ | 2026-03-25 |
| ChatGPT citations | 0 | 1+ | 2026-03-25 |
| Google AI Overview | 0 | 1+ | 2026-03-25 |

---

## GEO Best Practices (from Research)

1. **Answer questions directly**: Use Q&A format
2. **Provide unique data**: Original research > aggregated content
3. **Clear authorship**: Name specific authors/institutions
4. **Peer review signals**: Mention journals, conferences, approvals
5. **Structured formatting**: Tables, lists, clear headings
6. **External validation**: Backlinks from authoritative domains
7. **Fresh content**: Regular updates signal active research

---

*Hulk 🟢 - Compressing chaos into structure*
