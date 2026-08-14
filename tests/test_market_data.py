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
