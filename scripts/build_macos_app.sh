#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This build script creates a native macOS .app bundle and requires macOS." >&2
  exit 1
fi

PYTHON="$PROJECT_ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  echo "Create the project virtual environment first: python3 -m venv .venv" >&2
  exit 1
fi

SWIFT_SOURCE="$PROJECT_ROOT/src/trading_helper/macos_screen_ocr.swift"
OCR_HELPER="$PROJECT_ROOT/build/macos/screen-ocr"
SWIFT_MODULE_CACHE="$PROJECT_ROOT/build/macos/swift-modules"
mkdir -p "$SWIFT_MODULE_CACHE"
export PYINSTALLER_CONFIG_DIR="$PROJECT_ROOT/build/macos/pyinstaller-config"
echo "Compiling the local macOS OCR helper..."
/usr/bin/swiftc \
  -O \
  -module-cache-path "$SWIFT_MODULE_CACHE" \
  -framework AppKit \
  -framework Vision \
  "$SWIFT_SOURCE" \
  -o "$OCR_HELPER"
chmod 700 "$OCR_HELPER"

"$PYTHON" -m pip install -e '.[desktop]'
"$PYTHON" -m PyInstaller \
  --noconfirm \
  --windowed \
  --name TradingHelper \
  --osx-bundle-identifier com.developmenthouse.tradinghelper \
  --collect-all webview \
  --hidden-import webview.platforms.cocoa \
  --add-data "$PROJECT_ROOT/src/trading_helper/web:trading_helper/web" \
  --add-data "$PROJECT_ROOT/src/trading_helper/macos_screen_ocr.swift:trading_helper" \
  --add-binary "$OCR_HELPER:trading_helper" \
  --add-data "$PROJECT_ROOT/src/trading_helper/defaults:trading_helper/defaults" \
  --add-data "$PROJECT_ROOT/config/settings.example.yaml:config" \
  --add-data "$PROJECT_ROOT/.env.example:." \
  --specpath "$PROJECT_ROOT/build/macos" \
  --distpath "$PROJECT_ROOT/dist/macos" \
  --workpath "$PROJECT_ROOT/build/macos" \
  src/trading_helper/desktop_app.py

APP_DATA="${HOME}/Library/Application Support/TradingHelper"
mkdir -p "$APP_DATA/config" "$APP_DATA/data"
if [[ ! -f "$APP_DATA/.env" ]]; then
  if [[ -f .env ]]; then
    cp .env "$APP_DATA/.env"
  else
    cp .env.example "$APP_DATA/.env"
  fi
  chmod 600 "$APP_DATA/.env"
fi
if [[ ! -f "$APP_DATA/config/settings.yaml" ]]; then
  if [[ -f config/settings.yaml ]]; then
    cp config/settings.yaml "$APP_DATA/config/settings.yaml"
  else
    cp config/settings.example.yaml "$APP_DATA/config/settings.yaml"
  fi
fi

echo "Built: $PROJECT_ROOT/dist/macos/TradingHelper.app"
