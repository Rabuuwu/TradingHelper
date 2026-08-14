from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

import bcrypt

from trading_helper.config import Settings


class AuthManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.sessions: dict[str, datetime] = {}

    def login(self, username: str, password: str) -> str | None:
        if not self.settings.auth_enabled:
            return "auth-disabled"
        if username != self.settings.auth_username or not self.settings.auth_password_hash:
            return None
        try:
            valid = bcrypt.checkpw(password.encode(), self.settings.auth_password_hash.encode())
        except ValueError:
            return None
        if not valid:
            return None
        token = secrets.token_urlsafe(32)
        self.sessions[token] = datetime.now(UTC) + timedelta(hours=24)
        return token

    def valid(self, token: str | None) -> bool:
        if not self.settings.auth_enabled:
            return True
        if not token or token not in self.sessions:
            return False
        if self.sessions[token] <= datetime.now(UTC):
            self.sessions.pop(token, None)
            return False
        return True

    def logout(self, token: str | None) -> None:
        if token:
            self.sessions.pop(token, None)


def hash_password(password: str) -> str:
    if len(password) < 10:
        raise ValueError("Password must have at least 10 characters")
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
