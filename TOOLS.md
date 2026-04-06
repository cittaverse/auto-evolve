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

---

## 🔐 密钥安全规范（硬约束）

> 2026-03-23 起生效。起因：clawhub-500 仓库 API-KEYS.md 泄漏事故。

### 绝对禁止

1. **永远不把真实密钥写入任何可能被 Git 追踪的文件**
   - 包括 `.md`、`.yaml`、`.json`、`.py`、`.sh`、`.txt` 等所有文件类型
   - 包括"文档"、"说明"、"配置指南"、"setup 教程"等看似无害的文件
   - 包括"临时记录"、"验证结果"、"调试日志"

2. **永远不把密钥写入 commit message 或 PR description**

3. **永远不在公开仓库的 issue/discussion 中粘贴密钥**

### 唯一合法的密钥存放位置

| 场景 | 正确方式 |
|------|---------|
| **GitHub Actions** | GitHub Settings → Secrets and variables → Actions |
| **本地开发** | `~/.bashrc` 或 `~/.zshrc` 中的 `export VAR=xxx`（不入 Git） |
| **OpenClaw 环境** | 环境变量注入（已配置，直接 `$VAR` 使用） |
| **文档中引用** | 只写 `$TAVILY_API_KEY` 或 `[your-key-here]`，永远不写真实值 |

### 文档中的密钥引用模板

```markdown
# ✅ 正确
| Secret Name | Value |
|-------------|-------|
| `TAVILY_API_KEY` | (在 GitHub Secrets 中配置) |
| `OPENAI_API_KEY` | (在 GitHub Secrets 中配置) |

# ❌ 错误
| Secret Name | Value |
|-------------|-------|
| `TAVILY_API_KEY` | `[your-key-here]` |
```

### 安全扫描规范（执行密钥检查时必须遵守）

1. **先穷举所有仓库**：`find /workspace -name ".git" -type d` → 不假设目录结构
2. **文件名扫描**：`find . -iname "*key*" -o -iname "*secret*" -o -iname "*token*" -o -iname "*credential*" -o -iname "*.env"`
3. **内容 regex 扫描**：覆盖常见密钥格式（sk-/tvly-/ghp_/AKIA/AIza 等）
4. **Git 历史扫描**：`git log -p --all | grep` 密钥模式
5. **不遗漏任何路径**：扫描整个 workspace，不只扫 `github-repos/`

### 密钥轮换触发条件

以下任一情况发生时，**立即通知 V 轮换密钥**：
- 发现密钥出现在任何 Git 追踪的文件中
- 发现密钥出现在任何公开可访问的位置
- 密钥被意外打印到日志/输出中

### 事故响应流程

1. **立即**：从文件中删除密钥 → `[REDACTED]`
2. **立即**：`git filter-branch` 或 `git filter-repo` 重写历史
3. **立即**：`git push --force`
4. **立即**：通知 V 轮换密钥
5. **事后**：添加 `.gitignore` 规则防止复发

---

### Skills

**默认先假设工具能力会随 host / pairing / sidecar 状态漂移。不要把 `exec`、`browser`、`web_search` 的可用性当成恒定事实。**

研究任务默认顺序：
1. 先试原生 `web_search`；若当前 session 出现 key missing/invalid 或额度问题，立即切换，不要重试
2. 公开网页发现优先 `browser`；仅在需要 CLI fallback 且 `exec` 正常时才用 `ddg-search`
3. 原生 `web_fetch` 只用于解析到公网 IP 的公开 HTTP(S) 页面
4. 如果 `web_fetch` 返回 `Blocked: private/internal IP`，不要重试；公开站点改走 `browser`，明确受信任的内部目标才允许受控 `exec`
5. 如果 VPN/Clash 的 fake-IP 模式把公网域名解析到 `198.18.0.0/15`，也视为同类阻断，不要继续重试 `web_fetch`

环境变量规则：
- 只在当前 session 已确认存在时，才把某个 API key 当成可用
- `$SERPER_API_KEY` 即使存在，credits 用尽时也不要当 fallback
- `$GEMINI_API_KEY` 不保证每个 host 都可用；报错时按不可用处理

技能使用参考：`/Users/moondy/.openclaw/shared/SKILLS.md`

**快速备忘（直接在 bash 里跑）：**
- 原生工具优先，不要把下面这些 fallback 命令当第一选择
- google-search / 直连 Serper → 当前不要作为 fallback；Serper credits exhausted 时只会重复失败
- ddg-search → `/Users/moondy/.openclaw/workspace/node_modules/.bin/ddg-search -f compact "query"`（依赖可用 `exec` host，且可能触发 anti-bot）
- weather → `curl "https://wttr.in/城市?format=3"`
