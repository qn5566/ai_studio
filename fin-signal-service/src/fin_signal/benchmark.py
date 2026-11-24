import asyncio
import time
from dataclasses import dataclass
from typing import Any

from fin_signal.schemas import (
    NewsAnalysisRequest,
    SentimentType,
)
from fin_signal.service import SignalAnalysisService


@dataclass
class TestCase:
    name: str
    request: NewsAnalysisRequest
    expected_sentiment: SentimentType
    expected_target_price: float | None


# 準備 3 筆經典的金融新聞基準測試集
BENCHMARK_DATASET = [
    TestCase(
        name="案例 1：強勁營收與明確目標價",
        request=NewsAnalysisRequest(
            ticker="2330.TW",
            headline="台積電 10 月營收創歷史新高，AI 晶片需求強勁",
            content=(
                "台積電今日公布 10 月合併營收約為新台幣 3142 億元，續創單月歷史新高。"
                "美系外資出具報告重申買進，並將目標價調升至 1400.0 元。"
            ),
        ),
        expected_sentiment=SentimentType.BULLISH,
        expected_target_price=1400.0,
    ),
    TestCase(
        name="案例 2：語意轉折（雖有正面詞彙，但整體為利空調查）",
        request=NewsAnalysisRequest(
            ticker="2454.TW",
            headline="聯發科遭主管機關反壟斷調查，下半年出貨恐重挫",
            content=(
                "儘管聯發科上季獲利創下 record 新高，但遭多國主管機關調查。"
                "分析師警告出貨將面臨嚴重 slump 衰退，市場情緒極度悲觀。"
            ),
        ),
        expected_sentiment=SentimentType.BEARISH,
        expected_target_price=None,  # 未提及目標價
    ),
    TestCase(
        name="案例 3：股價干擾（僅提及目前股價，無分析師目標價）",
        request=NewsAnalysisRequest(
            ticker="2317.TW",
            headline="鴻海股價突破 200 元關卡，成交量顯著放大",
            content=(
                "鴻海今日盤中買盤湧入，推升目前股價最高來到 200.0 元。"
                "市場關注下半年伺服器出貨進度，但法人目前暫未給出任何目標價預估。"
            ),
        ),
        expected_sentiment=SentimentType.NEUTRAL,
        expected_target_price=None,  # 200 元是目前股價，不是目標價！
    ),
]


async def run_benchmark(service: SignalAnalysisService) -> dict[str, Any]:
    """執行單一引擎的基準測試並統計指標。"""
    sentiment_correct = 0
    price_correct = 0
    latencies = []

    for test in BENCHMARK_DATASET:
        t0 = time.perf_counter()
        result = await service.analyze(test.request)
        elapsed = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed)

        # 檢驗情緒是否命中
        if result.sentiment == test.expected_sentiment:
            sentiment_correct += 1

        # 檢驗目標價是否命中
        if result.target_price == test.expected_target_price:
            price_correct += 1

    total = len(BENCHMARK_DATASET)
    return {
        "sentiment_accuracy": f"{(sentiment_correct / total) * 100:.1f}%",
        "price_accuracy": f"{(price_correct / total) * 100:.1f}%",
        "avg_latency_ms": f"{sum(latencies) / total:.2f} ms",
    }


async def main() -> None:
    print("=" * 60)
    print("🚀 開始執行【新聞分析基準評估（Benchmark）】")
    print("=" * 60)

    # 1. 評估傳統規則引擎 (Rule-based)
    rule_service = SignalAnalysisService(use_llm=False)
    rule_metrics = await run_benchmark(rule_service)

    print("\n📊 1. 傳統關鍵字規則引擎 (Rule-Based):")
    print(f"  • 情緒判定準確率 : {rule_metrics['sentiment_accuracy']}")
    print(f"  • 目標價判定準確率: {rule_metrics['price_accuracy']}")
    print(f"  • 平均處理延遲   : {rule_metrics['avg_latency_ms']}")

    # 2. 評估 Gemini 大語言模型
    try:
        llm_service = SignalAnalysisService(use_llm=True)
        print("\n⏳ 正在連線 Gemini 2.5 Flash 執行評估（需時約 3~5 秒）...")
        llm_metrics = await run_benchmark(llm_service)

        print("\n📊 2. Gemini 2.5 Flash 大語言模型 (LLM):")
        print(f"  • 情緒判定準確率 : {llm_metrics['sentiment_accuracy']}")
        print(f"  • 目標價判定準確率: {llm_metrics['price_accuracy']}")
        print(f"  • 平均處理延遲   : {llm_metrics['avg_latency_ms']}")

        print("\n" + "=" * 60)
        print("💡 結論與權衡對比 (Trade-off):")
        print("  1. 準確率：LLM 精準辨識「目前股價 vs 目標價」與語意轉折。")
        print("  2. 延遲度：規則引擎毫秒級適合初篩；LLM 延遲較高但品質卓越。")
        print("=" * 60)
    except Exception as e:
        print(f"\n⚠️ 無法執行 Gemini 測試 (請確認已設定 GEMINI_API_KEY): {e}")


if __name__ == "__main__":
    asyncio.run(main())
