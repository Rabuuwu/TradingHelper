import pytest

from trading_helper.config import StrategySettings, load_settings


def test_strategy_settings_are_parsed() -> None:
    settings = StrategySettings.from_mapping({"universe": {"symbols": ["aapl"]}})
    assert settings.symbols == ("AAPL",)
    assert settings.scan_interval_seconds == 1800


def test_strategy_settings_require_symbols() -> None:
    with pytest.raises(ValueError):
        StrategySettings.from_mapping({})


def test_market_data_uses_real_provider_when_an_api_key_is_configured(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MARKET_DATA_PROVIDER", "")
    monkeypatch.setenv("MARKET_DATA_API_KEY", "configured-key")

    assert load_settings().market_data_provider == "twelve_data"


def test_market_data_keeps_offline_sample_when_no_provider_key_is_configured(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MARKET_DATA_PROVIDER", raising=False)
    monkeypatch.delenv("MARKET_DATA_API_KEY", raising=False)

    assert load_settings().market_data_provider == "sample"
