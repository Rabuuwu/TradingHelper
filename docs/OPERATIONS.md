# Uruchamianie 24/7 i operacje

## Zasada

Najpierw uruchamiamy ręcznie i stabilizujemy projekt. Dopiero po przejściu testów Paper konfigurujemy usługę systemd.

## Tryb developerski

Uruchom IB Gateway i zaloguj konto Paper, a w drugim terminalu:

```bash
cd ~/TradingHelper
source .venv/bin/activate
python -m trading_helper.main self-check
python -m trading_helper.main api
```

## Healthcheck

```bash
curl -fsS http://127.0.0.1:8787/health
```

## systemd

Przykład znajduje się w `deploy/trading-helper.service.example`. Przed aktywacją ustaw prawidłowego użytkownika, katalog projektu i ścieżkę do virtualenv.

## Backup

SQLite backup wykonujemy mechanizmem backup SQLite lub po kontrolowanym zatrzymaniu procesu. Pliku bazy nie commitujemy do Git.

## Aktualizacja

1. zatrzymaj helper,
2. `git pull`,
3. aktywuj `.venv`,
4. `pip install -e '.[dev]'`,
5. `make test`,
6. uruchom `self-check`,
7. uruchom usługę,
8. sprawdź `/health`.

## Monitoring minimalny

Monitorujemy proces, `/health`, połączenie z IBKR, czas ostatniego skanu i świecy, błędy skanera, miejsce na dysku i rozmiar SQLite.
