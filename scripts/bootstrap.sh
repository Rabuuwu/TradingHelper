#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
[[ -f .env ]] || cp .env.example .env
[[ -f config/settings.yaml ]] || cp config/settings.example.yaml config/settings.yaml
python -m trading_helper.main init-db
python -m trading_helper.main self-check
echo "Bootstrap complete. The offline sample provider is ready; no broker is required."
