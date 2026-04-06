---
name: sensitive_file_write
enabled: true
event: pre_file_write
conditions:
  - field: file_path
    operator: regex_match
    pattern: "\\.(env|pem|key|secret|credentials)$"
action: warn
timeout: 5
---
⚠️ **敏感文件写入检测**

检测到正在写入敏感文件：`{file_path}`

**风险**: 可能包含密码、API Key 等敏感信息。

**建议**:
- 使用环境变量存储敏感信息
- 添加到 `.gitignore`
- 使用加密存储

---
name: gitignore_write
enabled: true
event: pre_file_write
conditions:
  - field: file_path
    operator: equals
    pattern: ".gitignore"
action: warn
timeout: 5
---
ℹ️ **GitIgnore 文件写入**

检测到正在修改 `.gitignore`

**建议检查**:
- 是否包含了敏感文件模式 (`.env`, `*.pem`, `*.key`)
- 是否包含了构建产物 (`node_modules/`, `__pycache__/`)
- 是否包含了 IDE 配置 (`.vscode/`, `.idea/`)

---
name: overwrite_protection
enabled: true
event: pre_file_write
conditions:
  - field: old_content
    operator: contains
    pattern: "API_KEY"
action: warn
timeout: 5
---
⚠️ **覆盖保护警告**

检测到正在覆盖包含 API_KEY 的文件！

**风险**: 可能意外删除敏感配置。

**建议**:
- 先备份原文件
- 确认新内容不包含敏感信息
- 使用版本控制
