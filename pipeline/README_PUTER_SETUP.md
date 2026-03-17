# LLM API 替代方案说明

## 现状

经过调研，**完全免注册、免 API Key 的 LLM API 在 2026 年几乎不存在**。原因：
- 计算成本高，服务商需要防止滥用
- 需要基本的身份验证来配额管理

## 可行方案对比

| 方案 | 注册要求 | 免费额度 | 中文支持 | 推荐度 |
|------|---------|---------|---------|--------|
| **Groq** | 邮箱注册（1 分钟） | 500k tokens/天 | ✅ Qwen | ⭐⭐⭐⭐⭐ |
| **OpenRouter** | 邮箱注册（2 分钟） | 20 req/min, 50 req/day | ✅ Qwen | ⭐⭐⭐⭐ |
| **GitHub Models** | GitHub 账号 | 14,400 req/天 | ✅ | ⭐⭐⭐⭐ |
| **Google AI Studio** | Google 账号 | 250k tokens/min | ❌ Gemini | ⭐⭐⭐ |
| **Puter.js** | 浏览器登录 | 免费 | ✅ | ⭐⭐ (仅 JS) |
| **本地 Mock** | 无 | 无限 | ✅ | ⭐⭐⭐ (仅测试) |

---

## 推荐方案：Groq（最快注册）

### 为什么选 Groq
- ✅ **注册最快**：只需邮箱，无需信用卡
- ✅ **额度充足**：500k tokens/天，足够测试
- ✅ **中文支持好**：Qwen3-32b 原生支持中文
- ✅ **速度快**：LPU 硬件，300+ tokens/秒

### 注册步骤（1 分钟）
1. 访问 https://console.groq.com
2. 点击 "Sign Up"，用邮箱注册
3. 验证邮箱
4. 进入 API Keys 页面，创建新 Key
5. 复制 Key，添加到环境变量：
   ```bash
   export GROQ_API_KEY="gsk_..."
   ```

---

## 当前状态

### 已实现
- ✅ `pipeline/puter_llm_client.py` - Puter LLM 客户端（支持降级到 Mock）
- ✅ `pipeline/judge_agent_puter.py` - 评委 Agent（Puter 版）
- ✅ 自动降级：API 不可用时自动切换到 Mock 模式

### 测试结果
```
[Sensory] 完成：75.0 分 (置信度：0.80)
[Context] 完成：75.0 分 (置信度：0.80)
[Emotion] 完成：75.0 分 (置信度：0.80)
[Coherence] 完成：75.0 分 (置信度：0.80)
一致性判定：✅ 一致
```

**说明**：当前使用 Mock 模式，分数为模拟值。

---

## 下一步建议

### 方案 A：用 Groq 跑真实测试（推荐）
1. V 注册 Groq（1 分钟）
2. 获取 API Key
3. 我修改代码集成 Groq
4. 跑真实 LLM 评分

### 方案 B：继续用 Mock 推进其他工作
- 先跑通叙事评分 v0.5 其他模块
- 等 API Key 配置后再集成真实 LLM

### 方案 C：本地运行开源模型
- 需要安装 Ollama / llama.cpp
- 需要下载模型（几 GB）
- 适合长期开发，不适合快速测试

---

## 决策建议

**建议选方案 A**：
- Groq 注册成本极低（1 分钟）
- 真实 LLM 评分才能验证算法有效性
- Mock 只能测试流程，不能验证质量

**如果 V 暂时不想注册**：
- 先用 Mock 跑通其他模块
- 知乎文章可以先发（用 Mock 数据说明）
- 等 API Key 到位后再补真实测试

---

*Hulk 🟢 - 2026-03-17*
