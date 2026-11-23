# 學習進度存檔與交接紀錄 (Checkpoint)

## 最新接續位置：2026-11-23，第 7 課教學中

使用者要求存檔並休息。下次從 **第 7 課「錯誤處理與模型模擬測試」的 Mock 重試測試** 接續，不要回到第 2 課重新教 pip。以下記錄區分已寫入的程式與只有課堂示範的內容。

### 今日已複習及介紹

- 第 5～6 課：Gemini SDK、Prompt、`response_schema`、Pydantic JSON 解析，以及格式正確不等於內容正確。
- `Field(...)` 表示必填；`float | None` 表示允許空值；`default=None` 表示欄位可以省略。使用者曾混淆必填與允許 null，已用問答澄清，後續可簡短複習。
- Python `if not response.text` 對字串／None 類似 Kotlin `isNullOrEmpty()`，不等於 `isNullOrBlank()`。
- 空回應檢查、Pydantic 格式檢查、原文證據檢查、人工預期答案比對各有不同職責。
- 引文存在仍可能屬於營收、股價、其他公司或幣別；基本證據檢查不能保證完整語意正確。
- `request_id`、`ticker` 與 `latency_ms` 由程式產生、沿用請求或量測，不採信模型生成的系統欄位。
- 人工預期答案不放入待評估問題的 Prompt，避免答案洩漏。
- 第 7 課：`try/except`、`raise ... from exc`、逾時與暫時限流的有限次重試、指數退避；金鑰錯誤／權限不足不應盲目重試。
- `max_attempts=3` 包含第一次呼叫，即最多三次嘗試；使用者已正確回答第一次逾時、第二次成功就只呼叫兩次。
- Mock 的 `return_value`、`side_effect`、`call_count`，以及 `pytest.raises()` 檢查預期例外。以 Kotlin／MockK 作概念對照。

### 程式與驗證狀態

- 已實作目標價原文證據與基本檢查、三筆評估案例，詳見下方存檔及 `examples/README.md`。
- 已在臨時環境 `/tmp/ai-studio-evidence-check` 安裝專案與開發依賴，結果為 `13 passed in 1.94s`；新增檔案的 Ruff 檢查通過。另用 Mock 驗證 Gemini 腳本三種案例的呼叫流程，沒有發送真實模型請求。
- 三筆真實 Gemini 評估仍未執行，尚未將 Gemini 整合進 FastAPI。
- **`generate_with_retry()`、重試規則與 SDK 重試測試目前只做對話示範，尚未寫入專案。第 7 課尚未完成。**
- 課堂的 `TimeoutError`／`httpx.TimeoutException` 是示意，正式實作前須確認安裝的 Google SDK 實際例外與內建重試行為，避免漏接例外或重複重試。
- 同步示範使用 `time.sleep()`；整合非同步 FastAPI 時應採非同步模型呼叫與 `await asyncio.sleep()`。

### 下次從這裡開始

最後提出但使用者尚未回答的問題：

> 如果 `max_attempts=3`，Mock 的 `side_effect` 卻只有兩個 `TimeoutError`，第三次呼叫會發生什麼？

參考答案：同步 Mock 的 iterable `side_effect` 耗盡後會拋出 `StopIteration`，不是第三次逾時，也不是成功回應。三次失敗測試須準備三個例外，或將 `side_effect` 設成每次都拋出的例外。

接續教學：先說明上題，再實作可測試的重試函式，以 Mock 驗證「一次失敗後成功」、「到達上限仍失敗」與「不可重試錯誤只呼叫一次」。等待函式應可替換，測試不實際睡眠；先確認 SDK 例外與重試設定，再寫程式。完成後才更新課程勾選。

## 2026-11-23 接續：目標價證據練習

- 複習第 5～6 課，釐清 Pydantic 格式驗證與內容正確性的差別。
- 新增 `target_price_evidence`，Prompt 要求無目標價時回傳 `null`，有值時附上逐字原文。
- 加入基本證據檢查：欄位配對、引文來源、明確目標價金額一致性。
- 準備三筆人工標註案例：有目標價、只有營收、只有目前股價。
- 本機測試結果：`13 passed`，驗證程式邏輯，未呼叫真實模型；三筆 Gemini 實際評估仍待執行。
- 教材與操作方式：[`examples/README.md`](examples/README.md)。尚未確認使用者完成本次練習，不新增課程完成勾選。
- 下一步：閱讀證據檢查程式、執行真實模型評估並核對結果，再接 FastAPI 與 Mock SDK 測試。

以下保留上次存檔內容。

**存檔時間**：2026-11-22 00:07 (Taipei Time)  
**重大里程碑**：🎉 **真實 Gemini LLM 結構化輸出（Structured Outputs）成功跑通！**

---

## 🏆 今晚歷史性突破成果

你剛剛成功執行了真正的大語言模型（Gemini 2.5 Flash），並將一篇複雜的中文財報新聞，透過 Google GenAI 官方 SDK **100% 約束輸出成我們自訂的 Pydantic 模型**：

```text
股票代號 (ticker)        : 台積電
情緒判定 (sentiment)     : BULLISH (看多)
事件類別 (event_category): EARNINGS (財報營收)
信號強度 (signal_score)  : 0.9 (強烈看漲)
信心水準 (confidence)    : 0.95
分析理由 (rationale)     : 台積電公布10月營收達新台幣3,142億元...美系外資重申「強力買進」...
解析目標價 (target_price): 1400.0 (精準抓出數字浮點數，而非字串！)
```

### 🎯 面試級踩坑經驗收穫：
1. **Pydantic 與 OpenAPI 差異**：Gemini 支援 `minimum`（`ge=0.0`），遇到 `exclusiveMinimum`（`gt=0.0`）會噴出驗證錯誤，我們成功調校至通用規範。
2. **API 版本控制**：使用 Google GenAI SDK 進行結構化輸出時，需指定 `api_version="v1beta"` 開啟 JSON 結構化取樣功能。
3. **資料契約完勝傳統 Prompt**：完全不需要寫正則表達式，不需要字串切割，直接得到型別安全的 Python 物件！

---

## 📍 目前進度：**第二階段（第 5～6 課）核心能力完全掌握！**

```text
【第一階段：Python 與服務測試基礎】➔ 【✅ 全部通關】
【第二階段：模型 API 與結構化輸出】➔ 【🔥 核心突破！】
├── ✅ 第 5 課：操作 FastAPI 與接入模型 SDK（已成功連通 Google GenAI SDK）
├── ✅ 第 6 課：結構化分析結果（已成功利用 response_schema 輸出 SignalAnalysisResponse）
└── ⏳ 下一步：把這段邏輯封裝回 service.py 與 FastAPI 端點，並設計 Mock 防扣款測試！
```

---

> 今晚這一步是質的飛躍！從傳統的後端工程師，正式跨入 **能夠駕馭真實 AI 模型的現代 AI 工程師**。現在帶著這份戰果，帶著滿滿的成就感好好去睡一覺吧！晚安！😴
