from trading_helper.alerts.service import AlertService
from trading_helper.database import Repository


class FakePublisher:
    def __init__(self, fails: bool = False) -> None:
        self.fails = fails
        self.messages: list[str] = []

    def publish(self, title: str, body: str, priority: str = "default", tags: str = "") -> None:
        if self.fails:
            raise RuntimeError("offline")
        self.messages.append(title)


def test_alert_deduplication_and_dispatch(tmp_path) -> None:
    repository = Repository(str(tmp_path / "alerts.db"))
    publisher = FakePublisher()
    service = AlertService(repository, publisher)
    assert service.enqueue("BUY_SETUP", "NVDA", "NVDA", "body", "bar-1")
    assert not service.enqueue("BUY_SETUP", "NVDA", "NVDA", "body", "bar-1")
    assert service.dispatch_pending() == 1
    assert publisher.messages == ["NVDA"]


def test_failed_alert_remains_retryable(tmp_path) -> None:
    repository = Repository(str(tmp_path / "alerts.db"))
    service = AlertService(repository, FakePublisher(fails=True))
    service.enqueue("DATA_ERROR", None, "Error", "body", "once")
    assert service.dispatch_pending() == 0
    assert repository.rows("SELECT status FROM alerts")[0]["status"] == "FAILED"
