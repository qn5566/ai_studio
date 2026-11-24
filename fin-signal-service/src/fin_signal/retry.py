import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


class RetryableError(Exception):
    """可重試的暫態錯誤（例如網路連線逾時、服務端限流 429、服務短暫不可用 503）。"""

    pass


class NonRetryableError(Exception):
    """不可重試的致命錯誤（例如 API Key 錯誤 401、權限不足 403、請求格式錯誤 400）。"""

    pass


async def retry_async_call(
    operation: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    sleep_func: Callable[[float], Awaitable[Any]] = asyncio.sleep,
) -> T:
    """非同步呼叫重試包裝器（支援指數退避）。

    :param operation: 無參數的非同步回呼函式
    :param max_attempts: 最大嘗試次數（含首次呼叫）
    :param initial_delay: 首次重試等待秒數
    :param backoff_factor: 指數退避乘數（每次失敗等待時間乘以此係數）
    :param sleep_func: 睡眠等待函式（預設為 asyncio.sleep，可注入 Mock 供快速測試）
    :return: operation 的執行成果
    """
    current_delay = initial_delay

    for attempt in range(1, max_attempts + 1):
        try:
            return await operation()
        except NonRetryableError:
            # 致命錯誤：立即拋出，絕不重試
            raise
        except RetryableError:
            if attempt >= max_attempts:
                # 已達最大重試次數，將最後一次的暫態錯誤拋出
                raise
            # 等待退避時間
            await sleep_func(current_delay)
            current_delay *= backoff_factor

    # 理論上不會走到這裡，若發生則拋出常規異常
    raise RuntimeError("Unexpected retry termination")
