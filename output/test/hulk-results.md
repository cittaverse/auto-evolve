# Hulk 回归测试报告

**执行时间**: 2026-03-30T12:43:52+08:00  
**执行阶段**: hulk  
**测试类型**: 全量回归测试（单元测试 + 集成测试 + 端到端测试）

---

## 📊 测试摘要

| 指标 | 数值 |
|------|------|
| **tests_run** | 237 |
| **tests_passed** | 236 |
| **tests_failed** | 1 |
| **通过率** | 99.6% |
| **执行时间** | ~3 秒 |

---

## 📋 测试套件详情

### 1. 单元测试 (Unit Tests)

| 测试文件 | 测试数 | 通过 | 失败 | 状态 |
|----------|--------|------|------|------|
| `test_assessor.py` | 8 | 8 | 0 | ✅ |
| `pipeline/l0_quality_system_mock_test.py` | 1 | 1 | 0 | ✅ |
| `pipeline/metamemory_integration_test.py` | 9 | 9 | 0 | ✅ |
| `repos/pipeline/tests/test_assessor.py` | 8 | 8 | 0 | ✅ |
| `github-repos/narrative-scorer/tests/test_scorer.py` | 60 | 60 | 0 | ✅ |
| `github-repos/nlg-metricverse/tests/test_narrative_score_standalone.py` | 16 | 15 | 1 | ⚠️ |

**单元测试小计**: 102 tests, 101 passed, 1 failed

---

### 2. 集成测试 (Integration Tests)

| 测试文件 | 测试数 | 通过 | 失败 | 状态 |
|----------|--------|------|------|------|
| `pipeline/robustness_test.py` | 131 | 131 | 0 | ✅ |
| `pipeline/test_metamemory_randomization.py` | 1 | 1 | 0 | ✅ |
| `pipeline/asr_evaluation_test.py` | 3 | 3 | 0 | ✅ |

**集成测试小计**: 135 tests, 135 passed, 0 failed

---

## ❌ 失败用例详情

### 失败 #1: test_high_score

- **测试文件**: `github-repos/nlg-metricverse/tests/test_narrative_score_standalone.py`
- **测试类**: `TestLetterGrade`
- **行号**: 156
- **错误类型**: `AssertionError`
- **错误信息**: `'D' not found in ['S', 'A', 'B', 'C']`
- **问题分析**: 高分测试用例期望得到 S/A/B/C 等级，但实际得到 D 级。可能是评分逻辑或阈值配置问题。
- **建议修复**: 检查 `assign_grade()` 函数的分数阈值逻辑，或调整测试用例的输入数据。

---

## ⚠️ 已知脆弱点

来自 `robustness_test.py` 的警告：

- **情感词堆砌可欺骗唤醒度检测器**: 2 例
  - C-01-1: arousal=5.0 level=极高 ⚠️ GAMEABLE
  - C-01-3: arousal=5.0 level=极高 ⚠️ GAMEABLE

**建议**: 优化情绪唤醒度检测器，增加对"情感词堆砌"对抗样本的识别能力。

---

## 📈 测试覆盖模块

| 模块 | 测试状态 |
|------|----------|
| 事件提取 (Event Extraction) | ✅ |
| 图论计分 (Graph Scoring) | ✅ |
| 报告生成 (Report Generation) | ✅ |
| L0 质检多 Agent 系统 | ✅ |
| 元记忆策略选择器 | ✅ |
| 元记忆 Prompt 生成器 | ✅ |
| A/B 测试随机分组 | ✅ |
| ASR 评估框架 | ✅ |
| 鲁棒性测试 (噪声/边界/对抗) | ✅ |
| 叙事评分 v0.5 | ✅ |
| 字母等级判定 | ⚠️ (1 失败) |

---

## 🔧 下一步建议

1. **修复失败用例**: 调查 `test_high_score` 失败原因，修复评分逻辑或测试断言
2. **优化唤醒度检测器**: 增强对抗样本识别能力
3. **补充端到端测试**: 当前 E2E 测试覆盖较少，建议增加真实场景的端到端流程测试
4. **添加性能测试**: 对关键路径添加 P95/P99 延迟测试

---

## 📁 产物位置

- **完整报告**: `output/test/hulk-results.md`
- **鲁棒性报告**: `pipeline/robustness_report.json`
- **ASR 评估报告**: `pipeline/asr_test_results/asr_evaluation_*.json`

---

*报告生成时间: 2026-03-30T12:43:55+08:00*
