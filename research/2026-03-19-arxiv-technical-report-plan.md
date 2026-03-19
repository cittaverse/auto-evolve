# arXiv Technical Report — CittaVerse Narrative Scorer v0.5

**Target**: arXiv preprint (cs.CL / cs.HC categories)  
**Timeline**: 2026-03-20 to 2026-03-27 (7 days)  
**Status**: Outline & MVP Scope — GEO #45 (2026-03-19 22:04 UTC)

---

## 1. Proposed Title

**Option A (Technical)**:  
"Automated Narrative Quality Assessment for Reminiscence Therapy: A Neuro-Symbolic Pipeline with LLM-Based Event Extraction and Graph-Theoretic Structure Scoring"

**Option B (Application-focused)**:  
"CittaVerse: AI-Assisted Reminiscence Therapy for Older Adults with Mild Cognitive Impairment — Methodology and Pilot Evaluation Framework"

**Option C (Balanced)**:  
"Neuro-Symbolic Narrative Scoring for Digital Reminiscence Therapy: Methodology, Validation, and Clinical Pilot Design"

**Recommended**: Option C — balances technical contribution with clinical relevance

---

## 2. Abstract (Draft)

> Reminiscence therapy (RT) has demonstrated moderate effects on cognitive function and depression in older adults with mild cognitive impairment (MCI). However, scalable delivery and objective quality assessment remain challenges. We present CittaVerse, a digital reminiscence therapy platform featuring an automated narrative scoring pipeline that combines large language models (LLMs) for semantic event extraction with graph-theoretic structure analysis. Our neuro-symbolic approach scores six dimensions of narrative quality: internal events, external events, temporal coherence, causal coherence, character development, and information density distribution (central vs. peripheral information). The pipeline achieves V3 verification (static code review) and is deployed in an ongoing randomized controlled pilot study (N=50, 2-week intervention). We describe the methodology, validation approach, and evaluation framework integrating 2026 evidence on technology acceptance (STAM, Extended TAM), usability (Simplified SUS), and caregiver perspectives. This technical report provides the methodological foundation for future empirical validation and contributes to the emerging field of AI-enhanced digital therapeutics for cognitive health.

**Keywords**: reminiscence therapy, narrative assessment, large language models, neuro-symbolic AI, digital therapeutics, mild cognitive impairment, older adults

---

## 3. Paper Structure

### 1. Introduction
- Problem: RT efficacy established, but scalable delivery + objective assessment lacking
- Gap: No completed AI+RT systematic review exists (Shankar 2025 protocol only)
- Contribution: CittaVerse narrative scorer v0.5 methodology + pilot evaluation framework
- Paper overview

### 2. Background & Related Work
- **2.1 Reminiscence Therapy Evidence**
  - Meta-analyses: Pu 2025 (digital RT most effective), Ni 2026 (dual-stakeholder effects), Wang 2026 (cognitive efficacy MA)
  - Digital RT advantages: accessibility, personalization, scalability
- **2.2 Narrative Assessment Methods**
  - Traditional: Manual coding (labor-intensive, low inter-rater reliability)
  - LLM-based: Recent advances (LLM-as-a-Judge, automatic scoring)
  - Gap: No validated tools for Chinese older adults with MCI
- **2.3 Technology Acceptance for Older Adults**
  - STAM (Senior TAM), Extended TAM (2025-2026 evidence)
  - Key constructs: technology anxiety, privacy concerns, perceived personalization, emotional safety

### 3. System Architecture
- **3.1 Overview**
  - Neuro-symbolic design: LLM (neural) + graph theory (symbolic)
  - Rationale: LLMs excel at semantic understanding; graph methods provide interpretable structure scores
- **3.2 LLM Event Extraction**
  - Model: Qwen3.5-Plus (DashScope) or equivalent
  - Prompt design: 5W1H event extraction, central vs. peripheral classification
  - Output: Structured event graph (nodes = events, edges = temporal/causal links)
- **3.3 Graph-Theoretic Structure Scoring**
  - Metrics: Event count, temporal links, causal links, character mentions, network density
  - Normalization: Age-adjusted baselines (pending empirical data)
- **3.4 Six Scoring Dimensions**
  1. Internal events (thoughts, feelings, reflections)
  2. External events (actions, interactions, observable events)
  3. Temporal coherence (time markers, sequence clarity)
  4. Causal coherence (cause-effect reasoning)
  5. Character development (person mentions, relationship depth)
  6. **Information density distribution** (central vs. peripheral balance) ← Novel contribution

### 4. Implementation Details
- **4.1 Pipeline Architecture**
  - Monolithic Python script (OpenClaw sandbox constraints)
  - Dependencies: Standard library + requests (no external pip installs)
- **4.2 LLM Integration**
  - API: DashScope (qwen3.5-plus), fallback to Mock mode
  - Rate limiting: 500k tokens/day (Groq alternative evaluated)
- **4.3 Scoring Algorithm**
  - Weight configuration: Equal weights (v0.5), adjustable for A/B testing
  - Output: 0-100 composite score + letter grade (S/A/B/C/D) + natural language feedback
- **4.4 Emotional Arousal Detector**
  - Keyword-based + sentiment analysis
  - Triggers: High-arousal words, emotional intensity markers
  - Action: Adjust ideal central/peripheral ratio dynamically

### 5. Validation Strategy
- **5.1 Mock Testing (Completed)**
  - 5 mock participants, 5/5 tests passed
  - Integration test: End-to-end flow verified
- **5.2 Planned Empirical Validation**
  - Pilot RCT: N=50, 2-week intervention, 4 sessions
  - Primary outcome: Narrative quality improvement (pre-post)
  - Secondary outcomes: Usability (SUS), satisfaction (NPS), caregiver feedback
- **5.3 Comparison Baselines**
  - Human expert ratings (gold standard, pending)
  - Inter-rater reliability targets: κ > 0.75

### 6. Pilot Evaluation Framework
- **6.1 Participant Flow**
  - Screening: MoCA 18-25 (MCI), age ≥60, Mandarin/Cantonese
  - Randomization: A/B groups (standard vs. metamemory-enhanced guidance)
  - Retention: 80% target (4/5 sessions completed)
- **6.2 Assessment Timeline**
  - Day 1 (pre): Technology anxiety, privacy concerns, MoCA baseline
  - Day 1-4 (post): Perceived personalization, emotional safety, narrative score
  - Day 4: Simplified SUS, social influence
  - Day 7: Caregiver feedback
  - Day 28: Follow-up NPS
- **6.3 Evidence-Based Measures**
  - Technology Anxiety (STAM-adapted, 5 items)
  - Privacy Concerns (Extended TAM, 3 items)
  - Perceived Personalization (4 items)
  - Emotional Safety (4 items)
  - Simplified SUS (10 items, older adult validated)
  - Caregiver Observation Form (5 items + 2 open-ended)

### 7. Ethical Considerations
- **7.1 Safety Protocols**
  - Emotional safety: 3-level response (green/yellow/red)
  - Crisis escalation: Emergency contact on file
- **7.2 Privacy Protection**
  - Data encryption: AES-256 at rest, TLS in transit
  - Anonymization: PID-based identifiers, no PII in narrative storage
- **7.3 Regulatory Compliance**
  - China: Personal Information Protection Law (PIPL)
  - International: GDPR principles (data minimization, purpose limitation)

### 8. Limitations & Future Work
- **8.1 Current Limitations**
  - LLM bias: Training data may not reflect Chinese older adult speech patterns
  - ASR accuracy: Whisper lower performance on dementia speech (CHI 2026 evidence)
  - Validation: Empirical data pending (pilot ongoing)
- **8.2 Future Directions**
  - Fine-tuning: Chinese elderly speech corpus
  - Multimodal: Integrate facial expression, voice prosody
  - Long-term: 6-month follow-up for maintenance effects

### 9. Conclusion
- Summary: Neuro-symbolic narrative scorer provides scalable, objective RT quality assessment
- Contribution: Methodology + evaluation framework for AI-enhanced digital therapeutics
- Call to action: Empirical validation needed; CittaVerse pilot data will contribute to AI+RT evidence gap

### References
- ~40-50 references (RT meta-analyses, NLP/dementia, technology acceptance, LLM evaluation)

### Appendices
- **A. Prompt Templates** (event extraction, scoring dimensions)
- **B. Assessment Scales** (Chinese translations)
- **C. Code Repository** (GitHub link, MIT license)

---

## 4. MVP Scope for arXiv Submission

### Must-Have (Week 1: 03-20 to 03-27)
- [ ] **Narrative scorer code cleanup**
  - Remove mock data, production-ready version
  - Add docstrings, type hints, error handling
- [ ] **LaTeX template setup**
  - arXiv-compatible (cs.CL category)
  - Overleaf template or local TeX
- [ ] **Methods section draft** (Sections 3-4)
  - Architecture diagrams (TikZ or draw.io)
  - Algorithm pseudocode
- [ ] **Related work section draft** (Section 2)
  - 20-30 key references
- [ ] **GitHub repository preparation**
  - Public repo: `cittaverse/narrative-scorer`
  - README, LICENSE (MIT), requirements.txt
  - Example usage, mock test script

### Should-Have (Week 2: 03-27 to 04-03)
- [ ] **Introduction + Abstract** (Sections 1-2)
- [ ] **Evaluation framework** (Sections 5-6)
- [ ] **Ethical considerations** (Section 7)
- [ ] **Full reference list** (40-50 items)
- [ ] **Code documentation**
  - API reference, example notebooks

### Nice-to-Have (Week 3: 04-03 to 04-10)
- [ ] **Preliminary results** (if pilot data available)
- [ ] **Comparison baselines** (human expert ratings)
- [ ] **Appendix: Assessment scales** (Chinese + English)
- [ ] **Submission to cs.CL + cs.HC** (cross-listing)

---

## 5. Timeline & Milestones

| Date | Milestone | Owner |
|------|-----------|-------|
| 03-20 | GitHub repo created, code cleanup started | Hulk |
| 03-22 | LaTeX template ready, Methods section draft | Hulk |
| 03-24 | Related work complete, References 80% done | Hulk |
| 03-26 | Full draft v0.5 (all sections) | Hulk |
| 03-27 | V review + feedback | V |
| 03-29 | Revisions complete | Hulk |
| 03-30 | arXiv submission | V (requires account) |

---

## 6. arXiv Submission Requirements

### Account Setup
- **Endorsement**: cs.CL category requires endorsement (first-time submitters)
  - Need endorser: Established arXiv author in cs.CL
  - Alternative: Submit to cs.HC (Human-Computer Interaction) — no endorsement needed
- **Account**: V's email (cittaverse@gmail.com) or institutional email

### Format Requirements
- **PDF**: LaTeX-generated, embedded fonts
- **Abstract**: Single paragraph, 4-6 sentences, ~200 words
- **Length**: No strict limit (technical reports typically 8-15 pages)
- **License**: arXiv perpetual license (non-exclusive)

### Categories
- **Primary**: cs.CL (Computation and Language) — requires endorsement
- **Secondary**: cs.HC (Human-Computer Interaction) — no endorsement
- **Tertiary**: cs.CY (Computers and Society) — optional

**Recommendation**: Submit to cs.HC first (no endorsement delay), then cross-list to cs.CL after endorsement secured

---

## 7. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Endorsement delay | High (blocks cs.CL submission) | Submit to cs.HC first; seek endorser via academic network |
| Pilot data not ready | Medium (weakens empirical claims) | Frame as "methodology + evaluation framework" paper; empirical results in follow-up |
| Code not production-ready | Medium (reproducibility concerns) | Include mock test suite; clearly label as "research prototype" |
| V unavailable for review | High (blocks submission) | Async review via GitHub; 48h turnaround SLA |

---

## 8. Next Actions (GEO #45 → GEO #46)

1. **Create GitHub repo** (`cittaverse/narrative-scorer`)
2. **Code cleanup**: Remove mock data, add production error handling
3. **LaTeX setup**: Overleaf project or local template
4. **Draft Methods section**: Architecture + algorithm details
5. **V confirmation**: arXiv account status, endorser network

---

*GEO #45 Output — arXiv Technical Report Plan v0.1*  
*Hulk 🟢 — 2026-03-19 22:04 UTC*
