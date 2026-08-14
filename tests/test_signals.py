from datetime import UTC, datetime, timedelta

from trading_helper.database import Repository
from trading_helper.signals import SignalQueryService


def signal(symbol: str, created_at: str, score: int) -> dict:
    return {
        "created_at": created_at,
        "symbol": symbol,
        "score": score,
        "label": "WATCH",
        "reasons_json": "[]",
    }


def test_latest_signal_is_unique_per_symbol_and_history_is_retained(tmp_path) -> None:
    repository = Repository(str(tmp_path / "signals.db"))
    service = SignalQueryService(repository)
    old = (datetime.now(UTC) - timedelta(days=100)).isoformat()
    repository.add_signal(signal("AAPL", old, 40))
    repository.add_signal(signal("AAPL", datetime.now(UTC).isoformat(), 70))
    repository.add_signal(signal("MSFT", datetime.now(UTC).isoformat(), 60))
    assert [row["symbol"] for row in service.latest()] == ["AAPL", "MSFT"]
    assert len(service.history("AAPL")) == 2
    assert service.prune(90) == 1
    assert len(service.history("AAPL")) == 1
