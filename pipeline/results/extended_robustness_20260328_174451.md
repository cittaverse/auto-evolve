# Extended Robustness Experiment Report v0.7

**Date**: 2026-03-28T17:44:51.183174
**Cron Job**: hulk-🔬-夜间长跑实验
**Samples**: 28
**Success Rate**: 0/28 (0.0%)

## Executive Summary

本实验是 2026-03-28 夜间长跑实验的产出，测试 L0/VSNC 叙事评分器 v0.7 在 {len(results)} 个样本上的鲁棒性。


## Failures

- **P01** (positive): Event.__init__() got an unexpected keyword argument 'type'
- **P02** (positive): Event.__init__() got an unexpected keyword argument 'type'
- **P03** (positive): Event.__init__() got an unexpected keyword argument 'type'
- **P04** (positive): Event.__init__() got an unexpected keyword argument 'type'
- **P05** (positive): Event.__init__() got an unexpected keyword argument 'type'
- **N01** (negative): Event.__init__() got an unexpected keyword argument 'type'
- **N02** (negative): Event.__init__() got an unexpected keyword argument 'type'
- **N03** (negative): Event.__init__() got an unexpected keyword argument 'type'
- **M01** (neutral): Event.__init__() got an unexpected keyword argument 'type'
- **M02** (neutral): Event.__init__() got an unexpected keyword argument 'type'

*... and 18 more failures*

## Notes

- 本实验使用 v0.7 叙事评分器 (rule-based + mock LLM)
- DASHSCOPE_API_KEY 验证失败 (401 错误)，真实 LLM 测试阻塞 >348h
- 后续计划：API Key 轮换后执行 live validation
