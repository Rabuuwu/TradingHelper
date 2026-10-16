from __future__ import annotations

import json
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest
import uvicorn

from trading_helper import api
from trading_helper.auth import AuthManager
from trading_helper.config import Settings, StrategySettings
from trading_helper.market_data.sample import SampleMarketDataProvider
from trading_helper.service import TradingHelperService

playwright = pytest.importorskip("playwright.sync_api")


@pytest.fixture
def web_app(tmp_path, monkeypatch):
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", 0))
        except PermissionError:
            pytest.skip("The sandbox blocks local ports required by browser E2E tests.")
        port = probe.getsockname()[1]
    previous_service = api._service
    previous_auth = api._auth
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
    server = uvicorn.Server(uvicorn.Config(api.app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not server.started and time.monotonic() < deadline:
            time.sleep(0.05)
        assert server.started, "E2E ASGI server did not start"
        yield f"http://127.0.0.1:{port}", service
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        api.configure_service(previous_service)
        api._auth = previous_auth


def open_browser():
    runtime = playwright.sync_playwright().start()
    managed_chromium = Path(runtime.chromium.executable_path).is_file()
    chrome_app = Path("/Applications/Google Chrome.app")
    system_chrome = chrome_app.is_dir()
    if not managed_chromium and not system_chrome:
        runtime.stop()
        pytest.skip("No Playwright Chromium or system Google Chrome is installed.")
    try:
        print("E2E: starting browser", flush=True)
        profile = None
        endpoint = None
        if managed_chromium:
            browser = runtime.chromium.launch(headless=True, timeout=15_000)
            connected_over_cdp = False
        else:
            # LaunchServices must start the signed Chrome app on macOS. Starting
            # its executable directly can abort in HIServices/TransformProcessType.
            profile = tempfile.TemporaryDirectory(
                prefix="trading-helper-e2e-", ignore_cleanup_errors=True
            )
            with socket.socket() as probe:
                try:
                    probe.bind(("127.0.0.1", 0))
                except PermissionError:
                    profile.cleanup()
                    runtime.stop()
                    pytest.skip("The sandbox blocks the local CDP port required by system Chrome.")
                debug_port = probe.getsockname()[1]
            subprocess.Popen(
                [
                    "/usr/bin/open",
                    "-na",
                    str(chrome_app),
                    "--args",
                    "--headless=new",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--remote-allow-origins=*",
                    f"--remote-debugging-port={debug_port}",
                    f"--user-data-dir={profile.name}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            endpoint = f"http://127.0.0.1:{debug_port}"
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                try:
                    with urllib.request.urlopen(
                        f"{endpoint}/json/version", timeout=0.5
                    ) as response:
                        json.load(response)
                    break
                except (OSError, urllib.error.URLError):
                    time.sleep(0.1)
            else:
                profile.cleanup()
                raise RuntimeError(
                    "Google Chrome did not expose its debugging endpoint "
                    "within 15 seconds after LaunchServices launch."
                )
            browser = runtime.chromium.connect_over_cdp(endpoint, timeout=15_000)
            connected_over_cdp = True
    except Exception:
        runtime.stop()
        if profile is not None:
            profile.cleanup()
        raise
    page = browser.new_page()
    page.set_default_timeout(5_000)
    page.set_default_navigation_timeout(10_000)
    print("E2E: browser ready", flush=True)

    return runtime, browser, page, connected_over_cdp, endpoint, profile


def close_browser(runtime, browser, connected_over_cdp, endpoint, profile):
    try:
        if connected_over_cdp:
            browser.new_browser_cdp_session().send("Browser.close")
        else:
            browser.close()
    finally:
        runtime.stop()
        if profile is not None:
            if endpoint is not None:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    try:
                        with urllib.request.urlopen(f"{endpoint}/json/version", timeout=0.2):
                            time.sleep(0.1)
                    except (OSError, urllib.error.URLError):
                        break
            profile.cleanup()


@pytest.mark.e2e
def test_dashboard_escapes_stored_content_and_never_caches_private_api(web_app):
    base_url, _ = web_app
    runtime, browser, page, connected_over_cdp, endpoint, profile = open_browser()
    try:
        page.route("https://unpkg.com/**", lambda route: route.abort())
        print("E2E: opening dashboard", flush=True)
        page.goto(base_url, wait_until="domcontentloaded")
        print("E2E: dashboard loaded; checking watchlist update", flush=True)
        payload = '<img src=x onerror="window.__tradingHelperXss=1">'
        page.evaluate(
            """async payload => {
            const timeout = new Promise((_, reject) => setTimeout(
              () => reject(Error('watchlist request timed out')), 8000));
            const request = fetch('/watchlist', {method:'POST',
              headers:{'Content-Type':'application/json'},
              body:JSON.stringify({symbol:'AAPL',notes:payload})});
            return Promise.race([request, timeout]);
            }""",
            payload,
        )
        navigation = page.get_by_role("navigation", name="Nawigacja główna")
        navigation.locator("#moreMenu").locator("summary").click()
        navigation.get_by_role("button", name="Obserwowane symbole").click()
        page.get_by_text(payload, exact=False).wait_for()
        assert page.evaluate("window.__tradingHelperXss") is None
        page.evaluate(
            """() => {
            const timeout = new Promise((_, reject) => setTimeout(
              () => reject(Error('portfolio request timed out')), 8000));
            return Promise.race([fetch('/portfolio'), timeout]);
            }"""
        )
        cached_paths = page.evaluate(
            """async () => {await Promise.race([navigator.serviceWorker.ready,
            new Promise((_,reject)=>setTimeout(()=>reject(Error('SW timeout')),5000))]);
            const result=[];
            for(const key of await caches.keys()){const cache=await caches.open(key);
            for(const request of await cache.keys())
            result.push(new URL(request.url).pathname)}return result;}"""
        )
        assert "/portfolio" not in cached_paths
        assert all(path in {"/", "/sw.js"} or path.startswith("/static/") for path in cached_paths)
    finally:
        close_browser(runtime, browser, connected_over_cdp, endpoint, profile)


@pytest.mark.e2e
def test_simplified_navigation_keeps_every_area_reachable_and_keyboard_accessible(web_app):
    base_url, _ = web_app
    runtime, browser, page, connected_over_cdp, endpoint, profile = open_browser()
    try:
        page.goto(base_url, wait_until="domcontentloaded")
        navigation = page.get_by_role("navigation", name="Nawigacja główna")
        main_items = ["Pulpit", "Portfel", "Aktywność"]
        for name in main_items:
            assert navigation.get_by_role("button", name=name).count() == 1

        # A tab/Enter user can operate the primary navigation without a pointer.
        portfolio = navigation.get_by_role("button", name="Portfel")
        portfolio.focus()
        page.keyboard.press("Enter")
        assert portfolio.get_attribute("aria-current") == "page"
        assert page.get_by_role("heading", name="Portfel", exact=True).is_visible()

        activity = navigation.get_by_role("button", name="Aktywność")
        activity.click()
        assert activity.get_attribute("aria-current") == "page"
        assert page.get_by_role("heading", name="Aktywność").is_visible()
        trades_filter = page.get_by_role("button", name="Transakcje")
        trades_filter.click()
        assert trades_filter.get_attribute("aria-pressed") == "true"
        assert page.locator("#tradeActivity").is_visible()
        events_filter = page.get_by_role("button", name="System")
        events_filter.click()
        assert events_filter.get_attribute("aria-pressed") == "true"
        assert page.locator("#eventActivity").is_visible()

        more = navigation.locator("#moreMenu").locator("summary")
        more.focus()
        page.keyboard.press("Enter")
        for label, heading in (
            ("Obserwowane symbole", "Obserwowane symbole"),
            ("Stan systemu", "Stan systemu"),
            ("Ustawienia", "Ustawienia"),
        ):
            navigation.get_by_role("button", name=label).click()
            assert page.get_by_role("heading", name=heading).is_visible()
            if label != "Ustawienia":
                more.click()
    finally:
        close_browser(runtime, browser, connected_over_cdp, endpoint, profile)


@pytest.mark.e2e
def test_load_failure_is_explained_and_can_be_retried(web_app):
    base_url, _ = web_app
    runtime, browser, page, connected_over_cdp, endpoint, profile = open_browser()
    try:
        page.route(
            "**/watchlist",
            lambda route: route.fulfill(
                status=503,
                content_type="application/json",
                body='{"detail":"Temporarily unavailable"}',
            ),
        )
        page.goto(base_url, wait_until="domcontentloaded")
        navigation = page.get_by_role("navigation", name="Nawigacja główna")
        navigation.locator("#moreMenu").locator("summary").click()
        navigation.get_by_role("button", name="Obserwowane symbole").click()
        message = page.get_by_role("alert")
        message.wait_for()
        assert "nie udało" in message.inner_text().lower()
        assert message.get_by_role("button", name="Spróbuj ponownie").is_visible()
    finally:
        close_browser(runtime, browser, connected_over_cdp, endpoint, profile)


@pytest.mark.e2e
def test_portfolio_history_failure_does_not_hide_positions(web_app):
    base_url, _ = web_app
    runtime, browser, page, connected_over_cdp, endpoint, profile = open_browser()
    try:
        page.route(
            "**/portfolio/history?**",
            lambda route: route.fulfill(
                status=503,
                content_type="application/json",
                body='{"detail":"History unavailable"}',
            ),
        )
        page.goto(base_url, wait_until="domcontentloaded")
        page.get_by_role("navigation", name="Nawigacja główna").get_by_role(
            "button", name="Portfel"
        ).click()
        page.locator("#positions").get_by_text("Brak otwartych pozycji.").wait_for()
        page.locator("#portfolioChart").get_by_text(
            "Nie udało się wczytać danych.", exact=False
        ).wait_for()
    finally:
        close_browser(runtime, browser, connected_over_cdp, endpoint, profile)


@pytest.mark.e2e
def test_paper_reset_explains_rejection_in_the_form(web_app):
    base_url, _ = web_app
    runtime, browser, page, connected_over_cdp, endpoint, profile = open_browser()
    try:
        page.goto(base_url, wait_until="domcontentloaded")
        page.get_by_role("navigation", name="Nawigacja główna").get_by_role(
            "button", name="Portfel"
        ).click()
        advanced = page.locator(".advanced-settings")
        advanced.get_by_text("Ustawienia symulatora PAPER", exact=True).click()
        form = page.locator("#paperCapitalForm")
        explanation = advanced.locator('p[data-i18n="paperSettingsHelp"]')
        assert explanation.is_visible()
        explanation_text = explanation.inner_text().lower()
        assert "po zamknięciu wszystkich symulowanych pozycji" in explanation_text or (
            "after closing all simulated positions" in explanation_text
        )

        page.route(
            "**/paper/account",
            lambda route: (
                route.fulfill(
                    status=422,
                    content_type="application/json",
                    body='{"detail":"Zamknij otwarte pozycje PAPER przed resetem."}',
                )
                if route.request.method == "PUT"
                else route.continue_()
            ),
        )
        form.get_by_label("Kapitał początkowy").fill("25000")
        form.get_by_role("button", name="Zmień kapitał").click()
        confirmation = page.get_by_role("dialog")
        assert "Dostępna gotówka" in confirmation.inner_text()
        assert "Otwarte pozycje" in confirmation.inner_text()
        confirmation.get_by_role("button", name="Potwierdź reset").click()
        error = page.locator("#paperResetError")
        error.wait_for()
        assert "otwarte pozycje" in error.inner_text().lower()
    finally:
        close_browser(runtime, browser, connected_over_cdp, endpoint, profile)


@pytest.mark.e2e
def test_private_api_still_requires_authentication(web_app):
    base_url, service = web_app
    protected_settings = Settings(
        "127.0.0.1",
        0,
        service.settings.database_path,
        service.settings.settings_file,
        "sample",
        "",
        False,
        "https://ntfy.sh",
        "",
        True,
        "test-user",
        "not-used-by-this-test",
        "test-session-secret",
    )
    api._auth = AuthManager(protected_settings, service.repository)
    runtime, browser, page, connected_over_cdp, endpoint, profile = open_browser()
    try:
        page.goto(base_url, wait_until="domcontentloaded")
        response = page.request.get(f"{base_url}/portfolio")
        assert response.status == 401
    finally:
        close_browser(runtime, browser, connected_over_cdp, endpoint, profile)
