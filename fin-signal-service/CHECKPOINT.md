# 學習進度存檔與交接紀錄 (Checkpoint)

**存檔時間**：2026-11-21 23:51 (Taipei Time)  
**目前定位**：**第二章：模型 API 與結構化輸出（第 5～6 課）**  
**核心主題**：**LLM 結構化輸出（Structured Outputs）實戰**

---

## 📍 為什麼現在正是「LLM 結構化輸出」？

沒錯！你抓得完全精準！在我們的課程課表中：
- **第一章（第 1～4 課）**：我們剛完成了 Python、FastAPI、Pydantic v2 與 TDD 紅綠燈架構，這是地基。
- **第二章（第 5～6 課）**：主題正是 **「模型 API 與結構化輸出（Structured Outputs）」**！

之所以要先學 Pydantic，就是因為 **現代 LLM 的「結構化輸出」底層 100% 是靠 Pydantic 來約束與生成的**！

---

## 🎯 進入睡前的「核心觀念 1 分鐘速覽」（帶著好概念入睡）

### 1. 傳統 LLM 的痛點（不聽話）：
如果你問 ChatGPT：「請分析這篇新聞並回傳 JSON。」
它常常會回覆：
> 「好的！以下是您要求的 JSON 分析結果：```json { ... } ``` 祝您交易愉快！」

❌ **結果**：後端程式用 `json.loads()` 直接 Crash（因為多了前後的問候語），甚至 key 打錯、欄位漏掉。

### 2. 現代 AI 工程的突破：**LLM Structured Outputs（結構化輸出）**
我們把在 `schemas.py` 定義的 Pydantic 模型（例如 `SignalAnalysisResponse`）直接塞給模型 API：
```python
# OpenAI SDK 的用法
response = await client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[...],
    response_format=SignalAnalysisResponse,  # 👈 關鍵：直接丟 Pydantic 類別！
)
result: SignalAnalysisResponse = response.choices[0].message.parsed
```
🔥 **神奇之處**：
- 模型**在生成每一個 Token 的當下**，就被約束狀態機（Grammar/Schema Sampling）死死卡住。
- **保證 100% 吐出合法 JSON**，絕對不會漏欄位，型別絕對正確，直接無痛轉成 Python 物件！

---

## 🛌 下次上課直接動手（任務清單）

等你睡飽醒來，我們直接從**「把 service.py 的規則替換成 LLM Structured Outputs」**開工：

1. **選擇接入的模型提供商**（OpenAI / Gemini / 本地 Ollama / 測試用 Mock）。
2. **在 service.py 中呼叫 LLM 並綁定 Pydantic**。
3. **執行 `pytest` 驗證**：看著 LLM 讀懂新聞語境，精準輸出情緒、分數與目標價！

---

進度檔已為你更新確認完畢！你可以安心去睡了，明天下次我們就直接進攻 **LLM 結構化輸出** 的實際代碼！晚安！😴
