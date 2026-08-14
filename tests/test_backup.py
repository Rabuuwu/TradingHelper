from trading_helper.backup import backup_database
from trading_helper.database import Repository


def test_sqlite_backup_contains_user_data(tmp_path) -> None:
    source = tmp_path / "source.db"
    repository = Repository(str(source))
    repository.event("test", "persist me")
    target = backup_database(str(source), str(tmp_path / "backups"))
    assert (
        Repository(str(target)).rows("SELECT message FROM app_events")[0]["message"] == "persist me"
    )
