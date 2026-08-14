from __future__ import annotations

from datetime import UTC, datetime, time
from typing import Any

from trading_helper.database import Repository, utc_now
from trading_helper.market_data.provider import ProviderRateLimited


class ApiCreditBudget:
    """Persistent conservative credit accounting across restarts."""

    def __init__(
        self,
        repository: Repository,
        provider: str,
        daily_limit: int = 800,
        reserve: int = 80,
    ) -> None:
        if daily_limit <= 0 or reserve < 0 or reserve >= daily_limit:
            raise ValueError("Invalid provider credit budget")
        self.repository = repository
        self.provider = provider
        self.daily_limit = daily_limit
        self.reserve = reserve

    def bootstrap_from_scan_history(self) -> int:
        """Conservatively account for today's calls made before tracking was enabled."""
        start = datetime.combine(datetime.now(UTC).date(), time.min, UTC).isoformat()
        existing = self.repository.rows(
            """SELECT COUNT(*) AS count FROM provider_credit_usage
            WHERE provider=? AND used_at>=?""",
            (self.provider, start),
        )[0]["count"]
        if existing:
            return 0
        scans = self.repository.rows(
            """SELECT COALESCE(SUM(symbols_total * 2),0) AS estimate
            FROM scan_runs WHERE provider=? AND started_at>=?""",
            (self.provider, start),
        )[0]["estimate"]
        estimate = min(int(scans), self.daily_limit - self.reserve)
        if estimate:
            self.repository.execute(
                """INSERT INTO provider_credit_usage(used_at,provider,endpoint,credits)
                VALUES(?,?,?,?)""",
                (utc_now(), self.provider, "pre_tracker_estimate", estimate),
            )
        return estimate

    def consume(self, endpoint: str, credits: int = 1) -> None:
        if credits <= 0:
            raise ValueError("credits must be positive")
        start = datetime.combine(datetime.now(UTC).date(), time.min, UTC).isoformat()
        with self.repository.transaction() as connection:
            used = connection.execute(
                """SELECT COALESCE(SUM(credits),0) FROM provider_credit_usage
                WHERE provider=? AND used_at>=?""",
                (self.provider, start),
            ).fetchone()[0]
            usable = self.daily_limit - self.reserve
            if int(used) + credits > usable:
                raise ProviderRateLimited(
                    f"Daily {self.provider} background budget exhausted: "
                    f"{used}/{usable} credits; {self.reserve} reserved"
                )
            connection.execute(
                """INSERT INTO provider_credit_usage(used_at,provider,endpoint,credits)
                VALUES(?,?,?,?)""",
                (utc_now(), self.provider, endpoint, credits),
            )

    def status(self) -> dict[str, Any]:
        start = datetime.combine(datetime.now(UTC).date(), time.min, UTC).isoformat()
        rows = self.repository.rows(
            """SELECT endpoint,SUM(credits) AS credits FROM provider_credit_usage
            WHERE provider=? AND used_at>=? GROUP BY endpoint ORDER BY endpoint""",
            (self.provider, start),
        )
        used = sum(int(row["credits"]) for row in rows)
        usable = self.daily_limit - self.reserve
        return {
            "provider": self.provider,
            "used_today": used,
            "daily_limit": self.daily_limit,
            "background_limit": usable,
            "reserved": self.reserve,
            "background_remaining": max(usable - used, 0),
            "hard_remaining": max(self.daily_limit - used, 0),
            "by_endpoint": {row["endpoint"]: int(row["credits"]) for row in rows},
        }
