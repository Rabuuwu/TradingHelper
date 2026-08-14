# Instalacja Linux

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip curl
git clone https://github.com/Rabuuwu/TradingHelper.git
cd TradingHelper
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
cp config/settings.example.yaml config/settings.yaml
ruff check src tests
pytest
python -m trading_helper.main self-check
python -m trading_helper.main init-db
python -m trading_helper.main scan-once
python -m trading_helper.main run
```

Nie jest potrzebny IB Gateway, TWS, XTB API ani konto brokerskie. Provider `sample`
działa offline. Domyślny dashboard: `http://127.0.0.1:8787`.

## Auth

```bash
python -m trading_helper.main hash-password 'długie-bezpieczne-hasło'
```

Wklej wynik jako `AUTH_PASSWORD_HASH`, ustaw `AUTH_ENABLED=true`, `AUTH_USERNAME` oraz
losowy `SESSION_SECRET`. Nie commituj `.env`.

## systemd

Pliki w `deploy/` zakładają użytkownika `tradinghelper` i instalację w
`/opt/trading-helper`. Skopiuj repo i `.venv`, utwórz zapisywalny `data/`, następnie:

```bash
sudo cp deploy/trading-helper.service /etc/systemd/system/
sudo cp deploy/trading-helper-backup.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now trading-helper.service
sudo systemctl enable --now trading-helper-backup.timer
```

Dostosuj ścieżki/użytkownika, jeżeli instalacja jest inna.
