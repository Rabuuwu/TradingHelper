#!/usr/bin/env python3
"""Configure and verify a personal Twelve Data API key without printing it."""

from __future__ import annotations

import getpass
import os
import re
import sys
import tempfile
from pathlib import Path

from trading_helper.market_data.twelve_data import TwelveDataProvider


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
ENV_TEMPLATE = ROOT / ".env.example"


def update_environment(text: str, api_key: str) -> str:
    """Set only the market data provider and key, preserving other configuration."""
    replacements = {
        "MARKET_DATA_PROVIDER": "twelve_data",
        "MARKET_DATA_API_KEY": api_key,
    }
    seen: set[str] = set()
    result: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^\s*(?:export\s+)?([A-Z_]+)\s*=", line)
        key = match.group(1) if match else None
        if key not in replacements:
            result.append(line)
        elif key not in seen:
            result.append(f"{key}={replacements[key]}")
            seen.add(key)
    for key, value in replacements.items():
        if key not in seen:
            result.append(f"{key}={value}")
    return "\n".join(result).rstrip() + "\n"


def save_environment(text: str) -> None:
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".env.", dir=ENV_FILE.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.chmod(temporary, 0o600)
        os.replace(temporary, ENV_FILE)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    print("Free Twelve Data Basic setup — the key will not be displayed or sent in the URL.")
    print("Create a free key at https://twelvedata.com/pricing, then paste it below.")
    api_key = getpass.getpass("Twelve Data API key: ").strip()
    if not api_key:
        print("No key entered; configuration was not changed.", file=sys.stderr)
        return 2

    try:
        quote = TwelveDataProvider(api_key, requests_per_minute=7).get_quote("AAPL")
    except Exception:
        print(
            "Could not verify the key with Twelve Data (network, key, quota, or symbol error). "
            "Configuration was not changed; check the key and try again.",
            file=sys.stderr,
        )
        return 1

    source_text = (
        ENV_FILE.read_text(encoding="utf-8")
        if ENV_FILE.exists()
        else ENV_TEMPLATE.read_text(encoding="utf-8")
    )
    save_environment(update_environment(source_text, api_key))
    print(
        f"Connected successfully: {quote.symbol} {quote.price:.4f} {quote.currency} "
        f"({quote.provenance.timestamp.isoformat()}). Saved settings to .env."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
