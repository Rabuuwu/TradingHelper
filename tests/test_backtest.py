from datetime import UTC, datetime

from trading_helper.backtest import run_backtest
from trading_helper.market_data.sample import SampleMarketDataProvider
from trading_helper.risk.costs import CostProfile, FeeCalculator


def test_backtest_returns_metrics_without_lookahead_entry() -> None:
    frame = (
        SampleMarketDataProvider(now=datetime(2026, 1, 1, tzinfo=UTC))
        .get_candles("AAPL", "1d", limit=300)
        .frame
    )
    report = run_backtest(frame, FeeCalculator(CostProfile("free")), entry_score=0)
    assert report.total_trades > 0
    assert 0 <= report.win_rate <= 100
