# AI Agent Marketplace 提交指南

**创建日期**: 2026-03-14  
**执行者**: Hulk 🟢  
**目标**: 将 Auto-Evolve Framework 提交到 AI Agent Marketplace

---

## 目标平台

### DeepNLP AI Agent Marketplace

| 属性 | 值 |
|------|-----|
| **URL** | https://www.deepnlp.org/store/ai-agent |
| **提交方式** | 网站表单 / curl / CLI / Python |
| **审核时间** | 1-3 天 |
| **费用** | 免费 |
| **优势** | 10K+ AI Agent 索引，30+ 分类 |

---

## 提交方式对比

| 方式 | 复杂度 | 推荐度 | 说明 |
|------|--------|--------|------|
| 网站表单 | ⭐ | ✅ 推荐 | 最直观，即时反馈 |
| curl API | ⭐⭐ | ✅ 推荐 | 可脚本化，适合批量 |
| CLI 工具 | ⭐⭐⭐ | 🟡 备选 | 需安装 npm 包 |
| Python SDK | ⭐⭐⭐ | 🟡 备选 | 需安装 pip 包 |

---

## 提交材料准备

### 必需信息

| 字段 | 值 | 状态 |
|------|-----|------|
| **Agent Name** | CittaVerse Auto-Evolve Framework | ✅ |
| **Agent Website** | https://github.com/cittaverse/auto-evolve | ✅ |
| **Agent Description** | Self-evolving AI agent framework with closed-loop iteration (Research→Plan→Execute→Verify→Learn) | ✅ |
| **Category** | Developer Tools / AI Frameworks | ✅ |
| **Email** | cittaverse@gmail.com | ✅ |
| **GitHub Repo** | https://github.com/cittaverse/auto-evolve | ✅ |

### 可选信息

| 字段 | 值 | 状态 |
|------|-----|------|
| **Logo** | GitHub 默认 avatar | ⏳ 待上传 |
| **Demo Video** | 暂无 | ⏳ 可后续补充 |
| **Pricing** | Open Source (Free) | ✅ |
| **API Endpoint** | 暂无 (本地框架) | ⏳ 不适用 |

---

## 提交流程 (网站表单)

### Step 1: 访问提交页面

```
https://www.deepnlp.org/workspace/my_ai_services
```

### Step 2: 填写表单

1. **Agent Name**: `CittaVerse Auto-Evolve Framework`
2. **Agent Website**: `https://github.com/cittaverse/auto-evolve`
3. **Agent Description**: `Self-evolving AI agent framework with closed-loop iteration for GitHub SEO optimization and autonomous project improvement.`
4. **Category**: 选择 `Developer Tools` 或 `AI Frameworks`
5. **Email**: `cittaverse@gmail.com`
6. **GitHub Repo**: `https://github.com/cittaverse/auto-evolve`

### Step 3: 提交并等待审核

- 预计审核时间：1-3 天
- 审核通过后会在 https://www.deepnlp.org/store/ai-agent 展示

---

## 提交流程 (curl API)

### 准备 JSON 数据

```json
{
  "name": "CittaVerse Auto-Evolve Framework",
  "description": "Self-evolving AI agent framework with closed-loop iteration (Research→Plan→Execute→Verify→Learn). Validated with 18+ iterations, 100% success rate.",
  "website": "https://github.com/cittaverse/auto-evolve",
  "github": "https://github.com/cittaverse/auto-evolve",
  "category": "Developer Tools",
  "tags": ["ai-agent", "self-evolution", "github-automation", "geo", "autonomous-systems"],
  "open_source": true,
  "license": "MIT",
  "contact_email": "cittaverse@gmail.com"
}
```

### curl 提交命令

```bash
curl -X POST "https://www.deepnlp.org/api/agent/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CittaVerse Auto-Evolve Framework",
    "description": "Self-evolving AI agent framework with closed-loop iteration",
    "website": "https://github.com/cittaverse/auto-evolve",
    "github": "https://github.com/cittaverse/auto-evolve",
    "category": "Developer Tools",
    "contact_email": "cittaverse@gmail.com"
  }'
```

**注意**: 实际 API endpoint 需通过网站开发者文档确认

---

## 提交后追踪

| 检查项 | 检查时间 | 检查方式 |
|--------|----------|----------|
| 提交确认邮件 | 提交后 1 小时 | 邮箱 |
| 审核状态 | 提交后 24 小时 | 网站后台 |
| 公开展示 | 提交后 3 天 | 搜索平台 |

---

## 备选平台

### AiAgents.Directory

- **URL**: https://aiagents.directory/submit/
- **提交方式**: HTML 表单 (需 CSRF token)
- **状态**: ⏳ 待执行

### AI Agents List

- **URL**: https://aiagentslist.com/
- **提交方式**: 待调研
- **状态**: ⏳ 待调研

---

## 下一步行动

1. ✅ 准备提交材料 (已完成)
2. ⏳ 执行网站表单提交 (需人工操作，因需登录)
3. ⏳ 追踪审核状态 (提交后 24-72 小时)
4. ⏳ 记录收录链接 (更新 KANBAN.md)

---

*创建：2026-03-14 | GEO Iteration #19*
