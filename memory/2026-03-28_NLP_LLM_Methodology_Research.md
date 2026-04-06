# 研究日誌：NLP/LLM 方法论 2025-2026 (VSNC/L0 技術評估)

**日期**: 2026-03-28  
**研究類型**: 技術情報掃描 + 深度文獻分析  
**任務來源**: cron:94c66392-4878-4193-b5bc-e50cf109f722

---

## 搜索策略

### 初始搜索詞
1. `2025 2026 latest NLP LLM methodologies memory narrative therapy elderly care`
2. `2025 2026 long context LLM autobiographical memory personal modeling techniques`
3. `2025 2026 Chinese NLP elderly reminiscence therapy life review AI`

### 工具使用
- **ddg-search CLI**: 初始搜索 (遭遇 rate limit)
- **browser tool**: 訪問 arXiv、項目頁面、會議網站
- **web_fetch**: 嘗試但被 VPN fake-IP 阻斷 (改用 browser)

---

## 查閱過的主要來源

| 來源 | 類型 | 關鍵信息 |
|------|------|----------|
| em-llm.github.io | 項目頁面 | EM-LLM 架構詳解、性能對比圖 |
| arXiv:2407.09450 | ICLR 2025 論文 | EM-LLM 技術細節 |
| arXiv:2510.07925 | 預印本 (2025-10) | 持久化記憶 + 用戶畫像框架 |
| arXiv:2508.02232 | 預印本 (2025-08) | Eye2Recall 眼動 + LLM 回憶交互 |
| EMNLP 2025 Findings | 會議論文集 | 阿茲海默症早期檢測 LLM 應用 |
| Trends in Cognitive Sciences 2025 | 期刊 | 記憶敘事 NLP 分析方法論 |
| TACL 2025 | 系統回顧 (240+ 論文) | 痴呆症 NLP 應用全景 |

---

## 排除的方向

1. **純 RAG 優化**：EM-LLM 已證明超越傳統 RAG，且 RAG 缺乏事件分段能力
2. **純微調方案**：EM-LLM 無需微調，更适合快速集成
3. **通用長上下文模型**：專項記憶架構 (如 EM-LLM) 在敘事場景更優
4. **純醫療診斷應用**：合規風險高，優先聚焦健康用戶回憶療法

---

## 當前假設

1. EM-LLM 的事件分段機制可直接應用於用戶人生故事組織
2. 持久化用戶畫像框架可與現有 abao-profile 系統互補
3. 中文場景適配需要額外測試 (論文主要為英文)
4. 多模態交互 (眼動追蹤) 是差異化方向，但硬件成本需評估

---

## 下一步準備驗證

1. **EM-LLM 代碼審計** (Core 職責)
   - 檢查中文 tokenization 支持
   - 評估與現有 LLM 棧兼容性
   - 估算集成工作量

2. **用戶數據測試** (需 V 決策)
   - 使用現有阿寶會話數據測試事件分段效果
   - 對比人類標註的事件邊界

3. **專利檢索** (可選)
   - 檢查 EM-LLM 相關專利佈局
   - 評估自主專利申請機會

---

## 研究产出

- **正式報告**: `/home/node/.openclaw/workspace-hulk/research/NLP_LLM_Methodology_2025_2026_VSNC_L0.md`
- **HANDOFF**: `/home/node/.openclaw/workspace/HANDOFF.md` (交 Core 技術評估)

---

## 備註

- 研究過程中遭遇 ddg-search rate limit 和 web_fetch VPN 阻斷，改用 browser tool 成功獲取內容
- EM-LLM 是華為 Noah's Ark Lab + UCL 合作項目，學術背書強
- Eye2Recall 是中國團隊 (第一作者 Lei Han)，可能有中文場景經驗可合作
