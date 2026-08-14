import pytest
from fastapi import HTTPException, Response

from trading_helper.api import (
    PositionCreate,
    PublicSettingsUpdate,
    WatchlistInput,
    _decode_signal,
    add_position,
    add_watchlist,
    dashboard,
    delete_watchlist,
    health,
    market_candles,
    public_settings,
    ready,
    status,
    update_public_settings,
    watchlist,
)


def test_health() -> None:
    assert health()["status"] == "ok"


def test_core_api_handlers_work_without_broker(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRADING_HELPER_DB", str(tmp_path / "api.db"))
    monkeypatch.setenv("SETTINGS_FILE", "config/settings.example.yaml")

    assert ready(Response())["status"] == "ready"
    assert status()["server"] == "ONLINE"
    assert public_settings()["provider"] == "sample"
    assert "PLN" in public_settings()["supported_currencies"]
    assert str(dashboard().path).endswith("index.html")


def test_market_candles_include_ema_and_provenance(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRADING_HELPER_DB", str(tmp_path / "candles.db"))
    monkeypatch.setenv("SETTINGS_FILE", "config/settings.example.yaml")
    payload = market_candles("aapl", "1h", 240)
    assert payload["symbol"] == "AAPL"
    assert payload["source"] == "sample"
    assert len(payload["candles"]) == 240
    assert {"time", "open", "high", "low", "close", "volume", "ema20", "ema200"} <= set(
        payload["candles"][-1]
    )


def test_signal_values_are_converted_to_selected_display_currency(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRADING_HELPER_DB", str(tmp_path / "api.db"))
    monkeypatch.setenv("SETTINGS_FILE", "config/settings.example.yaml")
    update_public_settings(PublicSettingsUpdate(display_currency="PLN"))
    row = {
        "price": 100.0,
        "entry_low": 99.0,
        "reasons_json": "[]",
        "warnings_json": "[]",
        "breakdown_json": "{}",
        "details_json": '{"currency":"USD"}',
    }
    decoded = _decode_signal(row)
    assert decoded["instrument_currency"] == "USD"
    assert decoded["display_currency"] == "PLN"
    assert decoded["display_values"]["price"] == 400.0
    assert decoded["fx_rate_source"] == "YAML_CONFIG"
    assert decoded["fx_rate_status"] == "FALLBACK"


def test_watchlist_can_be_added_and_removed(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRADING_HELPER_DB", str(tmp_path / "api.db"))
    monkeypatch.setenv("SETTINGS_FILE", "config/settings.example.yaml")
    add_watchlist(WatchlistInput(symbol="nvda", notes="wybicie"))
    assert [(item["symbol"], item["notes"]) for item in watchlist()] == [("NVDA", "wybicie")]
    delete_watchlist("nvda")
    assert watchlist() == []


def test_generic_portfolio_endpoint_cannot_bypass_paper_ledger() -> None:
    with pytest.raises(HTTPException) as error:
        add_position(
            PositionCreate(
                symbol="AAPL",
                entry_price=10,
                quantity=1,
                currency="USD",
                entry_date="2026-08-14",
                mode="PAPER",
            )
        )
    assert error.value.status_code == 422
