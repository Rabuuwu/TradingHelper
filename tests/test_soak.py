from trading_helper.database import Repository
from trading_helper.soak import SoakMonitor, run_accelerated_paper_soak


def test_accelerated_paper_soak_preserves_accounting_invariants(tmp_path) -> None:
    report = run_accelerated_paper_soak(Repository(str(tmp_path / "soak.db")), cycles=250)
    assert report["status"] == "PASSED"
    assert report["open_positions"] == 0
    assert report["cash_balance"] == report["ledger_expected_cash"]


def test_real_soak_report_starts_with_observation(tmp_path) -> None:
    monitor = SoakMonitor(Repository(str(tmp_path / "soak.db")))
    assert monitor.report()["status"] == "NOT_STARTED"
    monitor.record("HEALTHY")
    assert monitor.report()["status"] == "RUNNING"
    assert monitor.report()["days_observed"] == 1
