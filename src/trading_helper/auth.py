from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt

from trading_helper.config import Settings
from trading_helper.database import Repository, utc_now


class LoginRateLimited(Exception):
    pass


class AuthManager:
    def __init__(self, settings: Settings, repository: Repository | None = None) -> None:
        self.settings = settings
        self.repository = repository

    def _token_hash(self, token: str) -> str:
        return hmac.new(
            self.settings.session_secret.encode(), token.encode(), hashlib.sha256
        ).hexdigest()

    def login(self, username: str, password: str, client_id: str = "local") -> str | None:
        if not self.settings.auth_enabled:
            return "auth-disabled"
        if not self.settings.session_secret:
            return None
        cutoff = (datetime.now(UTC) - timedelta(minutes=15)).isoformat()
        if self.repository:
            self.repository.execute("DELETE FROM auth_sessions WHERE expires_at<=?", (utc_now(),))
            self.repository.execute(
                "DELETE FROM auth_login_attempts WHERE attempted_at<?", (cutoff,)
            )
            failures = self.repository.rows(
                """SELECT COUNT(*) AS count FROM auth_login_attempts
                WHERE username=? AND client_id=? AND success=0 AND attempted_at>=?""",
                (username, client_id, cutoff),
            )[0]["count"]
            if failures >= 5:
                raise LoginRateLimited("Too many failed login attempts")
        if username != self.settings.auth_username or not self.settings.auth_password_hash:
            self._record_attempt(username, client_id, False)
            return None
        try:
            valid = bcrypt.checkpw(password.encode(), self.settings.auth_password_hash.encode())
        except ValueError:
            self._record_attempt(username, client_id, False)
            return None
        if not valid:
            self._record_attempt(username, client_id, False)
            return None
        token = secrets.token_urlsafe(32)
        expires = datetime.now(UTC) + timedelta(hours=24)
        if self.repository:
            self.repository.execute(
                """INSERT INTO auth_sessions(token_hash,created_at,expires_at,last_seen_at)
                VALUES(?,?,?,?)""",
                (self._token_hash(token), utc_now(), expires.isoformat(), utc_now()),
            )
        self._record_attempt(username, client_id, True)
        return token

    def _record_attempt(self, username: str, client_id: str, success: bool) -> None:
        if self.repository:
            self.repository.execute(
                """INSERT INTO auth_login_attempts(username,client_id,attempted_at,success)
                VALUES(?,?,?,?)""",
                (username, client_id, utc_now(), int(success)),
            )

    def valid(self, token: str | None) -> bool:
        if not self.settings.auth_enabled:
            return True
        if not token or not self.repository or not self.settings.session_secret:
            return False
        token_hash = self._token_hash(token)
        rows = self.repository.rows(
            "SELECT expires_at FROM auth_sessions WHERE token_hash=?", (token_hash,)
        )
        if not rows:
            return False
        if datetime.fromisoformat(rows[0]["expires_at"]) <= datetime.now(UTC):
            self.repository.execute("DELETE FROM auth_sessions WHERE token_hash=?", (token_hash,))
            return False
        self.repository.execute(
            "UPDATE auth_sessions SET last_seen_at=? WHERE token_hash=?", (utc_now(), token_hash)
        )
        return True

    def logout(self, token: str | None) -> None:
        if token and self.repository and self.settings.session_secret:
            self.repository.execute(
                "DELETE FROM auth_sessions WHERE token_hash=?", (self._token_hash(token),)
            )


def hash_password(password: str) -> str:
    if len(password) < 10:
        raise ValueError("Password must have at least 10 characters")
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
