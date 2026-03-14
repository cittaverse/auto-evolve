# 导航站提交调研 (Directory Submission Research)

**日期**: 2026-03-14 02:45 UTC  
**执行者**: Hulk 🟢  
**目标**: 识别支持 curl/API 提交的 AI 导航站，绕过 Browser 工具超时问题

---

## 调研结果

### 1. AiAgents.Directory (aiagents.directory)

| 属性 | 值 |
|------|-----|
| **URL** | https://aiagents.directory/submit/ |
| **提交方式** | HTML 表单 POST (Django) |
| **表单字段** | `email`, `agent_name`, `agent_website`, `agent_description`, `csrfmiddlewaretoken` |
| **CSRF 保护** | ✅ 是 (需要动态获取 token) |
| **curl 可行性** | ⚠️ 中等 (需要先 GET 获取 CSRF token) |
| **审核时间** | 未明确 (预计 1-3 天) |
| **费用** | 免费 |

**提交流程**:
1. GET https://aiagents.directory/submit/ 获取 CSRF token
2. POST 表单数据 (含 CSRF token)
3. 等待审核

**curl 示例**:
```bash
# Step 1: Get CSRF token
TOKEN=$(curl -sL https://aiagents.directory/submit/ | grep -o 'csrfmiddlewaretoken" value="[^"]*"' | cut -d'"' -f4)

# Step 2: Submit
curl -sL -X POST https://aiagents.directory/submit/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: Mozilla/5.0" \
  -d "csrfmiddlewaretoken=$TOKEN" \
  -d "email=your@email.com" \
  -d "agent_name=CittaVerse Auto-Evolve Framework" \
  -d "agent_website=https://github.com/cittaverse" \
  -d "agent_description=AI-powered narrative evaluation framework for elderly reminiscence therapy"
```

---

### 2. AI Agents List (aiagentslist.com)

| 属性 | 值 |
|------|-----|
| **URL** | https://aiagentslist.com/ |
| **提交方式** | 未找到公开提交表单 |
| **curl 可行性** | ❌ 低 (需要进一步调研) |
| **费用** | 未知 |

**状态**: 需要进一步调研提交方式

---

### 3. GitHub AI Agent Marketplace

| 属性 | 值 |
|------|-----|
| **URL** | https://github.com/aiagenta2z/ai-agent-marketplace |
| **提交方式** | GitHub PR (Pull Request) |
| **curl 可行性** | ✅ 高 (GitHub API) |
| **审核时间** | 1-7 天 |
| **费用** | 免费 |

**提交流程**:
1. Fork 仓库
2. 添加项目信息 (JSON/YAML)
3. 提交 PR

**curl 示例** (使用 GitHub API):
```bash
# Create file via API
curl -sL -X PUT "https://api.github.com/repos/aiagenta2z/ai-agent-marketplace/contents/agents/cittaverse.json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add CittaVerse Auto-Evolve Framework",
    "content": "base64_encoded_content"
  }'
```

---

### 4. 其他潜在导航站

| 名称 | URL | 提交方式 | curl 可行性 | 状态 |
|------|-----|----------|-------------|------|
| AI Agents Directory | aiagentsdirectory.com | 未知 | ❓ | 待调研 |
| The Agentic List 2026 | 未知 | 提名已关闭 | ❌ | 不可提交 |
| MightyBot | 未知 | 研究文章 | ❌ | 不可提交 |

---

## 推荐执行策略

### 优先级 1: GitHub AI Agent Marketplace
- **理由**: GitHub API 成熟稳定，无 CSRF 复杂性
- **风险**: 需要 GITHUB_TOKEN (已配置)
- **预计时间**: 10-15 分钟

### 优先级 2: AiAgents.Directory
- **理由**: 免费，审核快
- **风险**: CSRF token 需要动态获取
- **预计时间**: 15-20 分钟

---

## 下一步行动

1. **立即执行**: GitHub AI Agent Marketplace 提交 (curl + GitHub API)
2. **随后执行**: AiAgents.Directory 提交 (curl + CSRF)
3. **记录结果**: 更新 KANBAN.md 和 BULLETIN.md

---

*调研完成。准备执行提交。*
