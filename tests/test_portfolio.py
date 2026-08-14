from datetime import UTC, datetime

import pytest

from trading_helper.database import Repository
from trading_helper.journal import TradeJournal
from trading_helper.market_data.cache import CachedMarketData
from trading_helper.market_data.sample import SampleMarketDataProvider
from trading_helper.portfolio import ManualPortfolioService, PositionInput, PositionMonitor


def position() -> PositionInput:
    return PositionInput(
        "NVDA",
        "XTB",
        100,
        0.15,
        "USD",
        datetime.now(UTC).isoformat(),
        stop_price=95,
        target_price=110,
    )


def test_manual_fractional_position_and_journal(tmp_path) -> None:
    repository = Repository(str(tmp_path / "portfolio.db"))
    service = ManualPortfolioService(repository)
    position_id = service.add(position())
    assert service.list()[0]["quantity"] == 0.15
    service.close(position_id, 110, fees=0.5)
    stats = TradeJournal(repository).statistics()
    assert stats["wins"] == 1
    assert stats["net_pnl"] == 1.0


def test_invalid_long_stop_is_rejected(tmp_path) -> None:
    repository = Repository(str(tmp_path / "portfolio.db"))
    invalid = PositionInput("NVDA", "XTB", 100, 1, "USD", "2026-01-01", stop_price=101)
    with pytest.raises(ValueError):
        ManualPortfolioService(repository).add(invalid)


def test_paper_position_is_marked_as_simulation(tmp_path) -> None:
    repository = Repository(str(tmp_path / "portfolio.db"))
    ManualPortfolioService(repository).simulate(position())
    saved = ManualPortfolioService(repository).list()[0]
    assert saved["mode"] == "PAPER"
    assert saved["broker"] == "SIMULATION"


def test_position_monitor_updates_pnl_and_trailing(tmp_path) -> None:
    repository = Repository(str(tmp_path / "portfolio.db"))
    ManualPortfolioService(repository).simulate(position())
    market_data = CachedMarketData(SampleMarketDataProvider(), repository)
    result = PositionMonitor(repository, market_data).run()[0]
    assert "pnl" in result
    assert result["trailing_stop"] > 0
