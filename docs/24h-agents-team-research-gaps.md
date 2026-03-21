# 24h Agents Team 落地缺口分析

**调研日期**: 2026-03-19  
**作者**: Hulk 🟢  
**目的**: 识别当前方案与可落地之间的差距，制定深化调研计划

---

## 一、当前方案成熟度评估

### 已完成（V3 证据等级）

| 模块 | 状态 | 文档 |
|------|------|------|
| **架构设计** | ✅ 三报告共识 + 实战验证 | `24h-agents-team-implementation-plan.md` |
| **失败模式分析** | ✅ 12 种 failure modes | 同上 |
| **稳定性保障** | ✅ cron/heartbeat/hooks配置 | `STABLE_LOOP_GUIDE.md` |
| **Cron 配置** | ✅ 已修复 Hulk 6 个 cron | 实战验证 |

### 待深化（V1-V2 证据等级）

| 模块 | 当前状态 | 缺口 | 优先级 |
|------|---------|------|--------|
| **KANBAN.md 模板** | 仅有结构示例 | 缺少任务 ID 生成规则、状态机定义、验真标准 | P0 |
| **Orchestrator Prompt** | 未实现 | 缺少具体 prompt、任务分发逻辑、冲突解决策略 | P0 |
| **健康检查脚本** | 未实现 | 缺少具体实现、告警阈值、恢复流程 | P0 |
| **成本监控** | 仅有指标定义 | 缺少预算控制、自动止损、成本优化策略 | P1 |
| **故障注入测试** | 仅有测试项列表 | 缺少具体注入方法、预期行为、验收标准 | P1 |
| **SLO 定义** | 仅有目标值 | 缺少测量方法、基线数据、改进路径 | P1 |
| **安全加固** | 仅有原则 | 缺少具体 sandbox 配置、tool allowlist 模板、审计日志 | P0 |

---

## 二、深化调研计划

### Phase 1: 核心机制设计（Day 1-2）

#### 1.1 任务队列与状态机

**调研问题**：
- 任务 ID 生成规则（如何保证全局唯一 + 可追溯）
- 状态流转图（TODO→IN_PROGRESS→DONE/BLOCKED/FAILED）
- 并发控制（如何避免多 Agent 同时写 KANBAN.md）
- 幂等执行（如何保证重试不产生副作用）

**对标参考**：
- GitHub Issues 状态机
- Jira Workflow
- Kubernetes Job 状态管理

**交付物**：
- `KANBAN_TEMPLATE.md`（含完整字段定义）
- `TASK_STATE_MACHINE.md`（状态流转图 + 转换规则）
- `TASK_ID_SPEC.md`（ID 生成规则）

#### 1.2 Orchestrator Prompt 设计

**调研问题**：
- 任务分发策略（如何决定哪个任务分配给哪个 Spoke）
- 冲突解决（当多个 Spoke 报告同一任务完成时）
- 超时处理（Spoke 未按时完成任务时）
- 质量验真（如何判断 Spoke 输出是否合格）

**对标参考**：
- DevClaw Coordinator Agent
- AutoGen Group Chat Manager
- CrewAI Manager Agent

**交付物**：
- `ORCHESTRATOR_PROMPT.md`（完整 prompt）
- `TASK_ASSIGNMENT_RULES.md`（分发策略）
- `QUALITY_VERIFICATION.md`（验真标准）

#### 1.3 健康检查与告警

**调研问题**：
- 健康检查频率（多久检查一次）
- 告警阈值（什么情况下触发告警）
- 告警渠道（如何通知 V）
- 自动恢复（哪些故障可以自动恢复）

**对标参考**：
- Prometheus Alertmanager
- AWS CloudWatch Alarms
- OpenClaw failure-alert-channel

**交付物**：
- `HEALTH_CHECK_SCRIPT.sh`（可执行脚本）
- `ALERT_THRESHOLDS.md`（阈值定义）
- `RECOVERY_RUNBOOK.md`（恢复手册）

---

### Phase 2: 安全与成本（Day 3-4）

#### 2.1 安全加固方案

**调研问题**：
- sandbox 配置（Docker vs SSH vs OpenShell）
- tool allowlist（每个 Spoke 允许哪些工具）
- 审计日志（如何记录所有 Agent 操作）
- 凭据管理（如何安全存储 API Keys）

**对标参考**：
- OpenClaw sandbox 配置文档
- Microsoft Security 建议（隔离环境、专用凭据）
- Oasis 漏洞修复建议（升级到 2026.2.25+）

**交付物**：
- `SECURITY_CONFIG.md`（sandbox + tool 策略）
- `AUDIT_LOG_SPEC.md`（审计日志格式）
- `CREDENTIALS_MANAGEMENT.md`（凭据管理规范）

#### 2.2 成本监控与优化

**调研问题**：
- token 用量监控（如何实时统计）
- 预算控制（如何设置硬上限）
- 成本优化（isolatedSession + lightContext + 混合模型）
- 自动止损（超出预算时如何自动停止）

**对标参考**：
- OpenClaw sessions_status
- Anthropic Usage Dashboard
- Vercel AI Cost Tracking

**交付物**：
- `COST_MONITORING_SCRIPT.sh`（监控脚本）
- `BUDGET_CONTROL.md`（预算规则）
- `COST_OPTIMIZATION_GUIDE.md`（优化指南）

---

### Phase 3: 测试与验证（Day 5-7）

#### 3.1 故障注入测试

**调研问题**：
- 如何模拟 cron 超时
- 如何模拟网络中断
- 如何模拟 KANBAN.md 损坏
- 如何模拟 Orchestrator 假死

**对标参考**：
- Chaos Engineering 原则
- AWS Fault Injection Simulator
- Kubernetes Chaos Mesh

**交付物**：
- `CHAOS_TEST_PLAN.md`（测试计划）
- `FAULT_INJECTION_SCRIPTS.sh`（注入脚本）
- `TEST_RESULTS.md`（测试结果）

#### 3.2 24h 压测

**调研问题**：
- 压测场景设计（模拟真实负载）
- 指标采集（如何记录成功率/延迟/成本）
- 验收标准（什么情况下算通过）
- 问题定位（如何分析失败原因）

**对标参考**：
- Load Testing Best Practices
- OpenClaw cron runs 历史数据分析

**交付物**：
- `STRESS_TEST_PLAN.md`（压测计划）
- `METRICS_COLLECTION.md`（指标采集方案）
- `ACCEPTANCE_CRITERIA.md`（验收标准）

---

### Phase 4: SLO 与持续改进（Day 8-10）

#### 4.1 SLO 定义与测量

**调研问题**：
- 24h 存活率如何测量
- 任务成功率如何统计
- 平均恢复时间如何计算
- 人工介入率如何追踪

**对标参考**：
- Google SRE SLO/SLI 框架
- AWS Well-Architected Framework

**交付物**：
- `SLO_DEFINITION.md`（SLO 定义）
- `SLI_MEASUREMENT.md`（SLI 测量方法）
- `ERROR_BUDGET.md`（错误预算）

#### 4.2 持续改进机制

**调研问题**：
- 如何收集运行数据
- 如何分析问题根因
- 如何迭代优化
- 如何版本管理

**对标参考**：
- DevOps Feedback Loops
- Continuous Improvement Frameworks

**交付物**：
- `CONTINUOUS_IMPROVEMENT.md`（改进流程）
- `VERSION_CONTROL.md`（版本管理规范）

---

## 三、优先级排序

| 阶段 | 时间 | 关键交付物 | 阻塞后续 | 优先级 |
|------|------|-----------|---------|--------|
| **Phase 1** | Day 1-2 | KANBAN 模板 + Orchestrator Prompt + 健康检查 | Phase 2/3/4 | P0 |
| **Phase 2** | Day 3-4 | 安全配置 + 成本监控 | Phase 3 | P1 |
| **Phase 3** | Day 5-7 | 故障注入 + 24h 压测 | Phase 4 | P1 |
| **Phase 4** | Day 8-10 | SLO 定义 + 持续改进 | - | P2 |

---

## 四、立即行动（Day 1）

### 4.1 KANBAN.md 模板设计

**参考来源**：
- GitHub Projects
- Jira Kanban
- Linear Issues

**核心字段**：
```markdown
| ID | 任务 | 优先级 | 分配给 | 创建时间 | 截止时间 | 状态 | 依赖 | 输出 | 验真状态 |
```

**ID 生成规则**：
```
T-YYYYMMDD-NNN
- T: Task 前缀
- YYYYMMDD: 创建日期
- NNN: 当日序号（从 001 开始）
```

**状态机**：
```
TODO → IN_PROGRESS → DONE
              ↓
           BLOCKED → TODO (解除阻塞后)
              ↓
           FAILED → TODO (重试) 或 ARCHIVED
```

### 4.2 Orchestrator Prompt 骨架

**核心职责**：
1. 读取 KANBAN.md TODO 列
2. 根据 Spoke 能力分配任务
3. 创建 HANDOFF.md
4. 监控任务进度
5. 验真输出
6. 更新 KANBAN.md

**Prompt 骨架**：
```markdown
# 角色
你是 Orchestrator，负责协调 Hulk/Midas/Jobs 等 Spoke Agent 的工作。

# 职责
1. 每 30 分钟检查 KANBAN.md
2. 将 TODO 任务分配给合适的 Spoke
3. 监控 IN_PROGRESS 任务，超时则告警
4. 验真 DONE 任务的输出
5. 更新 KANBAN.md 状态

# 任务分配规则
- 研究任务 → Hulk
- 商业任务 → Midas
- 运维任务 → Jobs
- 紧急任务 → 直接 sessions_spawn
- 非紧急任务 → HANDOFF.md

# 验真标准
- 输出文件必须存在
- 输出内容必须包含关键字段
- 任务 ID 必须与 KANBAN.md 一致
```

### 4.3 健康检查脚本骨架

**检查项**：
```bash
#!/bin/bash
# 1. Gateway 进程检查
pgrep -f "openclaw" || exit 1

# 2. cron 状态检查
openclaw cron list | grep error | wc -l

# 3. 任务堆积检查
grep -c "^|.*|.*TODO" KANBAN.md

# 4. token 用量检查
openclaw sessions_status | grep token

# 5. 磁盘空间检查
df -h /home/node/.openclaw | awk '{print $5}'
```

---

## 五、风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| KANBAN.md 并发写冲突 | 中 | 高 | 单 Agent 写权限 + 文件锁 |
| Orchestrator 单点故障 | 低 | 高 | heartbeat 恢复 + 备份 Orchestrator |
| 成本失控 | 中 | 中 | 硬上限 + 自动止损 |
| 安全漏洞 | 低 | 高 | sandbox + tool allowlist + 审计日志 |

---

*Hulk 🟢 — 2026-03-19*  
*下一步：执行 Phase 1（Day 1-2）*
