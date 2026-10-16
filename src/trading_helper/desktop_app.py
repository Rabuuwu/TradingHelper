from __future__ import annotations

import logging
import os
import shutil
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)


def _resource_root() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    return Path(bundle_root) if bundle_root else Path(__file__).resolve().parents[2]


def user_data_dir(platform: str | None = None, environ: dict[str, str] | None = None) -> Path:
    """Return the per-user persistent data directory for this desktop app."""
    platform = platform or sys.platform
    environ = environ if environ is not None else os.environ
    home = Path.home()
    if platform == "darwin":
        return home / "Library" / "Application Support" / "TradingHelper"
    if platform == "win32":
        appdata = Path(environ.get("APPDATA") or home / "AppData" / "Roaming")
        return appdata / "TradingHelper"
    data_home = Path(environ.get("XDG_DATA_HOME") or home / ".local" / "share")
    return data_home / "TradingHelper"


def prepare_user_data(data_dir: Path, resource_root: Path | None = None) -> None:
    """Create persistent first-run configuration without overwriting user files."""
    root = resource_root or _resource_root()
    (data_dir / "config").mkdir(parents=True, exist_ok=True)
    (data_dir / "data").mkdir(parents=True, exist_ok=True)
    package_defaults = Path(__file__).with_name("defaults")
    defaults = (
        (
            (
                root / "config" / "settings.yaml",
                root / "config" / "settings.example.yaml",
                package_defaults / "settings.example.yaml",
            ),
            data_dir / "config" / "settings.yaml",
        ),
        (
            (root / ".env", root / ".env.example", package_defaults / "env.example"),
            data_dir / ".env",
        ),
    )
    for sources, target in defaults:
        if not target.exists():
            source = next((candidate for candidate in sources if candidate.is_file()), None)
            if source is not None:
                shutil.copyfile(source, target)
    env_path = data_dir / ".env"
    if env_path.exists():
        if os.name == "posix":
            env_path.chmod(0o600)


def configure_desktop_logging(data_dir: Path) -> None:
    log_dir = data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        log_dir / "desktop-app.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


def _health(url: str, timeout: float = 0.4) -> bool:
    try:
        with urllib.request.urlopen(f"{url}/health", timeout=timeout) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def _bound_local_socket(host: str, preferred_port: int) -> socket.socket:
    candidates = [preferred_port, 0] if preferred_port else [0]
    last_error: OSError | None = None
    for port in candidates:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((host, port))
            listener.listen(128)
            return listener
        except OSError as exc:
            last_error = exc
            listener.close()
    raise RuntimeError(f"Could not bind local TradingHelper server: {last_error}")


class ScreenReadingBridge:
    """Poll local macOS OCR and expose only the current reading to the UI."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._state: dict[str, Any] = {
            "symbol": None,
            "price": None,
            "message": "Wyszukuję widoczne okno TradingView…",
            "updated": None,
        }
        self._thread = threading.Thread(target=self._poll, name="screen-ocr", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def screen_reading(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def _set_state(self, **values: Any) -> None:
        with self._lock:
            self._state = {**self._state, **values}

    def _poll(self) -> None:
        from trading_helper.screen_ocr import (
            list_visible_browser_windows,
            parse_screen_reading,
            read_browser_window,
            screen_contains_tradingview,
            select_titleless_browser_windows,
            select_tradingview_window,
        )

        last_error: str | None = None
        last_ocr_diagnostic: tuple[str, int, bool, bool] | None = None
        if sys.platform != "darwin":
            self._set_state(
                symbol=None,
                price=None,
                message="Lokalny odczyt OCR ekranu jest dostępny w aplikacji macOS.",
                updated=datetime.now().astimezone().strftime("%H:%M:%S"),
            )
            return
        while not self._stop.is_set():
            try:
                windows = list_visible_browser_windows()
                window = select_tradingview_window(windows)
                title_matched = window is not None
                result = None
                if window is not None:
                    result = read_browser_window(int(window["id"]))
                else:
                    # Firefox can expose an empty CGWindowName on macOS. In that
                    # case inspect candidate browser windows locally and accept
                    # one only if OCR sees the TradingView brand in its contents.
                    for candidate in select_titleless_browser_windows(windows):
                        candidate_result = read_browser_window(int(candidate["id"]))
                        observations = candidate_result.get("observations", [])
                        verified = screen_contains_tradingview(observations)
                        diagnostic = (
                            str(candidate.get("app", "unknown")),
                            len(observations),
                            verified,
                            False,
                        )
                        if diagnostic != last_ocr_diagnostic:
                            _logger.info(
                                "OCR_DIAG titleless_browser=%s observations=%d "
                                "tradingview_screen_match=%s price_detected=false",
                                *diagnostic[:3],
                            )
                            last_ocr_diagnostic = diagnostic
                        if verified:
                            window = candidate
                            result = candidate_result
                            break
                if window is None:
                    self._set_state(
                        symbol=None,
                        price=None,
                        message="Czekam na TradingView w widocznym oknie przeglądarki.",
                        updated=datetime.now().astimezone().strftime("%H:%M:%S"),
                    )
                    delay = 5
                else:
                    assert result is not None
                    reading = parse_screen_reading(
                        window.get("title", ""), result.get("observations", [])
                    )
                    valid_price = reading.price and (
                        reading.confidence is None or reading.confidence >= 0.5
                    )
                    diagnostic = (
                        str(window.get("app", "unknown")),
                        len(result.get("observations", [])),
                        bool(valid_price),
                        title_matched,
                    )
                    if diagnostic != last_ocr_diagnostic:
                        _logger.info(
                            "OCR_DIAG selected_browser=%s observations=%d price_detected=%s "
                            "title_match=%s",
                            *diagnostic,
                        )
                        last_ocr_diagnostic = diagnostic
                    last_error = None
                    self._set_state(
                        symbol=reading.symbol,
                        price=reading.price if valid_price else None,
                        confidence=reading.confidence,
                        message=(
                            f"Okno: {window.get('title', 'TradingView')}"
                            if valid_price
                            else "Nie rozpoznano ceny. Ustaw wykres tak, by cena była widoczna."
                        ),
                        updated=datetime.now().astimezone().strftime("%H:%M:%S"),
                    )
                    delay = 2.5
            except (RuntimeError, OSError, TimeoutError) as exc:
                error = str(exc)
                if error != last_error:
                    _logger.warning("OCR polling failed: %s", error)
                    last_error = error
                self._set_state(
                    symbol=None,
                    price=None,
                    message=error,
                    updated=datetime.now().astimezone().strftime("%H:%M:%S"),
                )
                delay = 10
            self._stop.wait(delay)


SCREEN_READING_SCRIPT = r"""
(() => {
  if (document.getElementById('th-desktop-screen-reading')) return;
  const style = document.createElement('style');
  style.textContent = `
    #th-desktop-screen-reading{position:fixed;z-index:2147483000;right:18px;bottom:18px;
      width:min(300px,calc(100vw - 36px));padding:13px 15px;border:1px solid #334155;
      border-radius:12px;background:#101923;color:#f8fafc;box-shadow:0 8px 30px #0005;
      font:13px/1.45 -apple-system,BlinkMacSystemFont,sans-serif;}
    #th-desktop-screen-reading .th-title{font-size:11px;letter-spacing:.08em;
      text-transform:uppercase;
      color:#a8bacb;font-weight:700;margin-bottom:6px}
    #th-desktop-screen-reading .th-price{font-size:22px;font-weight:700;
      line-height:1.2;margin:3px 0}
    #th-desktop-screen-reading .th-meta{color:#bdc9d5;font-size:12px}
    #th-desktop-screen-reading .th-time{color:#93a4b4;font-size:11px;margin-top:4px}
    @media(max-width:700px){#th-desktop-screen-reading{right:10px;bottom:10px}}
  `;
  document.head.append(style);
  const panel = document.createElement('aside');
  panel.id = 'th-desktop-screen-reading';
  panel.setAttribute('aria-label', 'Odczyt ekranu TradingView');
  panel.innerHTML = '<div class="th-title">TradingHelper · ekran</div>' +
    '<div class="th-symbol">Szukam TradingView…</div><div class="th-price">—</div>' +
    '<div class="th-meta">Odczyt OCR pozostaje na tym komputerze.</div><div class="th-time"></div>';
  document.body.append(panel);
  let inFlight = false;
  const update = async () => {
    if (inFlight || !window.pywebview?.api?.screen_reading) return;
    inFlight = true;
    try {
      const data = await window.pywebview.api.screen_reading();
      panel.querySelector('.th-symbol').textContent = data.symbol
        ? `Symbol: ${data.symbol}` : data.message;
      panel.querySelector('.th-price').textContent = data.price ? `~ ${data.price}` : '—';
      panel.querySelector('.th-meta').textContent = data.symbol
        ? data.message : 'Odczyt OCR pozostaje na tym komputerze.';
      panel.querySelector('.th-time').textContent = data.updated ? `Odczyt: ${data.updated}` : '';
    } catch (_) {}
    finally { inFlight = false; }
  };
  window.addEventListener('pywebviewready', update, {once:true});
  setInterval(update, 1200);
})();
"""


def run_desktop_app() -> None:  # pragma: no cover - native window needs a desktop session
    if sys.platform not in {"darwin", "win32"}:
        raise SystemExit("TradingHelper desktop bundle supports macOS and Windows.")

    data_dir = user_data_dir()
    prepare_user_data(data_dir)
    configure_desktop_logging(data_dir)
    os.environ["APP_ENV_FILE"] = str(data_dir / ".env")
    os.environ["SETTINGS_FILE"] = str(data_dir / "config" / "settings.yaml")
    os.environ["TRADING_HELPER_DB"] = str(data_dir / "data" / "trading_helper.db")
    os.environ["APP_HOST"] = "127.0.0.1"

    import uvicorn
    import webview

    from trading_helper import api
    from trading_helper.config import load_settings
    from trading_helper.main import build_service, ensure_safe_bind

    settings = load_settings()
    ensure_safe_bind(settings.app_host, settings.auth_enabled)
    base_url = f"http://{settings.app_host}:{settings.app_port}"
    owned_server = False
    server: uvicorn.Server | None = None
    server_thread: threading.Thread | None = None
    service = None

    if not _health(base_url):
        listener = _bound_local_socket(settings.app_host, settings.app_port)
        port = int(listener.getsockname()[1])
        base_url = f"http://{settings.app_host}:{port}"
        service = build_service()
        api.configure_service(service)
        server = uvicorn.Server(
            uvicorn.Config(
                api.app,
                host=settings.app_host,
                port=port,
                log_level="info",
                log_config=None,
            )
        )

        def serve() -> None:
            import asyncio

            asyncio.run(server.serve(sockets=[listener]))

        server_thread = threading.Thread(target=serve, name="trading-helper-api", daemon=True)
        server_thread.start()
        owned_server = True
        deadline = time.monotonic() + 15
        while not server.started and time.monotonic() < deadline:
            time.sleep(0.05)
        if not server.started:
            server.should_exit = True
            raise RuntimeError("TradingHelper API did not start.")
        scheduler_thread = threading.Thread(
            target=service.run_forever,
            kwargs={"install_signal_handlers": False},
            name="trading-helper-scheduler",
            daemon=True,
        )
        scheduler_thread.start()
    else:
        scheduler_thread = None

    bridge = ScreenReadingBridge()
    bridge.start()
    window = webview.create_window(
        "TradingHelper",
        base_url,
        width=1320,
        height=860,
        min_size=(900, 640),
        background_color="#f4f6f8",
        text_select=True,
        js_api=bridge,
    )
    window.events.loaded += lambda: window.evaluate_js(SCREEN_READING_SCRIPT)
    try:
        webview.start(gui="cocoa" if sys.platform == "darwin" else None)
    finally:
        bridge.stop()
        if owned_server and server is not None:
            if service is not None:
                service.stop_event.set()
            server.should_exit = True
            if server_thread is not None:
                server_thread.join(timeout=10)
            if scheduler_thread is not None:
                scheduler_thread.join(timeout=5)


if __name__ == "__main__":
    run_desktop_app()
