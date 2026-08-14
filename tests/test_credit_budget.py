import pytest

from trading_helper.database import Repository
from trading_helper.market_data.credits import ApiCreditBudget
from trading_helper.market_data.provider import ProviderRateLimited


def test_credit_budget_is_persistent_and_preserves_reserve(tmp_path) -> None:
    repository = Repository(str(tmp_path / "credits.db"))
    first = ApiCreditBudget(repository, "twelve_data", daily_limit=10, reserve=2)
    for _ in range(8):
        first.consume("time_series")
    restarted = ApiCreditBudget(repository, "twelve_data", daily_limit=10, reserve=2)
    status = restarted.status()
    assert status["used_today"] == 8
    assert status["background_remaining"] == 0
    assert status["hard_remaining"] == 2
    with pytest.raises(ProviderRateLimited):
        restarted.consume("quote")


def test_credit_budget_bootstraps_from_existing_scan_history_once(tmp_path) -> None:
    repository = Repository(str(tmp_path / "credits.db"))
    repository.start_scan(5, "twelve_data")
    budget = ApiCreditBudget(repository, "twelve_data", daily_limit=800, reserve=80)
    assert budget.bootstrap_from_scan_history() == 10
    assert budget.bootstrap_from_scan_history() == 0
    assert budget.status()["by_endpoint"] == {"pre_tracker_estimate": 10}
