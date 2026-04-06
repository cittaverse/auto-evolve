# DASHSCOPE_API_KEY 修复记录

**修复时间**: 2026-03-29 04:30 UTC  
**修复方式**: V 提供新 API Key  
**验证状态**: ✅ 测试通过

---

## 问题历史

| 时间 | 状态 | 备注 |
|------|------|------|
| 03-13 前 | ✅ 正常 | 初始配置 |
| 03-13 ~ 03-28 | ❌ 401 错误 | Key 失效 (`sk-sp-4bad5c8618764aa5a52748dc9965421a`) |
| 03-29 04:30 UTC | ✅ 已修复 | V 提供新 Key |

---

## 当前配置

```bash
DASHSCOPE_API_KEY=sk-sp-4bad5c0618764aa5a52740dcc995421a
OPENAI_BASE_URL=https://coding.dashscope.aliyuncs.com/v1
```

**注意**: 有别于百炼控制台，使用 Coding Plan 专属 Base URL。

---

## 可用模型

| 品牌 | 模型 | 能力 |
|------|------|------|
| 千问 | qwen3.5-plus | 文本生成、深度思考、视觉理解 |
| 千问 | qwen3-max-2026-01-23 | 文本生成、深度思考 |
| 千问 | qwen3-coder-next | 文本生成 |
| 千问 | qwen3-coder-plus | 文本生成 |
| 智谱 | glm-5 | 文本生成、深度思考 |
| 智谱 | glm-4.7 | 文本生成、深度思考 |
| Kimi | kimi-k2.5 | 文本生成、深度思考、视觉理解 |
| MiniMax | MiniMax-M2.5 | 文本生成、深度思考 |

---

## 验证记录

**测试命令**:
```bash
curl -s -X POST "https://coding.dashscope.aliyuncs.com/v1/chat/completions" \
  -H "Authorization: Bearer sk-sp-4bad5c0618764aa5a52740dcc995421a" \
  -d '{"model": "qwen3.5-plus", "messages": [{"role": "user", "content": "Hello, this is a test."}]}'
```

**测试结果**: ✅ API 响应正常

---

## 解锁任务

- [x] L0 真实测试 (5 个老年叙事样本)
- [ ] GEO 内容生成 (不再 timeout)
- [ ] v0.7.0 live LLM validation
- [ ] PyPI 发布流程

---

**此文件用于持久化记录，避免 HEARTBEAT.md 截断导致重复报告。**

*Created: 2026-03-30 04:35 UTC*
