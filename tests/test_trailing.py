from trading_helper.risk.trailing import atr_trailing_stop


def test_trailing_stop_never_moves_down() -> None:
    assert atr_trailing_stop(110, 2, 2.5, previous_stop=106) == 106


def test_trailing_stop_moves_up_with_price() -> None:
    assert atr_trailing_stop(120, 2, 2.5, previous_stop=106) == 115
