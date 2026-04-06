# 夜间长跑实验 2026-03-28 | Extended Robustness Testing

**执行时间**: 2026-03-28T17:45 UTC  
**Cron Job**: hulk-🔬-夜间长跑实验 (3261d1be-e4a0-4698-9c4f-72500dd057ec)  
**执行者**: Hulk 🟢  
**状态**: ✅ Complete (with limitations)

---

## Question

L0/VSNC 叙事评分器 v0.7 在各类边界条件下的鲁棒性如何？包括噪声输入、边界情况、对抗样本、跨语言混合等场景。

## Bottom Line

**实验成功完成 (28/28 样本)，但所有样本均为 D 级 (28.5-53.2 分) — mock event extraction 信息不足导致评分偏低。真实 LLM 测试仍阻塞于 DASHSCOPE_API_KEY 失效 (>348h)。**

---

## Key Findings

### 1. 实验执行成功，但评分系统偏低

| 指标 | 数值 |
|------|------|
| 样本数 | 28 (14 original + 14 extended) |
| 成功率 | 100% (28/28) |
| 平均评分 | 40.72 ± 6.63 |
| 评分范围 | 28.50 - 53.20 |
| 平均延迟 | 0.10ms |
| 等级分布 | D: 28 (100%) |

### 2. 按类别分析

| Category | N | Avg Score | 解读 |
|----------|---|-----------|------|
| positive | 5 | 46.06 | 正向叙事评分最高 |
| traumatic | 2 | 43.75 | 创伤叙事评分较高 (情感深度) |
| noise_typo | 2 | 43.50 | 错别字对评分影响有限 |
| negative | 3 | 42.90 | 负向叙事中等 |
| reflective | 2 | 42.25 | 反思性叙事中等 |
| neutral | 2 | 40.00 | 中性叙事较低 |
| cross_lingual | 2 | 39.45 | 中英混合略低 |
| adversarial_emotion | 2 | 47.25 | 情感词堆砌反而得分较高 (异常) |
| adversarial_nonsense | 2 | 34.50 | 无意义文本评分最低 ✓ |
| noise_asr | 2 | 31.50 | ASR 噪声影响较大 |
| boundary_short | 3 | 29.00 | 极短文本评分最低 ✓ |
| boundary_long | 1 | 49.80 | 长文本评分最高 ✓ |

### 3. 维度统计

| Dimension | Mean | Std Dev | 解读 |
|-----------|------|---------|------|
| temporal_coherence | 100.00 | 0.00 | ⚠️ 异常 — mock event extraction 导致所有样本时序连贯性满分 |
| information_density | 67.08 | 8.11 | 信息密度相对较高 |
| event_richness | 26.79 | 13.11 | 事件丰富度低 — mock extraction 仅提取 1-5 个事件 |
| causal_coherence | 23.57 | 17.36 | 因果连贯性低 |
| identity_integration | 20.90 | 21.22 | 身份整合低 |
| emotional_depth | 8.05 | 23.46 | 情感深度最低 |

### 4. 关键洞察

1. **Mock event extraction 局限性**: 
   - 简单句子分割无法捕捉真实事件的丰富性
   - 导致 `temporal_coherence` 恒为 100 (异常)
   - `event_richness` 普遍偏低 (26.79 均值)

2. **边界条件响应符合预期**:
   - 极短文本 (<10 字) → 最低分 (28.5-30.0) ✓
   - 超长文本 (376 字) → 最高分 (49.8) ✓
   - 无意义文本 → 低分 (28.5-40.5) ✓

3. **对抗样本检测部分有效**:
   - 无意义堆砌 (ADV03, ADV04) → 低分 ✓
   - 情感词堆砌 (ADV01, ADV02) → 高分 ⚠️ (需改进)

4. **噪声鲁棒性**:
   - 错别字 (TYPO) → 影响较小 (43.5 均值)
   - ASR 噪声 (无标点) → 影响较大 (31.5 均值)

---

## Evidence

| 发现 | 验证等级 | 说明 |
|------|----------|------|
| 28 样本完整测试 | V4 | 实际运行验证 |
| 评分系统响应边界条件 | V4 | 短文本低分、长文本高分 |
| Mock event extraction 局限 | V3 | 代码静态复核 + 输出分析 |
| DASHSCOPE API 失效 | V4 | 401 错误实际验证 |

---

## Verification Status

| 内容 | 状态 | 说明 |
|------|------|------|
| 实验框架 | ✅ V4 | `pipeline/extended_robustness_experiment.py` |
| 测试数据集 | ✅ V3 | 28 条，覆盖 12 类别 |
| 评分器执行 | ✅ V4 | 28/28 成功，无报错 |
| Live 验证 | ❌ Blocked | DASHSCOPE_API_KEY 401 错误 (>348h) |
| Mock 局限性 | ✅ V3 | temporal_coherence=100 异常 |

---

## Confidence / Uncertainty

### 高置信度
- Mock event extraction 导致评分系统性偏低
- 边界条件响应符合预期 (短文本低分、长文本高分)
- DASHSCOPE_API_KEY 失效阻塞真实验证

### 不确定点
- 真实 LLM event extraction 会如何改变评分分布
- 对抗样本 (情感词堆砌) 在真实 LLM 下是否会被识别
- 实际老年叙事样本的评分分布

---

## Implications

### 对 v0.7 的影响

1. **Mock testing 价值有限**: 
   - 可验证系统稳定性 (100% 成功率)
   - 无法验证真实评分质量 (mock event extraction 瓶颈)

2. **Live 验证迫切性**:
   - DASHSCOPE_API_KEY 失效 >348h
   - 03-31 决策点：若未轮换，发布 v0.6.5 (rule-only)

3. **Event extraction 重要性**:
   - 评分质量高度依赖 LLM 事件提取
   - 需优先验证真实 LLM event extraction 效果

### 对论文的影响

- 可报告鲁棒性测试框架和方法
- 需注明"基于 mock event extraction，真实 LLM 验证进行中"
- 建议在 Pilot 研究中用真实数据复现

---

## Next Owner / Handoff

**当前状态**: Hulk 研究完成，等待 API Key 轮换

**下一步**:
1. **V**: 轮换 DASHSCOPE_API_KEY (阿里云控制台，~10 分钟) — 阻塞 >348h
2. **Hulk**: API Key 恢复后执行 live validation (50 样本 × 真实 LLM)
3. **Core**: 基于 live 结果决定 v0.7 发布策略

**阻塞点**: 
- 🔴 DASHSCOPE_API_KEY 401 错误 (>348h)
- 🔴 03-31 决策点：v0.6.5 (rule-only) vs v0.7.0 (delayed)

---

## 产物

| 文件 | 说明 | 位置 |
|------|------|------|
| `extended_robustness_experiment.py` | 实验脚本 | `pipeline/` |
| `extended_robustness_20260328_174528.json` | JSON 原始结果 | `pipeline/results/` |
| `extended_robustness_20260328_174528.md` | Markdown 报告 | `pipeline/results/` |
| 本日志 | 执行记录 | `memory/` |

---

## 与夜间长跑实验系列对比

| 日期 | 实验类型 | 样本数 | 核心发现 | 验证等级 |
|------|----------|--------|----------|----------|
| 03-26 | 消融研究 (12 配置) | 50 | 简化系统优于复杂系统 | V4 (Mock) |
| 03-27 | 权重敏感性 (5 配置) | 15 | 60/40 配置稳定 | V4 (Mock) |
| 03-28 | 鲁棒性测试 (12 类别) | 28 | Mock event extraction 局限 | V4 (Mock) |

**系列洞察**: 三次实验均基于 Mock，真实 LLM 验证迫切需求

---

*Execution Complete. Key insight: Mock testing validates stability but not quality. Live validation blocked by DASHSCOPE_API_KEY (>348h).*
