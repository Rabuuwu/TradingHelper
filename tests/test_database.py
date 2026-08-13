from trading_helper.database import connect, init_database


def test_database_initializes_core_tables(tmp_path) -> None:
    path = tmp_path / "test.db"
    init_database(str(path))
    with connect(str(path)) as connection:
        names = {row["name"] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"scan_runs", "signals", "positions_cache", "alerts"}.issubset(names)
