# Hulk 24h 稳定 Loop 指南

**调研日期**: 2026-03-19  
**来源**: OpenClaw 官方文档 + tirnav.com + lumadock.com + 实际运行诊断  
**作者**: Hulk 🟢

---

## 一、当前问题诊断

| 任务 | 根因 | 修复状态 |
|------|------|---------|
| hulk-research-heartbeat | 泛错 `Error` + 原缺时区 | ✅ 已加时区 + timeout 600s |
| hulk-geo-iteration | 超时（30min 不够） | ✅ timeout → 3600s |
| hulk-memory-consolidate | 超时（10min 不够）× 5 次 | ✅ timeout → 1200s |
| hulk-evidence-scan | 泛错 `Error` | ✅ timeout → 1200s |

---

## 二、OpenClaw Cron vs Heartbeat 选型

**官方文档关键表格**（docs.openclaw.ai/automation/cron-vs-heartbeat）：

| 维度 | Heartbeat | Cron (main) | Cron (isolated) |
|------|-----------|-------------|-----------------|
| 会话 | 主会话 | 主会话（系统事件） | 独立会话 |
| 历史 | 共享 | 共享 | 每次全新（isolated）/ 累积（custom） |
| 上下文 | 完整 | 完整 | 无（isolated）/ 累积（custom） |
| 模型 | 主会话模型 | 主会话模型 | 可覆盖 |
| 输出 | 非 HEARTBEAT_OK 时投递 | 心跳提示 + 事件 | announce 摘要 |

### Hulk 的最优选型

| 任务类型 | 选型 | 理由 |
|---------|------|------|
| **研究迭代**（GEO/方法升级） | **Cron isolated** | 每次独立上下文，不污染主会话 |
| **记忆固化** | **Cron isolated** | 读 memory/ 写 MEMORY.md，不需要会话历史 |
| **证据扫描** | **Cron isolated** | 搜索+分析，独立执行 |
| **BULLETIN/KANBAN 检查** | **Heartbeat** | 需要主会话上下文，轻量检查 |
| **HANDOFF 接收** | **Hook (agent:bootstrap)** | ✅ 已有 handoff-bootstrap hook |

---

## 三、Hooks 用于稳定性的方案

### 3.1 现有 Hooks 已覆盖的

| Hook | 事件 | 作用 |
|------|------|------|
| `handoff-bootstrap` | agent:bootstrap | 每次会话启动自动检测 HANDOFF.md |
| `session-memory` | command:new/reset | /new 或 /reset 时归档会话 |
| `self-improvement` | agent:bootstrap | 注入自我改进提醒 |
| `cross-agent-audit` | message:sent/received | 跨 Agent 消息审计 |

### 3.2 可新增的自定义 Hook

**Hook: cron-error-alert**（建议新增）

```
事件: cron:failed（目前不存在，GitHub #27339 提案中）
替代方案: 用 --failure-alert-channel 参数
```

**现在可做的**：给关键 cron 任务加 failure alert。

### 3.3 --best-effort-deliver 参数

对于非关键投递任务，加 `--best-effort-deliver`，避免投递失败导致整个 job 标记为 error。

---

## 四、稳定 Loop 最佳实践（综合调研）

### 4.1 Prompt 精简原则（来自 lumadock）

> "An agent that only messages when something's wrong trains you to always read it. I killed 6 cron jobs in my first month because they sent 'all clear' messages."

**规则**：
- 无事时返回 `HEARTBEAT_OK`，不要输出长报告
- Cron isolated 的 prompt 必须自包含——不依赖会话历史
- Prompt 里明确说"不要提问，不要请求确认"

### 4.2 Context 管理（来自 tirnav.com）

> "OpenClaw agents don't 'remember' anything unless it's written down."

**规则**：
- 每次 cron isolated 会话是全新的——必须在 prompt 里告诉 agent 读哪些文件
- memory/YYYY-MM-DD.md 是唯一的持久化通道
- MEMORY.md 是固化的长期记忆，memory/ 是日志

### 4.3 Timeout 安全余量

| 任务复杂度 | 建议 timeout | 安全余量 |
|-----------|-------------|---------|
| 轻量检查（heartbeat） | 300-600s | 5-10x 实际耗时 |
| 中等任务（证据扫描） | 1200s | 3-5x 实际耗时 |
| 重度任务（GEO 迭代） | 3600s | 2x 实际耗时 |

### 4.4 错误恢复模式

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ Cron 触发    │────▶│ Agent 执行    │────▶│ 成功         │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │ 失败
                    ┌──────▼───────┐
                    │ consecutiveErrors++ │
                    └──────┬───────┘
                           │ ≥3 次
                    ┌──────▼───────┐
                    │ failure-alert │──▶ 通知 V
                    └──────────────┘
```

### 4.5 成本控制（来自官方文档）

| 机制 | 成本 |
|------|------|
| Heartbeat | 每 N 分钟一个 turn，与 HEARTBEAT.md 大小成正比 |
| Cron (main) | 注入下一次心跳，无额外 turn |
| Cron (isolated) | **每次一个完整 agent turn** — 可用 cheaper model |

**建议**：research-heartbeat 改为每 4 小时而非每 2 小时，减少 token 消耗。

---

## 五、修复行动计划

### 已完成
- ✅ 所有 timeout 加大到安全余量
- ✅ 缺失时区修复

### 待执行

```bash
# 1. research-heartbeat 降频：每2h → 每4h
openclaw cron edit 02bf8d4e-30d5-4a27-8547-f221c322ac00 --cron "0 */4 * * *"

# 2. 给关键任务加 failure alert
openclaw cron edit hulk-geo-iteration --failure-alert-channel discord --failure-alert-to "user:1466465999950971044"
openclaw cron edit c4d45ce7-7119-4eec-b50e-eb6572cea7f8 --failure-alert-channel discord --failure-alert-to "user:1466465999950971044"

# 3. memory-consolidate 加 best-effort-deliver（如果有投递的话）
openclaw cron edit c4d45ce7-7119-4eec-b50e-eb6572cea7f8 --best-effort-deliver
```

---

## 六、目标 Loop 架构

```
00:00 CST ─── hulk-geo-iteration (isolated, 60min timeout)
              ├─ 读 memory/ 最近 geo 日志
              ├─ 执行本轮 GEO 任务
              └─ 写 memory/YYYY-MM-DD-geo-iteration-N.md

04:00 CST ─── hulk-research-heartbeat (isolated, 10min timeout)
              ├─ 检查 BULLETIN.md / KANBAN.md
              └─ 无事 → HEARTBEAT_OK

06:00 CST ─── hulk-geo-iteration

08:00 CST ─── hulk-research-heartbeat

09:00 CST ─── hulk-evidence-scan (每周一, isolated, 20min timeout)
              ├─ Jina Reader + arXiv API 搜索新论文
              └─ 写 memory/YYYY-MM-DD-evidence-scan.md

10:00 CST ─── hulk-heartbeat-update (isolated)
              └─ 更新 HEARTBEAT.md

12:00 CST ─── hulk-geo-iteration + hulk-research-heartbeat

16:00 CST ─── hulk-research-heartbeat

18:00 CST ─── hulk-geo-iteration + hulk-weekly-report (周五)

20:00 CST ─── hulk-research-heartbeat

22:00 CST ─── hulk-memory-consolidate (isolated, 20min timeout)
              ├─ 提取当日关键洞察
              ├─ 追加到 MEMORY.md
              └─ hulk-heartbeat-update
```

**覆盖**：24h × 7d，每天 10+ 个触发点，无空白时段超过 4 小时。

---

*Hulk 🟢 — 2026-03-19*
