# OpenClaw 下 24h 持续自主工作 Agent Team 技术方案

**调研日期**: 2026-03-19  
**作者**: Hulk 🟢（高级技术研究顾问）  
**版本**: 1.0  
**证据等级**: V3（官方文档 + 实战验证 + 竞品分析）

---

## 1. Executive Summary

### 核心判断

**在 OpenClaw 下搭建 24h 持续自主工作的 Agent Team 是值得做的，但有明确的边界条件。**

**值得做的理由**：
- ✅ OpenClaw 原生支持 cron/heartbeat/hooks/subagents — 基础设施完备
- ✅ 已有 7 个生产级 hooks（handoff-bootstrap/session-memory 等）— 可复用
- ✅ 多 Agent 架构已验证（Core/Hulk/Midas/Jobs/Odin/Styx）— 有实战基础

**不值得做的场景**：
- ❌ 需要强实时协同（OpenClaw 是异步架构）
- ❌ 需要共享内存状态（OpenClaw Agent 间通过文件/消息通信）
- ❌ 需要复杂工作流编排（Lobster 仅支持线性审批流）

### 技术难点（按优先级）

| 难点 | 严重度 | OpenClaw 原生支持 | 需自建 |
|------|--------|-----------------|--------|
| **状态一致性** | 🔴 高 | ❌ 无 | ✅ 需要 |
| **死循环检测** | 🔴 高 | ⚠️ 单 Agent 有，跨 Agent 无 | ✅ 需要 |
| **任务去重** | 🟡 中 | ❌ 无 | ✅ 需要 |
| **故障恢复** | 🟡 中 | ⚠️ cron 有 retry，无级联恢复 | ✅ 需要 |
| **可观测性** | 🟡 中 | ✅ cron runs / hooks list | ⚠️ 需整合 |
| **成本控制** | 🟢 低 | ✅ 可配置子 Agent 模型 | ⚠️ 需监控 |

### 最合理架构

**推荐：Hub-and-Spoke（中心调度 + 独立执行）**

- **Hub**: 1 个 Orchestrator Agent（建议 Core 或新增 Ops Agent）
- **Spokes**: N 个 Specialist Agent（Hulk/Midas/Jobs 等）
- **通信**: HANDOFF.md（异步）+ sessions_spawn（同步）
- **状态**: 共享 KANBAN.md + 各 Agent 独立 memory/

**为什么不选另外两套**：
- **纯去中心化**（Agent 间直接通信）→ 易死锁、难调试
- **严格流水线**（固定顺序执行）→ 灵活性差、单点故障影响大

### 关键设计原则

1. **异步优先** — 能用 HANDOFF.md 就不用 sessions_spawn
2. **幂等执行** — 每个任务必须有唯一 ID，可安全重试
3. **状态外置** — 不依赖 Agent 内存，所有状态写文件

### MVP 必备模块

1. **任务队列**（KANBAN.md + 任务 ID 生成）
2. **健康检查**（heartbeat + cron status 轮询）
3. **故障告警**（failure-alert-channel）
4. **人工接管**（/subagents kill + 手动编辑 KANBAN）

### 第一阶段不要做

1. ❌ 动态 Agent 扩缩容（OpenClaw 不支持运行时创建 Agent）
2. ❌ 复杂工作流引擎（Lobster 仅支持线性审批）
3. ❌ 实时状态同步（文件锁竞争会导致死锁）

---

## 2. Core Definitions

### 24h 持续自主工作

**定义**：系统在无人工干预的情况下，连续 24 小时执行预定任务并维持基本功能。

**OpenClaw 语境下的具体含义**：
- cron 任务按调度触发（允许±5min stagger）
- heartbeat 按间隔执行（默认 30min）
- 无死循环、无状态污染、无 token 失控
- 故障后能在 1 个心跳周期内恢复

**不承诺**：
- 100% 任务成功率（允许失败，但需告警）
- 零人工介入（严重故障需人工接管）

### 稳定运行

**量化指标**：
| 指标 | 目标值 | 测量方式 |
|------|--------|---------|
| 24h 存活率 | ≥95% | cron runs --limit 24h |
| 任务成功率 | ≥85% | 成功执行数 / 总触发数 |
| 平均恢复时间 | ≤30min | 故障→恢复时间戳差 |
| 人工介入率 | ≤5% | 人工接管次数 / 总任务数 |
| 成本上限 | ¥X/天 | sessions_list 统计 token |

### Agent Team

**OpenClaw 定义**：多个配置独立的 Agent（不同 `agents.list[].id`），通过以下机制协作：
- **HANDOFF.md** — 异步任务交接
- **sessions_spawn** — 同步子任务委派
- **共享文件** — KANBAN.md / BULLETIN.md / memory/
- **跨 Agent 消息** — sessions_send

**不是**：
- 同一 Agent 的多个会话（那是并发，不是 Team）
- 动态创建的临时 Agent（OpenClaw 不支持）

### OpenClaw 核心概念

| 概念 | 官方定义 | 工程含义 |
|------|---------|---------|
| **memory/** | 语义记忆存储 | Agent 的长期知识，跨会话持久化 |
| **HANDOFF.md** | 跨 Agent 任务交接文件 | 异步通信协议，handoff-bootstrap hook 自动注入 |
| **heartbeat** | 周期性 Agent turn | 后台检查机制，默认 30min |
| **scheduler** | Gateway cron | 定时任务系统，支持 at/every/cron 三种调度 |
| **workspace** | Agent 工作目录 | 文件系统隔离边界，`~/.openclaw/workspace-<id>/` |
| **tool use** | Agent 可调用的工具 | exec/web_search/browser/sessions_spawn 等 |

---

## 3. System Assumptions

### 事实（已验证）

1. OpenClaw Gateway 支持 cron 调度（`openclaw cron add`）
2. 支持 heartbeat 周期性检查（默认 30min）
3. 支持 hooks 事件驱动（7 个内置 hooks）
4. 支持 sub-agents（maxSpawnDepth 默认 1，可配 2）
5. 支持 HANDOFF.md 跨 Agent 交接（handoff-bootstrap hook）
6. 支持 sessions_spawn 同步委派（mode: run/session）
7. 支持 isolated session（每次执行全新上下文）
8. 支持 failure-alert-channel（cron 失败告警）

### 推断（合理但需验证）

1. cron job 超时后会自动标记为 error（需验证 retry 行为）
2. heartbeat 跳过 quiet-hours 后会自动补执行（需验证）
3. sub-agents announce 失败会 retry（文档说有指数退避）
4. hooks 执行失败不影响主流程（需验证）

### 猜测（不确定性高）

1. Gateway 重启后 cron 状态是否保留（猜测：jobs.json 持久化）
2. 多 Agent 并发写同一文件的锁行为（猜测：无锁，可能冲突）
3. 嵌套 sub-agents 的实际性能开销（猜测：每层+30s 延迟）

---

## 4. Candidate Architectures

### 架构 A：Hub-and-Spoke（推荐）

```
                    ┌─────────────┐
                    │ Orchestrator │
                    │   (Core)     │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
    │  Hulk   │      │  Midas  │      │  Jobs   │
    │ Research│      │ Business│      │  Ops    │
    └─────────┘      └─────────┘      └─────────┘
```

**通信模式**：
- Orchestrator → Spoke：HANDOFF.md（异步）或 sessions_spawn（同步）
- Spoke → Orchestrator：sessions_spawn announce 或写 KANBAN.md

**适用前提**：
- 有明确的任务分发逻辑
- Spoke 之间无需直接通信
- Orchestrator 可承受单点故障

**优势**：
- ✅ 架构清晰，易调试
- ✅ 任务去重由 Orchestrator 统一管理
- ✅ 新 Spoke 接入成本低

**主要风险**：
- 🔴 Orchestrator 故障 → 全系统停摆
- 🟡 Spoke 间协作需经 Orchestrator 中转

**OpenClaw 契合度**：⭐⭐⭐⭐⭐
- 完美匹配 handoff-bootstrap hook
- 可用 cron 调度 Orchestrator，heartbeat 调度 Spoke

**实施复杂度**：中
- 需实现 Orchestrator 逻辑
- Spoke 基本无需改动

**扩展性**：高
- 新增 Spoke 只需注册到 Orchestrator

**稳定性**：高
- 单点故障可通过 heartbeat 恢复

**调试难度**：低
- 所有任务流经过 Orchestrator，日志集中

---

### 架构 B：去中心化网状（不推荐）

```
    ┌─────────┐         ┌─────────┐
    │  Hulk   │◄───────►│  Midas  │
    └────┬────┘         └────┬────┘
         │                   │
         └────────┬──────────┘
                  │
             ┌────▼────┐
             │  Jobs   │
             └─────────┘
```

**通信模式**：
- Agent 间直接 HANDOFF.md 或 sessions_send

**适用前提**：
- Agent 间有频繁协作需求
- 无明确中心节点

**优势**：
- ✅ 无单点故障
- ✅ Agent 间协作路径短

**主要风险**：
- 🔴 易死锁（A 等 B，B 等 A）
- 🔴 任务去重困难
- 🔴 调试复杂度高

**OpenClaw 契合度**：⭐⭐
- handoff-bootstrap 是单向的（启动时注入）
- 无内置死锁检测

**实施复杂度**：高
- 需实现分布式锁
- 需实现死锁检测

**扩展性**：中
- 每新增一个 Agent，连接数 +N

**稳定性**：低
- 死锁风险高

**调试难度**：高
- 日志分散，需跨 Agent 追踪

---

### 架构 C：严格流水线（不推荐）

```
┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
│ A   │──►│ B   │──►│ C   │──►│ D   │
└─────┘   └─────┘   └─────┘   └─────┘
```

**通信模式**：
- 固定顺序 sessions_spawn 或 HANDOFF 接力

**适用前提**：
- 任务有严格先后依赖
- 每步处理时间可预测

**优势**：
- ✅ 流程清晰
- ✅ 易于监控进度

**主要风险**：
- 🔴 单步故障阻塞全流程
- 🔴 无法并行
- 🔴 灵活性差

**OpenClaw 契合度**：⭐⭐⭐
- Lobster 支持线性审批流，但不支持自动接力
- 需自行实现流水线引擎

**实施复杂度**：中
- 需实现状态机
- 需实现超时跳过/重试逻辑

**扩展性**：低
- 新增步骤需修改流水线定义

**稳定性**：中
- 单点故障影响大，但易于隔离

**调试难度**：中
- 可追踪当前步骤，但跨步骤状态难查

---

## 5. Failure Modes Analysis

### 死循环

| 维度 | 详情 |
|------|------|
| **触发条件** | Agent A 任务未完成→创建子任务→子任务完成→通知 A→A 认为未完成→再创建子任务 |
| **可观测信号** | sessions_list 显示同一任务重复 spawn |
| **检测方式** | 任务 ID 去重表 + 最大重试次数 |
| **缓解机制** | 任务 ID 必须包含父任务 ID + 时间戳 |
| **恢复机制** | /subagents kill + 手动标记任务完成 |
| **人工介入** | 是 |

### 自锁/互锁

| 维度 | 详情 |
|------|------|
| **触发条件** | A 等 B 的 HANDOFF，B 等 A 的 HANDOFF |
| **可观测信号** | KANBAN.md 中多个任务状态长期"blocked" |
| **检测方式** | 依赖图 + 环检测算法 |
| **缓解机制** | 超时自动标记为"failed"，通知 Orchestrator |
| **恢复机制** | Orchestrator 重新分配任务 |
| **人工介入** | 是（如果 Orchestrator 也故障） |

### 重复执行

| 维度 | 详情 |
|------|------|
| **触发条件** | cron retry + heartbeat 同时触发同一任务 |
| **可观测信号** | memory/ 中出现重复日志 |
| **检测方式** | 任务幂等 ID + 执行记录表 |
| **缓解机制** | 执行前检查记录表，已存在则跳过 |
| **恢复机制** | 自动（幂等设计） |
| **人工介入** | 否 |

### 任务漂移

| 维度 | 详情 |
|------|------|
| **触发条件** | 任务在多次重试中被不同 Agent 执行，上下文丢失 |
| **可观测信号** | 同一任务 ID 出现在不同 Agent 的 memory/ |
| **检测方式** | 任务元数据包含执行 Agent ID |
| **缓解机制** | 任务绑定到特定 Agent，不自动迁移 |
| **恢复机制** | Orchestrator 重新分配 |
| **人工介入** | 否 |

### 状态不一致

| 维度 | 详情 |
|------|------|
| **触发条件** | 多 Agent 并发写 KANBAN.md |
| **可观测信号** | KANBAN.md 内容错乱/丢失 |
| **检测方式** | 文件哈希校验 |
| **缓解机制** | 单 Agent 写权限 + 队列化更新 |
| **恢复机制** | 从备份恢复 + 人工校验 |
| **人工介入** | 是 |

### memory 污染

| 维度 | 详情 |
|------|------|
| **触发条件** | Agent 将临时/错误信息写入 memory/ |
| **可观测信号** | memory/ 文件过大或包含错误标记 |
| **检测方式** | memory 文件大小监控 + 关键词过滤 |
| **缓解机制** | memory 写入前审核（hook） |
| **恢复机制** | 手动删除污染文件 |
| **人工介入** | 是 |

### handoff 丢信息

| 维度 | 详情 |
|------|------|
| **触发条件** | HANDOFF.md 被覆盖或删除 |
| **可观测信号** | 接收方 Agent 启动时无 HANDOFF.md |
| **检测方式** | handoff-bootstrap hook 日志 |
| **缓解机制** | HANDOFF.md 写入后立即备份 |
| **恢复机制** | 从备份恢复 |
| **人工介入** | 否 |

### 工具失效

| 维度 | 详情 |
|------|------|
| **触发条件** | web_search API 限流/browser 崩溃 |
| **可观测信号** | cron runs 显示 tool 错误 |
| **检测方式** | 工具调用失败率监控 |
| **缓解机制** | 降级策略（如 web_search → ddg-search） |
| **恢复机制** | 自动切换备用工具 |
| **人工介入** | 否（除非所有备用都失效） |

### 网络超时

| 维度 | 详情 |
|------|------|
| **触发条件** | Gateway 无法连接外部 API |
| **可观测信号** | 多个 cron job 同时 timeout |
| **检测方式** | 网络健康检查（ping/curl） |
| **缓解机制** | 本地 Mock 降级 |
| **恢复机制** | 网络恢复后自动重试 |
| **人工介入** | 否 |

### 错误级联

| 维度 | 详情 |
|------|------|
| **触发条件** | Orchestrator 故障 → Spoke 无法接收任务 → 堆积 → 超时 |
| **可观测信号** | 多个 Agent 同时报错 |
| **检测方式** | 错误率突增告警 |
| **缓解机制** | Spoke 降级为独立运行模式 |
| **恢复机制** | Orchestrator 恢复后同步状态 |
| **人工介入** | 是（如果自动恢复失败） |

### 幻觉式完成

| 维度 | 详情 |
|------|------|
| **触发条件** | Agent 声称任务完成但实际未执行 |
| **可观测信号** | KANBAN.md 标记完成但无输出文件 |
| **检测方式** | 输出文件存在性校验 |
| **缓解机制** | 任务完成必须附带输出证明 |
| **恢复机制** | 自动重新执行 |
| **人工介入** | 否 |

### token/成本失控

| 维度 | 详情 |
|------|------|
| **触发条件** | 死循环子任务持续 spawn |
| **可观测信号** | sessions_list token 用量突增 |
| **检测方式** | 每日成本预算告警 |
| **缓解机制** | 硬上限（maxChildrenPerAgent） |
| **恢复机制** | 自动停止超出预算的子任务 |
| **人工介入** | 是（审查预算设置） |

---

## 6. Memory / State / Handoff Design

### 状态分层

```
┌─────────────────────────────────────────┐
│           全局状态 (共享)                │
│  - KANBAN.md (任务队列)                  │
│  - BULLETIN.md (公告)                   │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────▼───┐ ┌────▼────┐ ┌───▼───────┐
│  Hulk     │ │  Midas  │ │  Jobs     │
│  memory/  │ │ memory/ │ │  memory/  │
│  (私有)   │ │ (私有)  │ │  (私有)   │
└───────────┘ └─────────┘ └───────────┘
```

### KANBAN.md 结构

```markdown
# 任务看板

## 待办 (TODO)
| ID | 任务 | 优先级 | 分配给 | 创建时间 |
|----|------|--------|--------|---------|
| T-20260319-001 | GEO #41 | P1 | Hulk | 2026-03-19 00:00 |

## 进行中 (IN_PROGRESS)
| ID | 任务 | 分配给 | 开始时间 | 预计完成 |
|----|------|--------|---------|---------|
| T-20260319-002 | 竞品分析 | Midas | 2026-03-19 08:00 | 2026-03-19 12:00 |

## 已完成 (DONE)
| ID | 任务 | 分配给 | 完成时间 | 输出 |
|----|------|--------|---------|------|
| T-20260318-015 | 证据扫描 | Hulk | 2026-03-18 22:00 | memory/2026-03-18-evidence-scan.md |

## 阻塞 (BLOCKED)
| ID | 任务 | 阻塞原因 | 等待 |
|----|------|---------|------|
| T-20260318-010 | ASR 测试 | API Key 缺失 | V |
```

### HANDOFF.md 结构

```markdown
# HANDOFF: Midas → Hulk

**任务 ID**: T-20260319-003  
**创建时间**: 2026-03-19 10:00  
**截止时间**: 2026-03-19 18:00  

## 任务描述
请调研竞品 X 的最新功能更新。

## 背景信息
- 竞品 X 于 2026-03-18 发布 v2.0
- 关键功能：Y、Z
- 相关链接：[链接 1](url), [链接 2](url)

## 期望输出
1. 功能对比表格
2. 差异化分析
3. 建议行动项

## 优先级
P1（高）

---
*此文件由 handoff-bootstrap hook 自动注入*
```

### memory/ 结构

```
memory/
├── 2026-03-19.md           # 当日综合日志
├── 2026-03-19-geo-41.md    # GEO 迭代日志
├── 2026-03-19-evidence-scan.md  # 证据扫描日志
└── ...
```

### 状态流转

```
TODO → IN_PROGRESS → DONE
              ↓
           BLOCKED → TODO (解除阻塞后)
              ↓
           FAILED → TODO (重试) 或 归档
```

---

## 7. Stability, Recovery, and Governance

### 稳定性保障

| 机制 | 实现方式 | 覆盖故障 |
|------|---------|---------|
| **超时保护** | cron --timeout-seconds | 死循环、网络超时 |
| **失败重试** | cron 自动 retry（最多 3 次） | 临时故障 |
| **失败告警** | --failure-alert-channel | 持续故障 |
| **心跳检查** | heartbeat every 30m | Agent 假死 |
| **幂等执行** | 任务 ID + 执行记录表 | 重复执行 |

### 恢复机制

| 故障类型 | 自动恢复 | 人工恢复 |
|---------|---------|---------|
| cron 超时 | ✅ 下次调度自动执行 | /openclaw cron run |
| heartbeat 跳过 | ✅ 下次心跳自动执行 | - |
| sub-agent 卡死 | ⚠️ 需手动 kill | /subagents kill |
| HANDOFF.md 丢失 | ❌ | 从备份恢复 |
| KANBAN.md 损坏 | ❌ | 从备份恢复 + 人工校验 |
| memory 污染 | ❌ | 手动删除污染文件 |

### 可观测性

| 指标 | 采集方式 | 告警阈值 |
|------|---------|---------|
| cron 成功率 | openclaw cron runs | <80% |
| heartbeat 延迟 | openclaw system heartbeat last | >1h |
| sub-agent 数量 | sessions_list | >10 活跃 |
| token 用量 | sessions_status | >¥X/天 |
| 任务堆积 | KANBAN.md TODO 计数 | >20 |

### 人工接管

**触发条件**：
- 连续 3 次 cron 失败
- KANBAN.md 损坏
- 成本超出预算 50%

**接管方式**：
1. /subagents kill 所有活跃子任务
2. 手动编辑 KANBAN.md 标记任务状态
3. /openclaw cron disable 暂停自动化
4. 人工执行关键任务
5. 修复后 /openclaw cron enable 恢复

---

## 8. Recommended Architecture

### 推荐：Hub-and-Spoke

**为什么推荐**：
1. **与 OpenClaw 原生能力最契合** — handoff-bootstrap hook 就是为这个设计的
2. **调试成本最低** — 所有任务流经过 Orchestrator，日志集中
3. **扩展性最好** — 新增 Spoke 只需注册到 Orchestrator

**为什么不推荐另外两套**：
- **去中心化网状** — 死锁风险高，OpenClaw 无内置死锁检测
- **严格流水线** — 灵活性差，Lobster 不支持自动接力

### 三个关键设计原则

1. **异步优先** — 能用 HANDOFF.md 就不用 sessions_spawn，减少耦合
2. **状态外置** — 所有状态写 KANBAN.md，不依赖 Agent 内存
3. **幂等执行** — 任务 ID 唯一，可安全重试

### MVP 必备模块

1. **Orchestrator Agent**（可用 Core 或新建 Ops）
2. **KANBAN.md**（任务队列）
3. **健康检查脚本**（cron status 轮询）
4. **告警配置**（failure-alert-channel）

### 第一阶段不要做

1. ❌ 动态 Agent 扩缩容
2. ❌ 复杂工作流引擎
3. ❌ 实时状态同步

---

## 9. MVP Scope and Roadmap

### 核心模块清单

| 模块 | 功能 | 状态 |
|------|------|------|
| **Orchestrator** | 任务分发、状态追踪 | 需实现 |
| **KANBAN.md** | 任务队列 | 已有模板 |
| **HANDOFF.md** | 跨 Agent 交接 | ✅ 原生支持 |
| **健康检查** | cron status 轮询 | 需实现脚本 |
| **告警** | failure-alert-channel | ✅ 原生支持 |
| **日志** | memory/YYYY-MM-DD.md | ✅ 原生支持 |

### 状态流转说明

```
用户/定时触发
      │
      ▼
┌─────────────┐
│ Orchestrator │
│ 创建任务     │
│ 写入 KANBAN  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ HANDOFF.md  │
│ 投递 Spoke  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Spoke 执行   │
│ 写 memory/  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 更新 KANBAN │
│ 通知 Orch.  │
└─────────────┘
```

### 实施路线图

| 阶段 | 时间 | 交付物 | 验收标准 |
|------|------|--------|---------|
| **Phase 0** | Day 1 | KANBAN.md 模板 + Orchestrator prompt | 能手动创建任务 |
| **Phase 1** | Day 2-3 | 健康检查脚本 + 告警配置 | cron 失败自动通知 |
| **Phase 2** | Day 4-7 | HANDOFF 自动化 + Spoke 接入 | Hulk/Midas 能接收任务 |
| **Phase 3** | Week 2 | 24h 压测 + 故障注入 | 存活率≥95% |

---

## 10. Validation and Stress Test Plan

### 24h 持续运行验证

**方案**：
1. 部署 MVP 架构
2. 配置 10 个 cron 任务（间隔 1-4h）
3. 运行 24h，记录：
   - 触发次数
   - 成功次数
   - 失败次数
   - 平均执行时间
   - token 用量

**验收指标**：
- 任务成功率 ≥85%
- 无死循环
- 成本 ≤¥X/天

### 压测方案

**负载压测**：
- 同时创建 50 个任务
- 观察 Orchestrator 响应时间
- 观察 KANBAN.md 写入冲突

**并发压测**：
- 5 个 Spoke 同时写 KANBAN.md
- 观察文件损坏情况

### 故障注入

| 故障 | 注入方式 | 预期行为 |
|------|---------|---------|
| cron 超时 | 设置 timeout=10s + 长任务 | 标记 error + 告警 |
| network 中断 | 断网 5min | 降级 Mock + 恢复后重试 |
| Orchestrator 假死 | 手动 suspend | Spoke 独立运行 + 告警 |
| KANBAN.md 损坏 | 手动写入乱码 | 从备份恢复 + 告警 |

### 回归测试

**每次变更后执行**：
1. 创建 3 个测试任务
2. 验证全流程（创建→分发→执行→完成）
3. 验证告警（手动触发失败）

---

## 11. Risks / Unknowns

### 已知风险

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| KANBAN.md 并发写冲突 | 中 | 高 | 单 Agent 写权限 |
| Orchestrator 单点故障 | 低 | 高 | heartbeat 恢复 |
| 子任务 token 失控 | 中 | 中 | maxChildrenPerAgent |
| HANDOFF.md 丢失 | 低 | 中 | 备份机制 |

### 未知领域

| 未知 | 验证方式 |
|------|---------|
| Gateway 重启后 cron 状态 | 手动重启测试 |
| 嵌套 sub-agents 性能 | 压测 |
| 长期运行 memory 膨胀 | 监控文件大小 |

---

## 12. Final Recommendation

### 核心建议

**立即启动 Phase 0（Orchestrator + KANBAN.md），2 周内完成 MVP 验证。**

**理由**：
1. OpenClaw 基础设施已完备（cron/heartbeat/hooks/handoff）
2. 当前已有 3+ Agent（Hulk/Midas/Jobs），可立即作为 Spoke 验证
3. 技术风险可控（主要风险是并发写，已有缓解方案）

### 成功条件

1. **V 承诺**：允许 2 周实验期，接受可能的故障
2. **资源**：预留 ¥X/天 的 token 预算用于压测
3. **人工支持**：Phase 3 压测期间可随时接管

### 下一步行动

1. **今天**：创建 KANBAN.md 模板
2. **明天**：实现 Orchestrator prompt
3. **Day 3**：配置健康检查脚本
4. **Day 4-7**：接入 Hulk/Midas 作为 Spoke
5. **Week 2**：24h 压测

---

*Hulk 🟢 — 2026-03-19*  
*证据等级：V3（官方文档 + 实战验证）*  
*置信度：85%（未知领域已标注）*
