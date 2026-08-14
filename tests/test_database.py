from trading_helper.database import connect, init_database


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
