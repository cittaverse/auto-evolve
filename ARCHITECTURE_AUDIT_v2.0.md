# CittaVerse v2.0 架构优化方案评审报告

**评审者**: Hulk 🟢  
**日期**: 2026-03-08  
**状态**: 【需修改】

---

## 一、总体结论

**【需修改】**

方案方向正确，但存在**优先级错配**和**过度工程化风险**。当前 CittaVerse 处于商业模式验证关键期（VSNC 采矿 76% 完成），文档治理不应占用核心带宽。

---

## 二、关键风险点（按严重程度排序）

### 🔴 P0 - 优先级与阶段错配

| 风险项 | 描述 | 证据 |
|--------|------|------|
| 文档重构抢占产品带宽 | P0 任务（docs/目录 + gc_agent.py）合计 1.5h 预估严重低估 | 当前 AGENTS.md 214 行，涉及 5 个核心模块交叉引用 |
| 自动化清理循环过早 | Doc-Gardening 智能体需要稳定的文档格式才能工作，当前格式尚未收敛 | memory_auditor.py 已存在但 knowledge_tier 标记覆盖率 < 20% |
| 决策物理化增加摩擦 | "所有架构决策必须写入 ADR" 在验证期会拖慢迭代速度 | 当前无 decisions/ 目录，无 ADR 模板 |

**核心矛盾**: 方案假设文档系统已经稳定，实际上 CittaVerse 正处于快速迭代期，文档结构每周都在变。

### 🟠 P1 - 单点故障与过度工程

| 风险项 | 描述 | 缓解建议 |
|--------|------|----------|
| gc_agent.py 成为新依赖 | 垃圾回收脚本本身需要维护，增加认知负担 | 先用简单的 cron + shell 脚本替代 |
| 统一日志接口假设过多 | `/logs/{process}_{date}.log` 格式假设所有进程都按此输出 | 先观察现有 13 个 Python 脚本的实际日志模式 |
| ADR 强制写入机制 | 在 2 人团队（V + AI agents）中，ADR 是过度治理 | 改为 "重大决策建议写入" |

### 🟡 P2 - 成本低估

| 任务 | 预估时间 | 实际估算 | 偏差 |
|------|----------|----------|------|
| AGENTS.md 瘦身至 100 行 | 30min | 2-3h | **6x** |
| gc_agent.py 编写 | 1h | 3-4h（含测试） | **3x** |
| citta_watchdog.py 日志增强 | 1h | 2h（含接口设计） | **2x** |

**原因**: 预估未考虑交叉引用梳理、回归测试、文档同步成本。

---

## 三、优先级重排建议

### 当前阶段诊断

根据 `shared/CONTEXT.md`（不存在，说明项目状态分散在 memory/ 中）和 MEMORY.md：

- **产品阶段**: 商业模式验证期（一念万相 V0.2）
- **工程阶段**: 原型验证（pipeline_v0.2_neurosymbolic.py 已跑通）
- **团队规模**: 1 人 + AI agents
- **真实痛点**: 脚本散落在 PROTOTYPES/，无版本控制；memory/ 日志累积但无提炼机制

### 建议的新优先级

```
P0 (本周必须做):
├── 建立 scripts/ 目录，迁移 13 个 Python 文件（30min）
├── 编写 runbook.md：记录每个脚本的用途和运行方式（30min）
└── 设置 memory/ 的每周提炼提醒（15min）

P1 (下周做):
├── 选择 1-2 个核心脚本添加结构化日志（1h）
├── 整理本周关键决策到 memory/ 的 decisions/ 子目录（30min）
└── 评估是否需要 docs/ 目录（而非直接创建）

P2 (商业模式验证完成后):
├── AGENTS.md 瘦身
├── gc_agent.py 自动化清理
├── ADR 强制机制
└── citta_watchdog.py 日志增强
```

### 关键调整逻辑

1. **scripts/ 优先于 docs/**: 代码是活的，文档是死的。先让代码有地方住。
2. **runbook.md 优先于 ARCHITECTURE.md**: 当前需要的是"怎么跑起来"，不是"架构图"。
3. **手动提炼优先于自动化清理**: memory_auditor.py 已存在但知识分层标记不足，先人工跑几次提炼流程，再考虑自动化。

---

## 四、补充的关键实践

基于智能体优先工程范式的核心原则，方案遗漏了以下 3 点：

### 1. 显式上下文传递（Explicit Context Passing）

**现状问题**: AGENTS.md 第 4-5 行要求 "Read `shared/CONTEXT.md`"，但该文件不存在。agent 在启动时会困惑。

**建议**: 
- 在 AGENTS.md 顶部添加 "Context 状态检查清单"
- 每个 agent 启动时先验证必要文件存在性，缺失则向 Core 报告

### 2. 渐进式工具化（Progressive Tooling）

**现状问题**: 方案直接规划了完整的 docs/ 目录结构（ARCHITECTURE.md, decisions/, sop/, brand/），这是"大爆炸式"重构。

**建议**:
- 采用 "文件出现时创建目录" 策略
- 例如：当第 3 个 ADR 产生时，自动创建 decisions/ 目录
- 避免空目录的维护负担

### 3. 自愈优先于观测（Self-Healing > Observability）

**现状问题**: 方案强调 "统一日志接口" 和 "CLI 命令查看日志"，这是观测思维。

**建议**:
- 增加 "失败模式自动恢复" 设计
- 例如：当 pipeline_v0.2.py 调用 Gemini API 失败时，自动回退到本地规则引擎
- 日志是给人类看的，自愈是给系统用的

---

## 五、成本估算（修正版）

| 任务 | Token 消耗 | 时间成本 | 维护负担 | 建议 |
|------|------------|----------|----------|------|
| docs/ 目录 + 文档迁移 | ~50K | 4-6h | 高（需持续同步） | **推迟到 P2** |
| gc_agent.py | ~30K | 3-4h | 中（脚本本身需维护） | **推迟到 P2** |
| ADR 强制机制 | ~20K | 2-3h | 高（增加决策摩擦） | **改为建议性** |
| 日志接口统一 | ~40K | 4-5h | 中（接口变更需同步） | **P1 小范围试点** |
| AGENTS.md 瘦身 | ~15K | 2-3h | 低（一次性） | **P2 再做** |
| scripts/ 整理 | ~5K | 30min | 低 | **P0 立即做** |
| runbook.md | ~10K | 30min | 低 | **P0 立即做** |

---

## 六、可立即执行的最小改动

如果只能做一件事：

```bash
# 1. 创建 scripts/ 目录，迁移所有 Python 文件
mkdir -p scripts/{core,prototypes,utils}
mv PROTOTYPES/*.py scripts/prototypes/
mv memory_auditor.py scripts/utils/
mv extract_paper.py scripts/utils/

# 2. 创建最小化的 runbook.md
cat > runbook.md << 'EOF'
# CittaVerse 运行手册

## 核心脚本
- `scripts/core/pipeline_v0.2_neurosymbolic.py` - 神经符号评分引擎
- `scripts/utils/memory_auditor.py` - 记忆审计（待完善）

## 快速开始
```bash
python scripts/core/pipeline_v0.2_neurosymbolic.py
```

## 最近更新
- 2026-03-08: 脚本目录整理
EOF

# 3. 更新 AGENTS.md 的 First Run 部分
# 将 "Read shared/CONTEXT.md" 改为 "检查以下文件是否存在，缺失则向 Core 报告"
```

---

## 七、最终建议

1. **本周**: 做 scripts/ 整理 + runbook.md，耗时 1h，收益最大
2. **下周**: 评估是否真的需要 docs/ 目录（可能 memory/ + scripts/ 已足够）
3. **商业模式验证后**: 再考虑 gc_agent.py、ADR 机制等重治理工具

**记住**: 在验证期，"能跑起来" 优于 "治理完善"。

---

*评审完成。如有疑问，召唤 Styx 进行压力测试。*
