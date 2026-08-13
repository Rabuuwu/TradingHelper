from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any


class IbkrDependencyMissing(RuntimeError):
    pass


def ibapi_available() -> bool:
    try:
        import ibapi  # noqa: F401
    except ImportError:
        return False
    return True


@dataclass(frozen=True)
class IbkrEndpoint:
    host: str
    port: int
    client_id: int


class IbkrReadOnlyClient:
    """Minimal read-only TWS API adapter with no order methods exposed."""

    def __init__(self, endpoint: IbkrEndpoint) -> None:
        self.endpoint = endpoint
        self._app: Any | None = None
        self._thread: threading.Thread | None = None

    def connect(self) -> None:
        if not ibapi_available():
            raise IbkrDependencyMissing("Official ibapi is not installed. See docs/IBKR_SETUP.md.")
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper

        class App(EWrapper, EClient):
            def __init__(self) -> None:
                EClient.__init__(self, self)

        app = App()
        app.connect(self.endpoint.host, self.endpoint.port, self.endpoint.client_id)
        thread = threading.Thread(target=app.run, name="ibkr-api", daemon=True)
        thread.start()
        self._app = app
        self._thread = thread

    @property
    def connected(self) -> bool:
        return bool(self._app and self._app.isConnected())

    def disconnect(self) -> None:
        if self._app is not None:
            self._app.disconnect()
        self._app = None
        self._thread = None
