from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from trading_helper.database import Repository


class SignalQueryService:
    """Queries and retention rules for immutable signal history."""

    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def latest(self, minimum_score: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        return self.repository.rows(
            """SELECT s.* FROM signals s
            JOIN (SELECT symbol,MAX(id) AS id FROM signals GROUP BY symbol) latest
            ON latest.id=s.id WHERE s.score>=? ORDER BY s.score DESC,s.id DESC LIMIT ?""",
            (minimum_score, limit),
        )

    def history(self, symbol: str, limit: int = 100) -> list[dict[str, Any]]:
        return self.repository.rows(
            "SELECT * FROM signals WHERE symbol=? ORDER BY id DESC LIMIT ?",
            (symbol.upper(), limit),
        )

    def prune(self, retention_days: int) -> int:
        if retention_days < 1:
            raise ValueError("Signal retention must be at least one day")
        cutoff = (datetime.now(UTC) - timedelta(days=retention_days)).isoformat()
        with self.repository.transaction() as connection:
            cursor = connection.execute(
                """DELETE FROM signals WHERE created_at<? AND id NOT IN
                (SELECT MAX(id) FROM signals GROUP BY symbol) AND id NOT IN
                (SELECT signal_id FROM paper_ledger WHERE signal_id IS NOT NULL)""",
                (cutoff,),
            )
            return cursor.rowcount
