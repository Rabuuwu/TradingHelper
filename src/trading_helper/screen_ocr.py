from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScreenReading:
    symbol: str | None
    price: str | None
    confidence: float | None
    text: tuple[str, ...]


_compile_lock = threading.Lock()
_binary: Path | None = None
_logger = logging.getLogger(__name__)
_logged_diagnostics: set[str] = set()
_diagnostic_lock = threading.Lock()


def _helper_binary() -> Path:
    global _binary
    if sys.platform != "darwin":
        raise RuntimeError("Screen OCR is available only on macOS")
    if _binary and _binary.exists():
        return _binary
    with _compile_lock:
        if _binary and _binary.exists():
            return _binary
        bundle_root = getattr(sys, "_MEIPASS", None)
        if bundle_root:
            bundled_helper = Path(bundle_root) / "trading_helper" / "screen-ocr"
            if bundled_helper.is_file() and os.access(bundled_helper, os.X_OK):
                _binary = bundled_helper
                return bundled_helper
        source = Path(__file__).with_name("macos_screen_ocr.swift")
        if not source.is_file():
            raise RuntimeError("macOS OCR helper is missing from this installation")
        cache_dir = Path.home() / "Library" / "Caches" / "TradingHelper"
        cache_dir.mkdir(parents=True, exist_ok=True)
        module_cache_dir = cache_dir / "swift-modules"
        module_cache_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
        binary = cache_dir / f"screen-ocr-{digest}"
        if binary.is_file() and os.access(binary, os.X_OK):
            _binary = binary
            return binary
        try:
            result = subprocess.run(
                [
                    "/usr/bin/swiftc",
                    "-O",
                    "-framework",
                    "AppKit",
                    "-framework",
                    "Vision",
                    "-module-cache-path",
                    str(module_cache_dir),
                    str(source),
                    "-o",
                    str(binary),
                ],
                capture_output=True,
                text=True,
                # Development runs may need to compile locally. The packaged app
                # ships a precompiled helper and never pays this startup cost.
                timeout=300,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Timed out while compiling the macOS OCR helper") from exc
        if result.returncode:
            detail = result.stderr.strip().splitlines()
            reason = detail[-1] if detail else "Swift compiler returned an error"
            raise RuntimeError(f"Could not compile the macOS OCR helper: {reason}")
        os.chmod(binary, 0o700)
        _binary = binary
        return binary


def _invoke(*arguments: str) -> Any:
    try:
        result = subprocess.run(
            [str(_helper_binary()), *arguments],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        _logger.warning("OCR helper timed out during %s", arguments[0])
        raise RuntimeError("Screen OCR timed out; try again") from exc
    for line in result.stderr.splitlines():
        if line.startswith("OCR_DIAG "):
            with _diagnostic_lock:
                is_new = line not in _logged_diagnostics
                if is_new:
                    _logged_diagnostics.add(line)
            if is_new:
                _logger.info("%s", line)
        elif line.strip():
            _logger.warning("OCR helper stderr during %s: %s", arguments[0], line.strip())
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("The macOS OCR helper returned an invalid response") from exc
    if result.returncode or (isinstance(payload, dict) and payload.get("error")):
        message = (
            payload.get("error", "Screen OCR failed")
            if isinstance(payload, dict)
            else "Screen OCR failed"
        )
        _logger.warning("OCR helper failed during %s: %s", arguments[0], message)
        raise RuntimeError(message)
    return payload


def list_visible_browser_windows() -> list[dict[str, Any]]:
    """List visible browser windows for local TradingView title/OCR matching."""
    return _invoke("browser-windows")


def list_tradingview_windows() -> list[dict[str, Any]]:
    """List visible browser windows whose macOS title contains TradingView."""
    return [
        window
        for window in list_visible_browser_windows()
        if "tradingview" in str(window.get("title", "")).casefold()
    ]


def read_browser_window(window_id: int) -> dict[str, Any]:
    """OCR one visible browser window using the macOS Vision framework."""
    return _invoke("read", str(window_id))


def select_tradingview_window(windows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Choose the frontmost TradingView window from the system's front-to-back list."""
    return next(
        (
            window
            for window in windows
            if "tradingview" in str(window.get("title", "")).casefold()
        ),
        None,
    )


def select_titleless_browser_windows(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return windows macOS cannot identify by title for local OCR verification."""
    return [window for window in windows if not str(window.get("title", "")).strip()]


def screen_contains_tradingview(observations: list[dict[str, Any]]) -> bool:
    """Check OCR text for TradingView before parsing any titleless browser window."""
    return any(
        re.search(r"trading\s*view|tradingview(?:\.com)?", str(item.get("text", "")), re.I)
        for item in observations
    )


def parse_screen_reading(window_title: str, observations: list[dict[str, Any]]) -> ScreenReading:
    ordered = sorted(
        observations,
        key=lambda item: (-float(item.get("y", 0)), float(item.get("x", 0))),
    )
    lines = [str(item.get("text", "")).strip() for item in ordered]
    lines = [line for line in lines if line]
    combined = "\n".join([window_title, *lines])

    symbol_patterns = (
        (
            r"\b(?:NASDAQ|NYSE|AMEX|ARCA|CBOE|BINANCE|COINBASE|OANDA|FOREXCOM|FX_IDC)"
            r"\s*:\s*([A-Z0-9][A-Z0-9.^_-]{0,14})\b"
        ),
        r"^\s*([A-Z][A-Z0-9.^_-]{1,14})\s*[·|•]\s*(?:[0-9]+[A-Za-z]*|[A-Z]{2,})\b",
        r"^\s*([A-Z][A-Z0-9.^_-]{1,14})\s+\d[\d,.]*\s+(?:[+−-]|\()",
        r"(?:TradingView\s*[-|—]\s*)?([A-Z][A-Z0-9.^_-]{1,14})\s+\d[\d,.]*\s+[+−-]\d",
    )
    symbol = None
    for pattern in symbol_patterns:
        match = re.search(pattern, combined, re.IGNORECASE | re.MULTILINE)
        if match:
            symbol = match.group(1).upper()
            break

    number = r"[$€£]?([0-9][0-9,]*(?:\.[0-9]+)?)"
    price_pattern = re.compile(
        rf"\b(?:last|price|close|C)\s*[:=]?\s*{number}", re.IGNORECASE
    )
    price = None
    confidence = None
    # Bind a quote to the chart header. A watchlist may show several other
    # prices in the same window, so never accept an arbitrary first number.
    symbol_anchor = None
    if symbol:
        symbol_re = re.compile(rf"\b{re.escape(symbol)}\b", re.IGNORECASE)
        symbol_anchor = next(
            (item for item in ordered if symbol_re.search(str(item.get("text", "")))),
            None,
        )
    candidates: list[tuple[float, dict[str, Any], re.Match[str]]] = []
    for item in ordered:
        candidate_text = str(item.get("text", ""))
        match = price_pattern.search(candidate_text)
        if not match and symbol:
            match = re.search(
                rf"^\s*{re.escape(symbol)}\s+{number}\s+[+−-]\s*\d",
                candidate_text,
                re.IGNORECASE,
            )
        if not match:
            continue
        if symbol_anchor is None:
            # A labelled quote is safe without a detected symbol, but require
            # a unique candidate below.
            distance = 0.0
        else:
            dx = abs(float(item.get("x", 0)) - float(symbol_anchor.get("x", 0)))
            dy = abs(float(item.get("y", 0)) - float(symbol_anchor.get("y", 0)))
            distance = dx + dy
            if dx > 0.18 or dy > 0.12:
                continue
        candidates.append((distance, item, match))
    candidates.sort(key=lambda candidate: candidate[0])
    if candidates and (
        len(candidates) == 1 or candidates[1][0] - candidates[0][0] > 0.04
    ):
        _, item, match = candidates[0]
        price = match.group(1)
        confidence = float(item.get("confidence", 0))
    return ScreenReading(symbol, price, confidence, tuple(lines))
