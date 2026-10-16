from __future__ import annotations

import os
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path


def backup_database(source_path: str, backup_directory: str, retention_days: int = 14) -> Path:
    if retention_days < 0:
        raise ValueError("retention_days must be zero or greater")
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Database not found: {source}")
    directory = Path(backup_directory)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(directory, 0o700)
    target = directory / f"trading-helper-{datetime.now(UTC):%Y%m%d-%H%M%S-%f}.db"
    descriptor = os.open(target, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    os.close(descriptor)
    try:
        source_db = sqlite3.connect(source)
        target_db = sqlite3.connect(target)
        try:
            source_db.backup(target_db)
            integrity = target_db.execute("PRAGMA integrity_check").fetchone()
            if not integrity or integrity[0] != "ok":
                raise sqlite3.DatabaseError("Backup integrity check failed")
        finally:
            target_db.close()
            source_db.close()
        os.chmod(target, 0o600)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    if retention_days > 0:
        cutoff = datetime.now(UTC) - timedelta(days=retention_days)
        for candidate in directory.glob("trading-helper-*.db"):
            if candidate == target:
                continue
            modified = datetime.fromtimestamp(candidate.stat().st_mtime, UTC)
            if modified < cutoff:
                candidate.unlink()
    return target
