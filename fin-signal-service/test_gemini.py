import os
import sys
from google import genai
from google.genai import types
from fin_signal.schemas import SignalAnalysisResponse

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("\n❌ 尚未偵測到 GEMINI_API_KEY 環境變數！")
    print("👉 請在終端機執行：export GEMINI_API_KEY=\"你的API_KEY\"\n")
    sys.exit(1)

# 初始化 Google GenAI 客戶端，指定使用支援結構化輸出的 v1beta API
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(api_version="v1beta"),
)

prompt = """
請分析以下金融新聞，抽取交易信號、情緒、事件類型，以及是否有分析師目標價：

【新聞標題】台積電 10 月營收創歷史新高，AI 晶片需求強勁
【新聞內文】台積電今日公布 10 月合併營收約為新台幣 3,142 億元，月增 24.8%，較去年同期大幅增加 29.2%，續創單月歷史新高。主要受惠於蘋果 iPhone 新機處理器與輝達（NVIDIA）AI 伺服器晶片 Blackwell 的強勁投片需求。美系外資出具最新報告，重申「強力買進」評級，並將目標價調升至 1400.0 元。
"""

print("🚀 正在呼叫 Gemini 1.5 Flash 進行結構化輸出分析...")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=SignalAnalysisResponse,  # 👈 核心：直接綁定 Pydantic 類別！
    ),
)

# 驗證輸出結果
parsed_obj = SignalAnalysisResponse.model_validate_json(response.text)

print("\n🎉 分析成功！Gemini 輸出的強型別 Pydantic 物件：")
print(f"股票代號 (ticker)       : {parsed_obj.ticker}")
print(f"情緒判定 (sentiment)    : {parsed_obj.sentiment}")
print(f"事件類別 (category)     : {parsed_obj.event_category}")
print(f"信號強度 (signal_score) : {parsed_obj.signal_score}")
print(f"信心水準 (confidence)   : {parsed_obj.confidence}")
print(f"分析理由 (rationale)    : {parsed_obj.rationale}")
print(f"解析目標價 (target_price): {parsed_obj.target_price}")
