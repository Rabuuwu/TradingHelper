from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from trading_helper.alerts.ntfy import NtfyPublisher
from trading_helper.database import Repository, utc_now


class AlertService:
    def __init__(
        self, repository: Repository, publisher: NtfyPublisher | None, cooldown_minutes: int = 240
    ) -> None:
        self.repository = repository
        self.publisher = publisher
        self.cooldown = timedelta(minutes=cooldown_minutes)

    def enqueue(
        self, kind: str, symbol: str | None, title: str, body: str, occurrence_key: str
    ) -> bool:
        recent = self.repository.rows(
            """SELECT cooldown_until FROM alerts WHERE kind=? AND symbol IS ?
            ORDER BY id DESC LIMIT 1""",
            (kind, symbol),
        )
        if recent and recent[0]["cooldown_until"]:
            if datetime.fromisoformat(recent[0]["cooldown_until"]) > datetime.now(UTC):
                return False
        fingerprint = hashlib.sha256(f"{kind}:{symbol or ''}:{occurrence_key}".encode()).hexdigest()
        cooldown_until = (datetime.now(UTC) + self.cooldown).isoformat()
        created = self.repository.add_alert(
            {
                "kind": kind,
                "symbol": symbol,
                "fingerprint": fingerprint,
                "title": title,
                "body": body,
                "cooldown_until": cooldown_until,
            }
        )
        if created:
            self.repository.event("alert_queued", title, details={"kind": kind, "symbol": symbol})
        return created

    def dispatch_pending(self, limit: int = 20) -> int:
        if self.publisher is None:
            return 0
        alerts = self.repository.rows(
            """SELECT * FROM alerts WHERE status IN ('PENDING','FAILED')
            AND attempts < 5 ORDER BY id LIMIT ?""",
            (limit,),
        )
        sent = 0
        for alert in alerts:
            try:
                self.publisher.publish(alert["title"], alert["body"], priority="high")
            except Exception as exc:
                self.repository.execute(
                    """UPDATE alerts SET status='FAILED',attempts=attempts+1,
                    last_attempt_at=?,error=? WHERE id=?""",
                    (utc_now(), str(exc), alert["id"]),
                )
                self.repository.event("alert_failed", str(exc), "ERROR", {"alert_id": alert["id"]})
            else:
                self.repository.execute(
                    """UPDATE alerts SET status='SENT',sent=1,attempts=attempts+1,
                    last_attempt_at=?,last_sent_at=?,error=NULL WHERE id=?""",
                    (utc_now(), utc_now(), alert["id"]),
                )
                self.repository.set_state("last_notification", utc_now())
                self.repository.event(
                    "alert_sent", alert["title"], details={"alert_id": alert["id"]}
                )
                sent += 1
        return sent
