# 2026-04-03 NLP/LLM 方法论研究日志

**任务来源**: cron:94c66392-4878-4193-b5bc-e50cf109f722 hulk-📚-储备 - 方法论

**研究时间**: 2026-04-03 21:47 UTC

---

## 检索策略

1. **首选工具**: web_search → 遇到 DuckDuckGo bot-detection，切换 browser
2. **主要来源**: ACL Anthology (https://aclanthology.org/)
3. **搜索词**:
   - `memory narrative LLM`
   - `neurosymbolic memory reasoning`
   - `elderly life review reminiscence`

4. **失败尝试**:
   - Google Scholar: 触发反爬虫，显示 "your computer or network may be sending automated queries"
   - web_fetch: 解析到 internal IP 被阻止
   - DuckDuckGo: bot-detection challenge

---

## 检索到的关键论文

### 高相关性（直接应用于 VSNC）
1. **Amory** (EACL 2026) - 叙事驱动记忆框架
2. **HiAgent** (ACL 2025) - 层次化工作记忆管理
3. **TReMu** (ACL Findings 2025) - 神经符号时间推理

### 中相关性（参考思路）
4. **CSD** (ACL 2023) - 认知刺激对话系统（中文，针对认知障碍）

### 低相关性（浏览但未深入）
- Symbolic Working Memory (EMNLP 2024)
- Metagent-P (ACL Findings 2025)
- 多篇神经符号推理论文（聚焦数学/逻辑，非记忆/叙事）

---

## 排除的方向

1. **纯数学推理的神经符号方法**: LINC 等论文聚焦逻辑推理，与回忆叙事关联弱
2. **认知障碍专用系统**: CSD 虽然相关，但 VSNC 目标用户是健康老年人
3. **交互式戏剧/游戏**: 部分论文聚焦 NPC 对话，与回忆疗法场景不同

---

## 未完成的检索

由于时间限制，以下方向未深入：
- EMNLP 2025、NAACL 2026 的最新论文
- NeurIPS、ICLR 中的记忆/推理相关论文
- 中文论文和国内研究团队成果（如清华、北大、中科院）
- 产业界技术报告（Google、Meta、Anthropic 等）

---

## 下一步建议

1. 扩展检索到 EMNLP/NAACL/NeurIPS/ICLR
2. 获取 Amory/HiAgent/TReMu 的 PDF 全文，深入方法细节
3. 检查 HiAgent 的开源代码实现
4. 在 L0 原型上验证叙事记忆组织的可行性

---

## 研究产出

- 正式报告：`research/2026-04-03-nlp-llm-methodology-vsnc.md`
- 验证等级：V1（单来源确认）
- 状态：Ready for handoff → Core
