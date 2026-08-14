from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path


def backup_database(source_path: str, backup_directory: str, retention_days: int = 14) -> Path:
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Database not found: {source}")
    directory = Path(backup_directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"trading-helper-{datetime.now(UTC):%Y%m%d-%H%M%S}.db"
    source_db = sqlite3.connect(source)
    target_db = sqlite3.connect(target)
    try:
        source_db.backup(target_db)
    finally:
        target_db.close()
        source_db.close()
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    for candidate in directory.glob("trading-helper-*.db"):
        modified = datetime.fromtimestamp(candidate.stat().st_mtime, UTC)
        if modified < cutoff:
            candidate.unlink()
    return target
