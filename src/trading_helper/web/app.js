const $=s=>document.querySelector(s), api=async(path,options={})=>{const response=await fetch(path,
{headers:{"Content-Type":"application/json"},...options});if(response.status===401){
$('#loginDialog').showModal();throw new Error('401')}if(!response.ok)throw new Error(`${response.status}`);
return response.status===204?null:response.json()};
const fmt=n=>Number(n||0).toFixed(2);
const money=(value,currency)=>`${fmt(value)} ${currency||''}`.trim();
// Every value originating in the API or a user-controlled form must be escaped before
// it is interpolated into an HTML template. Static translation strings are trusted.
const esc=window.TradingHelperSecurity.escapeHtml;
const translations={pl:{nav_dashboard:'Pulpit',nav_portfolio:'Portfel',nav_journal:'Dziennik',
nav_watchlist:'Obserwowane',nav_system:'System',nav_settings:'Ustawienia',hero_badge:'NIEZALEŻNY ASYSTENT TRADINGOWY',
hero_title:'Rynek w jednym miejscu.',hero_text:'Analiza i monitoring. Każdą transakcję wykonujesz ręcznie.',
run_scan:'Uruchom skan',top_setups:'Najlepsze setupy',portfolio:'Portfel',simulate_entry:'Symuluj wejście',
portfolio_value_now:'Wartość',invested:'Kapitał',unrealized_pnl:'Niezrealizowany P/L',exit_signals:'Sygnały wyjścia',
positions:'Pozycje',portfolio_chart_note:'Wartość i niezrealizowany wynik portfela',
paper_capital:'Kapitał symulatora',reset_paper:'Ustaw / resetuj PAPER',cash:'Gotówka',equity:'Equity',
realized_pnl:'Zrealizowany P/L',paper_simulator:'Symulator PAPER',simulate_buy:'Symuluj kupno',simulate_sell:'Symuluj sprzedaż',
suggested:'Podpowiedź systemu',entry_date:'Data wejścia',currency:'Waluta',quantity:'Ilość',strategy:'Strategia',
paper_notes:'Notatki do transakcji',position_value:'Wartość pozycji',risk_value:'Ryzyko do SL',potential_tp1:'Potencjał do TP1',
choose_setup:'Wybierz setup na pulpicie i otwórz jego szczegóły.',
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
indicators:'Wskaźniki',details:'Szczegóły',data_source:'Dane',chart_loading:'Wczytywanie wykresu…',
verify:'Sprawdź aktualną cenę u brokera. TradingHelper nigdy nie wykonuje transakcji.',
CURRENT:'AKTUALNE',DELAYED:'OPÓŹNIONE',STALE:'NIEAKTUALNE',SIMULATION:'SYMULACJA',ACTIVE:'AKTYWNY',
BUY_SETUP:'SETUP KUPNA',STRONG_BUY_SETUP:'MOCNY SETUP KUPNA',EXCEPTIONAL_SETUP:'WYJĄTKOWY SETUP',
INTERESTING:'INTERESUJĄCY',WATCH:'OBSERWUJ',IGNORE:'IGNORUJ',HOLD:'TRZYMAJ',WATCH_EXIT:'OBSERWUJ WYJŚCIE',
TAKE_PROFIT:'REALIZACJA ZYSKU',TRAILING_STOP_WARNING:'OSTRZEŻENIE TRAILING STOP',EXIT_WARNING:'OSTRZEŻENIE WYJŚCIA'},
en:{nav_dashboard:'Dashboard',nav_portfolio:'Portfolio',nav_journal:'Journal',nav_watchlist:'Watchlist',
nav_system:'System',nav_settings:'Settings',hero_badge:'BROKER-INDEPENDENT ASSISTANT',hero_title:'The market in one place.',
hero_text:'Analysis and monitoring. You execute every trade manually.',run_scan:'Run scan',top_setups:'Top setups',
portfolio:'Portfolio',simulate_entry:'Simulate entry',trade_journal:'Trade journal',watchlist:'Watchlist',
portfolio_value_now:'Value',invested:'Invested',unrealized_pnl:'Unrealized P/L',exit_signals:'Exit signals',
positions:'Positions',portfolio_chart_note:'Portfolio value and unrealized result',
paper_capital:'Simulator capital',reset_paper:'Set / reset PAPER',cash:'Cash',equity:'Equity',
realized_pnl:'Realized P/L',paper_simulator:'PAPER simulator',simulate_buy:'Simulate buy',simulate_sell:'Simulate sell',
suggested:'System suggestion',entry_date:'Entry date',currency:'Currency',quantity:'Quantity',strategy:'Strategy',
paper_notes:'Trade notes',position_value:'Position value',risk_value:'Risk to SL',potential_tp1:'Potential to TP1',
choose_setup:'Choose a setup on the dashboard and open its details.',
system_events:'System events',safe_settings:'Safe settings',portfolio_value:'Portfolio value',risk_percent:'Risk %',
scan_interval:'Scan interval in seconds',display_currency:'Display currency',language:'Language',
fx_loading:'Checking FX rates…',fx_live:'FX rates: Twelve Data, cached up to 60 minutes.',
fx_fallback:'FX rates: configured YAML fallback.',fx_stale:'FX rates are stale.',save:'Save',sign_in:'Sign in',
username:'Username',password:'Password',invalid_credentials:'Invalid credentials',server_offline:'SERVER OFFLINE — displayed data may be stale',
no_signals:'No signals. Run the first scan.',no_positions:'No positions.',no_watchlist:'Watchlist is empty.',
symbol:'Symbol',notes:'Notes (optional)',add_to_watchlist:'Add to watchlist',remove:'Remove',
analyzed_price:'Analyzed price',display_value:'Display value',score_breakdown:'Score breakdown',trade_plan:'Trade plan',
costs:'Costs',estimated_total:'Estimated total',net_expected:'Expected net result',warnings:'Warnings',none:'None',
indicators:'Indicators',details:'Details',data_source:'Data',chart_loading:'Loading chart…',
verify:'Verify the current price in your broker. TradingHelper never executes trades.'}};
let language='pl';const tr=key=>translations[language]?.[key]||translations.en[key]||key;
const statusLabel=value=>tr(value)||value;function applyLanguage(){document.documentElement.lang=language;
document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=tr(el.dataset.i18n)})}
async function loadStatus(){try{const s=await api('/status');$('#statusButton').innerHTML=`<span class="dot"></span>
ONLINE · ${s.provider.toUpperCase()}`;const credits=s.provider_credits;
$('#healthPanel').innerHTML=`<b>Serwer:</b> ONLINE &nbsp; <b>Rynek:</b>
${statusLabel(s.market)} &nbsp; <b>Skaner:</b> ${statusLabel(s.scheduler)} &nbsp; <b>Dane:</b> ${statusLabel(s.data_status)}
${credits?` &nbsp; <b>API:</b> ${credits.used_today}/${credits.background_limit} · rezerwa ${credits.reserved}`:''}`;
$('#offline').classList.add('hidden')}catch(e){
$('#statusButton').textContent='● OFFLINE';$('#offline').classList.remove('hidden')}}
async function loadSignals(){const rows=await api('/signals?min_score=40&limit=30');$('#signals').innerHTML=rows.map(s=>
`<article class="signal" data-symbol="${esc(s.symbol)}"><div class="meta">${esc(s.symbol)} · ${esc(s.timeframe)}</div>
<div class="score">${s.score}</div><div class="label">${esc(statusLabel(s.label))}</div>
<p>${esc(money(s.price,s.instrument_currency))} · R:R ${fmt(s.risk_reward)}</p>
${s.display_values&&s.display_currency!==s.instrument_currency?`<p class="meta">≈ ${esc(money(s.display_values.price,s.display_currency))}</p>`:''}
${s.is_delayed?'<p class="warning">DATA DELAYED</p>':''}</article>`
).join('')||`<p>${tr('no_signals')}</p>`;$('#lastUpdate').textContent=new Date().toLocaleTimeString();
document.querySelectorAll('.signal').forEach(el=>el.onclick=()=>showSignal(el.dataset.symbol))}
let activeChart=null,chartObserver=null;
async function renderChart(signal,timeframe){const target=$('#priceChart');target.textContent=tr('chart_loading');
const data=await api(`/market/candles/${signal.symbol}?timeframe=${timeframe}&limit=240`);target.textContent='';
if(activeChart)activeChart.remove();if(chartObserver)chartObserver.disconnect();
if(!window.LightweightCharts){target.textContent='Chart library unavailable';return}
const chart=LightweightCharts.createChart(target,{height:360,layout:{background:{type:'solid',color:'#fff'},textColor:'#667085'},
grid:{vertLines:{color:'#f1f3f7'},horzLines:{color:'#f1f3f7'}},rightPriceScale:{borderColor:'#e5e9f0'},
timeScale:{borderColor:'#e5e9f0',timeVisible:timeframe!=='1d'},crosshair:{mode:0}});activeChart=chart;
const candles=chart.addSeries(LightweightCharts.CandlestickSeries,{upColor:'#16a36a',downColor:'#e05252',borderVisible:false,
wickUpColor:'#16a36a',wickDownColor:'#e05252'});candles.setData(data.candles.map(x=>({time:x.time,open:x.open,high:x.high,low:x.low,close:x.close})));
[['ema20','#2563eb'],['ema50','#f59e0b'],['ema200','#7c3aed']].forEach(([field,color])=>{const line=chart.addSeries(
LightweightCharts.LineSeries,{color,lineWidth:2,priceLineVisible:false,lastValueVisible:false});
line.setData(data.candles.map(x=>({time:x.time,value:x[field]})))});
const volume=chart.addSeries(LightweightCharts.HistogramSeries,{priceScaleId:'',priceFormat:{type:'volume'},
color:'#cbd5e1'});volume.priceScale().applyOptions({scaleMargins:{top:.82,bottom:0}});
volume.setData(data.candles.map(x=>({time:x.time,value:x.volume,color:x.close>=x.open?'#86d6b544':'#ef999944'})));
[[signal.entry_low,'ENTRY','#2563eb'],[signal.stop_price,'SL','#dc2626'],[signal.target_price,'TP1','#16a36a'],
[signal.target_price_2,'TP2','#15803d']].forEach(([price,title,color])=>{if(price)candles.createPriceLine({price,color,
lineWidth:1,lineStyle:2,axisLabelVisible:true,title})});chart.timeScale().fitContent();
chartObserver=new ResizeObserver(entries=>chart.applyOptions({width:entries[0].contentRect.width}));chartObserver.observe(target);
$('#chartMeta').textContent=`${data.source} · ${data.timeframe} · ${data.candles.length} świec · ${new Date(data.data_timestamp).toLocaleString()}${data.is_delayed?' · DELAYED':''} · plan: ${signal.timeframe}`}
async function showSignal(symbol){const s=await api(`/signals/${symbol}`),b=s.breakdown||{},d=s.details||{},i=d.indicators||{};
$('#signalDetails').innerHTML=`<div class="signal-head"><div><h2>${esc(s.symbol)} <small>${esc(s.name)}</small></h2>
<span class="pill">${esc(statusLabel(s.label))}</span></div><div class="score">${s.score}<small>/100</small></div></div>
<div class="compact-stats"><div><small>${tr('analyzed_price')}</small><b>${esc(money(s.price,s.instrument_currency))}</b></div>
<div><small>${tr('display_value')}</small><b>${esc(s.display_values?money(s.display_values.price,s.display_currency):'—')}</b></div>
<div><small>RSI</small><b>${fmt(i.rsi)}</b></div><div><small>ATR</small><b>${fmt(i.atr)}</b></div>
<div><small>R:R</small><b>1:${fmt(s.risk_reward)}</b></div><div><small>FX</small><b>${esc(s.fx_rate_source||'—')}</b></div></div>
<div class="chart-toolbar"><div>${['1d','4h','1h','15m'].map(tf=>`<button data-timeframe="${tf}" class="chart-tf ${tf===s.timeframe?'active':''}">${tf.toUpperCase()}</button>`).join('')}</div>
<small id="chartMeta"></small></div><div id="priceChart" class="price-chart"></div>
<a class="chart-credit" href="https://www.tradingview.com" target="_blank" rel="noopener">Charts by TradingView</a>
<div class="trade-grid"><div><small>ENTRY</small><b>${esc(money(s.entry_low,s.instrument_currency))}–${esc(money(s.entry_high,s.instrument_currency))}</b></div>
<div><small>STOP</small><b>${esc(money(s.stop_price,s.instrument_currency))}</b></div><div><small>TP1</small><b>${esc(money(s.target_price,s.instrument_currency))}</b></div>
<div><small>TP2</small><b>${esc(money(s.target_price_2,s.instrument_currency))}</b></div></div>
<details><summary>${tr('score_breakdown')}</summary><div class="breakdown-grid">${Object.entries(b).map(([k,v])=>`<div><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join('')}</div></details>
<details><summary>${tr('costs')}</summary><p>${tr('estimated_total')}: ${esc(money(s.estimated_total_cost,s.instrument_currency))} ·
${tr('net_expected')}: ${esc(money(s.expected_net_profit,s.instrument_currency))}</p></details>
<details ${s.warnings?.length?'open':''}><summary>${tr('warnings')}</summary><p>${(s.warnings||[]).map(esc).join('<br>')||tr('none')}</p></details>
<section class="paper-trade-box"><h3>${tr('paper_simulator')}</h3><p class="meta">${tr('suggested')} — pola możesz zmienić przed symulacją.</p>
<form id="paperBuyForm" class="paper-trade-form">
<label>${tr('symbol')}<input name="symbol" value="${esc(s.symbol)}" readonly></label>
<label>Broker / tryb<input value="SIMULATION / PAPER" readonly></label>
<label>${tr('entry_date')}<input name="entry_date" type="datetime-local" required></label>
<label>Entry<input name="price" type="number" min="0.0001" step="any" value="${((s.entry_low+s.entry_high)/2).toFixed(4)}" required></label>
<label>${tr('quantity')}<input name="quantity" type="number" min="0.000001" step="any" value="${s.recommended_quantity||''}" required></label>
<label>${tr('currency')}<input name="currency" maxlength="3" value="${esc(s.instrument_currency)}" required></label>
<label>Stop loss<input name="stop_price" type="number" min="0.0001" step="any" value="${s.stop_price||''}" required></label>
<label>Take profit 1<input name="target_price" type="number" min="0.0001" step="any" value="${s.target_price||''}" required></label>
<label>Take profit 2<input name="target_price_2" type="number" min="0.0001" step="any" value="${s.target_price_2||''}"></label>
<label>${tr('strategy')}<input name="strategy" maxlength="100" value="${esc(s.label||'')}"></label>
<label class="paper-notes">${tr('paper_notes')}<textarea name="notes" maxlength="1000" rows="2" placeholder="${tr('notes')}"></textarea></label>
<div id="paperBuyPreview" class="paper-preview"></div><button class="primary">${tr('simulate_buy')}</button></form>
<div id="signalPaperPositions"></div></section>
<p class="warning">${tr('verify')}</p>`;$('#signalDialog').showModal();
document.querySelectorAll('.chart-tf').forEach(button=>button.onclick=()=>{document.querySelectorAll('.chart-tf').forEach(x=>x.classList.remove('active'));
button.classList.add('active');renderChart(s,button.dataset.timeframe)});
$('#paperBuyForm').onsubmit=async event=>{event.preventDefault();const f=event.target;
const payload={symbol:s.symbol,signal_id:s.id,price:Number(f.price.value),quantity:Number(f.quantity.value),currency:f.currency.value.toUpperCase(),
entry_date:new Date(f.entry_date.value).toISOString(),stop_price:Number(f.stop_price.value),target_price:Number(f.target_price.value),
target_price_2:f.target_price_2.value?Number(f.target_price_2.value):null,strategy:f.strategy.value,notes:f.notes.value};
const result=await api('/paper/buy',{method:'POST',body:JSON.stringify(payload)}),account=await api('/paper/account');
alert(`${tr('simulate_buy')}: ${s.symbol} · ${money(result.total_account_currency,account.currency)}`);
await loadSignalPaperPositions(s.symbol);await loadPortfolio()};
const buyForm=$('#paperBuyForm');buyForm.entry_date.value=new Date(Date.now()-new Date().getTimezoneOffset()*60000).toISOString().slice(0,16);
const updatePaperPreview=()=>{const price=Number(buyForm.price.value)||0,quantity=Number(buyForm.quantity.value)||0,
stop=Number(buyForm.stop_price.value)||0,tp1=Number(buyForm.target_price.value)||0,currency=buyForm.currency.value.toUpperCase();
$('#paperBuyPreview').innerHTML=`<div><small>${tr('position_value')}</small><b>${esc(money(price*quantity,currency))}</b></div>
<div><small>${tr('risk_value')}</small><b>${esc(money(Math.max(0,price-stop)*quantity,currency))}</b></div>
<div><small>${tr('potential_tp1')}</small><b>${esc(money(Math.max(0,tp1-price)*quantity,currency))}</b></div>
<div><small>${tr('estimated_total')}</small><b>${esc(money(s.estimated_total_cost||0,s.instrument_currency))}</b></div>`};
buyForm.querySelectorAll('input').forEach(input=>input.addEventListener('input',updatePaperPreview));updatePaperPreview();
await loadSignalPaperPositions(s.symbol);await renderChart(s,s.timeframe||'1h')}
async function sellPaperPosition(id,symbol){if(!confirm(`${tr('simulate_sell')} ${symbol}?`))return;
await api('/paper/sell',{method:'POST',body:JSON.stringify({position_id:id})});await loadSignalPaperPositions(symbol);await loadPortfolio()}
async function loadSignalPaperPositions(symbol){const rows=await api('/portfolio');const matches=rows.filter(p=>p.mode==='PAPER'&&p.symbol===symbol);
const target=$('#signalPaperPositions');if(!target)return;target.innerHTML=matches.map(p=>`<div class="paper-position"><span><b>${esc(p.symbol)}</b> ${esc(p.quantity)} @ ${esc(money(p.entry_price,p.currency))}</span>
<button class="danger signal-paper-sell" data-id="${Number(p.id)}" data-symbol="${esc(p.symbol)}">${tr('simulate_sell')}</button></div>`).join('');
document.querySelectorAll('.signal-paper-sell').forEach(b=>b.onclick=()=>sellPaperPosition(Number(b.dataset.id),b.dataset.symbol))}
async function renderPortfolioChart(){const [history,account]=await Promise.all([api('/portfolio/history?limit=500'),api('/paper/account')]),target=$('#portfolioChart');
const currency=account.currency;$('#paperCapitalForm').initial_cash.value=account.initial_cash;$('#portfolioSummary').innerHTML=`
<div><small>${tr('cash')}</small><b>${money(account.cash_balance,currency)}</b></div>
<div><small>${tr('equity')}</small><b>${money(account.equity,currency)}</b></div>
<div><small>${tr('unrealized_pnl')}</small><b class="${account.unrealized_pnl>=0?'positive':'negative'}">${money(account.unrealized_pnl,currency)}</b></div>
<div><small>${tr('realized_pnl')}</small><b class="${account.realized_pnl>=0?'positive':'negative'}">${money(account.realized_pnl,currency)}</b></div>`;
if(!history.items.length||!window.LightweightCharts){target.innerHTML=`<p class="meta">${tr('no_positions')}</p>`;return}
target.textContent='';const chart=LightweightCharts.createChart(target,{height:230,layout:{background:{type:'solid',color:'#fff'},textColor:'#667085'},
grid:{vertLines:{color:'#f1f3f7'},horzLines:{color:'#f1f3f7'}},timeScale:{timeVisible:true},rightPriceScale:{borderVisible:false}});
const value=chart.addSeries(LightweightCharts.AreaSeries,{lineColor:'#2563eb',topColor:'#2563eb44',bottomColor:'#2563eb05',lineWidth:2});
value.setData(history.items.map(x=>({time:Math.floor(new Date(x.timestamp).getTime()/1000),value:x.total_value})));
const pnl=chart.addSeries(LightweightCharts.HistogramSeries,{priceScaleId:'pnl',priceLineVisible:false,lastValueVisible:true});
pnl.setData(history.items.map(x=>({time:Math.floor(new Date(x.timestamp).getTime()/1000),value:x.total_pnl,
color:x.total_pnl>=0?'#16a36a88':'#dc262688'})));chart.priceScale('pnl').applyOptions({scaleMargins:{top:.75,bottom:0}});
chart.timeScale().fitContent();new ResizeObserver(entries=>chart.applyOptions({width:entries[0].contentRect.width})).observe(target)}
async function loadPortfolio(){const rows=await api('/portfolio');$('#positions').innerHTML=rows.map(p=>
`<div class="row"><span><b>${esc(p.symbol)}</b><br><small>${esc(p.broker)} · ${esc(p.mode)}</small></span>
<span>${esc(p.quantity)} @ ${esc(money(p.entry_price,p.currency))}<br><small>${esc(p.monitor_status)} · P/L ${esc(money(p.pnl,p.currency))}
${p.display_pnl!=null&&p.display_currency!==p.currency?` · ≈ ${esc(money(p.display_pnl,p.display_currency))}`:''}</small></span></div>`).join('')||`<p>${tr('no_positions')}</p>`;
const exits=rows.filter(p=>p.monitor_status&&p.monitor_status!=='HOLD'&&p.monitor_status!=='PENDING');
$('#exitSignals').classList.toggle('hidden',!exits.length);$('#exitItems').innerHTML=exits.map(p=>
`<div class="exit-alert"><b>${esc(p.symbol)}</b><span>${esc(statusLabel(p.monitor_status))}</span><small>${esc(money(p.current_price,p.currency))} · P/L ${fmt(p.pnl_percent)}%</small></div>`).join('');
await renderPortfolioChart()}
async function loadTrades(){const result=await api('/trades');$('#stats').innerHTML=Object.entries(result.statistics)
.map(([k,v])=>`<div><small>${k.replaceAll('_',' ')}</small><br><b>${v}</b></div>`).join('');
$('#trades').innerHTML=result.items.map(t=>`<div class="row"><b>${esc(t.symbol)}</b><span>${esc(t.status)} · P/L ${fmt(t.pnl)}</span></div>`).join('')}
async function loadEvents(){const rows=await api('/events');$('#eventList').innerHTML=rows.map(e=>
`<div class="row"><span><b>${esc(e.event_type)}</b><br><small>${esc(e.message)}</small></span><small>${esc(new Date(e.created_at).toLocaleString())}</small></div>`).join('')}
async function loadWatchlist(){const rows=await api('/watchlist');$('#watchItems').innerHTML=rows.map(w=>
`<div class="row"><span><b>${esc(w.symbol)}</b><br><small>${esc(w.notes||'')}</small></span>
<button class="danger remove-watch" data-symbol="${esc(w.symbol)}">${tr('remove')}</button></div>`).join('')||`<p>${tr('no_watchlist')}</p>`;
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
$('#addPaper').onclick=()=>{document.querySelector('nav button[data-view="dashboard"]').click();alert(tr('choose_setup'))};
$('#watchlistForm').onsubmit=async event=>{event.preventDefault();const f=event.target;
await api('/watchlist',{method:'POST',body:JSON.stringify({symbol:f.symbol.value.trim().toUpperCase(),notes:f.notes.value.trim()})});
f.reset();await loadWatchlist()};
$('#paperCapitalForm').onsubmit=async event=>{event.preventDefault();const f=event.target;
await api('/paper/account',{method:'PUT',body:JSON.stringify({initial_cash:Number(f.initial_cash.value)})});await loadPortfolio()};
$('#settingsForm').onsubmit=async event=>{event.preventDefault();const f=event.target;
await api('/settings/public',{method:'PUT',body:JSON.stringify({portfolio_value:Number(f.portfolio_value.value),
risk_percent:Number(f.risk_percent.value),scan_interval_seconds:Number(f.scan_interval_seconds.value),
display_currency:f.display_currency.value,language:f.language.value})});language=f.language.value;applyLanguage();await loadSignals()};
$('#loginForm').onsubmit=async event=>{event.preventDefault();const f=event.target,response=await fetch('/auth/login',
{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:f.username.value,
password:f.password.value})});if(response.ok){$('#loginDialog').close();location.reload()}
else $('#loginError').classList.remove('hidden')};
$('#statusButton').onclick=()=>$('#healthPanel').classList.toggle('hidden');$('.close').onclick=()=>$('#signalDialog').close();
if('serviceWorker'in navigator)navigator.serviceWorker.register('/sw.js',{scope:'/'});
const events=new EventSource('/events/stream');let refreshTimer=null;events.addEventListener('update',()=>{
clearTimeout(refreshTimer);refreshTimer=setTimeout(()=>{loadSignals();loadStatus();
if(!$('#portfolio').classList.contains('hidden'))loadPortfolio()},500)});events.onerror=()=>$('#offline').classList.remove('hidden');
loadStatus();loadSignals();setInterval(loadStatus,30000);
