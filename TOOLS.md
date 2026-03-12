# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.


### 🤝 Agent 间通信（agentToAgent）

你可以直接召唤团队成员执行任务。**你有权限联系：`main`（Core）、`midas`**。

#### 方式一：spawn 一次性任务（最常用）

```javascript
sessions_spawn({
  agentId: "midas",          // 目标 agent ID
  task: "帮我调研这个市场机会：...",  // 给他的任务描述
  runtime: "subagent",
  mode: "run",               // run = 一次性，完成即返回
  cleanup: "delete"
})
```

#### 方式二：先查可用的 agent

```javascript
agents_list({})
// 返回你有权限联系的 agent 列表
```

#### 典型场景

- **Hulk → Midas**：研究发现商业机会，直接让 Midas 评估可行性
  ```
  task: "我发现了一个机会：[描述]。请你从商业化角度评估：市场规模、变现路径、风险点。"
  ```
- **Hulk → Core**：需要 Core 协调其他资源或做决策时
  ```
  task: "研究完成，结论如下：[摘要]。请 Core 决定下一步行动。"
  ```

#### 注意

- `mode: "run"` 是同步的，会等 Midas 回复才继续
- 任务描述要清晰，Midas 没有你的上下文，要把必要背景都写进去
- 不要频繁 spawn，高价值任务才值得跨 agent 协作

### Skills

**你已经在容器内运行。不需要 docker exec，不需要任何外部命令。直接用 bash 工具调用即可。**

研究任务默认顺序：
1. 先用原生 `web_search`
2. 再用原生 `web_fetch`
3. 只有原生工具失败时，才退回 `google-search` 或手写 `curl Serper`

所有 API Key 已注入你的环境变量，直接 $VAR 使用：
- $SERPER_API_KEY → google-search 已可用
- $GEMINI_API_KEY → nano-banana-pro 已可用

技能使用参考：`/home/node/.openclaw/shared/SKILLS.md`

**快速备忘（直接在 bash 里跑）：**
- 原生工具优先，不要把下面这些 fallback 命令当第一选择
- google-search → `curl -s -X POST "https://google.serper.dev/search" -H "X-API-KEY: $SERPER_API_KEY" -H "Content-Type: application/json" -d '{"q": "搜索词", "num": 10}'`
- ddg-search → `/home/node/.openclaw/workspace/node_modules/.bin/ddg-search -f compact "query"`
- weather → `curl "https://wttr.in/城市?format=3"`
