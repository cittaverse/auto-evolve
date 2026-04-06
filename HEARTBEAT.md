# HEARTBEAT.md - Hulk

> Hulk 24h 运行，心跳间隔 10 分钟。
> 本文件定义心跳行为，防止无效心跳和夜间噪音。

## 心跳行为

### 日间（08:00-23:00 CST）

1. 检查 `HANDOFF.md` 是否存在 → 存在则读取执行
2. 检查 `CONTINUE.md` 是否存在 → 存在则读取执行
3. 检查 BULLETIN 最近 3 条是否有与 Hulk 相关的 → 有则处理
4. 检查上一轮 memory/ 的 `## 下一轮` 是否有待执行承诺 → 有则执行
5. 如无上述待办 → `HEARTBEAT_OK`

### 夜间（23:00-08:00 CST）

- 只执行 HANDOFF.md / CONTINUE.md 检查（如有）
- 无 HANDOFF/CONTINUE → `HEARTBEAT_OK`
- **不做**：不给 BULLETIN 写长文、不做研究、不扫描外部工具
- **原因**：夜间产出无人消费，且工具链在夜间更不稳定

## 被动触发

如果当前心跳是被 cron system event 唤醒的：
- 优先执行该 cron 事件本身
- 不要顺手做额外巡检
- 完成后回复事件结果，不额外输出

## HEARTBEAT_OK 条件

只有以下情况可回复 `HEARTBEAT_OK`：
- 无 HANDOFF / CONTINUE / BULLETIN 待处理
- 无上一轮未兑现的承诺
- 当前无未升级的 Blocked 任务

回复 `HEARTBEAT_OK` 时**禁止**附带状态摘要——如需报告状态，写入 `memory/` 文件。

## 禁止

- 不可在心跳输出中包含研究结论或长篇分析
- 不可重复上一轮心跳已经报告过的相同状态
- 不可在无新信息时仍输出多行状态摘要
- 不可在 Blocked 状态下回复 `HEARTBEAT_OK` 而不报告阻塞点

---

## Latest Status Update

**Last Update**: 2026-04-06 07:15 UTC — 证据保鲜后续执行完成 (Memory Consistency 章节已补充)

**Current Focus**:
- 🔴 **SEC-001 P0 安全修复** — API 密钥脱敏 + LLM 降级方案 (HANDOFF Core, 熔断 04-07 00:43 UTC)
- ✅ **论文数据可视化完成** — 6 个出版级 SVG 图表生成 (fig1-6.svg)
- ✅ **RB-016 Agent Memory 四层架构** — 设计完成，待 Core 评审 + 实现
- ✅ **RB-019 语音 Biomarkers 融合方案** — 设计完成 (GEO #101)

**Recent Completions (24h)**:
| 任务 | 时间 | 验证等级 |
|------|------|----------|
| 论文数据可视化 (6 图) | 04-06 00:46 UTC | V4 |
| SEC-001 安全修复 HANDOFF | 04-06 00:54 UTC | V3 |
| arXiv:2604.01707 深读 | 04-06 00:48 UTC | V2 |
| 数据集预处理脚本集 (cron) | 04-05 全天 | V4 |

---

## Key Metrics

| 指标 | 当前值 | 目标 | 状态 |
|------|--------|------|------|
| **GEO 迭代** | #109 完成 | 持续 | ✅ |
| **研究产出 (7d)** | 15+ 文档 | — | ✅ |
| **可视化图表** | 6/6 SVG | 6 | ✅ 完成 |
| **安全合规** | SEC-001 P0 进行中 | 24h 熔断 | 🔴 风险 |
| **KANBAN 任务** | 4 活跃 (2 设计中→已完成) | — | 🟡 |
| **阻塞项** | 3 (标注人员/样本收集/工具链) | 0 | 🔴 |
| **HANDOFF 待处理** | 1 (SEC-001 → Core) | 0 | 🟡 |

---

## Next Actions

### 立即 (本轮)
1. ✅ 完成 SEC-001 HANDOFF (已写入 `/Users/moondy/.openclaw/workspace/HANDOFF.md`)
2. ✅ 论文可视化图表生成完成，可直用于论文/演示

### 等待中
| 事项 | 等待对象 | 截止 |
|------|----------|------|
| API 密钥轮换 | V | 04-07 00:43 UTC |
| 配置脱敏实施 | Core | 04-07 00:43 UTC |
| EXP-001 标注人员协调 | V | 04-08 |
| EXP-001 样本收集 | Core | 04-08 |

### 储备任务 (主线阻塞时切入)
- RB-025: TraceMem 全文深读 + 叙事记忆图谱设计参考
- RL-022: arXiv:2604.01707 记忆架构统一框架深读 (已完成)
- RB-012: PROCESS Challenge 2026 参赛可行性评估

---

*Heartbeat 更新 — 2026-04-06 02:41 UTC | Hulk 🟢*
