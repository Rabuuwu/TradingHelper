from dataclasses import replace
from datetime import UTC, datetime

from trading_helper.database import Repository
from trading_helper.market_data.cache import CachedMarketData
from trading_helper.market_data.sample import SampleMarketDataProvider


class CountingProvider(SampleMarketDataProvider):
    def __init__(self) -> None:
        super().__init__(now=datetime(2026, 1, 1, tzinfo=UTC))
        self.calls = 0

    def get_candles(self, *args, **kwargs):
        self.calls += 1
        return super().get_candles(*args, **kwargs)


class OtherCountingProvider(CountingProvider):
    name = "other"

    def get_candles(self, *args, **kwargs):
        batch = super().get_candles(*args, **kwargs)
        return replace(batch, provenance=replace(batch.provenance, source=self.name))


class ShortSeriesProvider(CountingProvider):
    def get_candles(self, symbol, timeframe, limit=300, **kwargs):
        self.calls += 1
        batch = super(CountingProvider, self).get_candles(symbol, timeframe, limit=limit)
        return replace(batch, frame=batch.frame.tail(20))


def test_sample_provider_is_deterministic() -> None:
    provider = SampleMarketDataProvider(now=datetime(2026, 1, 1, tzinfo=UTC))
    first = provider.get_candles("AAPL", "1h", limit=220)
    second = provider.get_candles("AAPL", "1h", limit=220)
    assert first.frame.equals(second.frame)
    assert provider.get_quote("AAPL").provenance.source == "sample"
    assert provider.search_symbols("apple")[0].symbol == "AAPL"


def test_market_data_cache_avoids_duplicate_fetch(tmp_path) -> None:
    provider = CountingProvider()
    cache = CachedMarketData(provider, Repository(str(tmp_path / "cache.db")), ttl_seconds=99999999)
    cache.get_candles("AAPL", "1h", 220)
    cache.get_candles("AAPL", "1h", 220)
    assert provider.calls == 1


def test_market_data_cache_never_reuses_another_provider_source(tmp_path) -> None:
    repository = Repository(str(tmp_path / "cache.db"))
    sample = CountingProvider()
    CachedMarketData(sample, repository).get_candles("AAPL", "1h", 220)
    other = OtherCountingProvider()
    batch = CachedMarketData(other, repository).get_candles("AAPL", "1h", 220)
    assert other.calls == 1
    assert batch.provenance.source == "other"
    assert len(repository.cached_candles("AAPL", "1h", 220, "other")) == 220


def test_short_candle_series_is_cached_for_the_normal_ttl(tmp_path) -> None:
    provider = ShortSeriesProvider()
    cache = CachedMarketData(provider, Repository(str(tmp_path / "short.db")))
    first = cache.get_candles("NEW", "1h", 220)
    second = cache.get_candles("NEW", "1h", 220)

    assert len(first.frame) == len(second.frame) == 20
    assert provider.calls == 1
