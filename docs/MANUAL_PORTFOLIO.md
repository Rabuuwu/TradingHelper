# Manual portfolio i simulation

Pozycja zawiera symbol, broker jako etykietę, entry, fractional quantity, currency, datę,
opcjonalne SL/TP i notes. `mode=MANUAL` opisuje pozycję wykonaną ręcznie u brokera;
`mode=PAPER` tworzy lokalną symulację. System nigdy nie wysyła zlecenia.

Monitor pobiera quote/candles, liczy P/L, najwyższą cenę, ATR trailing oraz HOLD,
WATCH_EXIT, TAKE_PROFIT, TRAILING_STOP_WARNING lub EXIT_WARNING. Trailing long może
pozostać bez zmian albo wzrosnąć. Zamknięcie pozycji aktualizuje journal i statystyki.

## Paper account

Symulator ma osobne saldo gotówki w walucie portfela. `Symuluj kupno` korzysta z
entry zone, position sizing, SL/TP i score wybranego sygnału. Formularz automatycznie
uzupełnia symbol, datę, cenę, ilość, walutę, SL, TP1, TP2 i strategię, ale pozwala
skorygować plan oraz dodać notatkę. Przed zatwierdzeniem pokazuje wartość pozycji,
ryzyko do SL, potencjał do TP1 i oszacowane koszty. Wartość zakupu i koszty są przeliczane przez FX i
odejmowane od gotówki. `Symuluj sprzedaż` zamyka wyłącznie lokalną pozycję PAPER,
dodaje przychód po kosztach i aktualizuje realized P/L.

`paper_ledger` przechowuje każdy wirtualny BUY/SELL, a `paper_accounts` saldo, kapitał
początkowy i zrealizowany wynik. Reset salda jest blokowany, dopóki istnieją otwarte
pozycje PAPER. Te endpointy nigdy nie komunikują się z brokerem ani nie wykonują zleceń.

Kupno, pozycja, trade, saldo i ledger są zapisywane w jednej transakcji SQLite. Pozycje
PAPER można tworzyć wyłącznie przez `/paper/buy`; ogólne `/portfolio` nie omija księgowości.
Historia rozdziela market value, cash, realized, unrealized i total P/L, uwzględniając koszt
wejścia zapisany przy historycznym kursie FX.
