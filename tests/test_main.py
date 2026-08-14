import pytest

from trading_helper.main import ensure_safe_bind


def test_remote_bind_requires_authentication() -> None:
    with pytest.raises(RuntimeError):
        ensure_safe_bind("0.0.0.0", False)
    ensure_safe_bind("100.64.0.1", True)
    ensure_safe_bind("127.0.0.1", False)
