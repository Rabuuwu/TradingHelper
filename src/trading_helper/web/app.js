const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const escapeHtml = window.TradingHelperSecurity.escapeHtml;
const translate = (key) => (translations[language] || translations.pl)[key] || translations.pl[key] || key;

const translations = {
  pl: {
    brandSubtitle: "Twój rynek, czytelny plan", activityFilter: "Rodzaj aktywności", mainNavigation: "Nawigacja główna",
    offlineMessage: "Brak połączenia z serwerem. Widoczne dane mogą być nieaktualne.",
    watchSymbols: "Obserwuj symbole", positionValue: "Wartość pozycji", riskToStop: "Ryzyko do SL",
    targetPotential: "Potencjał do celu", paperSellConfirm: "Zapis zostanie zamknięty w symulatorze PAPER. Nie zostanie wysłane zlecenie do brokera.",
    confirmSell: "Zamknij symulację", lastScan: "Ostatni skan", lastMarketUpdate: "Ostatnia aktualizacja danych",
    hours: "godz.", symbolsScanned: "symboli", noScans: "Brak zapisanych skanów.",
    uptime: "Czas pracy", apiUsage: "API", apiReserve: "rezerwa",
    noPortfolioHistory: "Brak zapisanej historii portfela.", availableCash: "Dostępna gotówka", openCount: "Otwarte pozycje", resetPreview: "Obecne konto:",
    sampleData: "Dane demonstracyjne — nie są notowaniami rynkowymi",
    tooManyLogins: "Zbyt wiele prób logowania. Spróbuj później.", badCredentials: "Nieprawidłowa nazwa użytkownika lub hasło.",
    active: "Aktywny", degraded: "Ograniczona praca", starting: "Uruchamianie", completed: "Zakończono",
    partial: "Częściowo", failed: "Błąd", error: "Błąd", watchExit: "Zbliża się do poziomu wyjścia",
    trailingWarning: "Ostrzeżenie stop kroczącego", exitWarning: "Sygnał wyjścia", takeProfit: "Poziom celu osiągnięty",
    navDashboard: "Pulpit", navPortfolio: "Portfel", navActivity: "Aktywność", navMore: "Więcej",
    dashboardEyebrow: "PULPIT RYNKU", dashboardTitle: "Najpierw to, co ważne.",
    dashboardIntro: "Sygnały, kondycja danych i otwarte pozycje w jednym widoku.", runScan: "Uruchom skan",
    analysis: "ANALIZA", setupHeading: "Setupy do sprawdzenia", waitingData: "Oczekiwanie na dane",
    portfolioEyebrow: "TWOJE POZYCJE", portfolioTitle: "Portfel", portfolioIntro: "Pozycje ręczne i symulacje PAPER są wyraźnie rozdzielone.",
    addPosition: "Dodaj pozycję", paperEyebrow: "PAPER", paperHeading: "Wartość symulatora", simulation: "Symulacja",
    portfolioHistory: "Wartość portfela w czasie", performance: "Wartość i wynik", portfolioChartLabel: "Wykres wartości portfela",
    chartNote: "Historia zapisana przez monitoring portfela.", attentionHeading: "Wymaga uwagi", monitoring: "MONITORING",
    openPositions: "Otwarte pozycje", show: "Pokaż", allPositions: "Wszystkie", manualPositions: "Ręczne", paperPositions: "PAPER",
    paperSettings: "Ustawienia symulatora PAPER", paperSettingsHelp: "Zmiana kapitału rozpoczyna nowe konto PAPER. Możesz to zrobić po zamknięciu wszystkich symulowanych pozycji.",
    initialCapital: "Kapitał początkowy", changeCapital: "Zmień kapitał", historyEyebrow: "HISTORIA", activityTitle: "Aktywność",
    activityIntro: "Transakcje i praca systemu, oddzielone prostym filtrem.", trades: "Transakcje", system: "System",
    toolsEyebrow: "NARZĘDZIA", watchlistTitle: "Obserwowane symbole", watchlistIntro: "Dodaj symbol, żeby łatwo wracać do wybranych rynków.",
    symbol: "Symbol", optionalNote: "Notatka (opcjonalnie)", addSymbol: "Dodaj symbol", filterWatchlist: "Filtruj obserwowane", searchSymbol: "Wpisz symbol lub notatkę",
    healthEyebrow: "KONDYCJA", systemTitle: "Stan systemu", systemIntro: "Połączenie, źródło i aktualność danych to osobne informacje.",
    refresh: "Odśwież", latestScans: "Ostatnie skany", preferences: "PREFERENCJE", settingsTitle: "Ustawienia",
    settingsIntro: "Parametry planowania i sposób prezentacji danych.", portfolioValue: "Wartość portfela", riskPerPosition: "Ryzyko na pozycję (%)",
    scanSeconds: "Skanowanie (sekundy)", displayCurrency: "Waluta prezentacji", languageLabel: "Język", saveSettings: "Zapisz ustawienia",
    manualPositionTitle: "Dodaj pozycję ręczną", manualPositionHelp: "Zapisz pozycję, którą otworzyłeś u swojego brokera. TradingHelper nie składa zleceń.",
    brokerSource: "Broker / źródło", entryPrice: "Cena wejścia", date: "Data wejścia", stopOptional: "Stop loss (opcjonalnie)",
    targetOptional: "Take profit (opcjonalnie)", login: "Zaloguj się", username: "Nazwa użytkownika", password: "Hasło", close: "Zamknij",
    confirmPaperTitle: "Rozpocząć nowe konto PAPER?", confirmPaperMessage: "Historia księgi PAPER zostanie wyczyszczona. Możesz zmienić kapitał tylko wtedy, gdy wszystkie pozycje PAPER są zamknięte.",
    cancel: "Anuluj", confirmReset: "Potwierdź reset", paperResetReason: "Zmiana kapitału wyczyści księgę PAPER. Zamknij wszystkie symulowane pozycje przed resetem.",
    activityEvents: "Zdarzenia systemowe", technicalDetails: "Szczegóły techniczne", remove: "Usuń", retry: "Spróbuj ponownie",
    online: "Połączono", offline: "Brak połączenia", connecting: "Łączenie…",
    noSignals: "Nie ma jeszcze sygnałów. Dodaj obserwowane symbole lub uruchom skan.",
    loading: "Wczytywanie…", errorLoad: "Nie udało się wczytać danych.",
    server: "Serwer", market: "Rynek", data: "Dane rynkowe", scanner: "Skaner", provider: "Źródło danych",
    attention: "Wymagają uwagi", current: "Aktualne", delayed: "Opóźnione",
    stale: "Nieaktualne", unknown: "Nieznane", source: "Źródło", noPositions: "Brak otwartych pozycji.",
    noTrades: "Brak zapisanych transakcji.", noEvents: "Brak zdarzeń systemowych.", noWatchlist: "Lista jest pusta. Dodaj pierwszy symbol.",
    scanStarted: "Skan został uruchomiony.", scanFailed: "Nie udało się uruchomić skanu.",
    paperResetSuccess: "Kapitał PAPER został zmieniony.",
    paperBuySuccess: "Dodano symulowaną pozycję", paperSellSuccess: "Zamknięto pozycję PAPER",
    manual: "Ręczna", paper: "Symulacja PAPER", status: "Status", price: "Cena", riskReward: "R:R",
    lastReport: "Dane z", action: "Akcja", buySetup: "Setup kupna", strongBuy: "Mocny setup",
    exceptional: "Wyjątkowy setup", interesting: "Interesujący", watch: "Obserwuj", ignore: "Pomiń",
    freshnessCurrent: "Dane aktualne", freshnessDelayed: "Dane opóźnione", freshnessStale: "Dane nieaktualne",
    freshnessUnknown: "Nieznana świeżość", marketClosed: "Rynek zamknięty", notStarted: "Jeszcze nie uruchomiono",
    run: "Uruchomiono", idle: "Oczekuje", detailSummary: "Plan i jakość setupu",
    chart: "Wykres ceny", indicators: "Wskaźniki", score: "Skład wyniku", costs: "Koszty i wynik netto",
    warnings: "Ostrzeżenia", none: "Brak", plan: "Plan poziomów", entry: "Wejście", stop: "Stop loss",
    target1: "Cel 1", target2: "Cel 2", estimatedCost: "Szacowany koszt", netProfit: "Wynik netto",
    paperTitle: "Dodaj do symulatora PAPER", paperHint: "To zapis symulacji. Nie wysyła zlecenia do brokera.",
    quantity: "Ilość", currency: "Waluta", strategy: "Strategia", notes: "Notatka",
    simulateBuy: "Zapisz symulowane wejście", simulateSell: "Zamknij symulację",
    chartUnavailable: "Wykres jest chwilowo niedostępny. Możesz sprawdzić poziomy i dane poniżej.",
    chartCredit: "Wykresy: TradingView", noChartData: "Brak świec dla wybranego interwału.",
    cash: "Gotówka PAPER", equity: "Wartość PAPER", unrealized: "Niezrealizowany wynik", realized: "Zrealizowany wynik",
    totalTrades: "Liczba transakcji", wins: "Zyskowne", losses: "Stratne", winRate: "Skuteczność",
    expectancy: "Średni wynik", netPnl: "Wynik łączny", open: "Otwarte", closed: "Zamknięte",
    dataDelay: "Opóźnione dane", dataAge: "Wiek danych", delayedFor: "Opóźnienie",
    unknownStatus: "Status nieznany", positionCreated: "Pozycja została zapisana.", settingsSaved: "Ustawienia zapisane.",
    watchAdded: "Symbol dodany do obserwowanych.", symbolRemoved: "Symbol usunięty.",
    invalidInput: "Sprawdź wprowadzone wartości.", loginRequired: "Zaloguj się ponownie, aby kontynuować.",
    chartLoading: "Wczytywanie wykresu…", interval: "Interwał", marketData: "Dane rynkowe",
    fxLive: "Kursy walut są aktualne z cache dostawcy.", fxFallback: "Kursy walut korzystają z wartości awaryjnych z konfiguracji.",
    fxStale: "Kursy walut są nieaktualne.", fxUnknown: "Nie udało się pobrać kursów walut.",
    autoExecution: "TradingHelper nie wykonuje zleceń. Każdą transakcję realizujesz ręcznie.",
  },
  en: {
    brandSubtitle: "Your market, clearly planned", activityFilter: "Activity type", mainNavigation: "Main navigation",
    offlineMessage: "Server connection lost. Displayed data may be stale.",
    watchSymbols: "Add symbols to watchlist", positionValue: "Position value", riskToStop: "Risk to stop",
    targetPotential: "Potential to target", paperSellConfirm: "This closes the PAPER simulation. No order will be sent to your broker.",
    confirmSell: "Close simulation", lastScan: "Last scan", lastMarketUpdate: "Last market data update",
    hours: "hours", symbolsScanned: "symbols", noScans: "No scans recorded.",
    uptime: "Uptime", apiUsage: "API", apiReserve: "reserved",
    noPortfolioHistory: "No portfolio history recorded.", availableCash: "Available cash", openCount: "Open positions", resetPreview: "Current account:",
    sampleData: "Demo data — these are not market quotes",
    tooManyLogins: "Too many sign-in attempts. Try again later.", badCredentials: "Incorrect username or password.",
    active: "Active", degraded: "Degraded", starting: "Starting", completed: "Completed",
    partial: "Partial", failed: "Failed", error: "Error", watchExit: "Near exit level",
    trailingWarning: "Trailing stop warning", exitWarning: "Exit signal", takeProfit: "Target reached",
    navDashboard: "Overview", navPortfolio: "Portfolio", navActivity: "Activity", navMore: "More",
    dashboardEyebrow: "MARKET OVERVIEW", dashboardTitle: "Start with what matters.",
    dashboardIntro: "Signals, data health and open positions in one view.", runScan: "Run scan",
    analysis: "ANALYSIS", setupHeading: "Setups to review", waitingData: "Waiting for data",
    portfolioEyebrow: "YOUR POSITIONS", portfolioTitle: "Portfolio", portfolioIntro: "Manual positions and PAPER simulations are clearly separated.",
    addPosition: "Add position", paperEyebrow: "PAPER", paperHeading: "Simulator value", simulation: "Simulation",
    portfolioHistory: "Portfolio value over time", performance: "Value and return", portfolioChartLabel: "Portfolio value chart",
    chartNote: "History recorded by portfolio monitoring.", attentionHeading: "Needs attention", monitoring: "MONITORING",
    openPositions: "Open positions", show: "Show", allPositions: "All", manualPositions: "Manual", paperPositions: "PAPER",
    paperSettings: "PAPER simulator settings", paperSettingsHelp: "Changing the capital starts a new PAPER account. Do this after closing all simulated positions.",
    initialCapital: "Initial capital", changeCapital: "Change capital", historyEyebrow: "HISTORY", activityTitle: "Activity",
    activityIntro: "Trades and system activity, separated by a simple filter.", trades: "Trades", system: "System",
    toolsEyebrow: "TOOLS", watchlistTitle: "Watchlist", watchlistIntro: "Add symbols to quickly return to markets you follow.",
    symbol: "Symbol", optionalNote: "Note (optional)", addSymbol: "Add symbol", filterWatchlist: "Filter watchlist", searchSymbol: "Enter a symbol or note",
    healthEyebrow: "HEALTH", systemTitle: "System status", systemIntro: "Connection, data source and freshness are shown separately.",
    refresh: "Refresh", latestScans: "Recent scans", preferences: "PREFERENCES", settingsTitle: "Settings",
    settingsIntro: "Planning parameters and display preferences.", portfolioValue: "Portfolio value", riskPerPosition: "Risk per position (%)",
    scanSeconds: "Scan interval (seconds)", displayCurrency: "Display currency", languageLabel: "Language", saveSettings: "Save settings",
    manualPositionTitle: "Add manual position", manualPositionHelp: "Record a position you opened with your broker. TradingHelper does not place orders.",
    brokerSource: "Broker / source", entryPrice: "Entry price", date: "Entry date", stopOptional: "Stop loss (optional)",
    targetOptional: "Take profit (optional)", login: "Sign in", username: "Username", password: "Password", close: "Close",
    confirmPaperTitle: "Start a new PAPER account?", confirmPaperMessage: "The PAPER ledger will be cleared. You can change capital after all PAPER positions are closed.",
    cancel: "Cancel", confirmReset: "Confirm reset", paperResetReason: "Changing capital clears the PAPER ledger. Close all simulated positions before resetting.",
    activityEvents: "System events", technicalDetails: "Technical details", remove: "Remove", retry: "Try again",
    online: "Connected", offline: "No connection", connecting: "Connecting…",
    noSignals: "No signals yet. Add symbols to the watchlist or run a scan.",
    loading: "Loading…", errorLoad: "Could not load data.",
    server: "Server", market: "Market", data: "Market data", scanner: "Scanner", provider: "Data source",
    attention: "Need attention", current: "Current", delayed: "Delayed",
    stale: "Stale", unknown: "Unknown", source: "Source", noPositions: "No open positions.",
    noTrades: "No trades recorded.", noEvents: "No system events.", noWatchlist: "The list is empty. Add your first symbol.",
    scanStarted: "Scan started.", scanFailed: "Could not start the scan.",
    paperResetSuccess: "PAPER capital updated.",
    paperBuySuccess: "Simulated position added", paperSellSuccess: "PAPER position closed",
    manual: "Manual", paper: "PAPER simulation", status: "Status", price: "Price", riskReward: "R:R",
    lastReport: "Data from", action: "Action", buySetup: "Buy setup", strongBuy: "Strong setup",
    exceptional: "Exceptional setup", interesting: "Interesting", watch: "Watch", ignore: "Ignore",
    freshnessCurrent: "Current data", freshnessDelayed: "Delayed data", freshnessStale: "Stale data",
    freshnessUnknown: "Freshness unknown", marketClosed: "Market closed", notStarted: "Not started",
    run: "Running", idle: "Waiting", detailSummary: "Setup quality and plan",
    chart: "Price chart", indicators: "Indicators", score: "Score breakdown", costs: "Costs and net result",
    warnings: "Warnings", none: "None", plan: "Price plan", entry: "Entry", stop: "Stop loss",
    target1: "Target 1", target2: "Target 2", estimatedCost: "Estimated cost", netProfit: "Net result",
    paperTitle: "Add to PAPER simulator", paperHint: "This records a simulation. It does not send a broker order.",
    quantity: "Quantity", currency: "Currency", strategy: "Strategy", notes: "Notes",
    simulateBuy: "Save simulated entry", simulateSell: "Close simulation",
    chartUnavailable: "The chart is temporarily unavailable. Price levels and data are shown below.",
    chartCredit: "Charts by TradingView", noChartData: "No candles for this interval.",
    cash: "PAPER cash", equity: "PAPER value", unrealized: "Unrealized result", realized: "Realized result",
    totalTrades: "Trades", wins: "Winning", losses: "Losing", winRate: "Win rate",
    expectancy: "Average result", netPnl: "Net result", open: "Open", closed: "Closed",
    dataDelay: "Delayed data", dataAge: "Data age", delayedFor: "Delay",
    unknownStatus: "Status unknown", positionCreated: "Position saved.", settingsSaved: "Settings saved.",
    watchAdded: "Symbol added to watchlist.", symbolRemoved: "Symbol removed.",
    invalidInput: "Check the values you entered.", loginRequired: "Please sign in again to continue.",
    chartLoading: "Loading chart…", interval: "Interval", marketData: "Market data",
    fxLive: "FX rates are current from the provider cache.", fxFallback: "FX rates use fallback values from configuration.",
    fxStale: "FX rates are stale.", fxUnknown: "FX rates could not be loaded.",
    autoExecution: "TradingHelper does not place orders. You execute every trade manually.",
  },
};

let language = localStorage.getItem("trading-helper-language") === "en" ? "en" : "pl";
let activeChart = null;
let chartObserver = null;
let portfolioChart = null;
let portfolioChartObserver = null;
let paperAccountSnapshot = null;
let toastTimer = null;
let currentView = "dashboard";
let activityView = "trades";
let watchlistRows = [];

class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (response.status === 401) {
    if (!$("#loginDialog").open) $("#loginDialog").showModal();
    throw new ApiError(translate("loginRequired"), response.status);
  }
  if (!response.ok) {
    let detail = "";
    try { detail = (await response.json()).detail || ""; } catch { /* non-JSON error */ }
    if (response.status >= 500) detail = `${translate("errorLoad")} (${response.status})`;
    throw new ApiError(detail || `${translate("errorLoad")} (${response.status})`, response.status);
  }
  return response.status === 204 ? null : response.json();
}

function number(value, digits = 2) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString(language === "pl" ? "pl-PL" : "en-US", {
    minimumFractionDigits: digits, maximumFractionDigits: digits,
  }) : "—";
}

function money(value, currency) {
  return `${number(value)} ${currency || ""}`.trim();
}

function inputNumber(value, digits = 6) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toFixed(digits).replace(/\.?0+$/, "") : "";
}

function formatDate(value, options = {}) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleString(language === "pl" ? "pl-PL" : "en-US", options);
}

function statusText(value) {
  const statuses = {
    CURRENT: translate("current"), DELAYED: translate("delayed"), STALE: translate("stale"),
    UNKNOWN: translate("unknown"), NO_DATA: translate("unknown"), ONLINE: translate("online"),
    OFFLINE: translate("offline"), IDLE_MARKET_CLOSED: translate("marketClosed"),
    NOT_STARTED: translate("notStarted"), RUNNING: translate("run"),
    BUY_SETUP: translate("buySetup"), STRONG_BUY_SETUP: translate("strongBuy"),
    EXCEPTIONAL_SETUP: translate("exceptional"), INTERESTING: translate("interesting"),
    WATCH: translate("watch"), IGNORE: translate("ignore"), HOLD: translate("open"),
    CLOSED: translate("closed"), OPEN: translate("open"), ACTIVE: translate("active"),
    DEGRADED: translate("degraded"), STARTING: translate("starting"), COMPLETED: translate("completed"),
    PARTIAL: translate("partial"), FAILED: translate("failed"), WATCH_EXIT: translate("watchExit"),
    TRAILING_STOP_WARNING: translate("trailingWarning"), EXIT_WARNING: translate("exitWarning"),
    TAKE_PROFIT: translate("takeProfit"), SIMULATION: translate("simulation"),
  };
  if (typeof value === "string" && value.startsWith("ERROR:")) return `${translate("error")}: ${value.slice(6).trim()}`;
  return statuses[value] || value || translate("unknownStatus");
}

function showToast(message, kind = "success") {
  const toast = $("#toast");
  toast.textContent = message;
  toast.className = `toast visible${kind === "error" ? " error" : ""}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 4500);
}

function setFormMessage(target, message, kind = "error") {
  target.textContent = message;
  target.classList.toggle("success", kind === "success");
}

function showLoadError(target, error, retry) {
  target.innerHTML = `<div class="empty-state" role="alert"><p>${escapeHtml(error.message || translate("errorLoad"))}</p>
    <button class="button button-secondary" type="button" data-retry>${escapeHtml(translate("retry"))}</button></div>`;
  $(`[data-retry]`, target).addEventListener("click", retry, { once: true });
}

function emptyState(message, action = "") {
  return `<div class="empty-state"><p>${escapeHtml(message)}</p>${action}</div>`;
}

function applyLanguage() {
  document.documentElement.lang = language;
  $$('[data-i18n]').forEach((element) => {
    const value = translate(element.dataset.i18n);
    const textNode = [...element.childNodes].find((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim());
    if (textNode) textNode.textContent = value;
    else element.textContent = value;
  });
  $$('[data-i18n-placeholder]').forEach((element) => { element.placeholder = translate(element.dataset.i18nPlaceholder); });
  $$('[data-i18n-aria-label]').forEach((element) => { element.setAttribute("aria-label", translate(element.dataset.i18nAriaLabel)); });
  const languageField = $("#language");
  if (languageField) languageField.value = language;
  renderNavigation();
}

function renderNavigation() {
  const mainPage = ["dashboard", "portfolio", "activity"].includes(currentView) ? currentView : "more";
  $$(".main-nav > button[data-view]").forEach((button) => {
    if (button.dataset.view === mainPage) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  $$(".more-popover [data-view]").forEach((button) => {
    if (button.dataset.view === currentView) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  const moreSummary = $("#moreMenu summary");
  if (mainPage === "more" && currentView !== "more") moreSummary.setAttribute("aria-current", "page");
  else moreSummary.removeAttribute("aria-current");
  $("#moreMenu").open = mainPage === "more" && currentView !== "more";
}

function setView(view) {
  currentView = view;
  $$("main > .view").forEach((section) => section.classList.toggle("hidden", section.id !== view));
  renderNavigation();
  $("#mainContent").focus({ preventScroll: true });
  const loaders = {
    dashboard: loadDashboard,
    portfolio: loadPortfolio,
    activity: loadActivity,
    watchlist: loadWatchlist,
    system: loadSystem,
    settings: loadSettings,
  };
  if (loaders[view]) loaders[view]();
}

function updateConnection(status) {
  $("#connectionLabel").textContent = `${translate("online")} · ${(status.provider || "").toUpperCase()}`;
  $("#statusButton").classList.remove("offline");
  $("#statusButton").classList.add("online");
  $("#offline").classList.add("hidden");
}

function setActivityView(view) {
  activityView = view;
  $("#tradeActivity").classList.toggle("hidden", view !== "trades");
  $("#eventActivity").classList.toggle("hidden", view !== "events");
  $$("[data-activity]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.activity === view)));
  if (view === "events") loadEvents(); else loadTrades();
}

function freshness(signal) {
  const warnings = signal.warnings || [];
  if (signal.data_source === "sample") return ["unknown", translate("sampleData")];
  const stale = warnings.some((warning) => /data stale|stale/i.test(warning));
  if (stale) return ["stale", translate("freshnessStale")];
  if (signal.is_delayed) return ["delayed", translate("freshnessDelayed")];
  if (signal.data_timestamp && signal.data_source && signal.data_source !== "UNKNOWN") {
    return ["current", translate("freshnessCurrent")];
  }
  return ["unknown", translate("freshnessUnknown")];
}

function renderSignalCard(signal) {
  const [freshClass, freshLabel] = freshness(signal);
  const currency = signal.instrument_currency || signal.currency || "";
  const values = signal.display_values && signal.display_currency !== currency ?
    `<small>≈ ${escapeHtml(money(signal.display_values.price, signal.display_currency))}</small>` : "";
  const rr = Number(signal.risk_reward);
  const scoreLabel = signal.label || "";
  return `<button type="button" class="signal-card" data-symbol="${escapeHtml(signal.symbol)}" aria-label="${escapeHtml(signal.symbol)} — ${escapeHtml(statusText(scoreLabel))}, wynik ${Number(signal.score)}">
    <span class="signal-top"><span class="symbol-line"><strong>${escapeHtml(signal.symbol)}</strong><small>${escapeHtml(signal.name || "")}</small></span>
      <span class="score-block"><span class="score">${Number(signal.score)}</span><span class="score-caption">/ 100</span></span></span>
    <span class="signal-metrics"><span>${translate("price")}<strong>${escapeHtml(money(signal.price, currency))}</strong>${values}</span>
      <span>${translate("riskReward")}<strong>${Number.isFinite(rr) ? `1:${number(rr)}` : "—"}</strong></span></span>
    <span class="signal-bottom"><span class="status-pill">${escapeHtml(statusText(scoreLabel))}</span>
      <span class="freshness ${freshClass}">${escapeHtml(freshLabel)}</span></span>
    <span class="signal-bottom"><small>${translate("lastReport")} ${escapeHtml(formatDate(signal.data_timestamp, { dateStyle: "short", timeStyle: "short" }))}</small>
      <small>${escapeHtml(signal.data_source || translate("unknown"))}</small></span>
  </button>`;
}

async function loadDashboard() {
  const summary = $("#dashboardSummary");
  const signals = $("#signals");
  signals.innerHTML = emptyState(translate("loading"));
  try {
    const [status, setups, positions] = await Promise.all([
      api("/status"), api("/signals?min_score=40&limit=30"), api("/portfolio"),
    ]);
    updateConnection(status);
    const attention = positions.filter((position) => position.monitor_status &&
      !["HOLD", "PENDING"].includes(position.monitor_status));
    const dataStatus = status.data_status || "NO_DATA";
    const dataTone = dataStatus === "CURRENT" ? "tone-good" : dataStatus === "NO_DATA" ? "" : "tone-warn";
    summary.innerHTML = [
      [translate("server"), statusText(status.server), status.server === "ONLINE" ? "tone-good" : "tone-bad"],
      [translate("data"), statusText(dataStatus), dataTone],
      [translate("openPositions"), String(positions.length), ""],
      [translate("attention"), String(attention.length), attention.length ? "tone-warn" : "tone-good"],
    ].map(([label, value, tone]) => `<div class="summary-item"><small>${escapeHtml(label)}</small><strong class="${tone}">${escapeHtml(value)}</strong></div>`).join("");
    signals.innerHTML = setups.map(renderSignalCard).join("") || emptyState(translate("noSignals"),
      `<button class="button button-secondary" type="button" data-open-watchlist>${escapeHtml(translate("watchSymbols"))}</button>`);
    $$('[data-symbol]', signals).forEach((card) => card.addEventListener("click", () => showSignal(card.dataset.symbol)));
    $("[data-open-watchlist]", signals)?.addEventListener("click", () => setView("watchlist"));
    const newest = setups[0]?.data_timestamp;
    $("#lastUpdate").textContent = newest ? `${translate("lastReport")} ${formatDate(newest)}` : translate("unknown");
    const credits = status.provider_credits;
    $("#healthPanel").innerHTML = `<strong>${translate("online")}</strong> · ${translate("market")}: ${escapeHtml(statusText(status.market))}
      · ${translate("scanner")}: ${escapeHtml(statusText(status.scheduler))} · ${translate("provider")}: ${escapeHtml(status.provider || "—")}
      ${credits ? ` · ${translate("apiUsage")}: ${Number(credits.used_today)}/${Number(credits.background_limit)}; ${translate("apiReserve")} ${Number(credits.reserved)}` : ""}`;
    $("#offline").classList.add("hidden");
  } catch (error) {
    summary.innerHTML = "";
    showLoadError(signals, error, loadDashboard);
  }
}

function detailWarning(signal) {
  if (!signal.warnings?.length) return translate("none");
  return signal.warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("");
}

async function renderChart(signal, timeframe) {
  const target = $("#priceChart");
  target.innerHTML = `<div class="empty-state">${escapeHtml(translate("chartLoading"))}</div>`;
  if (activeChart) { activeChart.remove(); activeChart = null; }
  if (chartObserver) { chartObserver.disconnect(); chartObserver = null; }
  try {
    const data = await api(`/market/candles/${encodeURIComponent(signal.symbol)}?timeframe=${encodeURIComponent(timeframe)}&limit=240`);
    if (!data.candles?.length) { target.innerHTML = emptyState(translate("noChartData")); return; }
    if (!window.LightweightCharts) { target.innerHTML = emptyState(translate("chartUnavailable")); return; }
    target.innerHTML = "";
    const chart = window.LightweightCharts.createChart(target, {
      width: target.clientWidth, height: target.clientHeight,
      layout: { background: { type: "solid", color: "#fff" }, textColor: "#617184" },
      grid: { vertLines: { color: "#edf1f4" }, horzLines: { color: "#edf1f4" } },
      rightPriceScale: { borderColor: "#dce4eb" }, timeScale: { borderColor: "#dce4eb", timeVisible: timeframe !== "1d" },
      crosshair: { mode: 0 },
    });
    activeChart = chart;
    const candles = chart.addSeries(window.LightweightCharts.CandlestickSeries, {
      upColor: "#14775f", downColor: "#a03c3c", borderVisible: false,
      wickUpColor: "#14775f", wickDownColor: "#a03c3c",
    });
    candles.setData(data.candles.map((row) => ({ time: row.time, open: row.open, high: row.high, low: row.low, close: row.close })));
    [["ema20", "#27678d"], ["ema50", "#945707"], ["ema200", "#526b83"]].forEach(([field, color]) => {
      const line = chart.addSeries(window.LightweightCharts.LineSeries, { color, lineWidth: 2, priceLineVisible: false, lastValueVisible: false });
      line.setData(data.candles.filter((row) => Number.isFinite(row[field])).map((row) => ({ time: row.time, value: row[field] })));
    });
    const volume = chart.addSeries(window.LightweightCharts.HistogramSeries, { priceScaleId: "", priceFormat: { type: "volume" }, color: "#cbd6df" });
    volume.priceScale().applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });
    volume.setData(data.candles.map((row) => ({ time: row.time, value: row.volume, color: row.close >= row.open ? "#8fcbb366" : "#d88e8666" })));
    [[signal.entry_low, translate("entry"), "#27678d"], [signal.stop_price, translate("stop"), "#a03c3c"],
      [signal.target_price, translate("target1"), "#14775f"], [signal.target_price_2, translate("target2"), "#38816d"]].forEach(([price, title, color]) => {
      if (Number(price) > 0) candles.createPriceLine({ price, color, lineWidth: 1, lineStyle: 2, axisLabelVisible: true, title });
    });
    chart.timeScale().fitContent();
    chartObserver = new ResizeObserver((entries) => chart.applyOptions({ width: entries[0].contentRect.width }));
    chartObserver.observe(target);
    $("#chartMeta").textContent = `${data.source || translate("unknown")} · ${data.timeframe} · ${data.candles.length} · ${formatDate(data.data_timestamp)}${data.is_delayed ? ` · ${translate("delayed")}` : ""}`;
  } catch (error) {
    target.innerHTML = emptyState(error.status === 401 ? translate("loginRequired") : translate("chartUnavailable"));
  }
}

function signalDetailMarkup(signal) {
  const details = signal.details || {};
  const indicators = details.indicators || {};
  const breakdown = signal.breakdown || {};
  const currency = signal.instrument_currency || details.currency || "";
  const [freshClass, freshLabel] = freshness(signal);
  const recommendation = signal.feasibility_status ? statusText(signal.feasibility_status) : "";
  return `<div class="signal-head"><div><h2 id="signalDialogTitle">${escapeHtml(signal.symbol)} <small>${escapeHtml(signal.name || "")}</small></h2>
      <span class="status-pill">${escapeHtml(statusText(signal.label))}</span> <span class="freshness ${freshClass}">${escapeHtml(freshLabel)}</span></div>
      <div class="detail-score">${Number(signal.score)}<small>/100</small></div></div>
    <p class="detail-lead">${escapeHtml(translate("autoExecution"))} ${recommendation ? ` ${escapeHtml(recommendation)}.` : ""}
      ${translate("lastReport")}: ${escapeHtml(formatDate(signal.data_timestamp))} · ${translate("source")}: ${escapeHtml(signal.data_source || translate("unknown"))}</p>
    <div class="detail-risk" aria-label="${translate("plan")}">
      <div><small>${translate("entry")}</small><strong>${escapeHtml(money(signal.entry_low, currency))}–${escapeHtml(money(signal.entry_high, currency))}</strong></div>
      <div><small>${translate("stop")}</small><strong>${escapeHtml(money(signal.stop_price, currency))}</strong></div>
      <div><small>${translate("target1")}</small><strong>${escapeHtml(money(signal.target_price, currency))}</strong></div>
      <div><small>${translate("riskReward")}</small><strong>1:${number(signal.risk_reward)}</strong></div>
    </div>
    <details open><summary>${translate("chart")}</summary><div class="chart-toolbar"><div class="chart-timeframes" role="group" aria-label="${translate("interval")}">
      ${["1d", "4h", "1h", "15m"].map((timeframe) => `<button type="button" data-timeframe="${timeframe}" aria-pressed="${timeframe === signal.timeframe}">${timeframe.toUpperCase()}</button>`).join("")}</div>
      <small id="chartMeta"></small></div><div id="priceChart" class="price-chart" aria-label="${translate("chart")}"></div>
      <a class="chart-credit" href="https://www.tradingview.com" target="_blank" rel="noopener">${translate("chartCredit")}</a></details>
    <details><summary>${translate("indicators")}</summary><div class="detail-plan">${[["RSI", indicators.rsi], ["ATR", indicators.atr], ["EMA 20", indicators.ema20], ["EMA 50", indicators.ema50], ["EMA 200", indicators.ema200], ["MACD", indicators.macd]].map(([label, value]) =>
      `<div><small>${escapeHtml(label)}</small><strong>${escapeHtml(number(value))}</strong></div>`).join("")}</div></details>
    <details><summary>${translate("score")}</summary><div class="breakdown-grid">${Object.entries(breakdown).map(([key, value]) =>
      `<div><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`).join("") || translate("none")}</div></details>
    <details><summary>${translate("costs")}</summary><div class="detail-plan">
      <div><small>${translate("estimatedCost")}</small><strong>${escapeHtml(money(signal.estimated_total_cost, currency))}</strong></div>
      <div><small>${translate("netProfit")}</small><strong>${escapeHtml(money(signal.expected_net_profit, currency))}</strong></div>
      <div><small>${translate("target2")}</small><strong>${escapeHtml(money(signal.target_price_2, currency))}</strong></div>
    </div></details>
    <details ${signal.warnings?.length ? "open" : ""}><summary>${translate("warnings")}</summary><ul>${detailWarning(signal)}</ul></details>
    <section class="paper-trade-box"><h3>${translate("paperTitle")}</h3><p>${translate("paperHint")}</p>
      <form id="paperBuyForm" class="paper-trade-form">
        <label>${translate("date")}<input name="entry_date" type="datetime-local" required></label>
        <label>${translate("entry")}<input name="price" type="number" min="0.0001" step="any" value="${inputNumber((Number(signal.entry_low) + Number(signal.entry_high)) / 2, 4)}" required></label>
        <label>${translate("quantity")}<input name="quantity" type="number" min="0.000001" step="any" value="${inputNumber(signal.recommended_quantity, 6)}" required></label>
        <label>${translate("currency")}<input name="currency" minlength="3" maxlength="3" value="${escapeHtml(currency)}" required></label>
        <label>${translate("stop")}<input name="stop_price" type="number" min="0.0001" step="any" value="${inputNumber(signal.stop_price, 4)}" required></label>
        <label>${translate("target1")}<input name="target_price" type="number" min="0.0001" step="any" value="${inputNumber(signal.target_price, 4)}" required></label>
        <label>${translate("target2")}<input name="target_price_2" type="number" min="0.0001" step="any" value="${inputNumber(signal.target_price_2, 4)}"></label>
        <label>${translate("strategy")}<input name="strategy" maxlength="100" value="${escapeHtml(signal.label || "")}"></label>
        <label class="paper-notes">${translate("notes")}<textarea name="notes" rows="2" maxlength="1000"></textarea></label>
        <div id="paperBuyPreview" class="paper-preview"></div><span id="paperBuyMessage" class="form-message" role="alert"></span>
        <button class="button button-primary" type="submit">${translate("simulateBuy")}</button>
      </form><div id="signalPaperPositions" class="list-stack"></div></section>`;
}

async function showSignal(symbol) {
  try {
    const signal = await api(`/signals/${encodeURIComponent(symbol)}`);
    $("#signalDetails").innerHTML = signalDetailMarkup(signal);
    $("#signalDialog").showModal();
    const dateInput = $("#paperBuyForm [name=entry_date]");
    dateInput.value = new Date(Date.now() - new Date().getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
    $$("[data-timeframe]").forEach((button) => button.addEventListener("click", () => {
      $$("[data-timeframe]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      renderChart(signal, button.dataset.timeframe);
    }));
    bindPaperForm(signal);
    updatePaperPreview(signal);
    await Promise.all([loadSignalPaperPositions(signal.symbol), renderChart(signal, signal.timeframe || "1h")]);
  } catch (error) { showToast(error.message || translate("errorLoad"), "error"); }
}

function updatePaperPreview(signal) {
  const form = $("#paperBuyForm");
  if (!form) return;
  const currency = form.elements.currency.value.toUpperCase();
  const price = Number(form.elements.price.value) || 0;
  const quantity = Number(form.elements.quantity.value) || 0;
  const stop = Number(form.elements.stop_price.value) || 0;
  const target = Number(form.elements.target_price.value) || 0;
  $("#paperBuyPreview").innerHTML = [
    [translate("positionValue"), money(price * quantity, currency)],
    [translate("riskToStop"), money(Math.max(0, price - stop) * quantity, currency)],
    [translate("targetPotential"), money(Math.max(0, target - price) * quantity, currency)],
    [translate("estimatedCost"), money(signal.estimated_total_cost, currency)],
  ].map(([label, value]) => `<div><small>${escapeHtml(label)}</small><strong>${escapeHtml(value)}</strong></div>`).join("");
}

function bindPaperForm(signal) {
  const form = $("#paperBuyForm");
  form.querySelectorAll("input").forEach((input) => input.addEventListener("input", () => updatePaperPreview(signal)));
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const submit = $("button[type=submit]", form);
    submit.disabled = true;
    setFormMessage($("#paperBuyMessage"), "");
    try {
      const response = await api("/paper/buy", { method: "POST", body: JSON.stringify({
        symbol: signal.symbol, signal_id: signal.id, price: Number(data.get("price")),
        quantity: Number(data.get("quantity")), currency: String(data.get("currency")).toUpperCase(),
        entry_date: new Date(String(data.get("entry_date"))).toISOString(),
        stop_price: Number(data.get("stop_price")), target_price: Number(data.get("target_price")),
        target_price_2: data.get("target_price_2") ? Number(data.get("target_price_2")) : null,
        strategy: data.get("strategy"), notes: data.get("notes"),
      }) });
      const account = await api("/paper/account");
      showToast(`${translate("paperBuySuccess")}: ${signal.symbol} · ${money(response.total_account_currency, account.currency)}`);
      await Promise.all([loadSignalPaperPositions(signal.symbol), loadPortfolio()]);
    } catch (error) { setFormMessage($("#paperBuyMessage"), error.message || translate("invalidInput")); }
    finally { submit.disabled = false; }
  });
}

async function loadSignalPaperPositions(symbol) {
  const target = $("#signalPaperPositions");
  if (!target) return;
  try {
    const rows = await api("/portfolio");
    const positions = rows.filter((position) => position.mode === "PAPER" && position.symbol === symbol);
    target.innerHTML = positions.map((position) => `<div class="paper-position"><span><strong>${escapeHtml(position.symbol)}</strong>
      <small>${escapeHtml(number(position.quantity, 4))} @ ${escapeHtml(money(position.entry_price, position.currency))}</small></span>
      <button type="button" class="row-action" data-sell-paper="${Number(position.id)}">${translate("simulateSell")}</button></div>`).join("");
    $$('[data-sell-paper]', target).forEach((button) => button.addEventListener("click", () => sellPaperPosition(Number(button.dataset.sellPaper), symbol)));
  } catch (error) { showLoadError(target, error, () => loadSignalPaperPositions(symbol)); }
}

async function sellPaperPosition(positionId, symbol) {
  const accepted = await requestConfirmation({ title: `${translate("simulateSell")} ${symbol}?`,
    message: translate("paperSellConfirm"), actionLabel: translate("confirmSell") });
  if (!accepted) return;
  try {
    await api("/paper/sell", { method: "POST", body: JSON.stringify({ position_id: positionId }) });
    showToast(`${translate("paperSellSuccess")}: ${symbol}`);
    await Promise.all([loadSignalPaperPositions(symbol), loadPortfolio()]);
  } catch (error) { showToast(error.message || translate("errorLoad"), "error"); }
}

async function renderPortfolioChart() {
  const [history, account] = await Promise.all([api("/portfolio/history?limit=500"), api("/paper/account")]);
  const target = $("#portfolioChart");
  paperAccountSnapshot = account;
  if (portfolioChart) { portfolioChart.remove(); portfolioChart = null; }
  if (portfolioChartObserver) { portfolioChartObserver.disconnect(); portfolioChartObserver = null; }
  $("#paperInitialCash").value = account.initial_cash;
  $("#paperCurrencyLabel").textContent = `(${escapeHtml(account.currency)})`;
  $("#portfolioSummary").innerHTML = [
    [translate("cash"), money(account.cash_balance, account.currency), ""],
    [translate("equity"), money(account.equity, account.currency), ""],
    [translate("unrealized"), money(account.unrealized_pnl, account.currency), account.unrealized_pnl >= 0 ? "positive" : "negative"],
    [translate("realized"), money(account.realized_pnl, account.currency), account.realized_pnl >= 0 ? "positive" : "negative"],
  ].map(([label, value, tone]) => `<div class="summary-item"><small>${escapeHtml(label)}</small><strong class="${tone}">${escapeHtml(value)}</strong></div>`).join("");
  if (!history.items.length || !window.LightweightCharts) {
    target.innerHTML = emptyState(history.items.length ? translate("chartUnavailable") : translate("noPortfolioHistory"));
    return;
  }
  target.textContent = "";
  const chart = window.LightweightCharts.createChart(target, {
    width: target.clientWidth, height: target.clientHeight,
    layout: { background: { type: "solid", color: "#fff" }, textColor: "#617184" },
    grid: { vertLines: { color: "#edf1f4" }, horzLines: { color: "#edf1f4" } },
    timeScale: { timeVisible: true }, rightPriceScale: { borderVisible: false },
  });
  const value = chart.addSeries(window.LightweightCharts.AreaSeries, { lineColor: "#27678d", topColor: "#9fc5d544", bottomColor: "#9fc5d505", lineWidth: 2 });
  value.setData(history.items.map((item) => ({ time: Math.floor(new Date(item.timestamp).getTime() / 1000), value: item.total_value })));
  const pnl = chart.addSeries(window.LightweightCharts.HistogramSeries, { priceScaleId: "pnl", priceLineVisible: false, lastValueVisible: true });
  pnl.setData(history.items.map((item) => ({ time: Math.floor(new Date(item.timestamp).getTime() / 1000), value: item.total_pnl,
    color: item.total_pnl >= 0 ? "#14775f88" : "#a03c3c88" })));
  chart.priceScale("pnl").applyOptions({ scaleMargins: { top: 0.75, bottom: 0 } });
  chart.timeScale().fitContent();
  portfolioChart = chart;
  portfolioChartObserver = new ResizeObserver((entries) => chart.applyOptions({ width: entries[0].contentRect.width }));
  portfolioChartObserver.observe(target);
}

function renderPosition(position) {
  const mode = position.mode === "PAPER" ? translate("paper") : translate("manual");
  const status = position.monitor_status ? statusText(position.monitor_status) : translate("unknownStatus");
  const profit = position.pnl == null ? translate("unknown") : money(position.pnl, position.currency);
  const [freshClass, freshLabel] = freshness(position);
  return `<article class="list-row"><div><strong>${escapeHtml(position.symbol)}</strong><small>${escapeHtml(mode)} · ${escapeHtml(position.broker || "")}</small></div>
    <div class="row-value">${escapeHtml(number(position.quantity, 4))} @ ${escapeHtml(money(position.entry_price, position.currency))}<small>${translate("status")}: ${escapeHtml(status)}</small></div>
    <div class="row-value">P/L ${escapeHtml(profit)}${position.pnl_percent == null ? "" : `<small>${escapeHtml(number(position.pnl_percent))}%</small>`}</div>
    <span class="freshness ${freshClass}">${escapeHtml(freshLabel)}</span></article>`;
}

async function loadPortfolio() {
  const target = $("#positions");
  target.innerHTML = emptyState(translate("loading"));
  let positions;
  try { positions = await api("/portfolio"); }
  catch (error) { showLoadError(target, error, loadPortfolio); return; }
  const filter = $("#positionFilter").value;
  const visible = positions.filter((position) => filter === "ALL" || position.mode === filter);
  target.innerHTML = visible.map(renderPosition).join("") || emptyState(translate("noPositions"));
  const exits = positions.filter((position) => position.monitor_status && !["HOLD", "PENDING"].includes(position.monitor_status));
  $("#exitSignals").classList.toggle("hidden", !exits.length);
  $("#exitItems").innerHTML = exits.map((position) => `<div class="exit-alert"><strong>${escapeHtml(position.symbol)}</strong>
    <span>${escapeHtml(statusText(position.monitor_status))}</span><small>${escapeHtml(money(position.current_price, position.currency))} · P/L ${escapeHtml(number(position.pnl_percent))}%</small></div>`).join("");
  try { await renderPortfolioChart(); }
  catch (error) { $("#portfolioChart").innerHTML = emptyState(error.message || translate("chartUnavailable")); }
}

async function loadTrades() {
  const target = $("#trades");
  target.innerHTML = emptyState(translate("loading"));
  try {
    const response = await api("/trades");
    const names = { total_trades: translate("totalTrades"), wins: translate("wins"), losses: translate("losses"), win_rate: translate("winRate"), expectancy: translate("expectancy"), net_pnl: translate("netPnl") };
    $("#stats").innerHTML = Object.entries(response.statistics).map(([key, value]) => `<div><small>${escapeHtml(names[key] || key)}</small><strong>${escapeHtml(number(value, key.includes("rate") ? 1 : 2))}</strong></div>`).join("");
    target.innerHTML = response.items.map((trade) => `<article class="list-row"><div><strong>${escapeHtml(trade.symbol)}</strong><small>${escapeHtml(trade.broker || translate("unknown"))}</small></div>
      <div class="row-value">${escapeHtml(formatDate(trade.entry_date, { dateStyle: "medium" }))}<small>${escapeHtml(statusText(trade.status))}</small></div>
      <div class="row-value">P/L ${escapeHtml(trade.pnl == null ? "—" : money(trade.pnl, trade.currency))}</div>
      <small>${escapeHtml(trade.strategy || "")}</small></article>`).join("") || emptyState(translate("noTrades"));
  } catch (error) { showLoadError(target, error, loadTrades); }
}

async function loadEvents() {
  const target = $("#eventList");
  target.innerHTML = emptyState(translate("loading"));
  try {
    const events = await api("/events?limit=100");
    target.innerHTML = events.map((event) => {
      let details = event.details;
      if (!details && event.details_json) {
        try { details = JSON.parse(event.details_json); } catch { details = event.details_json; }
      }
      const technical = details ? `<details><summary>${escapeHtml(translate("technicalDetails"))}</summary><pre>${escapeHtml(typeof details === "string" ? details : JSON.stringify(details, null, 2))}</pre></details>` : "";
      return `<article class="list-row"><div><strong>${escapeHtml(event.message || event.event_type)}</strong><small>${escapeHtml(event.event_type || "")}</small></div>
        <div class="row-value">${escapeHtml(formatDate(event.created_at))}</div>${technical}</article>`;
    }).join("") || emptyState(translate("noEvents"));
  } catch (error) { showLoadError(target, error, loadEvents); }
}

async function loadActivity() { if (activityView === "events") await loadEvents(); else await loadTrades(); }

async function loadWatchlist() {
  const target = $("#watchItems");
  target.innerHTML = emptyState(translate("loading"));
  try {
    watchlistRows = await api("/watchlist");
    renderWatchlist();
  } catch (error) { showLoadError(target, error, loadWatchlist); }
}

function renderWatchlist() {
  const target = $("#watchItems");
  const query = $("#watchSearch").value.trim().toLocaleLowerCase();
  const rows = watchlistRows.filter((item) => `${item.symbol} ${item.notes || ""}`.toLocaleLowerCase().includes(query));
  target.innerHTML = rows.map((item) => `<article class="list-row"><div><strong>${escapeHtml(item.symbol)}</strong><small>${escapeHtml(item.notes || "")}</small></div>
      <div class="row-value">${escapeHtml(item.created_at ? formatDate(item.created_at) : "")}</div><button class="row-action" type="button" data-remove-symbol="${escapeHtml(item.symbol)}">${translate("remove")}</button></article>`).join("") || emptyState(translate("noWatchlist"));
    $$('[data-remove-symbol]', target).forEach((button) => button.addEventListener("click", async () => {
      button.disabled = true;
      try { await api(`/watchlist/${encodeURIComponent(button.dataset.removeSymbol)}`, { method: "DELETE" }); showToast(translate("symbolRemoved")); await loadWatchlist(); }
      catch (error) { button.disabled = false; showToast(error.message, "error"); }
  }));
}

async function loadSystem() {
  const target = $("#systemDetails");
  target.innerHTML = emptyState(translate("loading"));
  try {
    const [status, scans] = await Promise.all([api("/status"), api("/scanner/status")]);
    const values = [
      [translate("server"), statusText(status.server)], [translate("market"), statusText(status.market)],
      [translate("data"), statusText(status.data_status)], [translate("scanner"), statusText(status.scheduler)],
      [translate("provider"), status.provider || translate("unknown")], [translate("lastScan"), formatDate(status.last_successful_scan)],
      [translate("lastMarketUpdate"), formatDate(status.last_market_data_update)],
      [translate("uptime"), `${Math.floor(Number(status.uptime_seconds || 0) / 3600)} ${translate("hours")}`],
    ];
    target.innerHTML = values.map(([label, value]) => `<div class="system-card"><small>${escapeHtml(label)}</small><strong>${escapeHtml(value)}</strong></div>`).join("");
    $("#scanRuns").innerHTML = scans.map((run) => `<article class="list-row"><div><strong>${escapeHtml(run.status || translate("unknown"))}</strong><small>${escapeHtml(run.symbols_ok ?? 0)}/${escapeHtml(run.symbols_total ?? 0)} ${escapeHtml(translate("symbolsScanned"))} · ${escapeHtml(run.provider || "")}</small></div>
      <div class="row-value">${escapeHtml(formatDate(run.started_at))}</div><small>${escapeHtml(run.error || "")}</small></article>`).join("") || emptyState(translate("noScans"));
    $("#offline").classList.add("hidden");
  } catch (error) { showLoadError(target, error, loadSystem); }
}

async function loadSettings() {
  const target = $("#settingsLoadError");
  try {
    const settings = await api("/settings/public");
    const form = $("#settingsForm");
    form.elements.portfolio_value.value = settings.portfolio_value;
    form.elements.risk_percent.value = settings.risk_percent;
    form.elements.scan_interval_seconds.value = settings.scan_interval_seconds;
    form.elements.display_currency.innerHTML = settings.supported_currencies.map((currency) =>
      `<option value="${escapeHtml(currency)}" ${currency === settings.display_currency ? "selected" : ""}>${escapeHtml(currency)}</option>`).join("");
    language = settings.language || "pl";
    applyLanguage();
    const fxText = { FALLBACK: "fxFallback", STALE: "fxStale", UNAVAILABLE: "fxUnknown" }[settings.fx_rate_status] || "fxLive";
    $("#fxStatus").textContent = translate(fxText);
    target.innerHTML = "";
    $("#offline").classList.add("hidden");
  } catch (error) { showLoadError(target, error, loadSettings); }
}

async function requestConfirmation({ title, message, actionLabel }) {
  $("#confirmTitle").textContent = title;
  $("#confirmMessage").textContent = message;
  $("#confirmAction").textContent = actionLabel;
  const dialog = $("#confirmDialog");
  const result = new Promise((resolve) => dialog.addEventListener("close", () => resolve(dialog.returnValue === "confirm"), { once: true }));
  dialog.showModal();
  return result;
}

function bindForms() {
  $("#scanButton").addEventListener("click", async () => {
    const button = $("#scanButton");
    button.disabled = true;
    try { await api("/scanner/run", { method: "POST" }); showToast(translate("scanStarted")); await loadDashboard(); }
    catch (error) { showToast(error.message || translate("scanFailed"), "error"); }
    finally { button.disabled = false; }
  });
  $("#watchlistForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const message = $("#watchlistMessage");
    try {
      await api("/watchlist", { method: "POST", body: JSON.stringify({ symbol: form.elements.symbol.value.trim().toUpperCase(), notes: form.elements.notes.value.trim() }) });
      form.reset(); setFormMessage(message, translate("watchAdded"), "success"); await loadWatchlist();
    } catch (error) { setFormMessage(message, error.message || translate("invalidInput")); }
  });
  $("#paperCapitalForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    try { if (!paperAccountSnapshot) paperAccountSnapshot = await api("/paper/account"); }
    catch (error) { setFormMessage($("#paperResetError"), error.message || translate("errorLoad")); return; }
    const account = paperAccountSnapshot;
    const accountSummary = `${translate("availableCash")}: ${money(account.cash_balance, account.currency)} · ${translate("openCount")}: ${Number(account.open_positions || 0)}.`;
    const accepted = await requestConfirmation({ title: translate("confirmPaperTitle"),
      message: `${translate("resetPreview")} ${accountSummary} ${translate("paperResetReason")}`, actionLabel: translate("confirmReset") });
    if (!accepted) return;
    const submit = $("button[type=submit]", form);
    submit.disabled = true; setFormMessage($("#paperResetError"), "");
    try {
      await api("/paper/account", { method: "PUT", body: JSON.stringify({ initial_cash: Number(form.elements.initial_cash.value) }) });
      setFormMessage($("#paperResetError"), translate("paperResetSuccess"), "success"); await loadPortfolio();
    } catch (error) { setFormMessage($("#paperResetError"), error.message || translate("invalidInput")); }
    finally { submit.disabled = false; }
  });
  $("#positionForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const payload = Object.fromEntries(data.entries());
    payload.symbol = String(payload.symbol).trim().toUpperCase();
    payload.currency = String(payload.currency).trim().toUpperCase();
    payload.entry_date = new Date(`${payload.entry_date}T12:00:00`).toISOString();
    payload.entry_price = Number(payload.entry_price); payload.quantity = Number(payload.quantity);
    payload.stop_price = payload.stop_price ? Number(payload.stop_price) : null;
    payload.target_price = payload.target_price ? Number(payload.target_price) : null;
    payload.target_price_2 = null; payload.mode = "MANUAL";
    try {
      await api("/portfolio", { method: "POST", body: JSON.stringify(payload) });
      $("#positionDialog").close(); form.reset(); $("#positionBroker").value = "MANUAL"; $("#positionCurrency").value = "USD";
      showToast(translate("positionCreated")); await loadPortfolio();
    } catch (error) { setFormMessage($("#positionMessage"), error.message || translate("invalidInput")); }
  });
  $("#positionFilter").addEventListener("change", loadPortfolio);
  $("#watchSearch").addEventListener("input", renderWatchlist);
  $("#addPosition").addEventListener("click", () => {
    $("#positionDate").value = new Date().toISOString().slice(0, 10);
    $("#positionMessage").textContent = "";
    $("#positionDialog").showModal();
    $("#positionSymbol").focus();
  });
  $("#settingsForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const message = $("#settingsMessage");
    try {
      await api("/settings/public", { method: "PUT", body: JSON.stringify({
        portfolio_value: Number(form.elements.portfolio_value.value), risk_percent: Number(form.elements.risk_percent.value),
        scan_interval_seconds: Number(form.elements.scan_interval_seconds.value), display_currency: form.elements.display_currency.value,
        language: form.elements.language.value,
      }) });
      language = form.elements.language.value;
      try { localStorage.setItem("trading-helper-language", language); } catch { /* preference remains on server */ }
      applyLanguage(); setFormMessage(message, translate("settingsSaved"), "success");
      await loadDashboard();
    } catch (error) { setFormMessage(message, error.message || translate("invalidInput")); }
  });
  $("#loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    try {
      const response = await fetch("/auth/login", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: form.elements.username.value, password: form.elements.password.value }) });
      if (!response.ok) throw new Error(response.status === 429 ? translate("tooManyLogins") : translate("badCredentials"));
      location.reload();
    } catch (error) { setFormMessage($("#loginError"), error.message); }
  });
}

function bindNavigation() {
  $$("[data-view]").forEach((button) => button.addEventListener("click", () => {
    setView(button.dataset.view);
    $("#moreMenu").open = false;
  }));
  $$("[data-activity]").forEach((button) => button.addEventListener("click", () => setActivityView(button.dataset.activity)));
  $("#statusButton").addEventListener("click", () => {
    const panel = $("#healthPanel");
    panel.classList.toggle("hidden");
    $("#statusButton").setAttribute("aria-expanded", String(!panel.classList.contains("hidden")));
  });
  $("#refreshSystem").addEventListener("click", loadSystem);
  $(".dialog-close").addEventListener("click", () => $("#signalDialog").close());
  $$("[data-close-dialog]").forEach((button) => button.addEventListener("click", () => button.closest("dialog").close()));
}

async function refreshVisibleData() {
  if (currentView === "dashboard") await loadDashboard();
  else if (currentView === "portfolio") await loadPortfolio();
  else if (currentView === "activity") await loadActivity();
  else if (currentView === "watchlist") await loadWatchlist();
  else if (currentView === "system") await loadSystem();
}

function initialize() {
  bindNavigation();
  bindForms();
  applyLanguage();
  loadDashboard();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(() => {});
  const stream = new EventSource("/events/stream");
  let refreshTimer;
  stream.addEventListener("update", () => {
    clearTimeout(refreshTimer);
    refreshTimer = setTimeout(refreshVisibleData, 450);
  });
  stream.onerror = () => $("#offline").classList.remove("hidden");
  setInterval(async () => {
    try {
      const status = await api("/status");
      updateConnection(status);
    } catch {
      $("#connectionLabel").textContent = translate("offline");
      $("#statusButton").classList.remove("online"); $("#statusButton").classList.add("offline");
      $("#offline").classList.remove("hidden");
    }
  }, 30_000);
}

initialize();
