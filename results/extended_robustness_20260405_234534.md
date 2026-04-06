# Extended Robustness Experiment Report v0.7

**Date**: 2026-04-05T23:45:34.011809
**Cron Job**: hulk-🔬-夜间长跑实验
**Samples**: 28
**Success Rate**: 28/28 (100.0%)

## Executive Summary

本实验是 2026-03-28 夜间长跑实验的产出，测试 L0/VSNC 叙事评分器 v0.7 在 {len(results)} 个样本上的鲁棒性。

**核心发现**:

- 平均评分：40.72 ± 6.63
- 平均延迟：0.16ms
- 评分范围：28.50 - 53.20

## Grade Distribution

| Grade | Count | Percentage |
|-------|-------|------------|
| D | 28 | 100.0% |

## By Category

| Category | N | Avg Score | Std Dev | Min | Max |
|----------|---|-----------|---------|-----|-----|
| adversarial_emotion | 2 | 47.25 | 1.25 | 46.00 | 48.50 |
| adversarial_nonsense | 2 | 34.50 | 6.00 | 28.50 | 40.50 |
| boundary_long | 1 | 49.80 | 0.00 | 49.80 | 49.80 |
| boundary_short | 3 | 29.00 | 0.71 | 28.50 | 30.00 |
| cross_lingual | 2 | 39.45 | 0.75 | 38.70 | 40.20 |
| negative | 3 | 42.90 | 2.95 | 40.20 | 47.00 |
| neutral | 2 | 40.00 | 0.00 | 40.00 | 40.00 |
| noise_asr | 2 | 31.50 | 3.00 | 28.50 | 34.50 |
| noise_typo | 2 | 43.50 | 0.00 | 43.50 | 43.50 |
| positive | 5 | 46.06 | 3.95 | 41.70 | 53.20 |
| reflective | 2 | 42.25 | 0.75 | 41.50 | 43.00 |
| traumatic | 2 | 43.75 | 0.75 | 43.00 | 44.50 |

## Dimension Statistics

| Dimension | Mean | Std Dev |
|-----------|------|---------|
| event_richness | 26.79 | 13.11 |
| temporal_coherence | 100.00 | 0.00 |
| causal_coherence | 23.57 | 17.36 |
| emotional_depth | 8.05 | 23.46 |
| identity_integration | 20.90 | 21.22 |
| information_density | 67.08 | 8.15 |

## Sample-Level Results

| ID | Category | Length | Score | Grade | Arousal | Latency |
|-----|----------|--------|-------|-------|---------|--------|
| P01 | positive | 75 | 46.2 | D | 极低 | 0.79ms |
| P02 | positive | 71 | 43.2 | D | 极低 | 0.12ms |
| P03 | positive | 70 | 53.2 | D | 低 | 0.22ms |
| P04 | positive | 78 | 46.0 | D | 中 | 0.19ms |
| P05 | positive | 77 | 41.7 | D | 高 | 0.18ms |
| N01 | negative | 74 | 41.5 | D | 极低 | 0.10ms |
| N02 | negative | 58 | 47.0 | D | 极低 | 0.10ms |
| N03 | negative | 48 | 40.2 | D | 低 | 0.15ms |
| M01 | neutral | 59 | 40.0 | D | 极低 | 0.15ms |
| M02 | neutral | 53 | 40.0 | D | 极低 | 0.09ms |
| R01 | reflective | 60 | 43.0 | D | 低 | 0.17ms |
| R02 | reflective | 54 | 41.5 | D | 低 | 0.16ms |
| T01 | traumatic | 67 | 44.5 | D | 极低 | 0.10ms |
| T02 | traumatic | 50 | 43.0 | D | 极低 | 0.09ms |
| ASR01 | noise_asr | 54 | 34.5 | D | 中 | 0.15ms |
| ASR02 | noise_asr | 44 | 28.5 | D | 极低 | 0.08ms |
| TYPO01 | noise_typo | 60 | 43.5 | D | 极低 | 0.09ms |
| TYPO02 | noise_typo | 44 | 43.5 | D | 极低 | 0.08ms |
| SHORT01 | boundary_short | 7 | 28.5 | D | 极低 | 0.07ms |
| SHORT02 | boundary_short | 6 | 30.0 | D | 极低 | 0.07ms |
| SHORT03 | boundary_short | 6 | 28.5 | D | 极低 | 0.06ms |
| LONG01 | boundary_long | 376 | 49.8 | D | 极高 | 0.44ms |
| ADV01 | adversarial_emotion | 73 | 46.0 | D | 极高 | 0.18ms |
| ADV02 | adversarial_emotion | 58 | 48.5 | D | 高 | 0.16ms |
| ADV03 | adversarial_nonsense | 60 | 40.5 | D | 极低 | 0.11ms |
| ADV04 | adversarial_nonsense | 61 | 28.5 | D | 极低 | 0.09ms |
| MIX01 | cross_lingual | 77 | 40.2 | D | 极低 | 0.10ms |
| MIX02 | cross_lingual | 75 | 38.7 | D | 极低 | 0.18ms |

## Notes

- 本实验使用 v0.7 叙事评分器 (rule-based + mock LLM)
- DASHSCOPE_API_KEY 验证失败 (401 错误)，真实 LLM 测试阻塞 >348h
- 后续计划：API Key 轮换后执行 live validation
