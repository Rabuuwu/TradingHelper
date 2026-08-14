from __future__ import annotations

import json
from datetime import UTC, date, datetime
from typing import Any

from trading_helper.database import Repository
from trading_helper.paper import PaperBuy, PaperPortfolioService


class SoakMonitor:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def record(self, status: str, details: dict[str, Any] | None = None) -> None:
        now = datetime.now(UTC)
        self.repository.execute(
            """INSERT INTO soak_observations(observation_date,observed_at,status,details_json)
            VALUES(?,?,?,?) ON CONFLICT(observation_date) DO UPDATE SET
            observed_at=excluded.observed_at,
            status=CASE WHEN soak_observations.status='UNHEALTHY' THEN 'UNHEALTHY'
            ELSE excluded.status END,details_json=excluded.details_json""",
            (now.date().isoformat(), now.isoformat(), status, json.dumps(details or {})),
        )

    def report(self) -> dict[str, Any]:
        rows = self.repository.rows(
            """SELECT observation_date,status,observed_at FROM soak_observations
            ORDER BY observation_date"""
        )
        if not rows:
            return {"status": "NOT_STARTED", "days_observed": 0, "required_days": 14}
        first = date.fromisoformat(rows[0]["observation_date"])
        last = date.fromisoformat(rows[-1]["observation_date"])
        unhealthy = sum(row["status"] != "HEALTHY" for row in rows)
        consecutive_span = (last - first).days + 1
        complete = len(rows) >= 14 and consecutive_span == len(rows) and unhealthy == 0
        return {
            "status": "PASSED" if complete else ("FAILED" if unhealthy else "RUNNING"),
            "days_observed": len(rows),
            "calendar_span_days": consecutive_span,
            "required_days": 14,
            "unhealthy_days": unhealthy,
            "started_at": rows[0]["observed_at"],
            "last_observation_at": rows[-1]["observed_at"],
        }


def run_accelerated_paper_soak(repository: Repository, cycles: int = 1000) -> dict[str, Any]:
    """Exercise accounting invariants repeatedly without pretending that time elapsed."""
    if cycles < 1:
        raise ValueError("cycles must be positive")
    paper = PaperPortfolioService(repository, 100_000, "PLN")
    initial = float(paper.account()["initial_cash"])
    for index in range(cycles):
        entry = 80 + index % 25
        exit_price = entry * (1.01 if index % 2 == 0 else 0.992)
        position_id = paper.buy(PaperBuy("TEST", entry, 0.1, "PLN", 1, 0.01))
        paper.sell(position_id, exit_price, 1, 0.01)
    account = paper.account()
    ledger_sum = repository.rows("SELECT COALESCE(SUM(cash_change),0) AS total FROM paper_ledger")[
        0
    ]["total"]
    expected_cash = initial + float(ledger_sum)
    open_positions = repository.rows(
        "SELECT COUNT(*) AS count FROM manual_positions WHERE mode='PAPER' AND status='OPEN'"
    )[0]["count"]
    passed = abs(float(account["cash_balance"]) - expected_cash) < 1e-6 and open_positions == 0
    return {
        "status": "PASSED" if passed else "FAILED",
        "cycles": cycles,
        "cash_balance": round(float(account["cash_balance"]), 4),
        "ledger_expected_cash": round(expected_cash, 4),
        "open_positions": open_positions,
    }
