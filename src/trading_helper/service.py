from __future__ import annotations

import json
import logging
import signal
import threading
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

from trading_helper.alerts.ntfy import NtfyPublisher
from trading_helper.alerts.service import AlertService
from trading_helper.config import Settings, StrategySettings, load_strategy_config
from trading_helper.database import Repository, utc_now
from trading_helper.fx import FxRateService
from trading_helper.market_data.cache import CachedMarketData
from trading_helper.market_data.factory import create_provider
from trading_helper.market_data.provider import MarketDataProvider
from trading_helper.paper import PaperPortfolioService
from trading_helper.portfolio import PositionMonitor
from trading_helper.risk.costs import CostEstimate, CostProfile, FeeCalculator
from trading_helper.risk.manager import check_trade_feasibility, risk_reward_ratio
from trading_helper.scanner.scanners import build_snapshot
from trading_helper.signal_engine import score_setup, snapshot_details
from trading_helper.signals import SignalQueryService
from trading_helper.soak import SoakMonitor

logger = logging.getLogger(__name__)


class TradingHelperService:
    def __init__(
        self,
        settings: Settings,
        strategy: StrategySettings,
        provider: MarketDataProvider | None = None,
        raw_config: dict[str, Any] | None = None,
    ) -> None:
        self.settings = settings
        self.strategy = strategy
        self.raw_config = raw_config or load_strategy_config()
        self.repository = Repository(settings.database_path)
        self.provider = provider or create_provider(settings, self.repository)
        if self.provider.name != "sample":
            purged = self.repository.purge_market_cache_except(self.provider.name)
            if purged["candles"] or purged["quotes"]:
                self.repository.event(
                    "market_cache_provider_cleanup",
                    "Removed cache rows belonging to a different market data provider",
                    details=purged,
                )
        self.market_data = CachedMarketData(
            self.provider,
            self.repository,
            ttl_seconds=min(strategy.scan_interval_seconds, 900),
        )
        fx_config = self.raw_config.get("fx", {})
        self.fx = FxRateService(
            self.repository,
            self.provider,
            strategy.fx_rates_to_portfolio,
            strategy.portfolio_currency,
            cache_minutes=int(fx_config.get("cache_minutes", 60)),
            stale_after_minutes=int(fx_config.get("stale_after_minutes", 1440)),
        )
        profile_data = (
            self.raw_config.get("costs", {}).get("profiles", {}).get(strategy.cost_profile, {})
        )
        self.fee_calculator = FeeCalculator(
            CostProfile.from_mapping(strategy.cost_profile, profile_data)
        )
        publisher = None
        if settings.ntfy_enabled:
            publisher = NtfyPublisher(settings.ntfy_server, settings.ntfy_topic)
        self.alerts = AlertService(
            self.repository, publisher, strategy.notification_cooldown_minutes
        )
        self.position_monitor = PositionMonitor(
            self.repository, self.market_data, strategy.atr_stop_multiplier
        )
        self.stop_event = threading.Event()
        self.started_at = datetime.now(UTC)

    def runtime_setting(self, key: str, default: Any) -> Any:
        rows = self.repository.rows("SELECT value FROM app_settings WHERE key=?", (key,))
        if not rows:
            return default
        try:
            return json.loads(rows[0]["value"])
        except (TypeError, json.JSONDecodeError):
            return default

    def provider_credit_status(self) -> dict[str, Any] | None:
        budget = getattr(self.provider, "credit_budget", None)
        return budget.status() if budget else None

    def self_check(self) -> list[str]:
        warnings: list[str] = []
        if self.settings.market_data_provider == "sample":
            warnings.append("Using offline SAMPLE market data; signals are simulation only")
        if self.settings.ntfy_enabled and not self.settings.ntfy_topic:
            warnings.append("ntfy is enabled but NTFY_TOPIC is empty")
        if self.settings.auth_enabled and (
            not self.settings.auth_username
            or not self.settings.auth_password_hash
            or not self.settings.session_secret
        ):
            warnings.append("Authentication is enabled but credentials are incomplete")
        return warnings

    def scan_once(self) -> dict[str, int]:
        symbols = self.scan_symbols()
        run_id = self.repository.start_scan(len(symbols), self.provider.name)
        self.repository.event("scanner_started", f"Scan {run_id} started")
        succeeded = failed = 0
        for symbol in symbols:
            try:
                self._scan_symbol(symbol, run_id)
                succeeded += 1
            except Exception as exc:
                failed += 1
                logger.exception("Scan failed for %s", symbol)
                self.repository.set_state(f"symbol:{symbol}", f"ERROR: {exc}")
                self.repository.event("provider_error", f"{symbol}: {exc}", "ERROR")
        status = "COMPLETED" if failed == 0 else ("PARTIAL" if succeeded else "FAILED")
        self.repository.finish_scan(run_id, succeeded, failed, status)
        if succeeded:
            self.repository.set_state("last_successful_scan", utc_now())
        self.repository.set_state("scanner", status)
        self.repository.set_state("provider", "OK" if succeeded else "ERROR")
        self.repository.event(
            "scanner_finished",
            f"Scan {run_id}: {status}",
            details={"ok": succeeded, "failed": failed},
        )
        self.alerts.dispatch_pending()
        deleted = SignalQueryService(self.repository).prune(self.strategy.signal_retention_days)
        if deleted:
            self.repository.event(
                "signal_history_pruned", f"Removed {deleted} expired signal records"
            )
        return {"run_id": run_id, "succeeded": succeeded, "failed": failed}

    def scan_symbols(self) -> tuple[str, ...]:
        dynamic = self.repository.rows(
            """SELECT symbol FROM watchlist UNION
            SELECT symbol FROM manual_positions WHERE status='OPEN'"""
        )
        return tuple(dict.fromkeys((*self.strategy.symbols, *(row["symbol"] for row in dynamic))))

    def _scan_symbol(self, symbol: str, run_id: int) -> int:
        trend_batch = self.market_data.get_candles(
            symbol, self.strategy.trend_timeframe, self.strategy.candle_limit
        )
        setup_batch = self.market_data.get_candles(
            symbol, self.strategy.setup_timeframe, self.strategy.candle_limit
        )
        info = self.provider.get_symbol_info(symbol)
        quote = self.market_data.get_quote(symbol)
        self.repository.upsert_symbol(
            info.symbol,
            info.name,
            info.asset_type,
            info.currency,
            info.exchange,
            self.provider.name,
        )
        trend = build_snapshot(trend_batch.frame)
        setup = build_snapshot(setup_batch.frame)
        combined = replace(
            setup,
            ema20=trend.ema20,
            ema50=trend.ema50,
            ema200=trend.ema200,
            trend_structure=trend.trend_structure,
        )
        entry_low = max(quote.price - setup.atr * 0.25, 0.0001)
        entry_high = quote.price + setup.atr * 0.25
        stop = max(quote.price - setup.atr * self.strategy.atr_stop_multiplier, 0.0001)
        risk_per_unit = quote.price - stop
        target_1 = quote.price + risk_per_unit * 2
        target_2 = quote.price + risk_per_unit * 3
        rr = risk_reward_ratio(quote.price, stop, target_2)
        fx = self.fx.get_rate(info.currency, self.strategy.portfolio_currency)
        fx_rate = fx.rate
        warnings: list[str] = []
        if fx.status == "FALLBACK":
            warnings.append(
                f"FX {info.currency}/{self.strategy.portfolio_currency} uses YAML fallback"
            )
        elif fx.status == "STALE":
            warnings.append(f"FX {info.currency}/{self.strategy.portfolio_currency} is stale")
        portfolio_value = float(
            self.runtime_setting("portfolio_value", self.strategy.portfolio_value)
        )
        risk_percent = float(
            self.runtime_setting("risk_percent", self.strategy.max_risk_per_trade_percent)
        )
        available_in_instrument_currency = (
            min(self.strategy.available_capital, portfolio_value) / fx_rate
        )
        portfolio_in_instrument_currency = portfolio_value / fx_rate
        preliminary = check_trade_feasibility(
            portfolio_in_instrument_currency,
            available_in_instrument_currency,
            risk_percent,
            quote.price,
            stop,
            self.strategy.max_single_position_percent,
            fractional=self.strategy.fractional_shares,
            expected_gross_profit=1,
            max_cost_to_profit_percent=100,
        )
        quantity = preliminary.sizing.quantity
        if quantity <= 0:
            costs = CostEstimate(0, 0, 0, 0, 0, 0, 0, 0)
            feasibility = preliminary
        else:
            costs = self.fee_calculator.estimate(
                quote.price,
                target_2,
                quantity,
                requires_fx=info.currency != self.strategy.portfolio_currency,
            )
            feasibility = check_trade_feasibility(
                portfolio_in_instrument_currency,
                available_in_instrument_currency,
                risk_percent,
                quote.price,
                stop,
                self.strategy.max_single_position_percent,
                fractional=self.strategy.fractional_shares,
                estimated_total_cost=costs.estimated_total_cost,
                expected_gross_profit=costs.gross_expected_profit,
                max_cost_to_profit_percent=self.strategy.max_cost_to_profit_percent,
            )
        score = score_setup(
            combined,
            risk_reward=rr,
            data_timestamp=setup_batch.provenance.timestamp,
            is_delayed=setup_batch.provenance.is_delayed,
            delay_minutes=setup_batch.provenance.delay_minutes,
        )
        warnings.extend(score.warnings)
        age_minutes = (datetime.now(UTC) - setup_batch.provenance.timestamp).total_seconds() / 60
        if age_minutes > self.strategy.stale_after_minutes:
            warnings.append(f"DATA STALE: last candle is {age_minutes:.0f} minutes old")
            self.repository.event("data_stale", f"{symbol} data is stale", "WARNING")
        if not feasibility.feasible:
            warnings.append(feasibility.reason)
        payload = {
            "scan_run_id": run_id,
            "created_at": utc_now(),
            "data_timestamp": setup_batch.provenance.timestamp.isoformat(),
            "symbol": symbol,
            "name": info.name,
            "score": score.score,
            "label": score.classification,
            "price": quote.price,
            "timeframe": self.strategy.setup_timeframe,
            "data_source": setup_batch.provenance.source,
            "is_delayed": int(setup_batch.provenance.is_delayed),
            "delay_minutes": setup_batch.provenance.delay_minutes,
            "entry_low": round(entry_low, 4),
            "entry_high": round(entry_high, 4),
            "stop_price": round(stop, 4),
            "target_price": round(target_1, 4),
            "target_price_2": round(target_2, 4),
            "risk_reward": round(rr, 2),
            "recommended_quantity": quantity,
            "estimated_total_cost": costs.estimated_total_cost,
            "expected_net_profit": costs.expected_net_profit,
            "feasibility_status": feasibility.status,
            "reasons_json": json.dumps(score.reasons),
            "warnings_json": json.dumps(warnings),
            "breakdown_json": json.dumps(score.breakdown),
            "details_json": json.dumps(
                {
                    "indicators": snapshot_details(combined),
                    "costs": costs.__dict__,
                    "currency": info.currency,
                    "fx_rate_to_portfolio": fx_rate,
                    "fx_rate_source": fx.source,
                    "fx_rate_status": fx.status,
                    "fx_rate_timestamp": fx.data_timestamp.isoformat(),
                }
            ),
        }
        signal_id = self.repository.add_signal(payload)
        self.repository.set_state(
            "last_market_data_update", setup_batch.provenance.timestamp.isoformat()
        )
        self.repository.set_state(f"symbol:{symbol}", "OK")
        self.repository.event(
            "signal_created",
            f"{symbol}: {score.classification}",
            details={"signal_id": signal_id, "score": score.score},
        )
        if score.score >= self.strategy.minimum_score_to_alert:
            data_status = "DELAYED" if setup_batch.provenance.is_delayed else "CURRENT"
            body = (
                f"Score {score.score}/100\nAnalyzed price: {quote.price:.2f} {info.currency}\n"
                f"Entry: {entry_low:.2f}-{entry_high:.2f}\nStop: {stop:.2f}\n"
                f"TP1: {target_1:.2f}\nTP2: {target_2:.2f}\nR:R 1:{rr:.1f}\n"
                f"Data: {data_status}\nVerify the current price in your broker before trading."
            )
            self.alerts.enqueue(
                score.classification,
                symbol,
                f"{symbol} — {score.classification}",
                body,
                setup_batch.provenance.timestamp.isoformat(),
            )
        return signal_id

    def monitor_positions(self) -> list[dict[str, Any]]:
        results = self.position_monitor.run()
        paper = PaperPortfolioService(
            self.repository,
            float(self.runtime_setting("portfolio_value", self.strategy.portfolio_value)),
            self.strategy.portfolio_currency,
        )
        account = paper.account()
        paper_market_value = 0.0
        for result in results:
            fx = self.fx.get_rate(result["currency"], self.strategy.portfolio_currency)
            if result["mode"] == "PAPER":
                paper_market_value += result["current_price"] * result["quantity"] * fx.rate
            if result["monitor_status"] != "HOLD":
                self.alerts.enqueue(
                    result["monitor_status"],
                    result["symbol"],
                    f"{result['symbol']} — {result['monitor_status']}",
                    (
                        f"Price {result['current_price']:.2f}; "
                        f"trailing stop {result['trailing_stop']:.2f}"
                    ),
                    f"{result['id']}:{result['monitor_status']}:{result['data_timestamp']}",
                )
        equity = float(account["cash_balance"]) + paper_market_value
        open_cost_rows = self.repository.rows(
            """SELECT COALESCE(-SUM(l.cash_change),0) AS cost
            FROM paper_ledger l JOIN manual_positions p ON p.id=l.position_id
            WHERE l.transaction_type='BUY' AND p.mode='PAPER' AND p.status='OPEN'"""
        )
        open_cost = float(open_cost_rows[0]["cost"])
        unrealized = paper_market_value - open_cost
        realized = float(account["realized_pnl"])
        total_pnl = equity - float(account["initial_cash"])
        self.repository.execute(
            """INSERT INTO portfolio_snapshots(timestamp,total_value,invested_value,
            unrealized_pnl,realized_pnl,total_pnl,cash_balance,currency)
            VALUES(?,?,?,?,?,?,?,?)""",
            (
                utc_now(),
                round(equity, 4),
                round(paper_market_value, 4),
                round(unrealized, 4),
                round(realized, 4),
                round(total_pnl, 4),
                round(float(account["cash_balance"]), 4),
                self.strategy.portfolio_currency,
            ),
        )
        self.alerts.dispatch_pending()
        return results

    def watchdog(self, scan_interval: int) -> str:
        rows = self.repository.rows(
            "SELECT value FROM system_state WHERE key='last_successful_scan'"
        )
        if not rows:
            return "STARTING"
        last_scan = datetime.fromisoformat(rows[0]["value"])
        age = (datetime.now(UTC) - last_scan).total_seconds()
        if age > max(scan_interval * 2, 3600):
            self.repository.set_state("watchdog", "DEGRADED")
            self.repository.event(
                "watchdog_warning",
                "Scanner missed its expected window",
                "WARNING",
                {"age_seconds": int(age)},
            )
            SoakMonitor(self.repository).record("UNHEALTHY", {"watchdog": "DEGRADED"})
            return "DEGRADED"
        self.repository.set_state("watchdog", "HEALTHY")
        SoakMonitor(self.repository).record("HEALTHY", {"watchdog": "HEALTHY"})
        return "HEALTHY"

    def run_forever(self) -> None:
        def stop_handler(signum: int, frame: object) -> None:
            logger.info("Received signal %s, stopping", signum)
            self.stop_event.set()

        signal.signal(signal.SIGTERM, stop_handler)
        signal.signal(signal.SIGINT, stop_handler)
        self.repository.event("server_started", "TradingHelper scheduler started")
        next_scan = next_monitor = next_watchdog = 0.0
        daily_state = self.repository.rows(
            "SELECT value FROM system_state WHERE key='last_daily_scan'"
        )
        last_daily_scan = (
            datetime.fromisoformat(daily_state[0]["value"]).date().isoformat()
            if daily_state
            else ""
        )
        last_closed_monitor = ""
        try:
            while not self.stop_event.is_set():
                now = datetime.now(UTC).timestamp()
                scanner_enabled = bool(self.runtime_setting("scanner_enabled", True))
                scan_interval = int(
                    self.runtime_setting(
                        "scan_interval_seconds", self.strategy.scan_interval_seconds
                    )
                )
                if self.provider.name == "twelve_data":
                    scan_interval = max(scan_interval, 3600)
                utc_now_value = datetime.now(UTC)
                daily_key = utc_now_value.date().isoformat()
                market_open = self.provider.get_market_status().status == "OPEN"
                if scanner_enabled and market_open and now >= next_scan:
                    try:
                        self.scan_once()
                    except Exception as exc:
                        logger.exception("Scheduled scan failed")
                        self.repository.set_state("scanner", f"ERROR: {exc}")
                        self.repository.event("scanner_failed", str(exc), "ERROR")
                    next_scan = now + scan_interval
                if (
                    scanner_enabled
                    and not market_open
                    and utc_now_value.weekday() < 5
                    and utc_now_value.hour >= self.strategy.daily_scan_hour_utc
                    and last_daily_scan != daily_key
                ):
                    try:
                        self.scan_once()
                        last_daily_scan = daily_key
                        self.repository.set_state("last_daily_scan", utc_now())
                    except Exception as exc:
                        logger.exception("Daily scan failed")
                        self.repository.event("daily_scan_failed", str(exc), "ERROR")
                if not market_open and scanner_enabled:
                    self.repository.set_state("scanner", "IDLE_MARKET_CLOSED")
                monitor_due = market_open and now >= next_monitor
                closed_monitor_due = (
                    not market_open
                    and utc_now_value.weekday() < 5
                    and utc_now_value.hour >= self.strategy.daily_scan_hour_utc
                    and last_closed_monitor != daily_key
                )
                if monitor_due or closed_monitor_due:
                    try:
                        self.monitor_positions()
                        if closed_monitor_due:
                            last_closed_monitor = daily_key
                    except Exception as exc:
                        logger.exception("Position monitor failed")
                        self.repository.set_state("position_monitor", f"ERROR: {exc}")
                        self.repository.event("position_monitor_failed", str(exc), "ERROR")
                    next_monitor = now + self.strategy.position_monitor_interval_seconds
                if now >= next_watchdog:
                    self.watchdog(scan_interval)
                    next_watchdog = now + 60
                self.repository.set_state("scheduler", "ACTIVE")
                self.stop_event.wait(1)
        except Exception as exc:
            logger.exception("Scheduler failed")
            self.repository.set_state("scheduler", f"ERROR: {exc}")
            raise
        finally:
            self.repository.event("server_stopped", "TradingHelper scheduler stopped")
