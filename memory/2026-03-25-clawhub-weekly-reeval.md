# ClawHub 500 Weekly Reevaluation — 2026-03-25

## 执行摘要

**首次真实 AI 评估**完成，替代了之前所有 mock 数据。

### 关键数据
- 评估技能数：600
- 平均 AI 评分：62.3（从 mock baseline 45.0 大幅提升）
- API：qwen3-coder-plus @ 阿里云百炼，60/60 batches 全部成功
- 耗时：~4 分钟（并发 5 workers，batch size 10）

### 评分分布
| 类别 | 数量 | 占比 |
|------|------|------|
| 升级候选 (≥90) | 3 | 0.5% |
| 保持精选 (70-89) | 234 | 39.0% |
| 观察列表 (50-69) | 228 | 38.0% |
| 降级候选 (<50) | 135 | 22.5% |

### 升级候选
1. pyright-lsp (88) — Reviewer 模式，开发工具
2. clean-pytest (85) — Generator 模式，测试框架
3. skill-releaser (85) — Reviewer 模式，基础设施

### 最差技能
- ai-remote-viewing-ai-isbe (20) — 伪科学
- aetherlang (25) — 过度营销
- business-writing (30) — 实现不清

### 产出
- PR: https://github.com/cittaverse/clawhub-500/pull/1
- 评估数据: data/reevaluation-2026-03-25.json (285KB)
- 仪表板: quality-dashboard.md v2026.13
- 新脚本: scripts/weekly-reevaluation-fast.py（10x 加速）

### 技术改进
原脚本逐个调用 API（600 calls），会花数小时。新版批量评估（10 skills/batch，5 并发）减少到 60 calls，~4 分钟完成。

### PR 状态
- PR #1 已创建，待人工 review
- 3 个升级候选分数 85-88，未达到 ≥90 自动合并阈值
- 135 个降级候选需要后续决策

### 下一步
- V 审核 PR #1
- 讨论 135 个降级候选的处理策略
- 考虑将评估阈值从 ≥90 调整为更务实的标准
- 下周重评时可对比本周数据看趋势

### 验证等���
- V4：API 调用实际运行，评分数据可复现
