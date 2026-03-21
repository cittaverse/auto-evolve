# arXiv Submission Checklist — CittaVerse Narrative Scorer v0.5

**Target Paper**: "CittaVerse Narrative Scorer v0.5: Six-Dimension Assessment for Chinese Autobiographical Memory Quality"  
**Authors**: Hulk, CittaVerse Team  
**Affiliation**: 一念万相科技 (CittaVerse)  
**Contact**: cittaverse@gmail.com  
**Target Date**: 2026-03-30  
**arXiv Categories**: cs.HC (primary) + cs.CL (secondary)

---

## Pre-Submission Checklist

### 1. Manuscript Files ✅

- [x] **LaTeX Source**: `paper.tex` (25KB, complete)
- [x] **Bibliography**: `references.bib` (475 lines, 50 references)
- [ ] **Compiled PDF**: Requires local compilation (sandbox lacks xelatex)
- [ ] **Figures/Tables**: 6 tables embedded in LaTeX
- [ ] **Appendices**: Source code reference, prompt templates, assessment scales

### 2. Content Verification

- [x] **Title**: Clear, specific, includes key contribution
- [x] **Abstract**: 150-250 words, states problem, method, results, implications
- [x] **Keywords**: 8 keywords (reminiscence therapy, narrative assessment, etc.)
- [x] **Introduction**: Motivation, problem statement, contributions, paper organization
- [x] **Related Work**: 5 subsections (autobiographical memory, automated assessment, LLM evaluation, technology acceptance, gap analysis)
- [x] **Methodology**: 6-dimension framework with theoretical basis + scoring formulas
- [x] **Implementation**: Architecture, feature extraction, algorithms, output format, performance
- [x] **Validation**: Mock testing completed, empirical validation ongoing (pilot RCT)
- [x] **Ethics**: Data privacy, emotional safety, algorithmic fairness, transparency
- [x] **Limitations**: 4 current limitations + 5 future directions
- [x] **Conclusion**: Summary + positioning as foundational contribution

### 3. References ✅

- [x] **Total Count**: 50 references
- [x] **Categories**:
  - RT Meta-analyses: 5
  - Autobiographical Memory: 8
  - NLP + Dementia/MCI: 6
  - LLM Evaluation: 6
  - Technology Acceptance: 5
  - Neuro-Symbolic AI: 5
  - Narrative & Identity: 8
  - Emotion & Memory: 7
- [x] **Format**: BibTeX (APA style compatible)
- [x] **Recency**: 35+ references from 2024-2026

### 4. arXiv Account Setup

- [ ] **arXiv Account**: Create/login at https://arxiv.org
- [ ] **Endorsement**: cs.HC does NOT require endorsement ✅
- [ ] **Endorsement**: cs.CL requires endorsement (cross-list after initial submission)
- [ ] **Author Profile**: Ensure cittaverse@gmail.com is verified

### 5. Submission Metadata

| Field | Value |
|-------|-------|
| **Title** | CittaVerse Narrative Scorer v0.5: Six-Dimension Assessment for Chinese Autobiographical Memory Quality |
| **Authors** | Hulk; CittaVerse Team |
| **Affiliation** | 一念万相科技 (CittaVerse), Hangzhou, China |
| **Abstract** | (copy from paper, ~200 words) |
| **Primary Category** | cs.HC (Human-Computer Interaction) |
| **Secondary Category** | cs.CL (Computation and Language) |
| **License** | CC BY 4.0 (recommended for open access) |
| **Comments** | 12 pages, 6 tables, 1 Python listing, 50 references. Source code: https://github.com/cittaverse/narrative-scorer |
| **ACM Classification** | H.5.2 (User Interfaces); I.2.7 (Natural Language Processing); J.3 (Life and Medical Sciences) |
| **MSC Classification** | 68T50 (Natural language processing); 91E40 (Memory and learning) |

### 6. PDF Compilation (Local Execution Required)

**Sandbox Limitation**: No xelatex available in OpenClaw sandbox.

**Local Compilation Commands**:
```bash
cd research/arxiv-paper/
xelatex paper.tex
bibtex paper.aux
xelatex paper.tex
xelatex paper.tex  # Second run for cross-references
```

**Expected Output**: `paper.pdf` (~400-500KB, 12 pages)

**Verification**:
- [ ] CJK fonts render correctly (Chinese terms in dimension names)
- [ ] Tables formatted properly (6 tables)
- [ ] Code listings visible (Python scoring algorithm)
- [ ] Hyperlinks functional (references, citations)
- [ ] Page numbers correct
- [ ] No compilation warnings/errors

### 7. GitHub Repository Sync

- [x] **Repository**: `cittaverse/narrative-scorer` (created per 14:35 UTC header)
- [ ] **Latest Code**: Ensure `src/scorer.py` matches paper description
- [ ] **README.md**: Includes citation reference to arXiv paper
- [ ] **LICENSE**: MIT license present
- [ ] **Tests**: 11 unit tests passing
- [ ] **Examples**: sample_input.txt + sample_output.json included

### 8. Supplementary Materials

- [ ] **Gradio Web UI**: `src/gradio_ui.py` (7.2KB, interactive demo)
- [ ] **Test Suite**: 11 tests with coverage report
- [ ] **Documentation**: README.md (4.7KB)
- [ ] **Sample Narratives**: 5+ examples across quality range (S/F grades)

---

## Submission Process

### Step 1: Compile PDF (Local)
```bash
cd /path/to/arxiv-paper
xelatex paper.tex
bibtex paper.aux
xelatex paper.tex
xelatex paper.tex
```

### Step 2: Upload to arXiv
1. Login to https://arxiv.org
2. Click "Start New Submission"
3. Fill metadata (see Section 5)
4. Upload `paper.pdf`
5. Upload `paper.tex` + `references.bib` as source
6. Select categories: cs.HC (primary), cs.CL (secondary)
7. Choose license: CC BY 4.0
8. Add comments: "12 pages, 6 tables, 1 Python listing, 50 references"

### Step 3: Review & Submit
1. Preview submission page
2. Verify all metadata
3. Confirm authorship
4. Submit

### Step 4: Post-Submission
- [ ] **Announce**: Share arXiv link on Twitter/LinkedIn/GitHub
- [ ] **Update README**: Add arXiv citation badge to narrative-scorer repo
- [ ] **Notify Community**: Email relevant researchers (optional)
- [ ] **Track Metrics**: Monitor downloads, citations (Google Scholar alert)

---

## arXiv Category Strategy

### Primary: cs.HC (Human-Computer Interaction)
- **Why**: Narrative scorer is a tool for human users (older adults, clinicians)
- **Endorsement**: NOT required ✅
- **Benefit**: Immediate submission, no delay

### Secondary: cs.CL (Computation and Language)
- **Why**: NLP methods for Chinese narrative analysis
- **Endorsement**: Required for cross-listing
- **Strategy**: Submit to cs.HC first, then seek endorsement for cs.CL cross-list

### Alternative Categories (if needed)
- cs.AI (Artificial Intelligence): Neuro-symbolic approach
- cs.SE (Software Engineering): Open-source tool release
- q-bio.NC (Neuroscience and Cognition): Memory assessment focus

---

## Timeline

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Manuscript Complete | 2026-03-20 | ✅ Done |
| LaTeX Template | 2026-03-20 | ✅ Done |
| References (50) | 2026-03-20 | ✅ Done |
| PDF Compilation | 2026-03-20 | ⏳ Local execution needed |
| arXiv Submission | 2026-03-30 | 📋 Pending |
| Announcement | 2026-03-30 | 📋 Pending |
| cs.CL Endorsement | 2026-04-15 | 📋 Pending |
| Cross-list to cs.CL | 2026-04-20 | 📋 Pending |

---

## Citation Format (for README + future papers)

### BibTeX
```bibtex
@article{hulk2026cittaverse,
  title={CittaVerse Narrative Scorer v0.5: Six-Dimension Assessment for Chinese Autobiographical Memory Quality},
  author={Hulk and CittaVerse Team},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2026},
  url={https://arxiv.org/abs/XXXX.XXXXX}
}
```

### APA
```
Hulk & CittaVerse Team. (2026). CittaVerse Narrative Scorer v0.5: Six-Dimension 
Assessment for Chinese Autobiographical Memory Quality. arXiv preprint 
arXiv:XXXX.XXXXX. https://arxiv.org/abs/XXXX.XXXXX
```

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| PDF compilation errors | Medium | High | Test locally before submission; fix LaTeX warnings |
| arXiv moderation delay | Low | Medium | Submit during weekday (Mon-Thu); avoid weekends |
| cs.CL endorsement denial | Low | Low | cs.HC primary ensures visibility; cross-list optional |
| Plagiarism flag | Very Low | High | All references properly cited; original contribution clear |
| Author name confusion | Medium | Low | Use consistent author name "Hulk" + affiliation |

---

## Post-Acceptance Actions

1. **GitHub Updates**:
   - Add arXiv badge to README.md
   - Update citation section
   - Link to arXiv paper in Gradio UI

2. **Social Announcement**:
   - Twitter thread (key contributions + demo GIF)
   - LinkedIn post (professional audience)
   - Reddit r/MachineLearning (if appropriate)
   - Hacker News "Show HN" (narrative-scorer tool)

3. **Community Outreach**:
   - Email 10-15 relevant researchers (authors of cited papers)
   - Submit to awesome lists (awesome-nlp, awesome-dementia-detection)
   - Consider workshop paper (ACL 2026, CHI 2026 Late-Breaking Work)

4. **Metrics Tracking**:
   - Google Scholar profile (create if not exists)
   - arXiv download stats (check monthly)
   - GitHub stars/forks (track correlation with paper release)

---

**Verification Status**: V3 (Static复核) — Checklist created, files verified, pending local PDF compilation

**Next Action**: Local PDF compilation → arXiv submission by 2026-03-30

---

*Created: 2026-03-20 21:21 UTC (GEO #49 Deliverable)*  
*Hulk 🟢 — CittaVerse*
