# Specyfikacja strategii i scoringu V1

## Założenie

Score 0–100 oznacza **jakość technicznego setupu według zdefiniowanych reguł**, a nie prawdopodobieństwo zysku.

## Dane wejściowe

Minimalnie 200 pełnych świec OHLCV dla EMA200. Jeśli danych jest za mało lub ostatnia świeca ma brakujące pola, sygnał ma status `INSUFFICIENT_DATA`.

## Bazowe komponenty

### Trend — do 30 pkt
- cena > EMA200,
- EMA20 > EMA50,
- EMA50 > EMA200.

### Momentum — do 25 pkt
- RSI w zdrowej strefie wzrostowej,
- MACD > signal,
- histogram MACD dodatni.

### Volume — do 15 pkt
- volume ratio względem średniej 20 świec.

### Setup — do 20 pkt
Docelowo breakout/pullback/support.

### Risk quality — do 10 pkt
Dodawany dopiero po wyliczeniu sensownego stop i R:R.

## Progi początkowe

- 0–39: IGNORE
- 40–59: NEUTRAL
- 60–74: WATCH
- 75–84: SETUP
- 85–100: STRONG_SETUP

Progi są hipotezą startową i muszą zostać zweryfikowane backtestem i Paper Trading.

## Exit helper

Exit bierze pod uwagę naruszenie stop/trailing, zmianę trendu, utratę wsparcia, momentum, realizację TP i aktualny R multiple.

## Zakaz overfittingu

Każda zmiana wag musi mieć uzasadnienie i być sprawdzona na danych poza próbką.
