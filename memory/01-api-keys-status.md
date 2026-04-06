# API Key 当前状态

**最后更新**: 2026-03-30 04:30 UTC

---

## DASHSCOPE_API_KEY ✅

```bash
DASHSCOPE_API_KEY=sk-sp-4bad5c0618764aa5a52740dcc995421a
OPENAI_BASE_URL=https://coding.dashscope.aliyuncs.com/v1
```

**状态**: ✅ 正常 (03-29 04:30 UTC 修复)  
**测试**: ✅ API 响应正常  
**可用模型**: qwen3.5-plus, qwen3-max-2026-01-23, qwen3-coder-next, qwen3-coder-plus, glm-5, glm-4.7, kimi-k2.5, MiniMax-M2.5

**历史记录**:
- 03-13 前: ✅ 正常
- 03-13 ~ 03-28: ❌ 401 错误 (旧 key 失效)
- 03-29 04:30 UTC: ✅ V 提供新 key，修复

---

## Serper API 🟡

**状态**: 🟡 Credits 耗尽  
**Fallback**: ddg-search 可替代  
**需补充**: 是

---

## Azure Speech API ❌

**状态**: ❌ 未配置  
**用途**: ASR 对比测试  
**需补充**: 是

---

## iFlytek API ❌

**状态**: ❌ 未配置  
**用途**: ASR 对比测试  
**需补充**: 是

---

## 密钥安全原则

1. **绝不写入 Git 追踪文件** — 只存在于环境变量或 GitHub Secrets
2. **文档中只写占位符** — `$VAR` 或 `[REDACTED]`，不写真实值
3. **轮换触发条件**:
   - 发现密钥出现在 Git 历史中
   - 发现密钥出现在公开位置
   - 密钥被意外打印到日志
4. **事故响应**:
   - 立即从文件删除 → `[REDACTED]`
   - `git filter-branch` 重写历史
   - `git push --force`
   - 通知 V 轮换密钥
   - 添加 `.gitignore` 规则

---

*最后更新：2026-03-30 04:45 UTC*
