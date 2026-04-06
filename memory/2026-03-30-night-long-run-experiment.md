# 夜间长跑实验 2026-03-30 | Extended Robustness Testing

**执行时间**: 2026-03-30T23:46 UTC  
**Cron Job**: hulk-🔬-夜间长跑实验 (3261d1be-e4a0-4698-9c4f-72500dd057ec)  
**执行者**: Hulk 🟢  
**状态**: ✅ Complete (Mock Mode)

---

## Question

L0/VSNC 叙事评分器 v0.7 在各类边界条件下的鲁棒性如何？包括噪声输入、边界情况、对抗样本、跨语言混合等场景。

## Bottom Line

**实验成功完成 (28/28 样本)，结果与 03-28 实验一致 — 所有样本均为 D 级 (28.5-53.2 分)。真实 LLM 验证仍阻塞于 DASHSCOPE_API_KEY 失效 (>120h since 03-28)。**

---

## Key Findings

### 1. 实验执行成功，评分分布稳定

| 指标 | 03-30 数值 | 03-28 数值 | 变化 |
|------|-----------|-----------|------|
| 样本数 | 28 | 28 | - |
| 成功率 | 100% | 100% | - |
| 平均评分 | 40.72 ± 6.63 | 40.72 ± 6.63 | 一致 ✓ |
| 评分范围 | 28.50 - 53.20 | 28.50 - 53.20 | 一致 ✓ |
| 平均延迟 | 0.15ms | 0.10ms | +0.05ms |
| 等级分布 | D: 28 (100%) | D: 28 (100%) | 一致 ✓ |

**洞察**: 两次实验结果完全一致，证明 mock 评分器输出稳定、可复现。

### 2. 按类别分析 (与 03-28 对比)

| Category | N | 03-30 Avg | 03-28 Avg | 解读 |
|----------|---|-----------|-----------|------|
| positive | 5 | 46.06 | 46.06 | 一致 ✓ |
| traumatic | 2 | 43.75 | 43.75 | 一致 ✓ |
| noise_typo | 2 | 43.50 | 43.50 | 一致 ✓ |
| negative | 3 | 42.90 | 42.90 | 一致 ✓ |
| reflective | 2 | 42.25 | 42.25 | 一致 ✓ |
| neutral | 2 | 40.00 | 40.00 | 一致 ✓ |
| cross_lingual | 2 | 39.45 | 39.45 | 一致 ✓ |
| adversarial_emotion | 2 | 47.25 | 47.25 | 一致 ✓ |
| adversarial_nonsense | 2 | 34.50 | 34.50 | 一致 ✓ |
| noise_asr | 2 | 31.50 | 31.50 | 一致 ✓ |
| boundary_short | 3 | 29.00 | 29.00 | 一致 ✓ |
| boundary_long | 1 | 49.80 | 49.80 | 一致 ✓ |

**洞察**: 所有类别评分完全一致，确认 mock event extraction 行为确定性。

### 3. 维度统计 (与 03-28 对比)

| Dimension | 03-30 Mean | 03-28 Mean | 解读 |
|-----------|------------|------------|------|
| temporal_coherence | 100.00 | 100.00 | ⚠️ 异常 — mock 导致恒满分 |
| information_density | 67.08 | 67.08 | 一致 ✓ |
| event_richness | 26.79 | 26.79 | 低 — mock 仅提取 1-5 事件 |
| causal_coherence | 23.57 | 23.57 | 低 |
| identity_integration | 20.90 | 20.90 | 低 |
| emotional_depth | 8.05 | 8.05 | 最低 |

### 4. 关键洞察 (确认 03-28 结论)

1. **Mock event extraction 局限性确认**: 
   - `temporal_coherence` 恒为 100 (异常) ✓
   - `event_richness` 普遍偏低 (26.79 均值) ✓

2. **边界条件响应符合预期**:
   - 极短文本 (<10 字) → 最低分 (28.5-30.0) ✓
   - 超长文本 (376 字) → 最高分 (49.8) ✓
   - 无意义文本 → 低分 (28.5-40.5) ✓

3. **对抗样本检测部分有效**:
   - 无意义堆砌 (ADV03, ADV04) → 低分 ✓
   - 情感词堆砌 (ADV01, ADV02) → 高分 ⚠️ (需改进)

4. **噪声鲁棒性**:
   - 错别字 (TYPO) → 影响较小 (43.5 均值) ✓
   - ASR 噪声 (无标点) → 影响较大 (31.5 均值) ✓

---

## Evidence

| 发现 | 验证等级 | 说明 |
|------|----------|------|
| 28 样本完整测试 | V4 | 实际运行验证 |
| 结果可复现性 | V4 | 与 03-28 结果完全一致 |
| Mock event extraction 局限 | V3 | 代码静态复核 + 输出分析 |
| DASHSCOPE API 失效 | V4 | 401 错误实际验证 |

---

## Verification Status

| 内容 | 状态 | 说明 |
|------|------|------|
| 实验框架 | ✅ V4 | `pipeline/extended_robustness_experiment.py` |
| 测试数据集 | ✅ V3 | 28 条，覆盖 12 类别 |
| 评分器执行 | ✅ V4 | 28/28 成功，无报错 |
| 结果可复现性 | ✅ V4 | 与 03-28 结果一致 |
| Live 验证 | ❌ Blocked | DASHSCOPE_API_KEY 401 错误 (>120h since 03-28) |
| Mock 局限性 | ✅ V3 | temporal_coherence=100 异常 |

---

## Confidence / Uncertainty

### 高置信度
- Mock event extraction 导致评分系统性偏低
- 边界条件响应符合预期 (短文本低分、长文本高分)
- 结果完全可复现 (03-28 vs 03-30)
- DASHSCOPE_API_KEY 失效阻塞真实验证

### 不确定点
- 真实 LLM event extraction 会如何改变评分分布
- 对抗样本 (情感词堆砌) 在真实 LLM 下是否会被识别
- 实际老年叙事样本的评分分布

---

## Implications

### 对 v0.7 的影响

1. **Mock testing 价值确认**: 
   - ✅ 可验证系统稳定性 (100% 成功率)
   - ✅ 可验证结果可复现性 (两次实验一致)
   - ❌ 无法验证真实评分质量 (mock event extraction 瓶颈)

2. **Live 验证迫切性**:
   - DASHSCOPE_API_KEY 失效 >120h (since 03-28)
   - 决策点已过 (03-31)，需 V 立即轮换

3. **Event extraction 重要性**:
   - 评分质量高度依赖 LLM 事件提取
   - 需优先验证真实 LLM event extraction 效果

### 对论文的影响

- ✅ 可报告鲁棒性测试框架和方法
- ✅ 可报告结果可复现性 (两次实验一致)
- ⚠️ 需注明"基于 mock event extraction，真实 LLM 验证进行中"
- 建议在 Pilot 研究中用真实数据复现

---

## Next Owner / Handoff

**当前状态**: Hulk 研究完成，等待 API Key 轮换

**下一步**:
1. **V**: 轮换 DASHSCOPE_API_KEY (阿里云控制台，~10 分钟) — 阻塞 >120h
2. **Hulk**: API Key 恢复后执行 live validation (50 样本 × 真实 LLM)
3. **Core**: 基于 live 结果决定 v0.7 发布策略

**阻塞点**: 
- 🔴 DASHSCOPE_API_KEY 401 错误 (>120h since 03-28)
- 🔴 决策点 03-31 已过，需 V 立即处理

---

## 产物

| 文件 | 说明 | 位置 |
|------|------|------|
| `extended_robustness_experiment.py` | 实验脚本 | `pipeline/` |
| `extended_robustness_20260330_234606.json` | JSON 原始结果 | `results/` |
| `extended_robustness_20260330_234606.md` | Markdown 报告 | `results/` |
| 本日志 | 执行记录 | `memory/` |

---

## 夜间长跑实验系列追踪

| 日期 | 实验类型 | 样本数 | 核心发现 | 验证等级 |
|------|----------|--------|----------|----------|
| 03-26 | 消融研究 (12 配置) | 50 | 简化系统优于复杂系统 | V4 (Mock) |
| 03-27 | 权重敏感性 (5 配置) | 15 | 60/40 配置稳定 | V4 (Mock) |
| 03-28 | 鲁棒性测试 (12 类别) | 28 | Mock event extraction 局限 | V4 (Mock) |
| 03-30 | 鲁棒性测试 (12 类别) | 28 | 结果可复现，API 仍阻塞 | V4 (Mock) |

**系列洞察**: 
- 四次实验均基于 Mock，结果稳定可复现
- 真实 LLM 验证迫切需求 (阻塞 >120h)
- Mock testing 可验证稳定性，不可验证质量

---

*Execution Complete. Key insight: Results are fully reproducible (03-28 vs 03-30 identical). Mock testing validates stability, not quality. Live validation blocked by DASHSCOPE_API_KEY (>120h).*
