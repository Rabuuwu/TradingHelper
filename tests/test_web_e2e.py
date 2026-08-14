from __future__ import annotations

import socket
import threading
import time

import pytest
import uvicorn

from trading_helper import api
from trading_helper.auth import AuthManager
from trading_helper.config import Settings, StrategySettings
from trading_helper.market_data.sample import SampleMarketDataProvider
from trading_helper.service import TradingHelperService

playwright = pytest.importorskip("playwright.sync_api")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.mark.e2e
def test_dashboard_escapes_stored_content_and_never_caches_private_api(tmp_path, monkeypatch):
    database = str(tmp_path / "e2e.db")
    monkeypatch.setenv("TRADING_HELPER_DB", database)
    monkeypatch.setenv("SETTINGS_FILE", "config/settings.example.yaml")
    settings = Settings(
        "127.0.0.1",
        0,
        database,
        "config/settings.example.yaml",
        "sample",
        "",
        False,
        "https://ntfy.sh",
        "",
        False,
        "",
        "",
        "",
    )
    service = TradingHelperService(
        settings,
        StrategySettings.from_mapping({"universe": {"symbols": ["AAPL"]}}),
        SampleMarketDataProvider(),
        {"costs": {"profiles": {"custom": {}}}},
    )
    api.configure_service(service)
    api._auth = AuthManager(settings, service.repository)
    port = free_port()
    server = uvicorn.Server(uvicorn.Config(api.app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 10
    while not server.started and time.time() < deadline:
        time.sleep(0.05)
    assert server.started
    try:
        with playwright.sync_playwright() as runtime:
            browser = runtime.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(5_000)
            page.route("https://unpkg.com/**", lambda route: route.abort())
            page.goto(f"http://127.0.0.1:{port}", wait_until="domcontentloaded")
            payload = '<img src=x onerror="window.__tradingHelperXss=1">'
            page.evaluate(
                """async payload => fetch('/watchlist',{method:'POST',headers:{
                'Content-Type':'application/json'},body:JSON.stringify({symbol:'AAPL',notes:payload})})""",
                payload,
            )
            page.click('nav button[data-view="watchlist"]')
            page.wait_for_selector("#watchItems .row")
            assert page.locator("#watchItems").inner_text().find(payload) >= 0
            assert page.evaluate("window.__tradingHelperXss") is None
            page.evaluate("fetch('/portfolio')")
            cached_paths = page.evaluate(
                """async () => {await Promise.race([navigator.serviceWorker.ready,
                new Promise((_,reject)=>setTimeout(()=>reject(Error('SW timeout')),5000))]);
                const result=[];
                for(const key of await caches.keys()){const cache=await caches.open(key);
                for(const request of await cache.keys())
                result.push(new URL(request.url).pathname)}return result;}"""
            )
            assert "/portfolio" not in cached_paths
            assert all(
                path in {"/", "/sw.js"} or path.startswith("/static/")
                for path in cached_paths
            )
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=10)
