import urllib.error

from trading_helper.desktop_companion import TradingHelperApiClient


class FakeClient(TradingHelperApiClient):
    def __init__(self, failure=None) -> None:
        super().__init__("http://server")
        self.failure = failure

    def request(self, path, method="GET", payload=None):
        if self.failure:
            raise self.failure
        if path == "/status":
            return {"provider": "sample"}
        return []


class LoginClient(TradingHelperApiClient):
    def __init__(self, response=None, failure=None) -> None:
        super().__init__("http://server")
        self.response = response
        self.failure = failure

    def request(self, path, method="GET", payload=None):
        assert path == "/auth/login"
        assert method == "POST"
        assert payload == {"username": "trader", "password": "secret-password"}
        if self.failure:
            raise self.failure
        return self.response


def test_companion_reads_central_server_only() -> None:
    state = FakeClient().snapshot()
    assert state.connection == "ONLINE"
    assert state.status["provider"] == "sample"


def test_companion_distinguishes_auth_and_offline() -> None:
    assert (
        FakeClient(urllib.error.HTTPError("u", 401, "", {}, None)).snapshot().connection
        == "AUTH_ERROR"
    )
    assert FakeClient(urllib.error.URLError("offline")).snapshot().connection == "OFFLINE"


def test_companion_login_reports_success_and_failure() -> None:
    assert LoginClient({"status": "ok"}).login("trader", "secret-password")
    error = urllib.error.HTTPError("u", 401, "", {}, None)
    assert not LoginClient(failure=error).login("trader", "secret-password")
