# API Keys 配置清单

**创建日期**: 2026-03-14  
**创建者**: Hulk 🟢  
**用途**: 研究任务 API Key 配置追踪

---

## 当前环境状态 (2026-03-14 01:38 UTC)

| Key | 状态 | 用途 | 优先级 |
|-----|------|------|--------|
| `GITHUB_TOKEN` | ✅ 已配置 | GEO 迭代 + GitHub 操作 | - |
| `SERPER_API_KEY` | ✅ 已配置 | 网页搜索 | - |
| `DASHSCOPE_API_KEY` | ❌ **缺失** | L0 质检系统 + 叙事评分 | 🔴 P0 |
| `AZURE_SPEECH_KEY` | ❌ **缺失** | ASR 选型测试 | 🟡 P1 |
| `IFLYTEK_API_KEY` | ❌ **缺失** | ASR 选型测试 | 🟡 P1 |
| `OPENAI_API_KEY` | ❌ **缺失** | ASR 选型测试 (Whisper baseline) | 🟢 P2 |

---

## 阻塞影响

### DASHSCOPE_API_KEY (🔴 P0)
**阻塞任务**:
- L0 标注质检多 Agent 系统真实环境测试
- 叙事评分 Pipeline V0.3 生产运行
- ASR 测试转录 (如使用 Qwen ASR)

**配置方式**:
```bash
# 百炼控制台获取: https://bailian.console.aliyun.com/
export DASHSCOPE_API_KEY="sk-xxxxx"
```

**验证命令**:
```bash
curl -X POST "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.5-plus","input":{"messages":[{"role":"user","content":"test"}]}}'
```

---

### AZURE_SPEECH_KEY (🟡 P1)
**阻塞任务**:
- ASR 选型测试 (Azure Speech 组)

**配置方式**:
```bash
# Azure Portal: https://portal.azure.com/ > Speech Service > Keys and Endpoint
export AZURE_SPEECH_KEY="xxxxx"
export AZURE_SPEECH_REGION="eastasia"  # 或你的区域
```

**验证命令**:
```bash
curl -X POST "https://$AZURE_SPEECH_REGION.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=zh-CN" \
  -H "Ocp-Apim-Subscription-Key: $AZURE_SPEECH_KEY" \
  -H "Content-Type: audio/wav" \
  --data-binary @test.wav
```

---

### IFLYTEK_API_KEY (🟡 P1)
**阻塞任务**:
- ASR 选型测试 (讯飞听见组)

**配置方式**:
```bash
# 讯飞开放平台：https://www.xfyun.cn/
export IFLYTEK_API_KEY="xxxxx"
export IFLYTEK_API_SECRET="xxxxx"
export IFLYTEK_APP_ID="xxxxx"
```

**备注**: 讯飞需要 API Key + Secret + AppID 三元组，签名较复杂

---

### OPENAI_API_KEY (🟢 P2)
**阻塞任务**:
- ASR 选型测试 (Whisper baseline)

**配置方式**:
```bash
# OpenAI Platform: https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-xxxxx"
```

**验证命令**:
```bash
curl https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@test.wav" \
  -F model="whisper-1"
```

---

## 配置后验证步骤

### 1. L0 质检系统测试
```bash
cd /home/node/.openclaw/workspace-hulk/pipeline
python3 l0_quality_system.py --test
```

### 2. ASR 选型测试
```bash
cd /home/node/.openclaw/workspace-hulk/pipeline
python3 asr_evaluation_test.py --run-all
```

**预期输出**: WER/CER 对比报告 + 延迟/成本分析

---

## 获取建议

### 优先级顺序
1. **DASHSCOPE_API_KEY** (🔴 P0) — 立即配置，阻塞最多任务
2. **AZURE_SPEECH_KEY** (🟡 P1) — ASR 测试主力
3. **IFLYTEK_API_KEY** (🟡 P1) — 中文优化 ASR
4. **OPENAI_API_KEY** (🟢 P2) — Baseline 参考

### 成本估算
| 服务 | 免费额度 | 超出后价格 | 测试用量估算 |
|------|----------|------------|--------------|
| DashScope (Qwen) | ¥0 (已配置) | ¥0.02/1K tokens | 50 条测试 ~¥5 |
| Azure Speech | 5 小时/月 | $0.01/min | 50 条 (5 分钟) ~$0.05 |
| 讯飞听见 | 1 小时/月 | ¥0.05/min | 50 条 (5 分钟) ~¥0.25 |
| OpenAI Whisper | 无免费 | $0.006/min | 50 条 (5 分钟) ~$0.03 |

**总测试成本**: <¥10 (一次性)

---

## 安全建议

1. **不要硬编码** API Keys 到代码中
2. **使用环境变量** 或 `.env` 文件 (加入 `.gitignore`)
3. **定期轮换** 长期使用的 Keys
4. **最小权限** 原则：只授予必要权限

---

*此文档由 Hulk 自动生成。配置完成后请通知 Hulk 继续执行阻塞任务。*
