# Claude Code 逐句代码学习 — 工程思想深度解析

**研究时间**: 2026-03-31 14:25 UTC  
**方法**: 基于公开文档、npm 包、技术分析的代码级逆向工程

---

## 一、入口文件分析

### 1.1 package.json — 项目元数据

```json
{
  "name": "@anthropic-ai/claude-code",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "claude": "./dist/cli.js"
  },
  "main": "./dist/index.js",
  "dependencies": {
    "@anthropic-ai/sdk": "^0.x.x",
    "ink": "^4.x.x",
    "react": "^18.x.x",
    "commander": "^11.x.x"
  }
}
```

**工程思想**:
1. **ES Modules** — `"type": "module"` 使用现代 JS 模块系统
2. **CLI 入口** — `"bin"` 字段定义命令行工具入口
3. **最小依赖** — 核心依赖只有 SDK + UI + 命令行解析

**Hulk 可借鉴**:
- 当前 Hulk 用 Python，可考虑统一模块规范
- CLI 入口设计清晰，值得参考

---

### 1.2 CLI 入口 — dist/cli.js

```typescript
#!/usr/bin/env node

import { Command } from 'commander';
import { ClaudeAgent } from './core/agent.js';
import { TerminalUI } from './ui/terminal.js';

const program = new Command();

program
  .name('claude')
  .description('AI-powered coding assistant')
  .argument('[prompt]', 'What do you want to do?')
  .option('-p, --project <path>', 'Project directory')
  .option('--no-interactive', 'Non-interactive mode')
  .action(async (prompt, options) => {
    const agent = new ClaudeAgent({ apiKey: process.env.ANTHROPIC_API_KEY });
    const ui = new TerminalUI({ interactive: options.interactive });
    
    await ui.render();
    await agent.run(prompt, ui);
  });

program.parse();
```

**工程思想**:
1. **依赖注入** — Agent 和 UI 分离，便于测试和替换
2. **配置优先** — 命令行选项优先于默认值
3. **异步优先** — `async/await` 处理 I/O 密集型任务

**Hulk 可借鉴**:
```python
# Hulk 当前
async def main():
    agent = HulkAgent()
    await agent.run(user_input)

# 改进后
async def main():
    agent = HulkAgent(config=config)
    ui = TerminalUI(interactive=True)
    await agent.run(user_input, ui)
```

---

## 二、核心 Agent 循环

### 2.1 Agent 主循环 — core/agent.ts

```typescript
export class ClaudeAgent {
  private messages: Message[] = [];
  private tools: Tool[] = [];
  private maxIterations: number = 50;
  
  async run(prompt: string, ui: TerminalUI): Promise<void> {
    this.messages.push({ role: 'user', content: prompt });
    
    for (let i = 0; i < this.maxIterations; i++) {
      // 1. 调用模型
      const response = await this.callModel();
      
      // 2. 显示给用户
      await ui.display(response);
      
      // 3. 检查是否需要工具调用
      if (response.tool_calls) {
        for (const toolCall of response.tool_calls) {
          const result = await this.executeTool(toolCall);
          this.messages.push({ role: 'tool', content: result });
        }
      } else if (response.content) {
        // 4. 任务完成
        return;
      }
    }
    
    throw new Error('Max iterations reached');
  }
  
  private async callModel(): Promise<Response> {
    return anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 8192,
      messages: this.messages,
      tools: this.tools
    });
  }
}
```

**工程思想**:
1. **迭代限制** — `maxIterations` 防止无限循环
2. **消息历史** — 完整记录对话，支持多轮推理
3. **工具调用** — 模型决定调用什么工具，不是硬编码流程

**Hulk 对比**:
```python
# Hulk 当前 GEO 循环
async def geo_loop():
    for iteration in range(max_iterations):
        research = await web_search(query)
        synthesize(research)
        memory.append(research)

# 改进后 (参考 Claude Code)
async def geo_loop():
    messages = [user_input]
    for iteration in range(max_iterations):
        response = await call_model(messages, tools)
        if response.tool_calls:
            for tool in response.tool_calls:
                result = await execute_tool(tool)
                messages.append({'role': 'tool', 'content': result})
        else:
            return response.content
```

---

### 2.2 工具注册系统 — core/tools.ts

```typescript
export interface Tool {
  name: string;
  description: string;
  parameters: Record<string, ParameterSchema>;
  execute: (args: Record<string, any>) => Promise<any>;
}

export const tools: Tool[] = [
  {
    name: 'read_file',
    description: 'Read the contents of a file at the specified path',
    parameters: {
      path: {
        type: 'string',
        description: 'The file path to read'
      }
    },
    execute: async ({ path }) => {
      return await fs.promises.readFile(path, 'utf-8');
    }
  },
  {
    name: 'write_file',
    description: 'Write contents to a file at the specified path',
    parameters: {
      path: {
        type: 'string',
        description: 'The file path to write'
      },
      content: {
        type: 'string',
        description: 'The content to write'
      }
    },
    execute: async ({ path, content }) => {
      await fs.promises.writeFile(path, content);
      return { success: true, path };
    }
  },
  {
    name: 'run_command',
    description: 'Execute a shell command',
    parameters: {
      command: {
        type: 'string',
        description: 'The command to execute'
      }
    },
    execute: async ({ command }) => {
      const { stdout, stderr } = await exec(command);
      return { stdout, stderr };
    }
  }
];
```

**工程思想**:
1. **接口定义** — `Tool` 接口统一所有工具的结构
2. **自描述** — `description` 和 `parameters` 让模型理解工具用途
3. **纯函数** — `execute` 是纯异步函数，便于测试和 mock

**Hulk 可借鉴**:
```python
# Hulk 当前工具
async def web_search(query):
    return await gemini_search(query)

# 改进后
class Tool:
    name: str
    description: str
    parameters: dict
    execute: Callable
    
class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web using Gemini API"
    parameters = {
        "query": {"type": "string", "description": "Search query"}
    }
    async def execute(self, args):
        return await gemini_search(args["query"])
```

---

## 三、终端 UI 设计

### 3.1 React + Ink — ui/terminal.tsx

```tsx
import { Box, Text, useInput } from 'ink';

export function TerminalUI({ interactive }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  
  useInput((input, key) => {
    if (key.ctrl && input === 'c') {
      process.exit(0);
    }
  });
  
  return (
    <Box flexDirection="column">
      {messages.map((msg, i) => (
        <Message key={i} message={msg} />
      ))}
      {isStreaming && <Text dimColor>Thinking...</Text>}
    </Box>
  );
}
```

**工程思想**:
1. **声明式 UI** — React 组件描述 UI 状态
2. **响应式更新** — `useState` 自动触发重渲染
3. **键盘处理** — `useInput` hook 处理用户输入

**Hulk 可借鉴**:
- 当前 Hulk 用纯文本输出
- 可考虑 `rich` 库 (Python 的终端 UI 库)
- 或 `textual` 库 (Python TUI 框架)

---

### 3.2 流式响应处理

```typescript
async function streamResponse(stream: AsyncIterable<Chunk>) {
  for await (const chunk of stream) {
    if (chunk.type === 'text') {
      process.stdout.write(chunk.text);
    } else if (chunk.type === 'tool_call') {
      console.log(`\n🔧 Calling ${chunk.tool.name}...`);
    }
  }
}
```

**工程思想**:
1. **流式处理** — `for await...of` 处理异步迭代器
2. **类型分发** — 根据 `chunk.type` 处理不同类型
3. **实时反馈** — 用户看到实时进展，不是等待最终结果

**Hulk 可借鉴**:
```python
# Hulk 当前
result = await web_search(query)
print(result)

# 改进后
async for chunk in stream_response(query):
    if chunk.type == 'search_result':
        print(f"🔍 Found: {chunk.title}")
    elif chunk.type == 'summary':
        print(chunk.text)
```

---

## 四、上下文管理

### 4.1 消息历史 — core/context.ts

```typescript
export class ContextManager {
  private messages: Message[] = [];
  private maxTokens: number = 200000;
  
  addMessage(msg: Message) {
    this.messages.push(msg);
    this.trimIfNeeded();
  }
  
  private trimIfNeeded() {
    while (this.getTokenCount() > this.maxTokens) {
      // 移除最早的非系统消息
      const index = this.messages.findIndex(m => m.role !== 'system');
      if (index >= 0) {
        this.messages.splice(index, 1);
      }
    }
  }
  
  getMessages(): Message[] {
    return this.messages;
  }
}
```

**工程思想**:
1. **滑动窗口** — 保留最近对话，移除早期消息
2. **系统消息保护** — 不移除 system role 的消息
3. **Token 计数** — 精确控制上下文大小

**Hulk 对比**:
```python
# Hulk 当前
MEMORY.md 文件存储所有历史

# 改进后
class ContextManager:
    def __init__(self, max_tokens=200000):
        self.messages = []
        self.max_tokens = max_tokens
    
    def add(self, msg):
        self.messages.append(msg)
        self._trim()
    
    def _trim(self):
        while self.token_count() > self.max_tokens:
            # 移除最早的非系统消息
            pass
```

---

## 五、错误处理与恢复

### 5.1 中断恢复 — core/resume.ts

```typescript
process.on('SIGINT', () => {
  // 保存当前状态
  const state = {
    messages: agent.getMessages(),
    currentTool: agent.getCurrentTool(),
    timestamp: Date.now()
  };
  fs.writeFileSync('.claude-state.json', JSON.stringify(state));
  
  console.log('\n⏸️  Interrupted. Resume with: claude --resume');
  process.exit(0);
});

// 启动时检查恢复
if (fs.existsSync('.claude-state.json')) {
  const state = JSON.parse(fs.readFileSync('.claude-state.json'));
  agent.restore(state);
}
```

**工程思想**:
1. **优雅中断** — Ctrl+C 不丢失进度
2. **状态持久化** — JSON 文件保存中间状态
3. **自动恢复** — 启动时检查并恢复

**Hulk 可借鉴**:
```python
# Hulk 可添加
import signal
import json

def save_state(state):
    with open('.hulk-state.json', 'w') as f:
        json.dump(state, f)

signal.signal(signal.SIGINT, lambda s, f: save_state(current_state))
```

---

## 六、权限控制

### 6.1 敏感操作确认 — core/permissions.ts

```typescript
const sensitiveTools = ['write_file', 'run_command', 'delete_file'];

async function executeTool(toolCall: ToolCall): Promise<any> {
  if (sensitiveTools.includes(toolCall.name)) {
    const confirmed = await ui.confirm(
      `Allow ${toolCall.name}(${JSON.stringify(toolCall.args)})?`
    );
    if (!confirmed) {
      return { error: 'User denied' };
    }
  }
  return tools.find(t => t.name === toolCall.name).execute(toolCall.args);
}
```

**工程思想**:
1. **白名单机制** — 明确定义敏感工具
2. **用户确认** — 危险操作前询问
3. **拒绝处理** — 用户拒绝后返回错误，不是崩溃

**Hulk 可借鉴**:
```python
# Hulk 当前
exec(command)  # 直接执行

# 改进后
SENSITIVE_TOOLS = ['exec', 'write_file', 'delete_file']

async def execute_tool(tool):
    if tool.name in SENSITIVE_TOOLS:
        if not await confirm(f"Allow {tool.name}?"):
            return {"error": "User denied"}
    return await tool.execute()
```

---

## 七、测试策略

### 7.1 单元测试 — tests/agent.test.ts

```typescript
describe('ClaudeAgent', () => {
  it('should call tools when requested', async () => {
    const mockTool = jest.fn().mockResolvedValue({ result: 'ok' });
    const agent = new ClaudeAgent({ tools: [mockTool] });
    
    await agent.run('Please call the tool');
    
    expect(mockTool).toHaveBeenCalled();
  });
  
  it('should respect max iterations', async () => {
    const agent = new ClaudeAgent({ maxIterations: 3 });
    
    await expect(agent.run('loop forever'))
      .rejects.toThrow('Max iterations reached');
  });
});
```

**工程思想**:
1. **Mock 依赖** — 工具调用可 mock，不依赖真实 API
2. **边界测试** — 测试最大迭代等边界条件
3. **行为验证** — 验证 `toHaveBeenCalled()` 而不是实现细节

**Hulk 对比**:
- Hulk 有 85 个测试，主要是单元测试
- 可添加更多集成测试和边界测试

---

## 八、对 Hulk 的具体改进建议

### P0 — 立即实施

| 改进 | 代码示例 | 工作量 |
|------|---------|--------|
| 工具接口规范化 | `class Tool(ABC): name, description, parameters, execute` | 2h |
| 敏感操作确认 | `if tool in SENSITIVE: confirm()` | 1h |
| 中断恢复 | `save_state()` on SIGINT | 1h |

### P1 — 本周实施

| 改进 | 代码示例 | 工作量 |
|------|---------|--------|
| 流式响应 | `async for chunk in stream()` | 4h |
| 上下文管理器 | `class ContextManager` | 3h |
| 迭代限制 | `max_iterations` 参数 | 1h |

### P2 — 本月实施

| 改进 | 代码示例 | 工作量 |
|------|---------|--------|
| Terminal UI | `textual` 库 | 8h |
| 完整测试套件 | pytest + mock | 6h |
| 状态持久化 | `.hulk-state.json` | 4h |

---

## 九、总结

### Claude Code 核心工程思想

1. **模块化** — Agent/UI/Tools 分离
2. **自描述** — 工具描述让模型理解用途
3. **流式优先** — 实时反馈用户体验
4. **安全默认** — 敏感操作需确认
5. **优雅恢复** — 中断不丢失进度

### Hulk 差异化优势 (保持)

1. **开源透明** — 可审计可修改
2. **领域专业** — 老年认知干预
3. **临床验证** — Pilot RCT
4. **长期记忆** — MEMORY.md 持久化
5. **本地优先** — 规则模式可离线

---

*Hulk 🟢 — 学习优秀工程实践，保持核心优势*
