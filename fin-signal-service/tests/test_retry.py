from unittest.mock import AsyncMock

import pytest

# 待實作的重試工具函式與例外類別（目前尚未實作，預期測試時會出現 ImportError，形成紅燈）
from fin_signal.retry import NonRetryableError, RetryableError, retry_async_call


@pytest.mark.asyncio
async def test_retry_success_after_one_failure():
    """案例 1：第一次失敗（暫態錯誤），第二次成功。

    預期：呼叫 2 次，最後成功返回結果。
    """
    mock_operation = AsyncMock()
    # 定義前一次拋出暫態錯誤，第二次返回正確結果
    mock_operation.side_effect = [
        RetryableError("Network timeout"),
        "Success Result",
    ]

    mock_sleep = AsyncMock()  # Mock 掉等待時間，讓測試在 0.01 秒內飛速完成

    result = await retry_async_call(
        operation=mock_operation,
        max_attempts=3,
        initial_delay=1.0,
        sleep_func=mock_sleep,
    )

    assert result == "Success Result"
    assert mock_operation.call_count == 2
    assert mock_sleep.call_count == 1
    mock_sleep.assert_awaited_with(1.0)


@pytest.mark.asyncio
async def test_retry_exceeds_max_attempts():
    """案例 2：持續遇到暫態錯誤，直到超過最大重試次數（3 次）。

    預期：重試 3 次後拋出最後的 RetryableError。
    """
    mock_operation = AsyncMock()
    # 準備 3 次暫態錯誤
    mock_operation.side_effect = [
        RetryableError("Timeout 1"),
        RetryableError("Timeout 2"),
        RetryableError("Timeout 3"),
    ]

    mock_sleep = AsyncMock()

    with pytest.raises(RetryableError) as exc_info:
        await retry_async_call(
            operation=mock_operation,
            max_attempts=3,
            initial_delay=0.5,
            backoff_factor=2.0,
            sleep_func=mock_sleep,
        )

    assert "Timeout 3" in str(exc_info.value)
    assert mock_operation.call_count == 3
    # 呼叫 3 次中會睡眠 2 次（第 1 次失敗後睡 0.5s，第 2 次失敗後睡 1.0s）
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_non_retryable_error_fails_immediately():
    """案例 3：遇到致命不可重試錯誤（如 401 認證失敗、400 格式錯誤）。

    預期：只呼叫 1 次，立即中斷拋出，完全不執行 sleep 與重試。
    """
    mock_operation = AsyncMock()
    mock_operation.side_effect = NonRetryableError("Invalid API Key (401)")

    mock_sleep = AsyncMock()

    with pytest.raises(NonRetryableError) as exc_info:
        await retry_async_call(
            operation=mock_operation,
            max_attempts=3,
            sleep_func=mock_sleep,
        )

    assert "Invalid API Key" in str(exc_info.value)
    assert mock_operation.call_count == 1
    assert mock_sleep.call_count == 0  # 絕不可浪費時間睡眠
