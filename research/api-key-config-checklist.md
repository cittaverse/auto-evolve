# API Key 配置清单

**日期**: 2026-03-14 05:48 UTC  
**执行者**: Hulk 🟢  
**目的**: 解锁 L0 质检系统真实环境测试 + ASR 选型测试

---

## 必需 API Keys

### 1. DASHSCOPE_API_KEY (百炼) 🔴 高优先级

| 属性 | 值 |
|------|-----|
| **用途** | L0 标注质检系统、叙事评分 Pipeline、内容生成 |
| **服务商** | 阿里云百炼 (qwen3.5-plus) |
| **配置位置** | OpenClaw 环境变量 / `.env` 文件 |
| **获取方式** | https://bailian.console.aliyun.com/ |
| **影响** | 阻塞 L0 真实环境测试、GEO 内容生成 |

**配置命令**:
```bash
# 方式 1: 临时环境变量 (当前会话)
export DASHSCOPE_API_KEY="sk-sp-xxxxxxxxxxxxxxxx"

# 方式 2: 写入 .env 文件 (持久化)
echo 'DASHSCOPE_API_KEY=sk-sp-xxxxxxxxxxxxxxxx' >> ~/.openclaw/.env

# 方式 3: OpenClaw Gateway 配置
openclaw gateway config.patch --env.DASHSCOPE_API_KEY=sk-sp-xxxxxxxxxxxxxxxx
```

**验证方式**:
```bash
# 测试 API Key 是否有效
python3 -c "import dashscope; dashscope.api_key='sk-sp-xxx'; print(dashscope.Generation.call('qwen3.5-plus', 'Hello'))"
```

---

### 2. Azure Speech API Key 🟡 中优先级

| 属性 | 值 |
|------|-----|
| **用途** | ASR 选型测试 (老年语音识别基准) |
| **服务商** | Microsoft Azure Speech-to-Text |
| **配置位置** | `pipeline/asr_evaluation_test.py` 或环境变量 |
| **获取方式** | https://portal.azure.com/ → Cognitive Services → Speech |
| **影响** | 阻塞 ASR 选型测试 (P5 技术壁垒) |

**配置命令**:
```bash
export AZURE_SPEECH_KEY="xxxxxxxxxxxxxxxx"
export AZURE_SPEECH_REGION="eastasia"  # 或你的区域
```

**免费额度**: 每月 500 分钟 (足够测试)

---

### 3. 讯飞听见 API Key 🟡 中优先级

| 属性 | 值 |
|------|-----|
| **用途** | ASR 选型测试 (中文老年语音优化) |
| **服务商** | 讯飞开放平台 |
| **配置位置** | `pipeline/asr_evaluation_test.py` 或环境变量 |
| **获取方式** | https://www.xfyun.cn/ → 控制台 → 听写 |
| **影响** | 阻塞 ASR 选型测试 (P5 技术壁垒) |

**配置命令**:
```bash
export IFLYTEK_APP_ID="xxxxxxxx"
export IFLYTEK_API_KEY="xxxxxxxxxxxxxxxx"
export IFLYTEK_API_SECRET="xxxxxxxxxxxxxxxx"
```

**免费额度**: 每日 500 条 (足够测试)

---

## 可选 API Keys

### 4. OpenRouter API Key (备用)

| 属性 | 值 |
|------|-----|
| **用途** | 备用 LLM (如百炼不可用) |
| **服务商** | OpenRouter |
| **状态** | ✅ 已配置 (`sk-or-v1-7c71...`) |
| **备注** | 当前主要使用百炼，此 Key 作为备用 |

---

## 配置优先级

| 优先级 | API Key | 阻塞任务 | 建议完成时间 |
|--------|---------|----------|--------------|
| 🔴 P0 | DASHSCOPE_API_KEY | L0 质检系统、GEO 内容生成 | **今日 (03-14)** |
| 🟠 P1 | Azure Speech API Key | ASR 选型测试 | 03-15 |
| 🟠 P1 | 讯飞听见 API Key | ASR 选型测试 | 03-15 |

---

## 配置后验证步骤

### L0 质检系统验证
```bash
cd /home/node/.openclaw/workspace-hulk/pipeline
python3 l0_quality_system.py --test --samples=5
```

**预期输出**:
- 5 条样本完成评分
- 4 个评委 Agent + 1 个仲裁 Agent 正常运行
- 输出一致性报告 (Kappa 系数)

### ASR 评估测试验证
```bash
cd /home/node/.openclaw/workspace-hulk/pipeline
python3 asr_evaluation_test.py --samples=10 --services=azure,iflytek,whisper
```

**预期输出**:
- WER/CER 对比报告
- 延迟测试结果
- 成本估算

---

## 安全提醒

1. **不要将 API Key 提交到 Git** — 已加入 `.gitignore`
2. **使用环境变量或 `.env` 文件** — 避免硬编码
3. **定期轮换 Key** — 建议每 90 天更新
4. **监控用量** — 设置预算告警

---

## V 行动项

- [ ] **今日**: 配置 DASHSCOPE_API_KEY (百炼控制台)
- [ ] **03-15**: 配置 Azure Speech API Key (Azure Portal)
- [ ] **03-15**: 配置讯飞听见 API Key (讯飞控制台)
- [ ] **配置后**: 通知 Hulk 执行验证测试

---

*配置清单已就绪。完成配置后，L0 和 ASR 测试将自动解锁。*
