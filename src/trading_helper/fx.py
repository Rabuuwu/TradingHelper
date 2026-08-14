from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from trading_helper.database import Repository
from trading_helper.market_data.provider import MarketDataProvider, ProviderError


@dataclass(frozen=True)
class FxRate:
    base_currency: str
    quote_currency: str
    rate: float
    source: str
    data_timestamp: datetime
    status: str


class FxRateService:
    def __init__(
        self,
        repository: Repository,
        provider: MarketDataProvider,
        configured_rates_to_portfolio: dict[str, float],
        portfolio_currency: str,
        *,
        cache_minutes: int = 60,
        stale_after_minutes: int = 1440,
    ) -> None:
        self.repository = repository
        self.provider = provider
        self.configured_rates = configured_rates_to_portfolio
        self.portfolio_currency = portfolio_currency.upper()
        self.cache_ttl = timedelta(minutes=cache_minutes)
        self.stale_after = timedelta(minutes=stale_after_minutes)

    def get_rate(self, base_currency: str, quote_currency: str) -> FxRate:
        base = base_currency.upper()
        quote = quote_currency.upper()
        now = datetime.now(UTC)
        if base == quote:
            return FxRate(base, quote, 1.0, "IDENTITY", now, "LIVE")
        cached = self.repository.latest_fx_rate(base, quote)
        if cached:
            fetched_at = datetime.fromisoformat(cached["fetched_at"])
            if now - fetched_at <= self.cache_ttl:
                return self._from_cached(cached, now)
        if self.provider.name != "sample":
            try:
                provider_quote = self.provider.get_quote(f"{base}/{quote}")
                if provider_quote.price <= 0:
                    raise ProviderError("FX rate must be positive")
                timestamp = provider_quote.provenance.timestamp
                self.repository.save_fx_rate(
                    base, quote, provider_quote.price, self.provider.name, timestamp.isoformat()
                )
                return FxRate(
                    base,
                    quote,
                    provider_quote.price,
                    self.provider.name,
                    timestamp,
                    self._market_status(timestamp, now),
                )
            except ProviderError:
                if cached:
                    return self._from_cached(cached, now)
        return self._configured_fallback(base, quote, now)

    def _from_cached(self, row: dict, now: datetime) -> FxRate:
        timestamp = datetime.fromisoformat(row["data_timestamp"])
        return FxRate(
            row["base_currency"],
            row["quote_currency"],
            float(row["rate"]),
            row["data_source"],
            timestamp,
            self._market_status(timestamp, now),
        )

    def _market_status(self, timestamp: datetime, now: datetime) -> str:
        return "STALE" if now - timestamp > self.stale_after else "LIVE"

    def _configured_fallback(self, base: str, quote: str, now: datetime) -> FxRate:
        base_rate = self.configured_rates.get(base)
        quote_rate = self.configured_rates.get(quote)
        if not base_rate or not quote_rate:
            raise ProviderError(f"No FX rate available for {base}/{quote}")
        return FxRate(
            base,
            quote,
            base_rate / quote_rate,
            "YAML_CONFIG",
            now,
            "FALLBACK",
        )
