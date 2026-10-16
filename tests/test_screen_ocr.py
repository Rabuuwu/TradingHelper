import logging
import subprocess
import sys
from unittest.mock import patch

import pytest

from trading_helper import screen_ocr
from trading_helper.screen_ocr import parse_screen_reading


def test_reads_ticker_and_us_price_from_tradingview_header() -> None:
    reading = parse_screen_reading(
        "Google Chrome — TradingView",
        [
            {"text": "NASDAQ:AAPL", "x": 0.1, "y": 0.9, "confidence": 0.98},
            {"text": "AAPL 192.50 +0.36%", "x": 0.1, "y": 0.85, "confidence": 0.91},
        ],
    )

    assert reading.symbol == "AAPL"
    assert reading.price == "192.50"
    assert reading.confidence == 0.91


def test_preserves_locale_decimal_and_thousands_separators() -> None:
    polish = parse_screen_reading(
        "TradingView",
        [{"text": "Price: 123,45", "x": 0.1, "y": 0.9, "confidence": 0.9}],
    )
    us = parse_screen_reading(
        "TradingView",
        [{"text": "Last: $1,234.56", "x": 0.1, "y": 0.9, "confidence": 0.9}],
    )

    assert polish.price == "123,45"
    assert us.price == "1,234.56"


def test_returns_no_price_when_screen_has_no_price_label_or_quote_row() -> None:
    reading = parse_screen_reading(
        "TradingView",
        [{"text": "NASDAQ:AAPL · 1D", "x": 0.1, "y": 0.9, "confidence": 0.99}],
    )

    assert reading.symbol == "AAPL"
    assert reading.price is None


def test_keeps_ocr_text_for_display_but_does_not_require_symbol() -> None:
    reading = parse_screen_reading(
        "Browser",
        [{"text": "Close: 42.10", "x": 0.4, "y": 0.5, "confidence": 0.82}],
    )

    assert reading.symbol is None
    assert reading.price == "42.10"
    assert reading.text == ("Close: 42.10",)


def test_helper_timeouts_are_reported_as_retryable_screen_errors() -> None:
    timeout = subprocess.TimeoutExpired("screen-ocr", timeout=15)
    with (
        patch.object(screen_ocr, "_helper_binary", return_value="screen-ocr"),
        patch.object(screen_ocr.subprocess, "run", side_effect=timeout),
        pytest.raises(RuntimeError, match="timed out"),
    ):
        screen_ocr.list_visible_browser_windows()


def test_helper_diagnostics_are_logged_without_window_titles(caplog) -> None:
    result = subprocess.CompletedProcess(
        args=["screen-ocr", "browser-windows"],
        returncode=0,
        stdout="[]",
        stderr=(
            "OCR_DIAG visible_windows=8 browser_windows=1 tradingview_title_matches=0\n"
            "OCR_DIAG browser=Firefox title_chars=24 tradingview_title=False\n"
        ),
    )
    with (
        patch.object(screen_ocr, "_helper_binary", return_value="screen-ocr"),
        patch.object(screen_ocr.subprocess, "run", return_value=result),
        caplog.at_level(logging.INFO, logger="trading_helper.screen_ocr"),
    ):
        screen_ocr.list_visible_browser_windows()

    assert "browser=Firefox" in caplog.text
    assert "tradingview_title=False" in caplog.text
    assert "24" in caplog.text
    assert "Actual tab title" not in caplog.text


def test_packaged_app_uses_precompiled_ocr_helper(tmp_path) -> None:
    helper = tmp_path / "trading_helper" / "screen-ocr"
    helper.parent.mkdir()
    helper.write_text("packaged helper")
    helper.chmod(0o700)
    original = screen_ocr._binary
    try:
        screen_ocr._binary = None
        with (
            patch.object(sys, "platform", "darwin"),
            patch.object(sys, "_MEIPASS", str(tmp_path), create=True),
            patch.object(screen_ocr.subprocess, "run") as run,
        ):
            assert screen_ocr._helper_binary() == helper
            run.assert_not_called()
    finally:
        screen_ocr._binary = original


def test_automatic_window_selection_ignores_non_tradingview_titles() -> None:
    windows = [
        {"id": 1, "app": "Safari", "title": "Mail — Inbox"},
        {"id": 2, "app": "Google Chrome", "title": "AAPL 1D — TradingView"},
        {"id": 3, "app": "Firefox", "title": "BTCUSD — TradingView"},
    ]

    assert screen_ocr.select_tradingview_window(windows) == windows[1]
    assert screen_ocr.select_tradingview_window(windows[:1]) is None


def test_automatic_window_selection_does_not_assume_app_name_is_tradingview() -> None:
    window = {"id": 1, "app": "Safari", "title": "TradingView — chart"}

    assert screen_ocr.select_tradingview_window([window]) is window


def test_titleless_firefox_window_can_be_verified_from_ocr_text() -> None:
    observations = [
        {"text": "tradingview.com", "x": 0.1, "y": 0.98},
        {"text": "NASDAQ:AAPL", "x": 0.1, "y": 0.9},
    ]

    assert screen_ocr.select_titleless_browser_windows(
        [{"id": 9, "app": "Firefox", "title": ""}]
    ) == [{"id": 9, "app": "Firefox", "title": ""}]
    assert screen_ocr.screen_contains_tradingview(observations)
    assert not screen_ocr.screen_contains_tradingview([{"text": "Inbox - Mail"}])


def test_quote_is_bound_to_chart_header_instead_of_another_watchlist_row() -> None:
    reading = parse_screen_reading(
        "AAPL · 1D — TradingView",
        [
            {"text": "NASDAQ:AAPL", "x": 0.12, "y": 0.91, "confidence": 0.98},
            {"text": "AAPL 192.50 +0.36%", "x": 0.12, "y": 0.85, "confidence": 0.91},
            {"text": "Last: 42.10", "x": 0.82, "y": 0.50, "confidence": 0.99},
        ],
    )

    assert reading.symbol == "AAPL"
    assert reading.price == "192.50"


def test_ambiguous_price_labels_are_not_reported_as_a_quote() -> None:
    reading = parse_screen_reading(
        "TradingView",
        [
            {"text": "Last: 100.00", "x": 0.2, "y": 0.7, "confidence": 0.9},
            {"text": "Price: 200.00", "x": 0.6, "y": 0.7, "confidence": 0.9},
        ],
    )

    assert reading.price is None
