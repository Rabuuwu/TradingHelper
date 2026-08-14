import json

import pytest

from trading_helper.auto_paper import AutoPaperConfig, AutoPaperTrader
from trading_helper.config import Settings, StrategySettings
from trading_helper.database import utc_now
from trading_helper.market_data.sample import SampleMarketDataProvider
from trading_helper.service import TradingHelperService


def make_settings(database_path: str) -> Settings:
    return Settings(
        app_host="127.0.0.1",
        app_port=8787,
        database_path=database_path,
        settings_file="unused",
        market_data_provider="sample",
        provider_api_key="",
        ntfy_enabled=False,
        ntfy_server="https://ntfy.sh",
        ntfy_topic="",
        auth_enabled=False,
        auth_username="",
        auth_password_hash="",
        session_secret="",
    )


def make_trader(tmp_path, initial_cash: float = 1000) -> AutoPaperTrader:
    settings = make_settings(str(tmp_path / "auto-paper.db"))
    strategy = StrategySettings.from_mapping({"universe": {"symbols": ["AAPL"]}})
    provider = SampleMarketDataProvider()
    service = TradingHelperService(
        settings,
        strategy,
        provider,
        {"costs": {"profiles": {"custom": {}}}},
    )
    price = provider.get_quote("AAPL").price
    service.repository.execute(
        """INSERT INTO signals(created_at,symbol,score,label,entry_low,entry_high,
        stop_price,target_price,target_price_2,recommended_quantity,feasibility_status,
        details_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            utc_now(),
            "AAPL",
            85,
            "STRONG_BUY_SETUP",
            price - 1,
            price + 1,
            price - 5,
            price + 5,
            price + 10,
            1,
            "FEASIBLE",
            json.dumps({"currency": "USD", "indicators": {"atr": 1.5}}),
        ),
    )
    return AutoPaperTrader(service, AutoPaperConfig(initial_cash, interval_seconds=30))


def test_auto_paper_opens_and_closes_without_adding_cash(tmp_path) -> None:
    trader = make_trader(tmp_path)
    initial = trader.account()["cash_balance"]
    opened = trader.cycle()
    assert opened["open_positions"] == 1
    assert trader.account()["cash_balance"] < initial

    position = trader.positions()[0]
    trader.repository.execute(
        "UPDATE auto_paper_positions SET target_price=? WHERE id=?",
        (position["entry_price"] - 1, position["id"]),
    )
    closed = trader.cycle()
    assert closed["open_positions"] == 0
    assert closed["closed_trades"] == 1
    assert [row["action"] for row in trader.repository.rows(
        "SELECT action FROM auto_paper_decisions ORDER BY id"
    )] == ["START", "BUY", "SELL"]


def test_auto_paper_rejects_changed_starting_balance(tmp_path) -> None:
    trader = make_trader(tmp_path, 1000)
    with pytest.raises(ValueError, match="top-ups and resets are intentionally disabled"):
        AutoPaperTrader(trader.service, AutoPaperConfig(2000, interval_seconds=30))
