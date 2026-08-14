from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


def _as_bool(value: str, default: bool) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


@dataclass(frozen=True)
class Settings:
    app_host: str
    app_port: int
    database_path: str
    settings_file: str
    market_data_provider: str
    provider_api_key: str
    ntfy_enabled: bool
    ntfy_server: str
    ntfy_topic: str
    auth_enabled: bool
    auth_username: str
    auth_password_hash: str
    session_secret: str
    provider_delay_minutes: int | None = None


@dataclass(frozen=True)
class StrategySettings:
    symbols: tuple[str, ...]
    trend_timeframe: str
    setup_timeframe: str
    minimum_score_to_watch: int
    minimum_score_to_alert: int
    scan_interval_seconds: int
    position_monitor_interval_seconds: int
    daily_scan_hour_utc: int
    candle_limit: int
    stale_after_minutes: int
    portfolio_value: float
    available_capital: float
    portfolio_currency: str
    fx_rates_to_portfolio: dict[str, float]
    max_risk_per_trade_percent: float
    minimum_risk_reward: float
    max_open_positions: int
    max_portfolio_exposure_percent: float
    max_single_position_percent: float
    fractional_shares: bool
    atr_stop_multiplier: float
    cost_profile: str
    max_cost_to_profit_percent: float
    notification_cooldown_minutes: int
    signal_retention_days: int

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> StrategySettings:
        universe = data.get("universe", {})
        scanner = data.get("scanner", {})
        risk = data.get("risk", {})
        trailing = data.get("trailing_stop", {})
        notifications = data.get("notifications", {})
        costs = data.get("costs", {})
        symbols = tuple(
            dict.fromkeys(
                str(item).strip().upper()
                for item in universe.get("symbols", [])
                if str(item).strip()
            )
        )
        if not symbols:
            raise ValueError("universe.symbols must contain at least one valid symbol")
        result = cls(
            symbols=symbols,
            trend_timeframe=str(scanner.get("trend_timeframe", "1d")),
            setup_timeframe=str(scanner.get("setup_timeframe", "1h")),
            minimum_score_to_watch=int(scanner.get("minimum_score_to_watch", 40)),
            minimum_score_to_alert=int(scanner.get("minimum_score_to_alert", 70)),
            scan_interval_seconds=int(scanner.get("scan_interval_seconds", 1800)),
            position_monitor_interval_seconds=int(
                scanner.get("position_monitor_interval_seconds", 300)
            ),
            daily_scan_hour_utc=int(scanner.get("daily_scan_hour_utc", 22)),
            candle_limit=int(scanner.get("candle_limit", 300)),
            stale_after_minutes=int(scanner.get("stale_after_minutes", 30)),
            portfolio_value=float(risk.get("portfolio_value", 100.0)),
            available_capital=float(risk.get("available_capital", 100.0)),
            portfolio_currency=str(risk.get("portfolio_currency", "PLN")),
            fx_rates_to_portfolio={
                str(key).upper(): float(value)
                for key, value in risk.get(
                    "fx_rates_to_portfolio", {"PLN": 1.0, "USD": 4.0}
                ).items()
            },
            max_risk_per_trade_percent=float(risk.get("max_risk_per_trade_percent", 1.0)),
            minimum_risk_reward=float(risk.get("minimum_risk_reward", 2.0)),
            max_open_positions=int(risk.get("max_open_positions", 8)),
            max_portfolio_exposure_percent=float(risk.get("max_portfolio_exposure_percent", 80.0)),
            max_single_position_percent=float(risk.get("max_single_position_percent", 20.0)),
            fractional_shares=bool(risk.get("fractional_shares", True)),
            atr_stop_multiplier=float(trailing.get("atr_multiplier", 2.5)),
            cost_profile=str(costs.get("active_profile", "custom")),
            max_cost_to_profit_percent=float(costs.get("max_cost_to_profit_percent", 30.0)),
            notification_cooldown_minutes=int(notifications.get("cooldown_minutes", 240)),
            signal_retention_days=int(scanner.get("signal_retention_days", 90)),
        )
        if not 0 <= result.minimum_score_to_watch <= result.minimum_score_to_alert <= 100:
            raise ValueError("scanner score thresholds must satisfy 0 <= watch <= alert <= 100")
        positive = (
            result.scan_interval_seconds,
            result.position_monitor_interval_seconds,
            result.candle_limit,
            result.stale_after_minutes,
            result.portfolio_value,
            result.available_capital,
            result.max_risk_per_trade_percent,
            result.max_single_position_percent,
            result.atr_stop_multiplier,
            result.signal_retention_days,
        )
        if any(value <= 0 for value in positive):
            raise ValueError("strategy numeric limits must be positive")
        if not 0 <= result.daily_scan_hour_utc <= 23:
            raise ValueError("daily_scan_hour_utc must be between 0 and 23")
        return result


def load_settings() -> Settings:
    load_dotenv()
    delay_value = os.getenv("MARKET_DATA_DELAY_MINUTES", "").strip()
    return Settings(
        app_host=os.getenv("APP_HOST", "127.0.0.1"),
        app_port=int(os.getenv("APP_PORT", "8787")),
        database_path=os.getenv("TRADING_HELPER_DB", "data/trading_helper.db"),
        settings_file=os.getenv("SETTINGS_FILE", "config/settings.yaml"),
        market_data_provider=os.getenv("MARKET_DATA_PROVIDER", "sample").lower(),
        provider_api_key=os.getenv("MARKET_DATA_API_KEY", ""),
        ntfy_enabled=_as_bool(os.getenv("NTFY_ENABLED", "false"), False),
        ntfy_server=os.getenv("NTFY_SERVER", "https://ntfy.sh").rstrip("/"),
        ntfy_topic=os.getenv("NTFY_TOPIC", ""),
        auth_enabled=_as_bool(os.getenv("AUTH_ENABLED", "false"), False),
        auth_username=os.getenv("AUTH_USERNAME", ""),
        auth_password_hash=os.getenv("AUTH_PASSWORD_HASH", ""),
        session_secret=os.getenv("SESSION_SECRET", ""),
        provider_delay_minutes=int(delay_value) if delay_value else None,
    )


def load_strategy_config(path: str | None = None) -> dict[str, Any]:
    settings = load_settings()
    target = Path(path or settings.settings_file)
    if not target.exists():
        example = Path("config/settings.example.yaml")
        if example.exists():
            target = example
        else:
            raise FileNotFoundError(f"Missing settings file: {target}")
    with target.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Root YAML configuration must be a mapping")
    return data


def load_strategy_settings(path: str | None = None) -> StrategySettings:
    return StrategySettings.from_mapping(load_strategy_config(path))
