import json
from unittest.mock import MagicMock

import pytest
from google.genai import errors

from fin_signal.retry import NonRetryableError
from fin_signal.schemas import NewsAnalysisRequest, SentimentType
from fin_signal.service import SignalAnalysisService


@pytest.mark.asyncio
async def test_llm_service_success_with_mock():
    """驗證 SignalAnalysisService (use_llm=True) 在成功情境下解析並通過證據檢核。"""
    service = SignalAnalysisService(use_llm=True, api_key="fake-test-key")

    # 模擬 Gemini SDK 回傳成功的 JSON 結構
    mock_response = MagicMock()
    mock_payload = {
        "request_id": "dummy-id",
        "ticker": "2330.TW",
        "sentiment": "BULLISH",
        "event_category": "EARNINGS",
        "signal_score": 0.9,
        "confidence": 0.95,
        "rationale": "台積電營收創歷史新高，分析師調升目標價至 1400.0 元。",
        "latency_ms": 10.0,
        "target_price": 1400.0,
        "target_price_evidence": "目標價調升至 1400.0 元",
    }
    mock_response.text = json.dumps(mock_payload)

    # Mock 掉底層 generate_content 呼叫
    service._client.models.generate_content = MagicMock(return_value=mock_response)

    req = NewsAnalysisRequest(
        ticker="2330.TW",
        headline="台積電 10 月營收創歷史新高",
        content=(
            "台積電今日公布 10 月營收達新台幣 3142 億元。"
            "美系外資重申買進，並將目標價調升至 1400.0 元。"
        ),
    )

    result = await service.analyze(req)

    assert result.ticker == "2330.TW"
    assert result.sentiment == SentimentType.BULLISH
    assert result.target_price == 1400.0
    assert result.target_price_evidence == "目標價調升至 1400.0 元"
    assert result.latency_ms > 0.0
    # 驗證底層呼叫次數正好為 1 次
    assert service._client.models.generate_content.call_count == 1


@pytest.mark.asyncio
async def test_llm_service_retries_on_rate_limit_and_succeeds():
    """驗證遇到 429 限流時會自動觸發重試機制，第二次成功時正常返回。"""
    service = SignalAnalysisService(use_llm=True, api_key="fake-test-key")

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "request_id": "dummy-id",
        "ticker": "NVDA",
        "sentiment": "BULLISH",
        "event_category": "GENERAL",
        "signal_score": 0.8,
        "confidence": 0.9,
        "rationale": "需求旺盛",
        "latency_ms": 10.0,
        "target_price": None,
        "target_price_evidence": None,
    })

    # 第一次拋出 429 限流錯誤，第二次成功回傳
    err_body = {"error": {"message": "Resource Exhausted"}}
    rate_limit_err = errors.ClientError(429, err_body)
    service._client.models.generate_content = MagicMock(
        side_effect=[rate_limit_err, mock_response]
    )

    req = NewsAnalysisRequest(
        ticker="NVDA",
        headline="Nvidia demand surges across data centers",
        content="Nvidia continues to see massive enterprise demand.",
    )

    result = await service.analyze(req)

    assert result.ticker == "NVDA"
    assert result.sentiment == SentimentType.BULLISH
    # 驗證確實重試了第二次
    assert service._client.models.generate_content.call_count == 2


@pytest.mark.asyncio
async def test_llm_service_fails_immediately_on_auth_error():
    """驗證遇到 401/403 致命錯誤時立即拋出 NonRetryableError，絕不重試。"""
    service = SignalAnalysisService(use_llm=True, api_key="fake-invalid-key")

    auth_err = errors.ClientError(401, {"error": {"message": "Invalid API Key"}})
    service._client.models.generate_content = MagicMock(side_effect=auth_err)

    req = NewsAnalysisRequest(
        ticker="AAPL",
        headline="Apple event today",
        content="Apple announces new product line.",
    )

    with pytest.raises(NonRetryableError) as exc_info:
        await service.analyze(req)

    assert "401" in str(exc_info.value)
    # 驗證只嘗試了 1 次，絕無無效重試
    assert service._client.models.generate_content.call_count == 1
