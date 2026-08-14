from trading_helper.auth import AuthManager, hash_password
from trading_helper.config import Settings


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


def test_bcrypt_login_and_session() -> None:
    manager = AuthManager(settings(hash_password("very-secret-password")))
    token = manager.login("trader", "very-secret-password")
    assert token and manager.valid(token)
    manager.logout(token)
    assert not manager.valid(token)


def test_wrong_password_is_rejected() -> None:
    manager = AuthManager(settings(hash_password("very-secret-password")))
    assert manager.login("trader", "wrong") is None
