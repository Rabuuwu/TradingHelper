from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from trading_helper.market_data.credits import ApiCreditBudget
from trading_helper.market_data.models import (
    CandleBatch,
    DataProvenance,
    MarketStatus,
    Quote,
    SymbolInfo,
)
from trading_helper.market_data.provider import (
    MarketDataProvider,
    ProviderError,
    ProviderRateLimited,
    ProviderTimeout,
)
from trading_helper.market_data.resilience import RateLimiter


class TwelveDataProvider(MarketDataProvider):
    """Official Twelve Data REST adapter. It never performs broker operations."""

    name = "twelve_data"
    base_url = "https://api.twelvedata.com"
    intervals = {"15m": "15min", "1h": "1h", "4h": "4h", "1d": "1day"}

    def __init__(
        self,
        api_key: str,
        *,
        timeout_seconds: float = 10,
        delay_minutes: int | None = None,
        session: requests.Session | None = None,
        requests_per_minute: int = 8,
        credit_budget: ApiCreditBudget | None = None,
    ) -> None:
        if not api_key.strip():
            raise ProviderError("MARKET_DATA_API_KEY is required for twelve_data")
        self.api_key = api_key.strip()
        self.timeout_seconds = timeout_seconds
        self.delay_minutes = delay_minutes
        self.session = session or requests.Session()
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.credit_budget = credit_budget
        self._quotes: dict[str, Quote] = {}
        self._quote_cached_at: dict[str, float] = {}
        self._info: dict[str, SymbolInfo] = {}
        self._market_status: tuple[float, MarketStatus] | None = None

    def _get(self, endpoint: str, **params: Any) -> Any:
        self.rate_limiter.wait()
        if self.credit_budget:
            self.credit_budget.consume(endpoint)
        try:
            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                headers={"Authorization": f"apikey {self.api_key}"},
                timeout=self.timeout_seconds,
            )
        except requests.Timeout as exc:
            raise ProviderTimeout("Twelve Data request timed out") from exc
        except requests.RequestException as exc:
            raise ProviderError(f"Twelve Data connection error: {exc}") from exc
        if response.status_code == 429:
            raise ProviderRateLimited("Twelve Data rate limit reached")
        try:
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise ProviderError("Invalid Twelve Data response") from exc
        if isinstance(payload, dict) and (
            payload.get("status") == "error"
            or (payload.get("code") and payload.get("message"))
        ):
            raise ProviderError(f"Twelve Data: {payload.get('message', 'provider error')}")
        return payload

    def _provenance(self, timestamp: datetime) -> DataProvenance:
        delayed = bool(self.delay_minutes and self.delay_minutes > 0)
        return DataProvenance(
            self.name, timestamp, delayed, self.delay_minutes if delayed else None
        )

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 300,
    ) -> CandleBatch:
        try:
            interval = self.intervals[timeframe]
        except KeyError as exc:
            raise ProviderError(f"Unsupported Twelve Data timeframe: {timeframe}") from exc
        params: dict[str, Any] = {
            "symbol": symbol.upper(),
            "interval": interval,
            "outputsize": min(max(limit, 1), 5000),
            "timezone": "UTC",
            "order": "ASC",
        }
        if start:
            params["start_date"] = start.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")
        if end:
            params["end_date"] = end.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")
        payload = self._get("time_series", **params)
        values = payload.get("values") or []
        if not values:
            raise ProviderError(f"Twelve Data returned no candles for {symbol.upper()}")
        frame = pd.DataFrame(values)
        required = {"datetime", "open", "high", "low", "close"}
        if not required.issubset(frame.columns):
            raise ProviderError("Twelve Data candle response is incomplete")
        frame["timestamp"] = pd.to_datetime(frame.pop("datetime"), utc=True)
        if "volume" not in frame:
            frame["volume"] = 0.0
        columns = ["open", "high", "low", "close", "volume"]
        frame[columns] = frame[columns].apply(pd.to_numeric, errors="coerce")
        frame = frame.dropna(subset=["timestamp", "open", "high", "low", "close"])
        frame = frame.set_index("timestamp")[columns].sort_index().tail(limit)
        if frame.empty:
            raise ProviderError(f"Twelve Data returned no usable candles for {symbol.upper()}")
        meta = payload.get("meta") or {}
        normalized = symbol.upper()
        currency = str(meta.get("currency") or "USD").upper()
        timestamp = frame.index[-1].to_pydatetime()
        provenance = self._provenance(timestamp)
        self._quotes[normalized] = Quote(
            normalized, float(frame["close"].iloc[-1]), currency, provenance
        )
        self._quote_cached_at[normalized] = time.monotonic()
        self._info[normalized] = SymbolInfo(
            normalized,
            str(meta.get("symbol") or normalized),
            str(meta.get("type") or "UNKNOWN").upper(),
            currency,
            str(meta.get("exchange") or ""),
            True,
        )
        return CandleBatch(normalized, timeframe, frame, provenance)

    def get_quote(self, symbol: str) -> Quote:
        normalized = symbol.upper()
        if (
            normalized in self._quotes
            and time.monotonic() - self._quote_cached_at.get(normalized, 0) < 60
        ):
            return self._quotes[normalized]
        payload = self._get("quote", symbol=normalized)
        price = payload.get("close") or payload.get("price")
        if price is None:
            raise ProviderError(f"Twelve Data returned no quote for {normalized}")
        raw_timestamp = payload.get("timestamp")
        timestamp = (
            datetime.fromtimestamp(int(raw_timestamp), UTC) if raw_timestamp else datetime.now(UTC)
        )
        quote = Quote(
            normalized,
            float(price),
            str(payload.get("currency") or "USD").upper(),
            self._provenance(timestamp),
        )
        self._quotes[normalized] = quote
        self._quote_cached_at[normalized] = time.monotonic()
        return quote

    def get_symbol_info(self, symbol: str) -> SymbolInfo:
        normalized = symbol.upper()
        if normalized in self._info:
            return self._info[normalized]
        matches = self.search_symbols(normalized)
        exact = next((item for item in matches if item.symbol == normalized), None)
        if exact is None:
            raise ProviderError(f"Twelve Data symbol not found: {normalized}")
        return exact

    def search_symbols(self, query: str) -> list[SymbolInfo]:
        payload = self._get("symbol_search", symbol=query, outputsize=20)
        results = []
        for row in payload.get("data") or []:
            symbol = str(row.get("symbol") or "").upper()
            if not symbol:
                continue
            info = SymbolInfo(
                symbol,
                str(row.get("instrument_name") or symbol),
                str(row.get("instrument_type") or "UNKNOWN").upper(),
                str(row.get("currency") or "USD").upper(),
                str(row.get("exchange") or ""),
                True,
            )
            self._info[symbol] = info
            results.append(info)
        return results

    def get_market_status(self) -> MarketStatus:
        now = datetime.now(UTC)
        eastern = now.astimezone(ZoneInfo("America/New_York"))
        open_now = (
            eastern.weekday() < 5
            and (eastern.hour, eastern.minute) >= (9, 30)
            and (eastern.hour, eastern.minute) < (16, 0)
        )
        result = MarketStatus(
            "UNITED_STATES",
            "OPEN" if open_now else "CLOSED",
            now,
        )
        self._market_status = (time.monotonic(), result)
        return result
