# Hulk 工具系统 v2.0 — P0 改进实现

**创建时间**: 2026-03-31 14:30 UTC  
**参考**: Claude Code 工程思想  
**状态**: ✅ P0 完成

---

## 文件结构

```
hulk-tools-v2/
├── tool_system.py        # 工具接口规范化
├── permission_system.py  # 敏感操作确认
├── resume_system.py      # 中断恢复机制
└── README.md            # 使用文档
```

---

## P0.1 — 工具接口规范化

**文件**: `tool_system.py`

### 核心改进

```python
# 之前
async def web_search(query):
    return await gemini_search(query)

# 改进后
class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web using search engine..."
    parameters = {
        "query": {"type": "string", "description": "..."},
        "count": {"type": "integer", "default": 5}
    }
    async def execute(self, args): ...
```

### 优势

1. **自描述** — 模型能理解工具用途
2. **类型安全** — 参数有明确类型定义
3. **易测试** — 接口统一，mock 方便

---

## P0.2 — 敏感操作确认

**文件**: `permission_system.py`

### 核心改进

```python
# 之前
exec(command)  # 直接执行

# 改进后
SENSITIVE_TOOLS = {"exec", "write_file", "delete_file"}

if tool_name in SENSITIVE_TOOLS:
    if not await confirm():
        return {"error": "User denied"}
```

### 优势

1. **安全默认** — 危险操作需确认
2. **白名单机制** — 明确定义敏感工具
3. **拒绝处理** — 用户拒绝不崩溃

---

## P0.3 — 中断恢复机制

**文件**: `resume_system.py`

### 核心改进

```python
# 之前
# Ctrl+C → 进度丢失

# 改进后
signal.signal(SIGINT, lambda: save_state())

# 恢复
python script.py --resume
```

### 优势

1. **优雅中断** — Ctrl+C 不丢失进度
2. **状态持久化** — JSON 保存中间状态
3. **自动恢复** — 启动时检查并恢复

---

## 使用示例

### 1. 基本使用

```python
from tool_system import registry

# 列出工具
for tool in registry.list_tools():
    print(f"{tool['name']}: {tool['description']}")

# 执行工具
result = await registry.execute("web_search", {"query": "AI news"})
```

### 2. 敏感操作

```python
from permission_system import PermissionManager, SafeToolExecutor

pm = PermissionManager()
executor = SafeToolExecutor(pm)

# 敏感工具会询问
result = await executor.execute("exec", {"command": "rm -rf temp"})
# ⚠️ 敏感操作确认:
#    工具：exec
#    参数：{'command': 'rm -rf temp'}
# 确认执行？(y/N):
```

### 3. 可恢复任务

```python
from resume_system import StateManager, ResumableTask

state = StateManager()
task = ResumableTask(state)

# 运行 (支持 --resume)
await task.run(resume=True)
```

---

## 测试

```bash
# 工具系统
python tool_system.py

# 权限系统
python permission_system.py

# 中断恢复 (测试中断)
python resume_system.py
# Ctrl+C
python resume_system.py --resume
```

---

## 下一步 (P1/P2)

| 优先级 | 改进 | 工作量 |
|--------|------|--------|
| P1 | 流式响应 | 4h |
| P1 | 上下文管理器 | 3h |
| P2 | Terminal UI | 8h |

---

*Hulk 🟢 — P0 基础工程规范完成*
