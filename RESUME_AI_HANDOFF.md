# 履歷更新參考：金融 AI 應用開發實作

整理日期：2026-11-26。以下根據 `fin-signal-service` 目前原始碼整理，提供給協助修改履歷的 AI 使用。

## 給履歷 AI 的任務

請閱讀我現有的履歷，將以下技能與專案經驗融入適當位置，維持既有格式、語言及篇幅。請直接提出可替換的履歷文字，並說明適合放在哪個區塊。

- 這是個人學習與實作專案，請放在「個人專案／專案作品」或「技術技能」，不要改寫成任職公司的正式產品成果。
- 以「實作、串接、建立」描述可確認的經驗；不要自行提升為「精通、專家、大規模正式環境經驗」。
- 若履歷已有 Android、PHP、MySQL 等工程經驗，可將本專案呈現為延伸至 Python 後端與 AI 應用工程的實作經驗；既有資歷與年資請以原履歷為準。
- 不要加入未提供的商業效益、模型準確率、使用人數、吞吐量或交易報酬。
- 優先挑選與目標職缺相關的 3～4 個重點，避免把所有關鍵字塞進履歷。

## 專案概要

**專案名稱：金融新聞分析服務與財報檢索原型（fin-signal-service）**

以 Python 開發金融文本分析服務，提供新聞情緒、事件類型、信號分數與分析師目標價的結構化輸出。分析服務支援規則模式與可選的 Gemini 模式，另實作財報文字切塊、向量相似度檢索、來源引用與資料不足拒答的基礎流程。

專案定位為 AI 應用工程實作，包含 API、資料驗證、外部模型串接、錯誤處理及自動化測試。新聞分析服務與財報檢索模組目前各自實作，尚未整合成完整上線產品。

## 已有程式碼支持的技能與經驗

| 能力 | 目前實作內容 | 技術／關鍵字 |
| --- | --- | --- |
| Python API 開發 | 建立健康檢查與單筆新聞分析端點，分離路由、資料模型與分析邏輯 | Python、FastAPI、Uvicorn、async/await |
| 資料契約與驗證 | 定義請求與回應模型、情緒／事件列舉、欄位長度與分數範圍、可空目標價欄位 | Pydantic v2、Type Hints、Schema Validation |
| LLM 串接 | 以 Google Gen AI SDK 呼叫 Gemini 2.5 Flash，要求 JSON 與指定 Schema，再解析驗證回應 | Gemini API、Structured Outputs、Prompt Design |
| 非同步服務整合 | 使用 `asyncio.to_thread` 將同步 SDK 呼叫移至執行緒，搭配非同步服務介面 | asyncio、同步／非同步整合 |
| 原文證據驗證 | 檢查目標價與引文是否成對、引文是否存在於新聞、明確目標價數字是否一致 | Evidence Validation、資訊抽取 |
| 錯誤處理 | 區分可重試／不可重試錯誤，實作有限次重試及指數退避 | Retry、Exponential Backoff |
| 財報文字處理 | 依頁面與段落切塊，保留公司代號、財報期間、頁碼及區塊識別碼，支援文字重疊 | Chunking、Metadata、來源追溯 |
| 基礎向量檢索 | 自行實作記憶體向量儲存、Cosine Similarity 與 Top-K 檢索 | Vector Search、Cosine Similarity、Top-K |
| 檢索引用與拒答 | 組合檢索段落與引用頁碼；無結果或相似度不足時回傳資料不足 | RAG 基礎、Citations、Refusal Guard |
| 自動化測試 | 撰寫 API、資料驗證、證據驗證、重試、LLM Mock 與檢索流程測試 | pytest、pytest-asyncio、HTTPX、Mock |
| 評估流程 | 建立三筆人工預期新聞案例，以及規則／LLM 的情緒、目標價與延遲評估程式 | Benchmark、人工標註案例、Latency |

## 可直接改寫進履歷的版本

### 技術技能：精簡版

Python、FastAPI、Pydantic、非同步程式設計、Gemini API 串接、LLM 結構化輸出、原文證據驗證、RAG 基礎實作、向量相似度檢索、pytest／Mock 自動化測試。

### 個人專案：建議版

**金融新聞分析服務與財報檢索原型｜Python、FastAPI、Gemini、Pydantic、pytest**

- 以 FastAPI 與 Pydantic 建立金融新聞分析 API，定義情緒、事件分類、信號分數與目標價等結構化資料契約。
- 串接 Gemini 2.5 Flash，實作 JSON Schema 輸出、目標價原文證據驗證，以及有限次重試與指數退避。
- 建立財報文字切塊與記憶體向量檢索原型，保留來源頁碼，支援 Top-K 檢索、段落引用及低相似度拒答。
- 使用 pytest、HTTPX 與 Mock 驗證 API、模型回應、錯誤處理及檢索流程，並建立固定新聞案例的評估程式。

### 履歷空間有限：兩點版

- 以 Python／FastAPI 開發金融新聞分析服務，串接 Gemini 結構化輸出，加入 Pydantic 驗證、原文證據核對與重試機制。
- 實作含來源頁碼與拒答機制的財報檢索原型，並以 pytest／Mock 驗證 API、LLM 串接與核心處理流程。

## 改寫時必須保留的實作界線

1. **API 預設仍採規則模式。** Gemini 已在分析服務層實作，可透過 `use_llm=True` 啟用；目前 FastAPI 啟動時未啟用此模式。不要寫成公開 API 已預設使用 Gemini。
2. **財報模組是檢索與回答組合原型。** 目前由呼叫端提供向量，以字串組合檢索段落作答，尚未串接真實 Embedding 模型與 LLM 回答生成；`query` 文字尚未用於生成查詢向量。
3. **向量儲存為自製記憶體結構。** 沒有使用或部署 Pinecone、Qdrant、Milvus、FAISS 等產品，也沒有持久化向量索引。
4. **切塊輸入是已取得的逐頁文字。** 不應寫成已完成 PDF 解析、OCR 或自動抓取財報的完整資料管線。
5. **相似度門檻是拒答規則。** 不代表已驗證答案正確、已校準模型信心，或能完全消除幻覺；原文證據驗證也有語意與幣別等限制。
6. **評估程式與案例不等於已驗證的成效。** 目前沒有可供履歷引用的完整模型比較報告；不要宣稱特定準確率或改善百分比。三筆案例也不足以代表整體品質。
7. **未完成項目不要列成既有能力成果。** 包括 LangGraph／多 Agent、模型微調、LoRA、PyTorch 訓練、量化交易回測、Docker 服務部署與正式環境維運。
8. **靜態教材網站發布不等於 API 部署。** 專案內 GitHub Pages 工作流程用途為發布學習教材，不能據此宣稱已建立服務部署或測試 CI/CD。
9. **信號分數不等於交易績效。** 尚無實盤、樣本外回測、收益或風險調整報酬的驗證。

## 驗證紀錄與原始碼依據

- `CHECKPOINT.md` 記載 2026-11-25 曾有 23 項測試通過；這是歷史紀錄。
- 2026-11-26 整理本文件時嘗試執行 `python3 -m pytest tests -q`，目前環境缺少 `google-genai`，在測試收集階段失敗，因此本次未重新確認全套測試通過。履歷建議寫「建立自動化測試」，暫不引用測試通過數量。
- 本次沒有呼叫真實 Gemini API，也未重新執行模型品質評估。
- `LEARNING_PROGRESS.md` 與其他說明文件有部分舊紀錄；判斷已實作內容時，優先核對以下程式碼。

| 原始碼 | 可核對的內容 |
| --- | --- |
| `fin-signal-service/src/fin_signal/main.py` | API 路由與預設服務模式 |
| `fin-signal-service/src/fin_signal/schemas.py` | 請求／回應模型與欄位限制 |
| `fin-signal-service/src/fin_signal/service.py` | 規則分析、Gemini 串接與結構化輸出 |
| `fin-signal-service/src/fin_signal/evidence.py` | 目標價原文證據驗證 |
| `fin-signal-service/src/fin_signal/retry.py` | 有限次重試與指數退避 |
| `fin-signal-service/src/fin_signal/rag.py` | 切塊、向量檢索、引用與拒答 |
| `fin-signal-service/src/fin_signal/benchmark.py` | 三筆新聞案例與評估指標計算 |
| `fin-signal-service/tests/` | API、LLM Mock、證據、重試與 RAG 測試 |

## 請履歷 AI 輸出

1. 適合現有履歷的「技術技能」更新文字。
2. 一個專案名稱及 2～4 點專案描述。
3. 如已提供目標職缺，依職缺調整重點；未提供時，以 Python 後端與 AI 應用工程方向撰寫。
4. 原履歷有英文版本時，再提供對應英文文字，保持相同事實範圍。

請先依上述已確認資訊完成草稿；只有實際會影響履歷內容的缺漏，再集中列出待確認事項。
