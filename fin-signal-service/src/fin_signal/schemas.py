from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class SentimentType(StrEnum):
    """金融情感極性"""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class EventCategory(StrEnum):
    """金融事件類型"""

    EARNINGS = "EARNINGS"
    MACRO = "MACRO"
    REGULATORY = "REGULATORY"
    M_AND_A = "M_AND_A"
    GENERAL = "GENERAL"


class NewsAnalysisRequest(BaseModel):
    """新聞分析請求 Payload"""

    model_config = ConfigDict(str_strip_whitespace=True)

    ticker: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="股票或資產代號，例如 AAPL, TSLA, 2330.TW",
    )
    headline: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="新聞標題",
    )
    content: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="新聞完整內文",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="新聞發布時間 (UTC)",
    )
    source: str = Field(
        default="UNKNOWN", 
        description="新聞來源，例如 Bloomberg, Reuters",
    )


class SignalAnalysisResponse(BaseModel):
    """量化信號分析回應 Payload"""

    model_config = ConfigDict(from_attributes=True)

    request_id: str = Field(..., description="唯一的請求識別碼 (UUID)")
    ticker: str = Field(..., description="股票代號")
    sentiment: SentimentType = Field(..., description="情感極性判定")
    event_category: EventCategory = Field(..., description="事件分類")
    signal_score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="量化信號分數 [-1.0 (強烈看跌) 至 +1.0 (強烈看漲)]",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="預測信心水準 [0.0 至 1.0]",
    )
    rationale: str = Field(..., description="分析推理理由")
    latency_ms: float = Field(..., description="處理延遲 (毫秒)")
    target_price: float | None = Field(
        default=None,
        ge=0.0,
        description="分析出的目標價",
    )
