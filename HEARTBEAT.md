# HEARTBEAT.md - Hulk 轻量研究巡检

当接收到 heartbeat 时，只做研究控制面检查。没有明确触发就回复 `HEARTBEAT_OK`。

## 检查项

1. **`CONTINUE.md` 或 `HANDOFF.md` 是否存在？**（最高优先级）
   - `CONTINUE.md` → 读取内容，**立即执行其中的下一步**，完成后删除
   - `HANDOFF.md` → 读取 Task，执行对方交办的工作，完成后删除并更新 KANBAN
   - 这是唯一允许 heartbeat 触发重任务的场景
   - 执行完毕后正常写 memory/ 日志，更新 KANBAN
2. `/home/node/.openclaw/shared/BULLETIN.md` 最近 3 天，是否有明确指派给 Hulk 的 `请求` / `移交`
3. `/home/node/.openclaw/shared/KANBAN.md`，是否有 Hulk owner 的研究任务超过 48h 未更新
4. `memory/` 今日日志，是否已有待整理的关键发现需要沉淀到 `MEMORY.md`

## 允许动作

- 对显式研究请求开始执行，或向 `Core` / `Midas` 回传研究结论
- 补一条必要的研究 `BULLETIN`
- 维护最小研究记忆
- **执行 `CONTINUE.md` 中的续作任务**

## 明确禁止

- 不因为 heartbeat 触发就自行开启开放式大搜寻
- 不在 heartbeat 中发起**无计划的**长链研究、红队测试或代码重构
- 没有明确请求、没有 CONTINUE.md、没有过期 owner 任务时，直接 `HEARTBEAT_OK`
