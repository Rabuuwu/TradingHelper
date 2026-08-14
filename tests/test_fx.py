from datetime import UTC, datetime

from trading_helper.database import Repository
from trading_helper.fx import FxRateService
from trading_helper.market_data.models import DataProvenance, Quote
from trading_helper.market_data.sample import SampleMarketDataProvider


class FxProvider(SampleMarketDataProvider):
    name = "fx_test"

    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def get_quote(self, symbol: str) -> Quote:
        self.calls += 1
        return Quote(symbol, 4.125, "PLN", DataProvenance(self.name, datetime.now(UTC)))


def test_fx_rate_uses_provider_and_sqlite_cache(tmp_path) -> None:
    repository = Repository(str(tmp_path / "fx.db"))
    provider = FxProvider()
    service = FxRateService(repository, provider, {"PLN": 1, "USD": 4}, "PLN")
    first = service.get_rate("USD", "PLN")
    second = service.get_rate("USD", "PLN")
    assert first.rate == second.rate == 4.125
    assert first.source == "fx_test"
    assert first.status == "LIVE"
    assert provider.calls == 1
    assert repository.latest_fx_rate("USD", "PLN")["rate"] == 4.125


def test_fx_rate_uses_yaml_only_as_offline_fallback(tmp_path) -> None:
    service = FxRateService(
        Repository(str(tmp_path / "fx.db")),
        SampleMarketDataProvider(),
        {"PLN": 1, "USD": 4, "EUR": 4.4},
        "PLN",
    )
    rate = service.get_rate("USD", "EUR")
    assert rate.rate == 4 / 4.4
    assert rate.source == "YAML_CONFIG"
    assert rate.status == "FALLBACK"


def test_fx_identity_does_not_call_provider(tmp_path) -> None:
    provider = FxProvider()
    service = FxRateService(Repository(str(tmp_path / "fx.db")), provider, {"PLN": 1}, "PLN")
    assert service.get_rate("PLN", "PLN").rate == 1
    assert provider.calls == 0
