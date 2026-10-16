import os

import pytest

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
    if os.name == "posix":
        assert target.stat().st_mode & 0o777 == 0o600
        assert target.parent.stat().st_mode & 0o777 == 0o700


def test_backup_rejects_negative_retention_without_deleting_data(tmp_path) -> None:
    source = tmp_path / "source.db"
    Repository(str(source))
    with pytest.raises(ValueError, match="retention_days"):
        backup_database(str(source), str(tmp_path / "backups"), retention_days=-1)
    assert not (tmp_path / "backups").exists()
