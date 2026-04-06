# Research Log: NLP/LLM Methodology for VSNC (2026-03-26)

**任务**: cron:94c66392-4878-4193-b5bc-e50cf109f722  
**执行者**: Hulk 🟢  
**时间**: 2026-03-26 21:46 UTC

---

## 检索过程

### 尝试 1: web_search (Gemini API)
- **结果**: 失败
- **错误**: `API Key not found`
- **应对**: 改用 browser 直接访问学术数据库

### 尝试 2: ddg-search CLI
- **命令**: `/home/node/.openclaw/workspace/node_modules/.bin/ddg-search -f compact "NLP LLM narrative memory elderly AI 2025 2026 research"`
- **结果**: 失败
- **错误**: `Anti-bot detection triggered on first request`
- **应对**: 改用 browser

### 尝试 3: arXiv 搜索
- **URL**: `https://arxiv.org/search/?query=reminiscence+therapy+AI+elderly`
- **结果**: 无匹配结果
- **原因**: 该主题在 arXiv 上论文较少，多为医学/心理学领域

### 尝试 4: ACL Anthology 搜索（成功）
- **搜索词**:
  - `life story generation LLM` → ~3,060 结果
  - `dementia speech language LLM 2024 2025` → ~104 结果
  - `autobiographical memory narrative assessment LLM` → ~164 结果
- **关键发现**:
  - GuideLLM (NAACL 2025)
  - PRIME (EMNLP 2025)
  - Methodological Biases in Narrative Flow (CoNLL 2025)
  - Can LLMs Help Recollect (CLiC-it 2025)

---

## 排除的方向

1. **纯技术论文**（如模型架构改进）：与 VSNC 产品应用距离较远
2. **纯医学诊断研究**：涉及医疗边界，需法务确认后才可深入
3. **非英文研究**：中文 NLP 在老年叙事方向的研究较少，暂以英文为主

---

## 假设与推断

1. **GuideLLM 三要素可直接迁移**：基于摘要描述，该框架具有通用性，但中文语境下的共情表达需适配
2. **PRIME dual-memory 架构适用于 L0**：当前 L0 的 memory/日志 + USER.md 结构与 episodic/semantic 记忆有天然对应
3. **Sequentiality 指标需谨慎使用**：CoNLL 2025 论文明确指出方法学偏差，建议采用多维评估

---

## 下一步验证计划

1. **获取论文全文**：尝试下载 PDF，补充方法细节
2. **代码复现性检查**：查看论文是否开源代码
3. **中文语料收集**：验证英文结论的跨语言适用性
4. **与 V 确认优先级**：短期/中期/长期建议的落地顺序

---

## 工具限制记录

- `web_search`：Gemini API Key 不可用
- `ddg-search`：反爬虫检测触发
- `web_fetch`：Blocked（解析到私有 IP）
- `browser`：可用，但需注意会话超时

**建议**：在 TOOLS.md 中更新 fallback 策略，明确当 web_search 失败时的替代方案
