#!/usr/bin/env bash
set -euo pipefail
PYTHONCLIENT_DIR="${1:-}"
if [[ -z "$PYTHONCLIENT_DIR" || ! -f "$PYTHONCLIENT_DIR/setup.py" ]]; then
  echo "Usage: $0 /path/to/IBJts/source/pythonclient"
  echo "Directory must come from the official TWS API package downloaded from IBKR."
  exit 2
fi
python -m pip install "$PYTHONCLIENT_DIR"
python - <<'PY'
import ibapi
print("ibapi import OK:", getattr(ibapi, "__version__", "version not exposed"))
PY
