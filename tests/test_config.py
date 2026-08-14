import pytest

from trading_helper.config import StrategySettings


def test_strategy_settings_are_parsed() -> None:
    settings = StrategySettings.from_mapping({"universe": {"symbols": ["aapl"]}})
    assert settings.symbols == ("AAPL",)
    assert settings.scan_interval_seconds == 1800


def test_strategy_settings_require_symbols() -> None:
    with pytest.raises(ValueError):
        StrategySettings.from_mapping({})
