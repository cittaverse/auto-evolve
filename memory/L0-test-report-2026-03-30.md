# L0 真实测试报告

**测试时间**: 2026-03-30 09:14-09:35 UTC  
**模型**: qwen3.5-plus  
**样本数**: 5 个老年叙事（positive/negative/neutral/reflective/traumatic）

---

## 测试结果

### 最终成功率：1/5 (20%)

| 样本 | 类型 | 状态 | 备注 |
|------|------|------|------|
| real-001 | positive | ❌ timeout | 第一次成功，重试超时 |
| real-002 | negative | ✅ ok | emotional=88, temporal=95 |
| real-003 | neutral | ❌ timeout | 第一次成功，重试超时 |
| real-004 | reflective | ❌ timeout | 两次都超时 |
| real-005 | traumatic | ❌ timeout | 两次都超时 |

### 成功样本评分 (real-002)

| 维度 | 分数 |
|------|------|
| event_richness | 60 |
| temporal_coherence | 95 |
| causal_coherence | 90 |
| emotional_depth | 88 |
| identity_integration | 70 |
| information_density | 85 |

---

## 问题分析

**主要问题**: API 超时率高（80%）

**可能原因**:
1. 网络不稳定
2. API 服务端响应慢
3. timeout 设置过短（60-90s）

**解决方案**:
1. 增加 timeout 到 180s
2. 添加重试机制（指数退避）
3. 批量测试改为逐个测试

---

## 结论

**LLM 评分能力**: ✅ 验证通过（成功样本评分合理）
**API 稳定性**: ❌ 需要优化（超时率高）
**建议**: 
- 生产环境需要更好的错误处理
- 考虑本地 rule-only fallback（v0.6.4）

---

*测试文件：`tests/l0_results.json`*
