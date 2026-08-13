# Przygotowanie Linuxa

Przykłady są dla Ubuntu/Debian.

## 1. Pakiety systemowe

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip build-essential curl unzip
```

## 2. Repo

```bash
git clone https://github.com/Rabuuwu/TradingHelper.git
cd TradingHelper
```

Jeśli repo jest prywatne, użyj uwierzytelnienia GitHub (SSH lub GitHub CLI).

## 3. Virtualenv

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
```

## 4. Konfiguracja

```bash
cp .env.example .env
cp config/settings.example.yaml config/settings.yaml
```

Nigdy nie commituj `.env` ani `config/settings.yaml`.

## 5. Testy bazowe

```bash
make lint
make test
python -m trading_helper.main self-check
python -m trading_helper.main init-db
```

## 6. IBKR

Przejdź do `docs/IBKR_SETUP.md`. Po instalacji oficjalnego TWS API uruchom:

```bash
./scripts/install_ibapi.sh ~/IBJts/source/pythonclient
python -m trading_helper.main self-check
```

## 7. API helpera

```bash
make run
```

Domyślnie działa na `http://127.0.0.1:8787`. Nie ustawiaj `APP_HOST=0.0.0.0`, dopóki nie zaprojektujemy uwierzytelnienia/firewalla lub bezpiecznego tunelu/VPN.
