from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS scan_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    symbols_total INTEGER NOT NULL DEFAULT 0,
    symbols_ok INTEGER NOT NULL DEFAULT 0,
    symbols_failed INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    symbol TEXT NOT NULL,
    score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 100),
    label TEXT NOT NULL,
    price REAL,
    reasons_json TEXT NOT NULL DEFAULT '[]',
    data_mode TEXT NOT NULL DEFAULT 'UNKNOWN'
);

CREATE INDEX IF NOT EXISTS idx_signals_symbol_created ON signals(symbol, created_at DESC);

CREATE TABLE IF NOT EXISTS positions_cache (
    account TEXT NOT NULL,
    con_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    quantity REAL NOT NULL,
    avg_cost REAL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY(account, con_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    kind TEXT NOT NULL,
    symbol TEXT,
    fingerprint TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    sent INTEGER NOT NULL DEFAULT 0
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_alerts_fingerprint ON alerts(fingerprint);
"""


def connect(path: str) -> sqlite3.Connection:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    return connection


def init_database(path: str) -> None:
    with connect(path) as connection:
        connection.executescript(SCHEMA)
        connection.commit()
