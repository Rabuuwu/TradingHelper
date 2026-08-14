from trading_helper.database import Repository
from trading_helper.paper import PaperBuy, PaperPortfolioService


def test_paper_buy_and_sell_update_cash_and_realized_pnl(tmp_path) -> None:
    repository = Repository(str(tmp_path / "paper.db"))
    paper = PaperPortfolioService(repository, 100, "PLN")
    position_id = paper.buy(PaperBuy("AAPL", 10, 2, "USD", 4, 1, stop_price=9, target_price=12))
    assert paper.account()["cash_balance"] == 19
    assert paper.ledger()[0]["transaction_type"] == "BUY"

    result = paper.sell(position_id, 12, 4, 1)
    account = paper.account()
    assert result == {"proceeds": 95.0, "realized_pnl": 14.0}
    assert account["cash_balance"] == 114
    assert account["realized_pnl"] == 14
    assert paper.ledger()[0]["transaction_type"] == "SELL"


def test_paper_buy_rejects_insufficient_cash(tmp_path) -> None:
    paper = PaperPortfolioService(Repository(str(tmp_path / "paper.db")), 100, "PLN")
    try:
        paper.buy(PaperBuy("AAPL", 100, 1, "USD", 4, 0))
    except ValueError as exc:
        assert "Insufficient paper cash" in str(exc)
    else:
        raise AssertionError("Expected insufficient paper cash")


def test_paper_reset_requires_closed_positions(tmp_path) -> None:
    repository = Repository(str(tmp_path / "paper.db"))
    paper = PaperPortfolioService(repository, 100, "PLN")
    position_id = paper.buy(PaperBuy("AAPL", 10, 1, "PLN", 1, 0))
    try:
        paper.reset(200)
    except ValueError as exc:
        assert "Close paper positions" in str(exc)
    else:
        raise AssertionError("Expected reset rejection")
    paper.sell(position_id, 10, 1, 0)
    paper.reset(200)
    assert paper.account()["cash_balance"] == 200


def test_paper_buy_is_fully_rolled_back_when_ledger_write_fails(tmp_path) -> None:
    repository = Repository(str(tmp_path / "paper.db"))
    paper = PaperPortfolioService(repository, 100, "PLN")
    repository.execute(
        """CREATE TRIGGER reject_paper_ledger BEFORE INSERT ON paper_ledger
        BEGIN SELECT RAISE(ABORT, 'forced ledger failure'); END"""
    )
    try:
        paper.buy(PaperBuy("AAPL", 10, 1, "PLN", 1, 0))
    except Exception as exc:
        assert "forced ledger failure" in str(exc)
    else:
        raise AssertionError("Expected forced transaction failure")
    assert paper.account()["cash_balance"] == 100
    assert repository.rows("SELECT * FROM manual_positions") == []
    assert repository.rows("SELECT * FROM trades") == []
