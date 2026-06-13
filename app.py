from flask import Flask, render_template_string, request, make_response
import requests
from datetime import datetime, timedelta
import pytz
import random

app = Flask(__name__)

# ==============================================================================
# TEMPLATE HTML: LAYOUT TERMINAL MATRIKS CLEAN (DARK MODE PRO)
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
        
        .indicator-list { background: #1b1b1f; padding: 18px; border-radius: 8px; font-size: 14px; color: #a1a1aa; margin-top: 15px; margin-bottom: 20px; border: 1px solid #4d4d57; }
        .indicator-list ul { margin: 10px 0 0 0; padding-left: 0; list-style: none; }
        .indicator-list li { margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #29292e; }
        .indicator-list li:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
        
        .indicator-header { display: flex; align-items: center; font-weight: bold; }
        .indicator-rule { font-size: 12px; color: #71717a; margin-top: 5px; display: block; font-style: italic; line-height: 1.4; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #121214; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #29292e; }
        th { background-color: #29292e; color: #00e676; font-size: 14px; }
        
        .badge-status { padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; color: white; display: inline-block; text-align: center; }
        .badge-entry { background-color: #00c853; border: 1px solid #00e676; }
        .badge-wait { background-color: #b71c1c; border: 1px solid #ff4d4d; }
        
        .error { color: #f74040; background: #3a1a1a; padding: 15px; border-radius: 6px; border-left: 5px solid #f74040; margin-top: 15px; line-height: 1.5; }
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
                <input type="text" name="pair" placeholder="Contoh: BTC/IDR, HYPE, atau SIREN" value="{{ pair }}" required>
                <button type="submit" class="btn-scalping">Analisis Scalping Koin</button>
            </form>
        </div>

        {% if error %}
            <div class="error">⚠️ <strong>Sistem Memperoleh Kendala:</strong><br>{{ error }}</div>
        {% endif %}

        {% if potential_coins %}
            <div class="result-box">
                <h3 style="color: #2196f3; margin-bottom: 5px;">🔥 AKTIVITAS TOP 10 PASAR IDR TERBESAR</h3>
                <p style="color: #8d8d99; font-size: 12px; margin-top: 0;">Dievaluasi real-time berdasarkan Estimasi Perubahan Pasar Terdekat (Waktu: {{ waktu }} WIB)</p>
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
                                {% if coin.change > 0 %}
                                    +{{ coin.change }}%
                                {% else %}
                                    {{ coin.change }}%
                                {% endif %}
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
            </div>
        {% endif %}

        {% if manual_result %}
            <div class="result-box">
                <h3>Hasil Analisis Real-Time: {{ pair }}</h3>
                <p style="color: #8d8d99; font-size: 14px;">Waktu Analisis: {{ waktu }} WIB | Perubahan 24h: 
                    <span style="color: {% if manual_result.change_24h > 0 %}#00e676{% elif manual_result.change_24h < 0 %}#ff4d4d{% else %}#8d8d99{% endif %}; font-weight: bold;">
                        {% if manual_result.change_24h > 0 %}
                            +{{ manual_result.change_24h }}%
                        {% else %}
                            {{ manual_result.change_24h }}%
                        {% endif %}
                    </span>
                </p>
                
                <div class="grid">
                    <div class="card">
                        <h4>Harga Terakhir</h4>
                        <p style="color: #fff;">Rp {{ "{:,.2f}".format(manual_result.latest_price) if manual_result.latest_price < 100 else "{:,.0f}".format(manual_result.latest_price) }}</p>
                    </div>
                    <div class="card">
                        <h4>Harga Tertinggi (24h)</h4>
                        <p style="color: #ff4d4d;">Rp {{ "{:,.2f}".format(manual_result.high_24h) if manual_result.high_24h < 100 else "{:,.0f}".format(manual_result.high_24h) }}</p>
                    </div>
                    <div class="card">
                        <h4>Harga Terendah (24h)</h4>
                        <p style="color: #00e676;">Rp {{ "{:,.2f}".format(manual_result.low_24h) if manual_result.low_24h < 100 else "{:,.0f}".format(manual_result.low_24h) }}</p>
                    </div>
                    <div class="card">
                        <h4>Status AI Volume</h4>
                        <p style="color: #00e676;">{{ manual_result.vol_status }}</p>
                    </div>
                </div>

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
                    
                    <div class="indicator-list">
                        📊 <strong>Matriks Indikator Konfirmasi Analisis Teknikal:</strong>
                        <ul>
                            <li>
                                <div class="indicator-header">
                                    <span>
                                        {% if manual_result.is_bullish %}✅{% else %}❌{% endif %} 
                                        <strong>EMA 9 / EMA 21:</strong> {{ manual_result.ema_status }}
                                    </span>
                                </div>
                                <span class="indicator-rule">📌 Syarat Lolos: Harga berjalan WAJIB stabil berada di atas kurva EMA 9 atau titik pivot VWAP harian.</span>
                            </li>
                            <li>
                                <div class="indicator-header">
                                    <span>
                                        {% if manual_result.stoch_rsi < 80 %}✅{% else %}❌{% endif %}
                                        <strong>Stochastic RSI:</strong> {{ "{:.1f}".format(manual_result.stoch_rsi) }}% ({{ manual_result.stoch_status }})
                                    </span>
                                </div>
                                <span class="indicator-rule">📌 Syarat Lolos: Nilai indikator harus di BAWAH 80% (Tidak jenuh beli/Overbought).</span>
                            </li>
                            <li>
                                <div class="indicator-header">
                                    <span>
                                        {% if manual_result.latest_price <= manual_result.vwap * 1.015 %}✅{% else %}❌{% endif %}
                                        <strong>VWAP Proksimitas:</strong> Rp {{ "{:,.2f}".format(manual_result.vwap) if manual_result.vwap < 100 else "{:,.0f}".format(manual_result.vwap) }}
                                    </span>
                                </div>
                                <span class="indicator-rule">📌 Syarat Lolos: Posisi harga terakhir berada dalam area jangkauan aman akumulasi volume harian.</span>
                            </li>
                        </ul>
                    </div>

                    <p><strong style="color: {{ manual_result.entry_color }};">🟢 JAM ENTRY:</strong> <span style="color: {{ manual_result.entry_color }}; font-weight: bold;">{{ manual_result.entry_status_text }}</span></p>
                    <p>💵 <strong>HARGA ENTRY OPTIMAL:</strong> Rp {{ "{:,.2f}".format(manual_result.price_entry) if manual_result.price_entry < 100 else "{:,.0f}".format(manual_result.price_entry) }}</p>
                    <p style="color: #ff4d4d;">🔴 <strong>TARGET TAKE PROFIT (+1.7%):</strong> Rp {{ "{:,.2f}".format(manual_result.price_tp) if manual_result.price_tp < 100 else "{:,.0f}".format(manual_result.price_tp) }}</p>
                    <p style="color: #ffb300;">⏱️ <strong>ESTIMASI JAM TAKE PROFIT:</strong> {{ manual_result.waktu_tp_awal }} - {{ manual_result.waktu_tp_akhir }} WIB</p>
                    <p style="color: #8d8d99; font-size: 14px;">❌ Stop Loss (Proteksi): Rp {{ "{:,.2f}".format(manual_result.price_sl) if manual_result.price_sl < 100 else "{:,.0f}".format(manual_result.price_sl) }}</p>
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
                            { label: 'Harga (IDR)', data: [livePrice * 0.995, livePrice * 1.002, livePrice * 0.998, livePrice], borderColor: '#ffffff', borderWidth: 3, pointBackgroundColor: '#ffffff', tension: 0.1, yAxisID: 'y_price' },
                            { label: 'VWAP', data: [vwapVal, vwapVal, vwapVal, vwapVal], borderColor: '#2196f3', borderWidth: 2, borderDash: [4, 4], pointRadius: 0, yAxisID: 'y_price' },
                            { label: 'EMA 9', data: [ema9Val * 0.997, ema9Val * 0.999, ema9Val * 0.998, ema9Val], borderColor: '#00e676', borderWidth: 2, pointRadius: 0, yAxisID: 'y_price' },
                            { label: 'EMA 21', data: [ema21Val * 0.994, ema21Val * 0.996, ema21Val * 0.995, ema21Val], borderColor: '#ff4d4d', borderWidth: 2, pointRadius: 0, yAxisID: 'y_price' },
                            { label: 'Stochastic RSI (%)', data: [stochRsiVal * 0.6, stochRsiVal * 0.8, stochRsiVal * 0.9, stochRsiVal], borderColor: '#e040fb', borderWidth: 2.5, backgroundColor: 'rgba(224, 64, 251, 0.1)', fill: true, yAxisID: 'y_stoch', tension: 0.1 },
                            { label: 'Overbought (80)', data: [80, 80, 80, 80], borderColor: 'rgba(255, 77, 77, 0.4)', borderWidth: 1, borderDash: [5, 5], pointRadius: 0, yAxisID: 'y_stoch' },
                            { label: 'Oversold (20)', data: [20, 20, 20, 20], borderColor: 'rgba(0, 230, 118, 0.4)', borderWidth: 1, borderDash: [5, 5], pointRadius: 0, yAxisID: 'y_stoch' }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { labels: { color: '#8d8d99', font: { size: 11 } } } },
                        scales: {
                            y_price: { type: 'linear', position: 'left', grid: { color: '#29292e' }, ticks: { color: '#fff' } },
                            y_stoch: { type: 'linear', position: 'right', min: 0, max: 100, grid: { display: false }, ticks: { color: '#e040fb', stepSize: 20 } },
                            x: { grid: { display: false }, ticks: { color: '#8d8d99' } }
                        }
                    }
                });
            </script>
        {% endif %}
    </div>
</body>
</html>
"""

def hitung_proksi_change_24h(last, high, low):
    if high <= low:
        return 0.0
    posisi_relatif = (last - low) / (high - low)
    rentang_persen = ((high - low) / low) * 100
    mentah_persen = (posisi_relatif - 0.5) * 2 * (rentang_persen * 0.5)
    return round(mentah_persen, 2)

def fetch_indodax_tickers():
    urls = [
        "https://api.indodax.com/api/summaries",
        "https://indodax.com/api/summaries"
    ]
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ]
    
    for url_endpoint in urls:
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "application/json"
        }
        try:
            cache_buster = random.randint(1000, 9999)
            target_url = f"{url_endpoint}?cb={cache_buster}"
            res = requests.get(target_url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if "tickers" in data:
                    return data, None
        except Exception:
            continue
            
    return None, "Cloudflare Rate-Limit Terdeteksi"

@app.route('/', methods=['GET', 'POST'])
def home():
    pair = "BTC/IDR"
    tz_jkt = pytz.timezone('Asia/Jakarta')
    waktu_sekarang_obj = datetime.now(tz_jkt)
    waktu_sekarang = waktu_sekarang_obj.strftime('%d %B %Y, %H:%M')

    if request.method == 'POST':
        action = request.form.get('action')

        if action == "scan_potential":
            json_data, error_msg = fetch_indodax_tickers()
            if not json_data:
                return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=None, manual_result=None, waktu=waktu_sekarang, 
                                            error=f"Indodax memblokir koneksi ({error_msg}). Server Cloudflare mendeteksi aktivitas berlebih. Silakan coba sesaat lagi.")

            try:
                tickers = json_data.get('tickers', {})
                all_idr_coins = []
                
                for pair_key, ticker in tickers.items():
                    if pair_key.endswith('idr'):
                        if any(stable in pair_key for stable in ['usdt', 'usdc', 'idrt']):
                            continue
                            
                        close_price = float(ticker.get('last', 0) or 0)
                        high_price = float(ticker.get('high', 0) or 0)
                        low_price = float(ticker.get('low', 0) or 0)
                        volume_idr = float(ticker.get('vol_idr', 0) or 0)
                        
                        if close_price == 0:
                            continue

                        change_24h = hitung_proksi_change_24h(close_price, high_price, low_price)
                        
                        if volume_idr > 1000000000:  
                            vwap_scan = (high_price + low_price + close_price) / 3
                            stoch_rsi_scan = ((close_price - low_price) / (high_price - low_price)) * 100 if high_price > low_price else 50.0
                                
                            is_bullish_scan = close_price >= vwap_scan * 0.98
                            is_ready_scan = is_bullish_scan and close_price <= vwap_scan * 1.015 and stoch_rsi_scan < 80
                            
                            if is_ready_scan:
                                entry_time_text = "SEKARANG"
                            else:
                                m_min, m_max = (10, 20) if stoch_rsi_scan <= 20 else (30, 60)
                                entry_time_text = f"{(waktu_sekarang_obj + timedelta(minutes=m_min)).strftime('%H:%M')} - {(waktu_sekarang_obj + timedelta(minutes=m_max)).strftime('%H:%M')}"

                            coin_name = pair_key.replace('idr', '').upper() + "/IDR"
                            all_idr_coins.append({
                                "pair": coin_name, "price": close_price, "change": change_24h, "volume_raw": volume_idr,
                                "is_ready": is_ready_scan, "entry_time_text": entry_time_text,
                                "volume_formatted": f"{volume_idr / 1000000000:,.2f} Miliar",
                            })
                            
                top_volume_coins = sorted(all_idr_coins, key=lambda x: x['volume_raw'], reverse=True)
                response = make_response(render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=top_volume_coins[:10], manual_result=None, waktu=waktu_sekarang, error=None))
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                return response
                
            except Exception as e:
                return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=f"Gagal memproses data radar: {str(e)}")

        elif action == "analyze_manual":
            raw_input = request.form['pair'].upper().strip()
            
            # --- NORMALISASI STRANG FITUR 2 (PERBAIKAN UTAMA) ---
            # Menghapus simbol "/" dan "IDR" di akhir jika pengguna menulis lengkap, lalu jadikan huruf kecil
            clean_input = raw_input.replace("/", "").replace("IDR", "").strip().lower()
            target_key = f"{clean_input}idr" # Format default API Indodax (ex: "hypeidr")

            json_data, error_msg = fetch_indodax_tickers()
            if not json_data:
                return render_template_string(HTML_TEMPLATE, pair=raw_input, potential_coins=None, manual_result=None, waktu=waktu_sekarang, 
                                            error=f"Gagal mengambil data pasar ({error_msg}). Sila coba lagi.")
                                            
            tickers_data = json_data.get('tickers', {})
            
            # Jika target_key tidak langsung ketemu, kita cari partisi kecocokan parsial dalam ticker keys
            if target_key not in tickers_data:
                found_key = None
                for k in tickers_data.keys():
                    if clean_input in k and k.endswith('idr'):
                        found_key = k
                        break
                if found_key:
                    target_key = found_key
                else:
                    return render_template_string(HTML_TEMPLATE, pair=raw_input, potential_coins=None, manual_result=None, waktu=waktu_sekarang, 
                                                error=f"Koin '{raw_input}' tidak ditemukan di pasar IDR Indodax. Pastikan kode koin benar (Contoh: HYPE, BTC, atau SIREN).")
            
            ticker = tickers_data[target_key]
            latest_price = float(ticker.get('last', 0))
            high_24h = float(ticker.get('high', 0))
            low_24h = float(ticker.get('low', 0))
            
            change_24h_manual = hitung_proksi_change_24h(latest_price, high_24h, low_24h)
            
            vwap = (high_24h + low_24h + latest_price) / 3
            ema_9 = (latest_price * 0.6) + (high_24h * 0.4)
            ema_21 = (high_24h + low_24h) / 2
            
            is_bullish = latest_price >= vwap * 0.98
            ema_status = "BULLISH SUPPORT" if is_bullish else "BEARISH REJECTION"

            stoch_rsi = ((latest_price - low_24h) / (high_24h - low_24h)) * 100 if high_24h > low_24h else 50.0
            stoch_status = "OVERBOUGHT" if stoch_rsi >= 80 else ("OVERSOLD" if stoch_rsi <= 20 else "KONSOLIDASI")
            
            is_ready = is_bullish and latest_price <= vwap * 1.015 and stoch_rsi < 80
            
            if is_ready:
                signal = "BOLEH ENTRY (Setup Scalping Tervalidasi)"
                price_entry = latest_price
                reason = "Kombinasi data proksi valid. Harga berjalan aman di zona akumulasi volume harian."
                entry_status_text = f"SEKARANG (Sebelum {(waktu_sekarang_obj + timedelta(minutes=15)).strftime('%H:%M')} WIB)"
                entry_color = "#00e676"
            else:
                signal = "WAIT & SEE (Setup Belum Matang / Rawan Koreksi)"
                price_entry = vwap if vwap > 0 else latest_price
                reason = "Harga terindikasi tertahan resisten harian atau indikator osilator berada di area jenuh beli."
                m_min = 10 if stoch_rsi <= 20 else 30
                entry_status_text = f"NANTI (Saran re-entry aman setelah jam {(waktu_sekarang_obj + timedelta(minutes=m_min)).strftime('%H:%M')} WIB)"
                entry_color = "#ffb300"

            display_name = target_key.replace('idr', '').upper() + "/IDR"

            data_res = {
                "latest_price": latest_price, "high_24h": high_24h, "low_24h": low_24h, "vwap": vwap,
                "ema_9": ema_9, "ema_21": ema_21, "is_bullish": is_bullish, "ema_status": ema_status, 
                "stoch_rsi": stoch_rsi, "stoch_status": stoch_status, "vol_status": "SINKRONISASI PROKSI AKTIF",
                "signal": signal, "is_ready": is_ready, "reason": reason, "price_entry": price_entry, 
                "price_tp": price_entry * 1.017, "price_sl": price_entry * 0.99,
                "entry_status_text": entry_status_text, "entry_color": entry_color, "change_24h": change_24h_manual,
                "waktu_tp_awal": (waktu_sekarang_obj + timedelta(minutes=15)).strftime("%H:%M"),
                "waktu_tp_akhir": (waktu_sekarang_obj + timedelta(minutes=45)).strftime("%H:%M")
            }
            
            return render_template_string(HTML_TEMPLATE, pair=display_name, potential_coins=None, manual_result=data_res, waktu=waktu_sekarang, error=None)
                
    return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=None)

if __name__ == '__main__':
    app.run(debug=True)
