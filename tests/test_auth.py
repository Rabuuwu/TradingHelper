import pytest

from trading_helper.auth import AuthManager, LoginRateLimited, hash_password
from trading_helper.config import Settings
from trading_helper.database import Repository


def settings(password_hash: str) -> Settings:
    return Settings(
        "127.0.0.1",
        8787,
        "db",
        "config",
        "sample",
        "",
        False,
        "https://ntfy.sh",
        "",
        True,
        "trader",
        password_hash,
        "secret",
    )


def test_bcrypt_login_and_session_persists_across_manager_restart(tmp_path) -> None:
    configured = settings(hash_password("very-secret-password"))
    repository = Repository(str(tmp_path / "auth.db"))
    manager = AuthManager(configured, repository)
    token = manager.login("trader", "very-secret-password")
    restarted = AuthManager(configured, repository)
    assert token and restarted.valid(token)
    restarted.logout(token)
    assert not restarted.valid(token)


def test_wrong_password_is_rejected(tmp_path) -> None:
    manager = AuthManager(
        settings(hash_password("very-secret-password")), Repository(str(tmp_path / "auth.db"))
    )
    assert manager.login("trader", "wrong") is None


def test_login_is_rate_limited_after_five_failures(tmp_path) -> None:
    manager = AuthManager(
        settings(hash_password("very-secret-password")), Repository(str(tmp_path / "auth.db"))
    )
    for _ in range(5):
        assert manager.login("trader", "wrong", "client") is None
    with pytest.raises(LoginRateLimited):
        manager.login("trader", "very-secret-password", "client")
