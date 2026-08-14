from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import TypeVar

from trading_helper.market_data.provider import (
    ProviderError,
    ProviderRateLimited,
    ProviderTimeout,
)

T = TypeVar("T")


class RateLimiter:
    def __init__(self, requests_per_minute: int = 6000) -> None:
        if requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be positive")
        self.minimum_interval = 60 / requests_per_minute
        self.last_request = 0.0
        self.lock = threading.Lock()

    def wait(self) -> None:
        with self.lock:
            delay = self.minimum_interval - (time.monotonic() - self.last_request)
            if delay > 0:
                time.sleep(delay)
            self.last_request = time.monotonic()


def with_retry(
    operation: Callable[[], T], attempts: int = 3, base_delay_seconds: float = 0.25
) -> T:
    if attempts < 1:
        raise ValueError("attempts must be positive")
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return operation()
        except ProviderRateLimited:
            raise
        except (ProviderError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(base_delay_seconds * (2**attempt))
    raise ProviderTimeout(
        f"Provider failed after {attempts} attempts: {last_error}"
    ) from last_error
