# GEO #54 — Rememo (CHI 2026) Differentiation Analysis

**Date**: 2026-03-21 22:30 UTC  
**Theme**: Rememo (CHI 2026) Competitive Differentiation Analysis  
**Status**: ✅ Complete

---

## Executive Summary

**Scheduled**: 22:00 UTC 03-21  
**Executed**: 22:00-22:30 UTC 03-21  
**Duration**: ~30 minutes

**Key Achievement**: Completed comprehensive differentiation analysis between Rememo (CHI 2026) and CittaVerse Narrative Scorer. Key finding: **complementary, not competitive** — Rememo focuses on pre-session preparation (generating memory triggers), while CittaVerse focuses on post-session assessment (narrative quality scoring). Identified 4 unique value propositions for CittaVerse and proposed collaboration strategy.

---

## GEO #54 Deliverables

### 1. Rememo Information Collection

**Sources Verified**:
- arXiv:2602.17083 [cs.HC] ✅
- CHI 2026 Program Page ✅
- DDG Search (10 results) ✅
- arXiv HTML version (full paper content) ✅

**Key Rememo Facts**:
- **Title**: Rememo: A Research-through-Design Inquiry Towards an AI-in-the-loop Therapist's Tool for Dementia Reminiscence
- **Authors**: Celeste Seah et al. (NUS + ECON Healthcare, Singapore)
- **Publication**: CHI 2026 (April 13-17, Barcelona)
- **Core Function**: Generate personalized visual memory triggers for RT sessions
- **Technology**: Generative AI (SDXL/Flux.1/Imagen) + LLM for guiding questions
- **Validation**: 2-week field study, 5 caregivers, 21 residents, 151 generated images
- **Key Insight**: AI should augment (not replace) therapists' relational work

**Verification Level**: V2 (multi-source cross-confirmation)

---

### 2. Differentiation Analysis

**5 Comparison Dimensions**:

| Dimension | Rememo | CittaVerse |
|-----------|--------|------------|
| **Workflow Stage** | Pre-session (preparation) | Post-session (assessment) |
| **Core Value** | Improve session prep efficiency | Quantify session outcomes |
| **AI Paradigm** | Generative AI (images) | Neuro-symbolic AI (scoring) |
| **Primary Users** | Frontline caregivers | Researchers/clinicians |
| **Cultural Focus** | Singapore (4 languages) | China (Chinese narratives) |

**Key Insight**: Rememo and CittaVerse serve different stages of the RT workflow. They can be integrated into a complete "Prepare → Execute → Assess" toolchain.

**Verification Level**: V1 (analysis based on collected evidence)

---

### 3. CittaVerse Unique Value Propositions

**UVP #1: Theoretical Depth**
- 6-dimension framework based on autobiographical memory theory
- Each dimension has explicit theoretical basis and scoring formula
- Supports cross-study comparison and meta-analysis

**UVP #2: Chinese Specificity**
- First narrative quality assessment tool designed for Chinese autobiographical memory
- Scoring thresholds calibrated for Chinese older adults
- Supports dialect and regional cultural differences (future extension)

**UVP #3: Explainability & Reproducibility**
- Neuro-symbolic AI (LLM extraction + rule-based scoring)
- High determinism (same input → same score)
- 6-dimension scores are traceable (each score has clear calculation basis)

**UVP #4: Product Iteration Support**
- Serves researchers + product teams
- Quantitative metrics + unit tests
- Supports A/B testing and product iteration (score changes are trackable)

**Verification Level**: V1 (strategic inference based on analysis)

---

### 4. Collaboration Strategy

**Short-term (1-2 weeks)**:
1. Accelerate arXiv submission (target: 03-25)
2. Update README.md with differentiation positioning
3. Contact Rememo team (celestes@nus.edu.sg) — express appreciation, propose collaboration

**Medium-term (1-3 months)**:
1. Explore feature integration (Rememo images + CittaVerse scoring)
2. Execute Path B Pilot (10-20 Chinese older adults)
3. Plan academic publication (JMIR Aging, CHI 2027)

**Long-term (3-12 months)**:
1. Productization path (B2B licensing, B2C life story service)
2. Standardization initiative (Chinese narrative quality assessment standard)
3. Joint workshop at CHI 2027

**Verification Level**: V1 (strategic planning)

---

### 5. Evidence Papers Tracking

**Updated Count**: 13 papers (+1: Rememo)

**New Addition**:
- Rememo (CHI 2026): AI-in-the-loop therapist tool for dementia reminiscence

**Previous 12** (unchanged from GEO #53):
- Yang 2026, Pu 2025, Ni 2026, Wang 2026, RemVerse 2025, Kimono 2025, IET 2026, etc.

**Verification Level**: V3 (static file update)

---

## Git Commit & Push

**Repository**: `cittaverse/auto-evolve`  
**Commit**: `535fbfd`  
**Message**: `docs: GEO #54 - Rememo (CHI 2026) differentiation analysis`  
**Files Changed**: 
- `research/evidence/rememo-differentiation-analysis.md` (new, 11KB)
- `HEARTBEAT.md` (updated status + GEO #54 completion)

**Verification**: V4 (push confirmed)

---

## Verification Status

| Task | Verification Level | Status |
|------|-------------------|--------|
| Rememo info collection | V2 (multi-source) | ✅ Complete |
| Differentiation analysis | V1 (inference) | ✅ Complete |
| UVP identification | V1 (inference) | ✅ Complete |
| Collaboration strategy | V1 (planning) | ✅ Complete |
| Evidence tracking update | V3 (file update) | ✅ Complete |
| Git commit & push | V4 (push confirmed) | ✅ Complete |

---

## Key Insights

### 1. Rememo is Complementary, Not Competitive
Rememo focuses on **pre-session preparation** (generating memory triggers), while CittaVerse focuses on **post-session assessment** (narrative quality scoring). They can be integrated into a complete RT workflow toolchain.

### 2. CittaVerse Has Clear Differentiation
- **Assessment expertise**: 6-dimension framework (Rememo doesn't have this)
- **Chinese specificity**: Focus on Chinese older adults (Rememo is Singapore-focused)
- **Explainability**: Neuro-symbolic method supports clinical decisions
- **Product orientation**: Open-source tool + API for rapid integration

### 3. Collaboration > Competition
- Joint research can produce greater academic impact
- Market education can expand the pie together
- Data sharing (Rememo's 151 images + CittaVerse scores) can reveal "image type → narrative quality" relationships

### 4. arXiv Submission Urgency
Rememo has been published at CHI 2026. CittaVerse should establish academic presence ASAP (target: 03-25). Cite Rememo in the paper to show awareness of state-of-the-art.

---

## Blocked Items Summary

| Blocker | Owner | Duration | Impact |
|---------|-------|----------|--------|
| arXiv submission execution | V | >72h | Paper not citable |
| Path B recruitment | V | >72h | Pilot not started |
| DASHSCOPE_API_KEY | V | >84h | L0 real testing blocked |
| Azure/iFlytek API Keys | V | >132h | ASR comparison blocked |

**Note**: GitHub auth issue RESOLVED. PR monitoring functional.

---

## Next Actions

### Immediate (Post-GEO #54)
1. 🔴 **03-22 V Decision: Path B** — Continue (execute community outreach) or Pause (backtrack方案设计)
2. 🟡 **arXiv Submission** — V to execute (files ready 72h+, 30-45 min task)
3. 🟢 **Rememo Team Contact** — Draft email to Celeste Seah (celestes@nus.edu.sg)

### GEO #55 (Scheduled: 04:00 UTC 03-22 / 12:00 CST)
- Theme: Path B Decision Integration OR arXiv Submission Confirmation
- If Path B continues: Integrate recruitment progress into evidence docs
- If arXiv submitted: Update tracking docs + plan next academic submission
- If neither: Deepen Rememo collaboration strategy (draft contact email)

### PR Monitoring
- PR #11 (caramaschiHG/awesome-ai-agents-2026): Day 12 (03-22) — Continue monitoring
- PR #23 (onejune2018/Awesome-LLM-Eval): Day 4 — Continue monitoring
- PR #112 (kakoni/awesome-healthcare): Day 5 — Continue monitoring

---

## 下一轮优先级 (GEO #55)

**日期**: 2026-03-22 04:00 UTC (12:00 CST)  
**主题**: Path B 决策整合 / arXiv 提交确认

**待执行** (取决于 V 行动):

**场景 A: V 确认 Path B 继续**
- 整合招募进展到 evidence 文档
- 更新 HEARTBEAT 招募状态
- 准备 Day 1 执行追踪模板

**场景 B: V 完成 arXiv 提交**
- 更新 arXiv 追踪文档 (submission ID, status)
- 规划下一波学术投稿 (CHI 2027? JMIR?)
- 准备论文宣传材料 (Twitter/LinkedIn/知乎)

**场景 C: 两者皆未完成**
- 深化 Rememo 合作策略（起草联系邮件）
- 更新 README.md 差异化定位
- 准备 Path B 招募材料优化建议

---

*Hulk 🟢 - Compressing chaos into structure*
