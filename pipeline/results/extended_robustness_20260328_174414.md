# Extended Robustness Experiment Report v0.7

**Date**: 2026-03-28T17:44:14.338083
**Cron Job**: hulk-🔬-夜间长跑实验
**Samples**: 28
**Success Rate**: 0/28 (0.0%)

## Executive Summary

本实验是 2026-03-28 夜间长跑实验的产出，测试 L0/VSNC 叙事评分器 v0.7 在 {len(results)} 个样本上的鲁棒性。


## Failures

- **P01** (positive): score_narrative_v0_5() missing 1 required positional argument: 'events'
- **P02** (positive): score_narrative_v0_5() missing 1 required positional argument: 'events'
- **P03** (positive): score_narrative_v0_5() missing 1 required positional argument: 'events'
- **P04** (positive): score_narrative_v0_5() missing 1 required positional argument: 'events'
- **P05** (positive): score_narrative_v0_5() missing 1 required positional argument: 'events'
- **N01** (negative): score_narrative_v0_5() missing 1 required positional argument: 'events'
- **N02** (negative): score_narrative_v0_5() missing 1 required positional argument: 'events'
- **N03** (negative): score_narrative_v0_5() missing 1 required positional argument: 'events'
- **M01** (neutral): score_narrative_v0_5() missing 1 required positional argument: 'events'
- **M02** (neutral): score_narrative_v0_5() missing 1 required positional argument: 'events'

*... and 18 more failures*

## Notes

- 本实验使用 v0.7 叙事评分器 (rule-based + mock LLM)
- DASHSCOPE_API_KEY 验证失败 (401 错误)，真实 LLM 测试阻塞 >348h
- 后续计划：API Key 轮换后执行 live validation
