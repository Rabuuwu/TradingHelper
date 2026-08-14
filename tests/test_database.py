from datetime import UTC, datetime

from trading_helper.database import Repository, connect, init_database
from trading_helper.market_data.sample import SampleMarketDataProvider


def test_database_initializes_core_tables(tmp_path) -> None:
    path = tmp_path / "test.db"
    init_database(str(path))
    with connect(str(path)) as connection:
        names = {
            row["name"]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    assert {
        "scan_runs",
        "signals",
        "positions_cache",
        "alerts",
        "account_summary",
        "system_state",
        "fx_rates",
        "portfolio_snapshots",
        "paper_accounts",
        "paper_ledger",
        "provider_credit_usage",
        "auto_paper_accounts",
        "auto_paper_positions",
        "auto_paper_decisions",
    }.issubset(names)


def test_legacy_signal_table_is_migrated_without_data_loss(tmp_path) -> None:
    path = tmp_path / "legacy.db"
    with connect(str(path)) as connection:
        connection.execute(
            """CREATE TABLE signals(id INTEGER PRIMARY KEY,created_at TEXT NOT NULL,
            symbol TEXT NOT NULL,score INTEGER NOT NULL,label TEXT NOT NULL,price REAL,
            reasons_json TEXT NOT NULL DEFAULT '[]',data_mode TEXT NOT NULL DEFAULT 'UNKNOWN')"""
        )
        connection.execute(
            """INSERT INTO signals(created_at,symbol,score,label)
            VALUES('2025-01-01','AAPL',60,'WATCH')"""
        )
    init_database(str(path))
    with connect(str(path)) as connection:
        row = connection.execute("SELECT symbol,breakdown_json FROM signals").fetchone()
    assert row["symbol"] == "AAPL"
    assert row["breakdown_json"] == "{}"


def test_market_cache_cleanup_only_removes_other_provider_rows(tmp_path) -> None:
    repository = Repository(str(tmp_path / "cache.db"))
    provider = SampleMarketDataProvider(now=datetime(2026, 8, 14, tzinfo=UTC))
    batch = provider.get_candles("AAPL", "1h", limit=20)
    repository.save_candles("AAPL", "1h", batch.frame, "sample", False, None)
    repository.save_quote(provider.get_quote("AAPL"))
    removed = repository.purge_market_cache_except("twelve_data")
    assert removed == {"candles": 20, "quotes": 1}
    assert repository.rows("SELECT * FROM candles") == []
    assert repository.rows("SELECT * FROM quotes") == []
