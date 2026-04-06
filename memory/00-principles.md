# 原则与工作协议

---

## Session 启动协议

1. **先读 `memory/01-api-keys-status.md`** — 了解当前 API Key 状态
2. **再读 `memory/00-principles.md`** — 重温工作原则
3. **`memory_search` 最新日志** — `memory/2026-MM-DD.md` (倒序)
4. **最后读 HEARTBEAT.md** — 补充短期状态（注意可能被截断）

---

## 状态变更记录协议

**关键状态变更必须同时写入**：
1. `HEARTBEAT.md` — 短期状态（会被截断）
2. `memory/日期.md` — 持久化日志（时间倒序）
3. `memory/01-api-keys-status.md` — API Key 状态（覆盖更新）

**禁止**: 只更新 HEARTBEAT.md 而不持久化到 `memory/`

---

## 安全扫描协议

执行密钥检查时必须：
1. **穷举所有仓库**: `find . -name ".git" -type d`
2. **文件名扫描**: `find . -iname "*key*" -o -iname "*secret*" ...`
3. **内容 regex 扫描**: 覆盖常见密钥格式
4. **Git 历史扫描**: `git log -p --all | grep`
5. **不假设目录结构**: 扫描整个 workspace

---

## arXiv 提交 SOP

1. Overleaf 编译 PDF (XeLaTeX + ctex)
2. 登录 arXiv → Start New Submission
3. 填写元数据 (cs.HC primary + cs.CL secondary)
4. 上传 PDF + source (tar.gz)
5. 选择 CC BY 4.0 license
6. 提交后更新 README 加 arXiv 徽章

---

## PR 跟进协议

| 天数 | 行动 |
|------|------|
| Day 0 | 提交 PR |
| Day 3 | 检查状态 (无回复→正常) |
| Day 7 | 发友好 follow-up comment |
| Day 14 | 第二次 follow-up 或放弃 |
| Day 30 | 关闭或继续等待 |

---

## 密钥轮换触发条件

以下任一情况发生时，**立即通知 V 轮换密钥**：
- 发现密钥出现在任何 Git 追踪的文件中
- 发现密钥出现在任何公开可访问的位置
- 密钥被意外打印到日志/输出中

---

## 事故响应流程

1. **立即**: 从文件中删除密钥 → `[REDACTED]`
2. **立即**: `git filter-branch` 或 `git filter-repo` 重写历史
3. **立即**: `git push --force`
4. **立即**: 通知 V 轮换密钥
5. **事后**: 添加 `.gitignore` 规则防止复发

---

*最后更新：2026-03-30 04:45 UTC*
