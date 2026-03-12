# CittaVerse Paper Roadmap: Neuro-Symbolic AI for Narrative Memory Scoring

## 1. Core Hypothesis
A Neuro-symbolic LLM pipeline achieves comparable accuracy to state-of-the-art pure LLM regression models in scoring Autobiographical Interviews (Levine 2002), while providing 100% deterministic traceability and clinical explainability, overcoming the black-box limitations of current neural approaches.

## 2. Experimental Design (The "Bake-Off")
- **Dataset**: 50-100 autobiographical narratives (Either DementiaBank/Pitt Corpus or high-fidelity LLM-synthesized clinical personas).
- **Ground Truth**: Human expert scoring (2 independent raters calculating ICC).
- **Baseline Model (Neural)**: Fine-tuned or Zero-shot LLM (e.g., Gemini 2.5 Pro / Llama-3) outputting a continuous regression score.
- **Proposed Model (Neuro-Symbolic)**: LLM (Entity Extractor) + Python Expert System (Levine 2002 Logic Tree).

## 3. Key Metrics
- **Accuracy/Reliability**: Pearson's r and Intraclass Correlation Coefficient (ICC) against human raters.
- **Explainability Score**: Percentage of scoring decisions directly traceable to a specific clinical rule.
- **Error Analysis**: Qualitative analysis of edge cases where the pure LLM hallucinated but the Neuro-symbolic model remained robust.

## 4. Target Venues
- **Journals**: npj Digital Medicine, Journal of Medical Internet Research (JMIR), Alzheimer's & Dementia (TRCI).
- **Conferences**: Machine Learning for Healthcare (MLHC), ACM Conference on Health, Inference, and Learning (CHIL).