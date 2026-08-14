const $=s=>document.querySelector(s), api=async(path,options={})=>{const response=await fetch(path,
{headers:{"Content-Type":"application/json"},...options});if(response.status===401){
$('#loginDialog').showModal();throw new Error('401')}if(!response.ok)throw new Error(`${response.status}`);
return response.status===204?null:response.json()};
const fmt=n=>Number(n||0).toFixed(2);
const money=(value,currency)=>`${fmt(value)} ${currency||''}`.trim();
const translations={pl:{nav_dashboard:'Pulpit',nav_portfolio:'Portfel',nav_journal:'Dziennik',
nav_watchlist:'Obserwowane',nav_system:'System',nav_settings:'Ustawienia',hero_badge:'NIEZALEŻNY ASYSTENT TRADINGOWY',
hero_title:'Rynek w jednym miejscu.',hero_text:'Analiza i monitoring. Każdą transakcję wykonujesz ręcznie.',
run_scan:'Uruchom skan',top_setups:'Najlepsze setupy',portfolio:'Portfel',simulate_entry:'Symuluj wejście',
trade_journal:'Dziennik transakcji',watchlist:'Lista obserwowanych',system_events:'Zdarzenia systemowe',
safe_settings:'Bezpieczne ustawienia',portfolio_value:'Wartość portfela',risk_percent:'Ryzyko %',
scan_interval:'Interwał skanowania w sekundach',display_currency:'Waluta prezentacji',language:'Język',
fx_loading:'Sprawdzanie kursów walut…',fx_live:'Kursy walut: Twelve Data, cache do 60 minut.',
fx_fallback:'Kursy walut: awaryjny kurs z konfiguracji YAML.',fx_stale:'Kursy walut są nieaktualne.',save:'Zapisz',sign_in:'Zaloguj się',
username:'Nazwa użytkownika',password:'Hasło',invalid_credentials:'Nieprawidłowe dane logowania',
server_offline:'SERWER OFFLINE — wyświetlane dane mogą być nieaktualne',no_signals:'Brak sygnałów. Uruchom pierwszy skan.',
no_positions:'Brak pozycji.',no_watchlist:'Lista obserwowanych jest pusta.',analyzed_price:'Analizowana cena',
symbol:'Symbol',notes:'Notatka (opcjonalnie)',add_to_watchlist:'Dodaj do listy',remove:'Usuń',
display_value:'Wartość prezentacyjna',score_breakdown:'Podział punktów',trade_plan:'Plan transakcji',costs:'Koszty',
estimated_total:'Szacowany koszt',net_expected:'Oczekiwany wynik netto',warnings:'Ostrzeżenia',none:'Brak',
verify:'Sprawdź aktualną cenę u brokera. TradingHelper nigdy nie wykonuje transakcji.',
CURRENT:'AKTUALNE',DELAYED:'OPÓŹNIONE',STALE:'NIEAKTUALNE',SIMULATION:'SYMULACJA',ACTIVE:'AKTYWNY',
BUY_SETUP:'SETUP KUPNA',STRONG_BUY_SETUP:'MOCNY SETUP KUPNA',EXCEPTIONAL_SETUP:'WYJĄTKOWY SETUP',
INTERESTING:'INTERESUJĄCY',WATCH:'OBSERWUJ',IGNORE:'IGNORUJ',HOLD:'TRZYMAJ',WATCH_EXIT:'OBSERWUJ WYJŚCIE',
TAKE_PROFIT:'REALIZACJA ZYSKU',TRAILING_STOP_WARNING:'OSTRZEŻENIE TRAILING STOP',EXIT_WARNING:'OSTRZEŻENIE WYJŚCIA'},
en:{nav_dashboard:'Dashboard',nav_portfolio:'Portfolio',nav_journal:'Journal',nav_watchlist:'Watchlist',
nav_system:'System',nav_settings:'Settings',hero_badge:'BROKER-INDEPENDENT ASSISTANT',hero_title:'The market in one place.',
hero_text:'Analysis and monitoring. You execute every trade manually.',run_scan:'Run scan',top_setups:'Top setups',
portfolio:'Portfolio',simulate_entry:'Simulate entry',trade_journal:'Trade journal',watchlist:'Watchlist',
system_events:'System events',safe_settings:'Safe settings',portfolio_value:'Portfolio value',risk_percent:'Risk %',
scan_interval:'Scan interval in seconds',display_currency:'Display currency',language:'Language',
fx_loading:'Checking FX rates…',fx_live:'FX rates: Twelve Data, cached up to 60 minutes.',
fx_fallback:'FX rates: configured YAML fallback.',fx_stale:'FX rates are stale.',save:'Save',sign_in:'Sign in',
username:'Username',password:'Password',invalid_credentials:'Invalid credentials',server_offline:'SERVER OFFLINE — displayed data may be stale',
no_signals:'No signals. Run the first scan.',no_positions:'No positions.',no_watchlist:'Watchlist is empty.',
symbol:'Symbol',notes:'Notes (optional)',add_to_watchlist:'Add to watchlist',remove:'Remove',
analyzed_price:'Analyzed price',display_value:'Display value',score_breakdown:'Score breakdown',trade_plan:'Trade plan',
costs:'Costs',estimated_total:'Estimated total',net_expected:'Expected net result',warnings:'Warnings',none:'None',
verify:'Verify the current price in your broker. TradingHelper never executes trades.'}};
let language='pl';const tr=key=>translations[language]?.[key]||translations.en[key]||key;
const statusLabel=value=>tr(value)||value;function applyLanguage(){document.documentElement.lang=language;
document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=tr(el.dataset.i18n)})}
async function loadStatus(){try{const s=await api('/status');$('#statusButton').innerHTML=`<span class="dot"></span>
ONLINE · ${s.provider.toUpperCase()}`;$('#healthPanel').innerHTML=`<b>Serwer:</b> ONLINE &nbsp; <b>Rynek:</b>
${statusLabel(s.market)} &nbsp; <b>Skaner:</b> ${statusLabel(s.scheduler)} &nbsp; <b>Dane:</b> ${statusLabel(s.data_status)}`;
$('#offline').classList.add('hidden')}catch(e){
$('#statusButton').textContent='● OFFLINE';$('#offline').classList.remove('hidden')}}
async function loadSignals(){const rows=await api('/signals?min_score=40&limit=30');$('#signals').innerHTML=rows.map(s=>
`<article class="signal" data-symbol="${s.symbol}"><div class="meta">${s.symbol} · ${s.timeframe}</div>
<div class="score">${s.score}</div><div class="label">${statusLabel(s.label)}</div>
<p>${money(s.price,s.instrument_currency)} · R:R ${fmt(s.risk_reward)}</p>
${s.display_values&&s.display_currency!==s.instrument_currency?`<p class="meta">≈ ${money(s.display_values.price,s.display_currency)}</p>`:''}
${s.is_delayed?'<p class="warning">DATA DELAYED</p>':''}</article>`
).join('')||`<p>${tr('no_signals')}</p>`;$('#lastUpdate').textContent=new Date().toLocaleTimeString();
document.querySelectorAll('.signal').forEach(el=>el.onclick=()=>showSignal(el.dataset.symbol))}
async function showSignal(symbol){const s=await api(`/signals/${symbol}`),b=s.breakdown||{},d=s.details||{};
$('#signalDetails').innerHTML=`<h2>${s.symbol} — ${s.name}</h2><div class="score">${s.score}/100</div>
<h3>${statusLabel(s.label)}</h3><p>${tr('analyzed_price')}: ${money(s.price,s.instrument_currency)}</p>
${s.display_values?`<p>${tr('display_value')}: ≈ ${money(s.display_values.price,s.display_currency)}
<small> (${s.fx_rate_source})</small></p>`:''}<h3>${tr('score_breakdown')}</h3>
${Object.entries(b).map(([k,v])=>`<div class="row"><span>${k}</span><b>${v}</b></div>`).join('')}
<h3>${tr('trade_plan')}</h3><p>Entry ${money(s.entry_low,s.instrument_currency)}–${money(s.entry_high,s.instrument_currency)} ·
SL ${money(s.stop_price,s.instrument_currency)} · TP1 ${money(s.target_price,s.instrument_currency)} ·
TP2 ${money(s.target_price_2,s.instrument_currency)}</p><h3>${tr('costs')}</h3><p>${tr('estimated_total')}:
${money(s.estimated_total_cost,s.instrument_currency)} · ${tr('net_expected')}: ${money(s.expected_net_profit,s.instrument_currency)}</p>
${s.display_values?`<p>Converted costs: ≈ ${money(s.display_values.estimated_total_cost,s.display_currency)} ·
net: ≈ ${money(s.display_values.expected_net_profit,s.display_currency)}</p>`:''}<h3>${tr('warnings')}</h3>
<p>${(s.warnings||[]).join('<br>')||tr('none')}</p><p class="warning">${tr('verify')}</p>`;$('#signalDialog').showModal()}
async function loadPortfolio(){const rows=await api('/portfolio');$('#positions').innerHTML=rows.map(p=>
`<div class="row"><span><b>${p.symbol}</b><br><small>${p.broker} · ${p.mode}</small></span>
<span>${p.quantity} @ ${money(p.entry_price,p.currency)}<br><small>${p.monitor_status} · P/L ${money(p.pnl,p.currency)}
${p.display_pnl!=null&&p.display_currency!==p.currency?` · ≈ ${money(p.display_pnl,p.display_currency)}`:''}</small></span></div>`).join('')||`<p>${tr('no_positions')}</p>`}
async function loadTrades(){const result=await api('/trades');$('#stats').innerHTML=Object.entries(result.statistics)
.map(([k,v])=>`<div><small>${k.replaceAll('_',' ')}</small><br><b>${v}</b></div>`).join('');
$('#trades').innerHTML=result.items.map(t=>`<div class="row"><b>${t.symbol}</b><span>${t.status} · P/L ${fmt(t.pnl)}</span></div>`).join('')}
async function loadEvents(){const rows=await api('/events');$('#eventList').innerHTML=rows.map(e=>
`<div class="row"><span><b>${e.event_type}</b><br><small>${e.message}</small></span><small>${new Date(e.created_at).toLocaleString()}</small></div>`).join('')}
async function loadWatchlist(){const rows=await api('/watchlist');$('#watchItems').innerHTML=rows.map(w=>
`<div class="row"><span><b>${w.symbol}</b><br><small>${w.notes||''}</small></span>
<button class="danger remove-watch" data-symbol="${w.symbol}">${tr('remove')}</button></div>`).join('')||`<p>${tr('no_watchlist')}</p>`;
document.querySelectorAll('.remove-watch').forEach(button=>button.onclick=async()=>{
await api(`/watchlist/${encodeURIComponent(button.dataset.symbol)}`,{method:'DELETE'});await loadWatchlist()})}
async function loadSettings(){const s=await api('/settings/public'),f=$('#settingsForm');
f.portfolio_value.value=s.portfolio_value;f.risk_percent.value=s.risk_percent;
f.scan_interval_seconds.value=s.scan_interval_seconds;f.display_currency.innerHTML=s.supported_currencies.map(currency=>
`<option value="${currency}" ${currency===s.display_currency?'selected':''}>${currency}</option>`).join('');
language=s.language||'pl';f.language.value=language;applyLanguage();
const fxStatus=$('#fxStatus');if(s.fx_rate_status==='FALLBACK'){fxStatus.textContent=tr('fx_fallback')}
else if(s.fx_rate_status==='STALE'){fxStatus.textContent=tr('fx_stale')}
else{fxStatus.textContent=tr('fx_live')}}
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{document.querySelectorAll('nav button').forEach(x=>x.classList.remove('active'));
b.classList.add('active');document.querySelectorAll('.view').forEach(x=>x.classList.add('hidden'));$('#'+b.dataset.view).classList.remove('hidden');
({portfolio:loadPortfolio,journal:loadTrades,watchlist:loadWatchlist,events:loadEvents,
settings:loadSettings}[b.dataset.view]||loadSignals)()});
$('#scanButton').onclick=async()=>{await api('/scanner/run',{method:'POST'});await loadSignals()};
$('#addPaper').onclick=async()=>{const symbol=prompt('Symbol, e.g. NVDA');if(!symbol)return;
const entry=Number(prompt('Entry price')),quantity=Number(prompt('Quantity (fractional allowed)'));
if(!entry||!quantity)return;await api('/portfolio',{method:'POST',body:JSON.stringify({symbol,
broker:'SIMULATION',entry_price:entry,quantity,currency:'USD',entry_date:new Date().toISOString(),mode:'PAPER'})});
await loadPortfolio()};
$('#watchlistForm').onsubmit=async event=>{event.preventDefault();const f=event.target;
await api('/watchlist',{method:'POST',body:JSON.stringify({symbol:f.symbol.value.trim().toUpperCase(),notes:f.notes.value.trim()})});
f.reset();await loadWatchlist()};
$('#settingsForm').onsubmit=async event=>{event.preventDefault();const f=event.target;
await api('/settings/public',{method:'PUT',body:JSON.stringify({portfolio_value:Number(f.portfolio_value.value),
risk_percent:Number(f.risk_percent.value),scan_interval_seconds:Number(f.scan_interval_seconds.value),
display_currency:f.display_currency.value,language:f.language.value})});language=f.language.value;applyLanguage();await loadSignals()};
$('#loginForm').onsubmit=async event=>{event.preventDefault();const f=event.target,response=await fetch('/auth/login',
{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:f.username.value,
password:f.password.value})});if(response.ok){$('#loginDialog').close();location.reload()}
else $('#loginError').classList.remove('hidden')};
$('#statusButton').onclick=()=>$('#healthPanel').classList.toggle('hidden');$('.close').onclick=()=>$('#signalDialog').close();
if('serviceWorker'in navigator)navigator.serviceWorker.register('/static/sw.js');
const events=new EventSource('/events/stream');let refreshTimer=null;events.addEventListener('update',()=>{
clearTimeout(refreshTimer);refreshTimer=setTimeout(()=>{loadSignals();loadStatus();
if(!$('#portfolio').classList.contains('hidden'))loadPortfolio()},500)});events.onerror=()=>$('#offline').classList.remove('hidden');
loadStatus();loadSignals();setInterval(loadStatus,30000);
