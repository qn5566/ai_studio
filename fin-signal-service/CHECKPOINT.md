# 學習進度存檔與交接紀錄 (Checkpoint)

**存檔時間**：2026-11-25 00:03 (Taipei Time)  
**重大里程碑**：🎉 **第二階段：模型 API 與結構化輸出（第 5～8 課）圓滿通關！進入第三階段預備！**

---

## 📍 最新學習進度地圖：8 / 24 課（完成率 33.3%）

```text
【第一階段：Python 與服務測試基礎】（第 1～4 課）➔ 【✅ 全部通關】
├── ✅ 第 1 課：執行自動化測試（pytest 基礎與斷言）
├── ✅ 第 2 課：Python 環境與專案設定（.venv、pyproject.toml、Ruff）
├── ✅ 第 3 課：讀懂 Python 與現有測試（Pydantic schemas 與三層架構）
└── ✅ 第 4 課：新增測試與 API 驗證（TDD 紅綠燈實戰：擴充 source 與 target_price）

【第二階段：模型 API 與結構化輸出】（第 5～8 課）➔ 【🎉 今日全數通關！】
├── ✅ 第 5 課：操作 FastAPI 與接入模型 SDK（整合 google-genai 官方 SDK）
├── ✅ 第 6 課：結構化分析結果（response_schema、Pydantic JSON 解析與原文證據驗證）
├── ✅ 第 7 課：錯誤處理與模型模擬測試（指數退避 retry_async_call 與 0 成本 Mock 測試）
└── ✅ 第 8 課：新聞分析基準評估（Benchmark：自動化評估管線，量化比較規則 vs LLM）
```

---

## 🏆 今日核心亮點與深度收穫（面試亮點）

1. **實作高可用非同步重試機制 (`src/fin_signal/retry.py`)**：
   - 區分暫態錯誤（429 限流、網路逾時）與致命錯誤（401 金鑰無效、400 格式錯誤）。
   - 實踐依賴注入（Dependency Injection），透過 `mock_sleep` 讓重試測試在毫秒內瞬間完成，完全不用白白等待。
   - 深入理解 Python 高階型別標註：`Callable[[], Awaitable[T]]`（相當於 Dart 的 `Future<T> Function()` 或 Kotlin 的 `suspend () -> T`）。

2. **打通真實 Gemini 2.5 Flash 結構化輸出並回測 (`src/fin_signal/service.py`)**：
   - 雙軌制切換：`use_llm=False`（規則備援）與 `use_llm=True`（大模型深度理解）。
   - 外掛原文證據鏈核對（`validate_target_price_evidence`），防範 LLM 幻覺將「目前股價」誤判為「目標價」。

3. **打造量化 AI 評估引擎 Benchmark (`src/fin_signal/benchmark.py`)**：
   - 深入理解 `run_benchmark` 函式的架構：
     - 計分器模式（Counters）與高精度計時 `time.perf_counter()`。
     - 自動比對標準答案（Ground Truth），計算情緒準確率、目標價準確率與平均處理延遲（Latency）。
     - 具備金融量化工程師必備的 Trade-off 權衡思維（規則低延遲適合初篩 vs LLM 高準確率適合複雜語意決策）。

4. **測試品質保證**：
   - 全專案 **19 項單元與整合測試全綠通過（19 passed in 2.31s）**。
   - Ruff 程式碼檢查 100% 乾淨（All checks passed）。

---

## 🚀 下一次上課起點：【第三階段：財報 RAG 與品質評估】（第 9～12 課）

當你準備好開始下一階段時，我們將邁入量化 AI 最熱門的核心技術：
- **第 9 課：財報資料處理與 Chunking 切塊（解析上百頁 PDF，保留公司、期間與頁碼）**
- **第 10 課：向量嵌入（Embedding）與向量資料庫檢索（Vector Search）**
- **第 11 課：有依據的財報問答（精準溯源 Citation，杜絕幻覺）**
- **第 12 課：RAG 檢索品質評估與 Rerank 重排序**

---

> 恭喜你！在短短幾堂課內，你已經從完全沒寫過 AI 應用的全端工程師，成功跨越了現代 Python 工程化、Pydantic 強型別約束、TDD 流程、Gemini 結構化輸出、指數重試與自動化 Eval 基準評估！進度非常驚人，隨時準備好就告訴我！
