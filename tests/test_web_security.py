from pathlib import Path

WEB = Path("src/trading_helper/web")


def test_service_worker_only_caches_allowlisted_static_assets() -> None:
    source = (WEB / "sw.js").read_text(encoding="utf-8")
    assert "ASSETS.includes(url.pathname)" in source
    assert "'/sw.js'" in source
    for private_path in ("/portfolio", "/paper", "/events", "/settings", "/signals"):
        assert private_path not in source.split("ASSETS=")[1].split(";")[0]


def test_frontend_uses_central_html_escaping() -> None:
    app = (WEB / "app.js").read_text(encoding="utf-8")
    security = (WEB / "security.js").read_text(encoding="utf-8")
    assert "TradingHelperSecurity.escapeHtml" in app
    assert "replace(/[&<>'\"]" in security
