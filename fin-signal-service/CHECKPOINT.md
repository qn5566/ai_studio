# 學習進度存檔與交接紀錄 (Checkpoint)

**存檔時間**：2026-11-25 23:53 (Taipei Time)  
**重大里程碑**：🎉 **第 11 課「有依據的財報問答（RAG Citation & Refusal Guard）」TDD 全綠！全專案 23 項測試通過！**

---

## 📍 最新學習進度地圖：11 / 24 課（完成率 45.8%）

```text
【第一階段：Python 與服務測試基礎】（第 1～4 課）➔ 【✅ 全部通關】
【第二階段：模型 API 與結構化輸出】（第 5～8 課）➔ 【✅ 全部通關】

【第三階段：財報 RAG 與品質評估】（第 9～12 課）➔ 【🔥 即將通關第三階段！】
├── ✅ 第 9 課：財報資料與切塊（Financial Chunking & Metadata 來源追溯）
├── ✅ 第 10 課：向量嵌入（Embedding）與向量資料庫檢索（Vector Search & Cosine Similarity）
├── ✅ 第 11 課：有依據的財報問答（RAG Citation 來源頁碼引用 & 資料不足拒答防護）
└── ⏳ 第 12 課：評估與改善 RAG（RAG 檢索評估、混合檢索 Hybrid Search 與 Rerank）👈【下一步！】
```

---

## 🏆 第 11 課完成的核心架構與亮點（面試必聊）

1. **金融問答強型別資料契約 (`FinancialQAResponse`)**：
   - 包含 `answer`, `is_sufficient`, `source_pages`, `citations`。
   - 杜絕模糊不清的回答，精準標記引用的 PDF 頁碼。

2. **拒答防護機制（Confidence / Refusal Guard）**：
   - 設定相似度安全門檻（`min_similarity_threshold: float = 0.6`）。
   - 當使用者提問與財報無關或檢索分數過低時，系統立即觸發防護，回傳 `is_sufficient=False` 與「資料不足無法回答」，**徹底杜絕大模型憑空捏造的幻覺**。

3. **測試與工程品質**：
   - 全專案 **23 項單元與整合測試全數通過（23 passed in 2.20s）**。
   - Ruff 檢查 0 Error 100% 通過。
