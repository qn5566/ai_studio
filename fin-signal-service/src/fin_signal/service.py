import re
import time
import uuid

from fin_signal.schemas import (
    EventCategory,
    NewsAnalysisRequest,
    SentimentType,
    SignalAnalysisResponse,
)


class SignalAnalysisService:
    """金融新聞與事件量化信號分析服務。"""

    def __init__(self) -> None:
        self._bullish_keywords = {
            "beats",
            "record",
            "growth",
            "surge",
            "jumped",
            "profit",
            "skyrocket",
        }
        self._bearish_keywords = {
            "misses",
            "drop",
            "plunge",
            "decline",
            "investigation",
            "loss",
            "slump",
        }
        self._earnings_keywords = {
            "earnings",
            "revenue",
            "quarterly",
            "net income",
            "guidance",
        }
        self._macro_keywords = {
            "inflation",
            "fed",
            "interest rate",
            "cpi",
            "central bank",
        }

    async def analyze(self, request: NewsAnalysisRequest) -> SignalAnalysisResponse:
        """非同步分析單筆金融新聞並輸出量化交易信號。"""
        start_time = time.perf_counter()

        text = f"{request.headline} {request.content}".lower()

        # 1. 判斷事件分類 (Event Category)
        if any(kw in text for kw in self._earnings_keywords):
            category = EventCategory.EARNINGS
        elif any(kw in text for kw in self._macro_keywords):
            category = EventCategory.MACRO
        else:
            category = EventCategory.GENERAL

        # 2. 判斷情緒與信號分數 (Sentiment & Signal Score)
        bullish_hits = sum(1 for kw in self._bullish_keywords if kw in text)
        bearish_hits = sum(1 for kw in self._bearish_keywords if kw in text)

        total_hits = bullish_hits + bearish_hits
        if total_hits == 0:
            sentiment = SentimentType.NEUTRAL
            signal_score = 0.0
            confidence = 0.5
            rationale = "No strong directional sentiment keywords identified."
        elif bullish_hits > bearish_hits:
            sentiment = SentimentType.BULLISH
            signal_score = round(min(1.0, 0.4 + (bullish_hits * 0.2)), 2)
            confidence = round(min(0.95, 0.6 + (bullish_hits * 0.1)), 2)
            rationale = f"Detected {bullish_hits} bullish signal indicator(s)."
        elif bearish_hits > bullish_hits:
            sentiment = SentimentType.BEARISH
            signal_score = round(max(-1.0, -0.4 - (bearish_hits * 0.2)), 2)
            confidence = round(min(0.95, 0.6 + (bearish_hits * 0.1)), 2)
            rationale = f"Detected {bearish_hits} bearish signal indicator(s)."
        else:
            sentiment = SentimentType.NEUTRAL
            signal_score = 0.0
            confidence = 0.6
            rationale = "Mixed sentiment signals detected with equal polarity."

        # 3. 抽取目標價 (Target Price)
        pattern = r"target price (?:to|of|is)?\s*[:$]?\s*([0-9]+(?:\.[0-9]+)?)"
        price_match = re.search(pattern, text)
        target_price = float(price_match.group(1)) if price_match else None

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return SignalAnalysisResponse(
            request_id=str(uuid.uuid4()),
            ticker=request.ticker.upper(),
            sentiment=sentiment,
            event_category=category,
            signal_score=signal_score,
            confidence=confidence,
            rationale=rationale,
            latency_ms=elapsed_ms,
            target_price=target_price,
        )
