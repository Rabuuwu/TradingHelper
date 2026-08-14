from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@contextmanager
def connect(path: str):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA busy_timeout=5000")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


BASE_SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS symbols (
    symbol TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    asset_type TEXT NOT NULL DEFAULT 'STOCK',
    currency TEXT NOT NULL DEFAULT 'USD',
    exchange TEXT NOT NULL DEFAULT '',
    data_source TEXT NOT NULL DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candles (
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    data_source TEXT NOT NULL,
    is_delayed INTEGER NOT NULL DEFAULT 0,
    delay_minutes INTEGER,
    fetched_at TEXT NOT NULL,
    PRIMARY KEY(symbol, timeframe, timestamp)
);
CREATE INDEX IF NOT EXISTS idx_candles_lookup
ON candles(symbol, timeframe, timestamp DESC);

CREATE TABLE IF NOT EXISTS quotes (
    symbol TEXT PRIMARY KEY,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    data_source TEXT NOT NULL,
    is_delayed INTEGER NOT NULL DEFAULT 0,
    delay_minutes INTEGER,
    fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fx_rates (
    base_currency TEXT NOT NULL,
    quote_currency TEXT NOT NULL,
    rate REAL NOT NULL,
    data_source TEXT NOT NULL,
    data_timestamp TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    PRIMARY KEY(base_currency, quote_currency)
);
CREATE INDEX IF NOT EXISTS idx_fx_rates_timestamp
ON fx_rates(base_currency, quote_currency, data_timestamp DESC);

CREATE TABLE IF NOT EXISTS scan_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    symbols_total INTEGER NOT NULL DEFAULT 0,
    symbols_ok INTEGER NOT NULL DEFAULT 0,
    symbols_failed INTEGER NOT NULL DEFAULT 0,
    provider TEXT NOT NULL DEFAULT '',
    error TEXT
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id INTEGER,
    created_at TEXT NOT NULL,
    data_timestamp TEXT,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 100),
    label TEXT NOT NULL,
    price REAL,
    timeframe TEXT NOT NULL DEFAULT '',
    data_source TEXT NOT NULL DEFAULT 'UNKNOWN',
    is_delayed INTEGER NOT NULL DEFAULT 0,
    delay_minutes INTEGER,
    entry_low REAL,
    entry_high REAL,
    stop_price REAL,
    target_price REAL,
    target_price_2 REAL,
    risk_reward REAL,
    recommended_quantity REAL,
    estimated_total_cost REAL,
    expected_net_profit REAL,
    feasibility_status TEXT,
    reasons_json TEXT NOT NULL DEFAULT '[]',
    warnings_json TEXT NOT NULL DEFAULT '[]',
    breakdown_json TEXT NOT NULL DEFAULT '{}',
    details_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(scan_run_id) REFERENCES scan_runs(id)
);
CREATE INDEX IF NOT EXISTS idx_signals_symbol_created ON signals(symbol, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_score_created ON signals(score DESC, created_at DESC);

CREATE TABLE IF NOT EXISTS signal_details (
    signal_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    points INTEGER NOT NULL,
    details_json TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY(signal_id, category),
    FOREIGN KEY(signal_id) REFERENCES signals(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS watchlist (
    symbol TEXT PRIMARY KEY,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY(symbol) REFERENCES symbols(symbol)
);

CREATE TABLE IF NOT EXISTS manual_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    broker TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'MANUAL',
    entry_price REAL NOT NULL,
    quantity REAL NOT NULL,
    currency TEXT NOT NULL,
    entry_date TEXT NOT NULL,
    stop_price REAL,
    target_price REAL,
    target_price_2 REAL,
    highest_price REAL NOT NULL,
    trailing_stop REAL,
    current_price REAL,
    pnl REAL,
    pnl_percent REAL,
    distance_to_stop_percent REAL,
    distance_to_target_percent REAL,
    monitor_status TEXT NOT NULL DEFAULT 'PENDING',
    last_price_at TEXT,
    status TEXT NOT NULL DEFAULT 'OPEN',
    notes TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_positions_symbol_status ON manual_positions(symbol, status);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id INTEGER,
    symbol TEXT NOT NULL,
    broker TEXT NOT NULL,
    status TEXT NOT NULL,
    entry_date TEXT NOT NULL,
    entry_price REAL NOT NULL,
    quantity REAL NOT NULL,
    currency TEXT NOT NULL,
    exit_date TEXT,
    exit_price REAL,
    fees REAL NOT NULL DEFAULT 0,
    pnl REAL,
    pnl_percent REAL,
    strategy TEXT NOT NULL DEFAULT '',
    signal_score_at_entry INTEGER,
    notes TEXT NOT NULL DEFAULT '',
    FOREIGN KEY(position_id) REFERENCES manual_positions(id)
);
CREATE INDEX IF NOT EXISTS idx_trades_status_date ON trades(status, entry_date DESC);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    kind TEXT NOT NULL,
    symbol TEXT,
    fingerprint TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    sent INTEGER NOT NULL DEFAULT 0,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TEXT,
    last_sent_at TEXT,
    error TEXT,
    cooldown_until TEXT
);

CREATE TABLE IF NOT EXISTS app_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    event_type TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    details_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_events_created ON app_events(created_at DESC);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Legacy tables retained so existing user data is never deleted during migration.
CREATE TABLE IF NOT EXISTS positions_cache (
    account TEXT NOT NULL, con_id INTEGER NOT NULL, symbol TEXT NOT NULL,
    quantity REAL NOT NULL, avg_cost REAL, updated_at TEXT NOT NULL,
    PRIMARY KEY(account, con_id)
);
CREATE TABLE IF NOT EXISTS account_summary (
    account TEXT NOT NULL, tag TEXT NOT NULL, value TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL,
    PRIMARY KEY(account, tag, currency)
);
"""


SIGNAL_COLUMNS: dict[str, str] = {
    "scan_run_id": "INTEGER",
    "data_timestamp": "TEXT",
    "name": "TEXT NOT NULL DEFAULT ''",
    "timeframe": "TEXT NOT NULL DEFAULT ''",
    "data_source": "TEXT NOT NULL DEFAULT 'UNKNOWN'",
    "is_delayed": "INTEGER NOT NULL DEFAULT 0",
    "delay_minutes": "INTEGER",
    "entry_low": "REAL",
    "entry_high": "REAL",
    "stop_price": "REAL",
    "target_price": "REAL",
    "target_price_2": "REAL",
    "risk_reward": "REAL",
    "recommended_quantity": "REAL",
    "estimated_total_cost": "REAL",
    "expected_net_profit": "REAL",
    "feasibility_status": "TEXT",
    "warnings_json": "TEXT NOT NULL DEFAULT '[]'",
    "breakdown_json": "TEXT NOT NULL DEFAULT '{}'",
    "details_json": "TEXT NOT NULL DEFAULT '{}'",
}

POSITION_COLUMNS: dict[str, str] = {
    "current_price": "REAL",
    "pnl": "REAL",
    "pnl_percent": "REAL",
    "distance_to_stop_percent": "REAL",
    "distance_to_target_percent": "REAL",
    "monitor_status": "TEXT NOT NULL DEFAULT 'PENDING'",
    "last_price_at": "TEXT",
}


def _ensure_columns(connection: sqlite3.Connection, table: str, additions: dict[str, str]) -> None:
    columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    for name, definition in additions.items():
        if name not in columns:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


def init_database(path: str) -> None:
    with connect(path) as connection:
        connection.executescript(BASE_SCHEMA)
        _ensure_columns(connection, "signals", SIGNAL_COLUMNS)
        _ensure_columns(connection, "manual_positions", POSITION_COLUMNS)
        _ensure_columns(
            connection,
            "alerts",
            {
                "status": "TEXT NOT NULL DEFAULT 'PENDING'",
                "attempts": "INTEGER NOT NULL DEFAULT 0",
                "last_attempt_at": "TEXT",
                "last_sent_at": "TEXT",
                "error": "TEXT",
                "cooldown_until": "TEXT",
            },
        )
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (2, ?)",
            (utc_now(),),
        )
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (3, ?)",
            (utc_now(),),
        )


class Repository:
    def __init__(self, path: str) -> None:
        self.path = path
        init_database(path)

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        with connect(self.path) as connection:
            cursor = connection.execute(query, params)
            return int(cursor.lastrowid or 0)

    def rows(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with connect(self.path) as connection:
            return [dict(row) for row in connection.execute(query, params).fetchall()]

    def set_state(self, key: str, value: str) -> None:
        self.execute(
            """INSERT INTO system_state(key,value,updated_at) VALUES (?,?,?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
            (key, value, utc_now()),
        )

    def event(
        self,
        event_type: str,
        message: str,
        level: str = "INFO",
        details: dict[str, Any] | None = None,
    ) -> int:
        return self.execute(
            """INSERT INTO app_events(created_at,event_type,level,message,details_json)
            VALUES(?,?,?,?,?)""",
            (utc_now(), event_type, level, message, json.dumps(details or {})),
        )

    def start_scan(self, total: int, provider: str) -> int:
        return self.execute(
            """INSERT INTO scan_runs(started_at,status,symbols_total,provider)
            VALUES(?,'RUNNING',?,?)""",
            (utc_now(), total, provider),
        )

    def finish_scan(
        self, run_id: int, ok: int, failed: int, status: str = "COMPLETED", error: str | None = None
    ) -> None:
        self.execute(
            """UPDATE scan_runs SET finished_at=?,status=?,symbols_ok=?,symbols_failed=?,error=?
            WHERE id=?""",
            (utc_now(), status, ok, failed, error, run_id),
        )

    def upsert_symbol(
        self,
        symbol: str,
        name: str = "",
        asset_type: str = "STOCK",
        currency: str = "USD",
        exchange: str = "",
        source: str = "",
    ) -> None:
        self.execute(
            """INSERT INTO symbols(symbol,name,asset_type,currency,exchange,data_source,updated_at)
            VALUES(?,?,?,?,?,?,?) ON CONFLICT(symbol) DO UPDATE SET name=excluded.name,
            asset_type=excluded.asset_type,currency=excluded.currency,exchange=excluded.exchange,
            data_source=excluded.data_source,updated_at=excluded.updated_at""",
            (symbol, name, asset_type, currency, exchange, source, utc_now()),
        )

    def save_candles(
        self,
        symbol: str,
        timeframe: str,
        frame: Any,
        source: str,
        is_delayed: bool,
        delay_minutes: int | None,
    ) -> None:
        rows = [
            (
                symbol,
                timeframe,
                str(index),
                float(row.open),
                float(row.high),
                float(row.low),
                float(row.close),
                float(row.volume),
                source,
                int(is_delayed),
                delay_minutes,
                utc_now(),
            )
            for index, row in frame.iterrows()
        ]
        with connect(self.path) as connection:
            connection.executemany(
                """INSERT OR REPLACE INTO candles(symbol,timeframe,timestamp,open,high,low,close,
                volume,data_source,is_delayed,delay_minutes,fetched_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                rows,
            )

    def save_quote(self, quote: Any) -> None:
        self.execute(
            """INSERT INTO quotes(symbol,price,currency,timestamp,data_source,is_delayed,
            delay_minutes,fetched_at) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(symbol) DO UPDATE SET
            price=excluded.price,currency=excluded.currency,timestamp=excluded.timestamp,
            data_source=excluded.data_source,is_delayed=excluded.is_delayed,
            delay_minutes=excluded.delay_minutes,fetched_at=excluded.fetched_at""",
            (
                quote.symbol,
                quote.price,
                quote.currency,
                quote.provenance.timestamp.isoformat(),
                quote.provenance.source,
                int(quote.provenance.is_delayed),
                quote.provenance.delay_minutes,
                utc_now(),
            ),
        )

    def latest_quote(self, symbol: str) -> dict[str, Any] | None:
        rows = self.rows("SELECT * FROM quotes WHERE symbol=?", (symbol.upper(),))
        return rows[0] if rows else None

    def save_fx_rate(
        self,
        base_currency: str,
        quote_currency: str,
        rate: float,
        source: str,
        data_timestamp: str,
    ) -> None:
        self.execute(
            """INSERT INTO fx_rates(base_currency,quote_currency,rate,data_source,
            data_timestamp,fetched_at) VALUES(?,?,?,?,?,?) ON CONFLICT(base_currency,
            quote_currency) DO UPDATE SET rate=excluded.rate,data_source=excluded.data_source,
            data_timestamp=excluded.data_timestamp,fetched_at=excluded.fetched_at""",
            (
                base_currency.upper(),
                quote_currency.upper(),
                rate,
                source,
                data_timestamp,
                utc_now(),
            ),
        )

    def latest_fx_rate(self, base_currency: str, quote_currency: str) -> dict[str, Any] | None:
        rows = self.rows(
            "SELECT * FROM fx_rates WHERE base_currency=? AND quote_currency=?",
            (base_currency.upper(), quote_currency.upper()),
        )
        return rows[0] if rows else None

    def cached_candles(self, symbol: str, timeframe: str, limit: int) -> list[dict[str, Any]]:
        rows = self.rows(
            """SELECT * FROM candles WHERE symbol=? AND timeframe=?
            ORDER BY timestamp DESC LIMIT ?""",
            (symbol.upper(), timeframe, limit),
        )
        return list(reversed(rows))

    def add_signal(self, payload: dict[str, Any]) -> int:
        columns = tuple(payload)
        values = tuple(payload[column] for column in columns)
        placeholders = ",".join("?" for _ in columns)
        return self.execute(
            f"INSERT INTO signals({','.join(columns)}) VALUES({placeholders})", values
        )

    def add_alert(self, payload: dict[str, Any]) -> bool:
        with connect(self.path) as connection:
            cursor = connection.execute(
                """INSERT OR IGNORE INTO alerts(created_at,kind,symbol,fingerprint,title,body,
                status,cooldown_until) VALUES(?,?,?,?,?,?,'PENDING',?)""",
                (
                    utc_now(),
                    payload["kind"],
                    payload.get("symbol"),
                    payload["fingerprint"],
                    payload["title"],
                    payload["body"],
                    payload.get("cooldown_until"),
                ),
            )
            return cursor.rowcount == 1
