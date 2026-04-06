# Claude Code 源码深度分析

**研究时间**: 2026-03-31 14:20 UTC  
**信息来源**: GitHub, npm, 官方文档，技术分析文章

---

## 一、Claude Code 是什么

**Claude Code** 是 Anthropic 2025 年推出的**终端原生 AI 编程助手**，直接集成到开发工作流中。

**核心定位**:
- 不是 IDE 插件，而是**终端原生命令行工具**
- 基于 Claude 3.7 Sonnet (后来升级到 Claude 4 系列)
- 支持代码生成、调试、重构、测试、文档等全流程

**官方链接**:
- GitHub: https://github.com/anthropics/claude-code
- npm: https://www.npmjs.com/package/@anthropic-ai/claude-code
- 文档：https://docs.anthropic.com/claude-code/

---

## 二、核心架构

### 2.1 技术栈

| 层级 | 技术 |
|------|------|
| **运行时** | Node.js / Bun |
| **语言** | TypeScript |
| **包管理** | npm / yarn |
| **API** | Anthropic API (Claude 模型) |
| **终端 UI** | Ink (React for CLI) / blessed |

### 2.2 核心模块

```
claude-code/
├── src/
│   ├── core/           # 核心逻辑
│   │   ├── agent.ts    # Agent 循环
│   │   ├── tools.ts    # 工具定义
│   │   └── planner.ts  # 任务规划
│   ├── cli/            # 命令行界面
│   │   ├── ui.tsx      # Terminal UI (Ink)
│   │   └── commands.ts # 命令解析
│   ├── integrations/   # 外部集成
│   │   ├── git.ts      # Git 操作
│   │   ├── shell.ts    # Shell 执行
│   │   └── editor.ts   # 编辑器集成
│   └── utils/          # 工具函数
├── package.json
└── README.md
```

### 2.3 核心工作流程

```
用户输入 → 命令解析 → 任务规划 → 工具调用 → 执行 → 结果反馈 → 迭代
                ↓
          Claude API (模型推理)
                ↓
          工具选择 + 参数生成
```

---

## 三、关键设计模式

### 3.1 Agent 循环 (ReAct 模式)

```typescript
async function agentLoop(userInput: string) {
  let messages: Message[] = [userInput];
  
  while (true) {
    // 1. 调用 Claude API
    const response = await claude(messages, { tools });
    
    // 2. 检查是否需要调用工具
    if (response.tool_calls) {
      for (const tool of response.tool_calls) {
        // 3. 执行工具
        const result = await executeTool(tool.name, tool.args);
        messages.push({ tool_result: result });
      }
    } else {
      // 4. 返回最终结果
      return response.content;
    }
  }
}
```

**特点**:
- 多轮迭代，直到任务完成
- 工具调用结果反馈给模型，形成闭环
- 支持中断和人工确认

### 3.2 工具系统

```typescript
const tools = {
  read_file: {
    description: "Read contents of a file",
    parameters: { path: "string" },
    execute: async ({ path }) => fs.readFile(path)
  },
  write_file: {
    description: "Write contents to a file",
    parameters: { path: "string", content: "string" },
    execute: async ({ path, content }) => fs.writeFile(path, content)
  },
  run_command: {
    description: "Execute a shell command",
    parameters: { command: "string" },
    execute: async ({ command }) => exec(command)
  },
  search_code: {
    description: "Search codebase for pattern",
    parameters: { pattern: "string" },
    execute: async ({ pattern }) => grep(pattern)
  }
};
```

**设计原则**:
- 每个工具有清晰的 description 和 parameters
- 工具执行结果结构化返回
- 支持权限控制 (某些工具需要用户确认)

### 3.3 上下文管理

```typescript
class ContextManager {
  private maxTokens: number = 200000; // Claude 上下文窗口
  private messages: Message[] = [];
  
  addMessage(msg: Message) {
    this.messages.push(msg);
    this.trimIfNeeded();
  }
  
  trimIfNeeded() {
    while (this.getTokenCount() > this.maxTokens) {
      // 移除最早的消息
      this.messages.shift();
    }
  }
}
```

**策略**:
- 滑动窗口保留最近对话
- 重要信息 (如文件内容) 优先保留
- 支持摘要压缩长上下文

---

## 四、与 CittaVerse/Hulk 对比

| 维度 | Claude Code | CittaVerse (Hulk) |
|------|-------------|-------------------|
| **定位** | 通用编程助手 | 垂直领域 (老年认知干预) |
| **架构** | Agent 循环 + 工具系统 | GEO 迭代 + Memory 系统 |
| **运行时** | Node.js/终端 | OpenClaw/Python |
| **模型** | Claude 3.7/4 | qwen3.5-plus + 规则 |
| **工具** | 文件/Shell/Git | web_search/browser/exec/memory |
| **上下文** | 200K tokens | MEMORY.md + memory/*.md |
| **开源** | ❌ 闭源 | ✅ 开源 (MIT) |
| **临床验证** | ❌ 无 | ✅ Pilot RCT |

### 可借鉴设计

1. **Agent 循环模式** — Hulk 的 GEO 迭代可参考 ReAct 模式
2. **工具系统设计** — 清晰的 description/parameters/execute 分离
3. **Terminal UI** — Ink (React for CLI) 比纯文本更友好
4. **权限控制** — 敏感操作需要用户确认

---

## 五、技术亮点

### 5.1 流式响应

```typescript
const stream = await claude.stream(messages, { tools });
for await (const chunk of stream) {
  if (chunk.type === 'text') process.stdout.write(chunk.text);
  if (chunk.type === 'tool_call') await handleTool(chunk);
}
```

**优势**: 用户实时看到进展，不是等待最终结果

### 5.2 中断恢复

```typescript
process.on('SIGINT', () => {
  // 保存当前状态
  saveState({ messages, currentTool });
  // 优雅退出
  console.log('\nInterrupted. Resume with: claude-code --resume');
  process.exit(0);
});
```

**优势**: 长任务中断后可恢复，不丢失进度

### 5.3 多文件编辑

```typescript
async function editMultipleFiles(changes: FileChange[]) {
  // 批量读取
  const contents = await Promise.all(changes.map(c => fs.readFile(c.path)));
  
  // 批量修改
  const updated = contents.map((c, i) => applyChange(c, changes[i]));
  
  // 批量写入 (事务性)
  await Promise.all(changes.map((c, i) => fs.writeFile(c.path, updated[i])));
}
```

**优势**: 跨文件重构时保持一致性

---

## 六、局限性

| 局限 | 说明 |
|------|------|
| **闭源** | 核心逻辑不公开，无法审计 |
| **依赖 Anthropic API** | 离线不可用 |
| **终端限制** | 复杂 UI 场景不如 GUI |
| **无长期记忆** | 会话结束即遗忘 |
| **无领域优化** | 通用编程，非垂直领域 |

---

## 七、对 Hulk 的启示

### 7.1 架构改进

**当前 Hulk**:
```
用户输入 → GEO 迭代 → Memory 更新 → 输出
```

**参考 Claude Code**:
```
用户输入 → Agent 循环 → 工具调用 → 结果反馈 → 迭代 → Memory 持久化
```

### 7.2 具体行动

| 行动 | 优先级 | 说明 |
|------|--------|------|
| **工具系统重构** | P0 | description/parameters/execute 分离 |
| **流式响应** | P1 | 用户实时看到进展 |
| **中断恢复** | P1 | 长任务保存状态 |
| **Terminal UI** | P2 | Ink 渲染更友好 |
| **权限控制** | P2 | 敏感操作需确认 |

### 7.3 差异化优势

| CittaVerse 优势 | 说明 |
|----------------|------|
| **开源透明** | 代码可审计，可修改 |
| **领域专业** | 老年认知干预专用 |
| **临床验证** | Pilot RCT 证据 |
| **长期记忆** | MEMORY.md 持久化 |
| **本地优先** | 规则模式可离线 |

---

## 八、总结

**Claude Code 核心价值**:
1. 终端原生的开发体验
2. Agent 循环 + 工具系统的成熟模式
3. 流式响应 + 中断恢复的用户体验

**Hulk 学习方向**:
1. 工具系统规范化
2. 流式响应实现
3. 中断恢复机制

**Hulk 保持优势**:
1. 开源透明
2. 领域专业化
3. 长期记忆
4. 临床验证

---

*Hulk 🟢 — 学习优秀设计，保持差异化优势*
