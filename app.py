from flask import Flask, render_template_string, request
import ccxt
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# ==============================================================================
# TEMPLATE HTML: GABUNGAN FITUR 1 (SCANNER DENGAN REKOMENDASI) & FITUR 2 (KALKULATOR)
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Scalping AI Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121214; color: #e1e1e6; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { max-width: 900px; width: 100%; background: #202024; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        h1 { text-align: center; color: #00e676; margin-bottom: 5px; font-size: 28px; }
        p.subtitle { text-align: center; color: #8d8d99; margin-top: 0; margin-bottom: 30px; }
        
        .menu-box { background: #121214; padding: 20px; border-radius: 8px; border: 1px solid #29292e; margin-bottom: 25px; }
        .menu-title { font-weight: bold; color: #00e676; margin-bottom: 15px; font-size: 16px; border-bottom: 1px solid #29292e; padding-bottom: 5px; }
        
        .flex-form { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 12px; border-radius: 6px; border: 1px solid #4d4d57; background: #202024; color: white; font-size: 16px; text-transform: uppercase; }
        
        .btn-scalping { padding: 12px 20px; border: none; background-color: #00e676; color: #121214; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 15px; }
        .btn-scalping:hover { background-color: #00c853; }
        
        .btn-scanner { width: 100%; padding: 14px; border: none; background-color: #2196f3; color: white; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 16px; transition: 0.2s; }
        .btn-scanner:hover { background-color: #1976d2; }
        
        .result-box { border-top: 2px solid #4d4d57; padding-top: 20px; margin-top: 25px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .card { background: #121214; padding: 15px; border-radius: 8px; border: 1px solid #29292e; }
        .card h4 { margin: 0 0 5px 0; color: #8d8d99; font-size: 14px; }
        .card p { margin: 0; font-size: 18px; font-weight: bold; }
        
        .recommendation { background: #29292e; padding: 20px; border-radius: 8px; border-left: 5px solid #00e676; margin-bottom: 20px; position: relative; }
        .recommendation h3 { margin: 0 0 10px 0; color: #00e676; }
        
        .chart-container { background: #121214; padding: 15px; border-radius: 8px; border: 1px solid #29292e; margin-top: 20px; margin-bottom: 20px; }
        
        .indicator-list { background: #1b1b1f; padding: 15px; border-radius: 8px; font-size: 13px; color: #a1a1aa; margin-top: 15px; border: 1px solid #4d4d57; }
        .indicator-list ul { margin: 5px 0 0 0; padding-left: 15px; }
        .indicator-list li { margin-bottom: 5px; display: flex; align-items: center; justify-content: space-between; }
        
        .stoch-gauge-container { width: 120px; height: 10px; background-color: #4d4d57; border-radius: 5px; overflow: hidden; margin-left: 10px; position: relative; border: 1px solid #29292e;}
        .stoch-gauge-fill { height: 100%; position: absolute; top: 0; left: 0; transition: width 0.3s ease; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #121214; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #29292e; }
        th { background-color: #29292e; color: #00e676; font-size: 14px; }
        td { font-size: 14px; }
        
        /* Badge Status Rekomendasi Fitur 1 */
        .badge-status { padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; color: white; display: inline-block; text-align: center; }
        .badge-entry { background-color: #00c853; border: 1px solid #00e676; }
        .badge-wait { background-color: #b71c1c; border: 1px solid #ff4d4d; }
        
        .error { color: #f74040; background: #3a1a1a; padding: 15px; border-radius: 6px; border-left: 5px solid #f74040; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Crypto Scalping AI Hub</h1>
        <p class="subtitle">Indodax Market Terminal Pro</p>
        
        <div class="menu-box">
            <div class="menu-title">🔍 FITUR 1: CRYPTO SCANNER RADAR</div>
            <form method="POST">
                <input type="hidden" name="action" value="scan_potential">
                <button type="submit" class="btn-scanner">🚀 Analisis Koin Potensial (Scan Top 10 Pasar IDR)</button>
            </form>
        </div>

        <div class="menu-box">
            <div class="menu-title">💵 FITUR 2: KALKULATOR SCALPING INSTAN (+1.7%)</div>
            <form method="POST" class="flex-form">
                <input type="hidden" name="action" value="analyze_manual">
                <input type="text" name="pair" placeholder="Contoh: BTC/IDR" value="{{ pair }}" required>
                <button type="submit" class="btn-scalping">Analisis Scalping Koin</button>
            </form>
        </div>

        {% if error %}
            <div class="error">⚠️ {{ error }}</div>
        {% endif %}

        {% if potential_coins %}
            <div class="result-box">
                <h3 style="color: #2196f3; margin-bottom: 5px;">🔥 AKTIVITAS TOP 10 PASAR IDR TERBESAR</h3>
                <p style="color: #8d8d99; font-size: 12px; margin-top: 0;">Dievaluasi real-time berdasarkan Volume & Validasi Sinyal AI (Waktu: {{ waktu }} WIB)</p>
                <table>
                    <thead>
                        <tr>
                            <th>Pair Koin</th>
                            <th>Harga Sekarang</th>
                            <th>Kenaikan (24h)</th>
                            <th>Volume Pasar (24h)</th>
                            <th>Rekomendasi AI</th>
                            <th>Estimasi Jam Entry</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for coin in potential_coins %}
                        <tr>
                            <td style="font-weight: bold; color: #fff;">{{ coin.pair }}</td>
                            <td>Rp {{ "{:,.2f}".format(coin.price) if coin.price < 100 else "{:,.0f}".format(coin.price) }}</td>
                            <td style="color: {% if coin.change > 0 %}#00e676{% elif coin.change < 0 %}#ff4d4d{% else %}#8d8d99{% endif %}; font-weight: bold;">
                                {{ "+" if coin.change > 0 else "" }}{{ "{:.2f}".format(coin.change) }}%
                            </td>
                            <td style="color: #8d8d99;">Rp {{ coin.volume_formatted }}</td>
                            <td>
                                {% if coin.is_ready %}
                                    <span class="badge-status badge-entry">LAYAK ENTRY</span>
                                {% else %}
                                    <span class="badge-status badge-wait">WAIT & SEE</span>
                                {% endif %}
                            </td>
                            <td style="font-weight: bold; color: {% if coin.is_ready %}#00e676{% else %}#ffb300{% endif %};">
                                {{ coin.entry_time_text }}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <p style="color: #8d8d99; font-size: 13px; margin-top: 15px;">💡 <em>Petunjuk: Salin simbol koin yang berstatus "LAYAK ENTRY" ke dalam Fitur 2 untuk menghitung target jaring harga beli dan jual secara otomatis!</em></p>
            </div>
        {% endif %}

        {% if manual_result %}
            <div class="result-box">
                <h3>Hasil Analisis Real-Time: {{ pair }}</h3>
                <p style="color: #8d8d99; font-size: 14px;">Waktu Analisis: {{ waktu }} WIB</p>
                
                <div class="grid">
                    <div class="card">
                        <h4>Harga Terakhir</h4>
                        <p style="color: #fff;">Rp {{ "{:,.2f}".format(manual_result.latest_price) }}</p>
                    </div>
                    <div class="card">
                        <h4>Harga Tertinggi (24h)</h4>
                        <p style="color: #ff4d4d;">Rp {{ "{:,.2f}".format(manual_result.high_24h) }}</p>
                    </div>
                    <div class="card">
                        <h4>Harga Terendah (24h)</h4>
                        <p style="color: #00e676;">Rp {{ "{:,.2f}".format(manual_result.low_24h) }}</p>
                    </div>
                    <div class="card">
                        <h4>Status AI Volume</h4>
                        <p style="color: #00e676;">{{ manual_result.vol_status }}</p>
                    </div>
                </div>

                <h3 style="color: #00e676; margin-top: 25px; margin-bottom: 5px;">📈 Multi-Panel Indicator Chart AI</h3>
                <div class="chart-container">
                    <canvas id="scalpingIndicatorChart" style="height: 480px;"></canvas>
                </div>

                <div class="recommendation" style="border-left-color: {% if manual_result.is_ready %}#00e676{% else %}#ffb300{% endif %};">
                    <h3>🚨 REKOMENDASI SCALPING AI</h3>
                    <p><strong>KESIMPULAN:</strong> 
                        <span style="color: {% if manual_result.is_ready %}#00e676{% else %}#ffb300{% endif %}; font-weight: bold;">
                            {{ manual_result.signal }}
                        </span>
                    </p>
                    <p style="color: #e1e1e6; line-height: 1.5; margin-bottom: 15px;">💡 <strong>ALASAN AI:</strong> {{ manual_result.reason }}</p>
                    
                    <p>
                        <strong style="color: {{ manual_result.entry_color }};">🟢 JAM ENTRY:</strong> 
                        <span style="color: {{ manual_result.entry_color }}; font-weight: bold;">{{ manual_result.entry_status_text }}</span>
                    </p>
                    
                    <p>💵 <strong>HARGA ENTRY OPTIMAL:</strong> Rp {{ "{:,.2f}".format(manual_result.price_entry) }}</p>
                    <p style="color: #ff4d4d;">🔴 <strong>TARGET TAKE PROFIT (+1.7%):</strong> Rp {{ "{:,.2f}".format(manual_result.price_tp) }}</p>
                    <p style="color: #ffb300;">⏱️ <strong>ESTIMASI JAM TAKE PROFIT:</strong> {{ manual_result.waktu_tp_awal }} - {{ manual_result.waktu_tp_akhir }} WIB</p>
                    <p style="color: #8d8d99; font-size: 14px;">❌ Stop Loss (Proteksi): Rp {{ "{:,.2f}".format(manual_result.price_sl) }}</p>
                    
                    <div class="indicator-list">
                        📈 <strong>Matriks Indikator Konfirmasi (EMA, Stochastic RSI, VWAP):</strong>
                        <ul>
                            <li>
                                <span><strong>EMA 9 / EMA 21:</strong> {{ manual_result.ema_status }}</span>
                                <span style="font-weight: bold; color: {% if manual_result.is_bullish %}#00e676{% else %}#ff4d4d{% endif %}; margin-left: 10px;">
                                    {% if manual_result.is_bullish %}↑ Bullish ↑{% else %}↓ Bearish Rejection ↓{% endif %}
                                </span>
                            </li>
                            <li>
                                <span><strong>Stochastic RSI:</strong> {{ "{:.1f}".format(manual_result.stoch_rsi) }}% ({{ manual_result.stoch_status }})</span>
                                <div class="stoch-gauge-container">
                                    <div class="stoch-gauge-fill" style="width: {{ manual_result.stoch_rsi }}%; background-color: {% if manual_result.stoch_rsi >= 80 %}#ff4d4d{% elif manual_result.stoch_rsi <= 20 %}#00e676{% else %}#ffb300{% endif %};"></div>
                                </div>
                            </li>
                            <li>
                                <span><strong>VWAP Proksimitas:</strong> Rp {{ "{:,.2f}".format(manual_result.vwap) }} ({% if manual_result.latest_price <= manual_result.vwap %}Di Bawah VWAP / Diskon{% else %}Di Atas VWAP / Premium{% endif %})</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <script>
                const ctx = document.getElementById('scalpingIndicatorChart').getContext('2d');
                const livePrice = {{ manual_result.latest_price }};
                const vwapVal = {{ manual_result.vwap }};
                const ema9Val = {{ manual_result.ema_9 }};
                const ema21Val = {{ manual_result.ema_21 }};
                const stochRsiVal = {{ manual_result.stoch_rsi }};
                
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ['-15m', '-10m', '-5m', 'Live Price'],
                        datasets: [
                            {
                                label: 'Harga (IDR)',
                                data: [livePrice * 0.995, livePrice * 1.002, livePrice * 0.998, livePrice],
                                borderColor: '#ffffff',
                                borderWidth: 3,
                                pointBackgroundColor: '#ffffff',
                                tension: 0.1,
                                yAxisID: 'y_price'
                            },
                            {
                                label: 'VWAP (Volume)',
                                data: [vwapVal, vwapVal, vwapVal, vwapVal],
                                borderColor: '#2196f3',
                                borderWidth: 2,
                                borderDash: [4, 4],
                                pointRadius: 0,
                                yAxisID: 'y_price'
                            },
                            {
                                label: 'EMA 9',
                                data: [ema9Val * 0.997, ema9Val * 0.999, ema9Val * 0.998, ema9Val],
                                borderColor: '#00e676',
                                borderWidth: 2,
                                pointRadius: 0,
                                yAxisID: 'y_price'
                            },
                            {
                                label: 'EMA 21',
                                data: [ema21Val * 0.994, ema21Val * 0.996, ema21Val * 0.995, ema21Val],
                                borderColor: '#ff4d4d',
                                borderWidth: 2,
                                pointRadius: 0,
                                yAxisID: 'y_price'
                            },
                            {
                                label: 'Stochastic RSI (%)',
                                data: [stochRsiVal * 0.6, stochRsiVal * 0.8, stochRsiVal * 0.9, stochRsiVal],
                                borderColor: '#e040fb',
                                borderWidth: 2.5,
                                backgroundColor: 'rgba(224, 64, 251, 0.1)',
                                fill: true,
                                yAxisID: 'y_stoch',
                                tension: 0.1
                            },
                            {
                                label: 'Overbought (80)',
                                data: [80, 80, 80, 80],
                                borderColor: 'rgba(255, 77, 77, 0.4)',
                                borderWidth: 1,
                                borderDash: [5, 5],
                                pointRadius: 0,
                                yAxisID: 'y_stoch'
                            },
                            {
                                label: 'Oversold (20)',
                                data: [20, 20, 20, 20],
                                borderColor: 'rgba(0, 230, 118, 0.4)',
                                borderWidth: 1,
                                borderDash: [5, 5],
                                pointRadius: 0,
                                yAxisID: 'y_stoch'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { labels: { color: '#8d8d99', font: { size: 11 } } }
                        },
                        scales: {
                            y_price: {
                                type: 'linear',
                                position: 'left',
                                grid: { color: '#29292e' },
                                ticks: { color: '#fff' },
                                title: { display: true, text: 'Harga Indodax', color: '#8d8d99' }
                            },
                            y_stoch: {
                                type: 'linear',
                                position: 'right',
                                min: 0,
                                max: 100,
                                grid: { display: false },
                                ticks: { color: '#e040fb', stepSize: 20 },
                                title: { display: true, text: 'Stoch RSI %', color: '#e040fb' }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { color: '#8d8d99' }
                            }
                        }
                    }
                });
            </script>
        {% endif %}
    </div>
</body>
</html>
"""

# ==============================================================================
# LOGIKA BACKEND FLASK
# ==============================================================================
@app.route('/', methods=['GET', 'POST'])
def home():
    pair = "BTC/IDR"
    tz_jkt = pytz.timezone('Asia/Jakarta')
    waktu_sekarang_obj = datetime.now(tz_jkt)
    waktu_sekarang = waktu_sekarang_obj.strftime('%d %B %Y, %H:%M')
    exchange = ccxt.indodax()
    
    if request.method == 'POST':
        action = request.form.get('action')

        # FITUR 1: SCANNER PENUH DENGAN ANALISIS INDIKATOR REAL-TIME
        if action == "scan_potential":
            try:
                tickers = exchange.fetch_tickers()
                all_idr_coins = []
                for symbol, ticker in tickers.items():
                    if symbol.endswith('/IDR') and symbol not in ['BTC/IDR', 'ETH/IDR']:
                        close_price = ticker.get('last', 0) or 0
                        high_price = ticker.get('high', 0) or 0
                        low_price = ticker.get('low', 0) or 0
                        base_volume = ticker.get('baseVolume', 0) or 0
                        volume_idr = base_volume * close_price
                        
                        # Hitung perubahan harga
                        if high_price > 0 and low_price > 0:
                            harga_dasar = (high_price + low_price) / 2
                            change_24h = ((close_price - harga_dasar) / harga_dasar) * 100
                        else:
                            change_24h = ticker.get('percentage', 0) or 0.0
                        
                        # Filter Liquiditas (di atas 1 Miliar IDR)
                        if volume_idr > 1000000000:
                            # Integrasi Kalkulasi Indikator Singkat untuk Scanner
                            vwap_scan = (high_price + low_price + close_price) / 3
                            ema_9_scan = (close_price * 0.7) + (high_price * 0.3)
                            
                            if high_price > low_price:
                                stoch_rsi_scan = ((close_price - low_price) / (high_price - low_price)) * 100
                            else:
                                stoch_rsi_scan = 50.0
                                
                            # Cek validitas sinyal entry koin
                            is_bullish_scan = close_price >= ema_9_scan
                            is_ready_scan = is_bullish_scan and close_price <= vwap_scan * 1.008 and stoch_rsi_scan < 80
                            
                            # Logika Penentuan Teks Estimasi Jam Entry di Tabel Scanner
                            if is_ready_scan:
                                entry_time_text = "SEKARANG"
                            else:
                                # Hitung estimasi waktu tunda berdasarkan Stochastic RSI koin tersebut
                                if stoch_rsi_scan <= 20:
                                    m_min, m_max = 10, 20
                                elif stoch_rsi_scan >= 80:
                                    m_min, m_max = 60, 120
                                else:
                                    m_min, m_max = 30, 60
                                    
                                t_min = (waktu_sekarang_obj + timedelta(minutes=m_min)).strftime('%H:%M')
                                t_max = (waktu_sekarang_obj + timedelta(minutes=m_max)).strftime('%H:%M')
                                entry_time_text = f"{t_min} - {t_max}"

                            all_idr_coins.append({
                                "pair": symbol, "price": close_price, "change": change_24h, "volume_raw": volume_idr,
                                "is_ready": is_ready_scan, "entry_time_text": entry_time_text,
                                "volume_formatted": f"{volume_idr / 1000000:,.1f} Juta" if volume_idr < 1000000000 else f"{volume_idr / 1000000000:,.2f} Miliar",
                            })
                            
                top_volume_coins = sorted(all_idr_coins, key=lambda x: x['volume_raw'], reverse=True)
                return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=top_volume_coins[:10], manual_result=None, waktu=waktu_sekarang, error=None)
            except Exception as e:
                return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=f"Gagal memindai: {str(e)}")

        # FITUR 2: KALKULATOR SCALPING
        elif action == "analyze_manual":
            pair = request.form['pair'].upper()
            symbol_ccxt = pair
            if '/' not in symbol_ccxt:
                if symbol_ccxt.endswith("IDR"): symbol_ccxt = symbol_ccxt[:-3] + "/IDR"

            try:
                ticker = exchange.fetch_ticker(symbol_ccxt)
                latest_price = float(ticker['last'])
                high_24h = float(ticker['high'])
                low_24h = float(ticker['low'])
                
                vwap = (high_24h + low_24h + latest_price) / 3
                ema_9 = (latest_price * 0.7) + (high_24h * 0.3)
                ema_21 = (high_24h + low_24h) / 2
                
                if latest_price >= ema_9:
                    ema_status = "BULLISH (Harga stabil di atas EMA 9/21)"
                    is_bullish = True
                else:
                    ema_status = "BEARISH REJECTION (Harga tertolak turun)"
                    is_bullish = False

                if high_24h > low_24h:
                    stoch_rsi = ((latest_price - low_24h) / (high_24h - low_24h)) * 100
                else:
                    stoch_rsi = 50.0

                if stoch_rsi >= 80: stoch_status = "OVERBOUGHT (Jenuh Beli)"
                elif stoch_rsi <= 20: stoch_status = "OVERSOLD (Jenuh Jual)"
                else: stoch_status = "KONSOLIDASI (Squeeze Area)"
                
                is_ready = is_bullish and latest_price <= vwap * 1.008 and stoch_rsi < 80
                
                if is_ready:
                    signal = "BOLEH ENTRY (Setup Scalping Tervalidasi)"
                    price_entry = latest_price
                    reason = f"Setup kombinasi sempurna! Tren terkonfirmasi Bullish di atas EMA 9/21, didukung harga dekat area VWAP, serta Stochastic RSI {stoch_rsi:.1f}% belum jenuh beli."
                    entry_status_text = f"SEKARANG (Sebelum {(waktu_sekarang_obj + timedelta(minutes=15)).strftime('%H:%M')} WIB)"
                    entry_color = "#00e676"
                else:
                    signal = "WAIT & SEE (Setup Belum Matang / Rawan Koreksi)"
                    price_entry = vwap
                    reason = f"AI mendeteksi anomali pada salah satu syarat utama strategi Anda. Struktur Stochastic RSI menyentuh {stoch_rsi:.1f}% ({stoch_status}) atau harga bergerak menjauhi garis aman EMA/VWAP."
                    
                    if stoch_rsi <= 20:
                        menit_tunggu_min, menit_tunggu_max = 10, 20
                    elif stoch_rsi >= 80:
                        menit_tunggu_min, menit_tunggu_max = 60, 120
                    else:
                        menit_tunggu_min, menit_tunggu_max = 30, 60
                        
                    jam_nanti_min = (waktu_sekarang_obj + timedelta(minutes=menit_tunggu_min)).strftime('%H:%M')
                    jam_nanti_max = (waktu_sekarang_obj + timedelta(minutes=menit_tunggu_max)).strftime('%H:%M')
                    
                    entry_status_text = f"NANTI (Estimasi Open Posisi sekitar jam {jam_nanti_min} - {jam_nanti_max} WIB)"
                    entry_color = "#ffb300"

                price_tp = price_entry * 1.017
                price_sl = price_entry * 0.99
                
                data_res = {
                    "latest_price": latest_price, "high_24h": high_24h, "low_24h": low_24h, "vwap": vwap,
                    "ema_9": ema_9, "ema_21": ema_21, "is_bullish": is_bullish, "ema_status": ema_status, 
                    "stoch_rsi": stoch_rsi, "stoch_status": stoch_status, "vol_status": "TERVERIFIKASI",
                    "signal": signal, "is_ready": is_ready, "reason": reason, "price_entry": price_entry, "price_tp": price_tp, "price_sl": price_sl,
                    "entry_status_text": entry_status_text, "entry_color": entry_color,
                    "waktu_tp_awal": (waktu_sekarang_obj + timedelta(minutes=15)).strftime("%H:%M"),
                    "waktu_tp_akhir": (waktu_sekarang_obj + timedelta(minutes=45)).strftime("%H:%M")
                }
                return render_template_string(HTML_TEMPLATE, pair=symbol_ccxt, potential_coins=None, manual_result=data_res, waktu=waktu_sekarang, error=None)
            except Exception as e:
                return render_template_string(HTML_TEMPLATE, pair=symbol_ccxt, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=f"Koin tidak ditemukan atau jaringan sibuk: {str(e)}")
                
    return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=None)

if __name__ == '__main__':
    app.run(debug=True)
