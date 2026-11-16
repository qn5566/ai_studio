from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from fin_signal.schemas import NewsAnalysisRequest, SignalAnalysisResponse
from fin_signal.service import SignalAnalysisService

signal_service: SignalAnalysisService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """管理服務生命週期（連線池、AI 模型熱身載入等）。"""
    global signal_service
    signal_service = SignalAnalysisService()
    yield
    signal_service = None


app = FastAPI(
    title="Financial Signal Service",
    description="Quantitative trading signal microservice from financial news",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """服務健康檢查端點。"""
    return {"status": "healthy", "service": "fin-signal-service"}


@app.post(
    "/api/v1/signals/analyze",
    response_model=SignalAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_news_signal(request: NewsAnalysisRequest) -> SignalAnalysisResponse:
    """分析單筆金融新聞與事件，返回量化信號結構。"""
    global signal_service
    if signal_service is None:
        signal_service = SignalAnalysisService()
    return await signal_service.analyze(request)
