import pytest
from httpx import ASGITransport, AsyncClient

from fin_signal.main import app
from fin_signal.schemas import EventCategory, NewsAnalysisRequest, SentimentType
from fin_signal.service import SignalAnalysisService


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    """測試健康檢查 API 是否正常返回 200 OK。"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "fin-signal-service"}


@pytest.mark.asyncio
async def test_signal_service_domain_logic():
    """單元測試：測試 SignalAnalysisService 核心領域邏輯。"""
    service = SignalAnalysisService()
    req = NewsAnalysisRequest(
        ticker="AAPL",
        headline="Apple beats earnings expectations with record iPhone revenue",
        content=(
            "Apple today reported quarterly revenue up 15% year over year, "
            "driven by strong growth in services and iPhone sales."
        ),
    )
    result = await service.analyze(req)

    assert result.ticker == "AAPL"
    assert result.sentiment == SentimentType.BULLISH
    assert result.event_category == EventCategory.EARNINGS
    assert result.signal_score > 0.0
    assert 0.0 <= result.confidence <= 1.0
    assert result.latency_ms >= 0.0


@pytest.mark.asyncio
async def test_analyze_endpoint_success(async_client: AsyncClient):
    """整合測試：POST /api/v1/signals/analyze 成功案例。"""
    payload = {
        "ticker": "NVDA",
        "headline": "Nvidia revenues surge amid generative AI boom",
        "content": (
            "Nvidia reported net income jumped more than 200 percent as "
            "datacenter demand continues to skyrocket."
        ),
    }
    response = await async_client.post("/api/v1/signals/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "NVDA"
    assert data["sentiment"] in ["BULLISH", "BEARISH", "NEUTRAL"]
    assert -1.0 <= data["signal_score"] <= 1.0
    assert "request_id" in data


@pytest.mark.asyncio
async def test_analyze_endpoint_validation_error(async_client: AsyncClient):
    """整合測試：驗證不合法輸入時應觸發 422 錯誤。"""
    invalid_payload = {
        "ticker": "",  # 不符合最小長度限制
        "headline": "Hi",  # 過短
        "content": "Short",  # 過短
    }
    response = await async_client.post("/api/v1/signals/analyze", json=invalid_payload)
    assert response.status_code == 422
