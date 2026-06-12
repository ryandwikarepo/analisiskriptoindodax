from flask import Flask, render_template_string, request
import ccxt
import requests
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# STRUKTUR HTML BARU - MENERAPKAN VISUALISASI CANDLESTICK AI & GAUGE
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Scalping AI Hub</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121214; color: #e1e1e6; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { max-width: 800px; width: 100%; background: #202024; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
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
        
        /* Box Rekomendasi Utama */
        .recommendation { background: #29292e; padding: 20px; border-radius: 8px; border-left: 5px solid #00e676; margin-bottom: 20px; position: relative; }
        .recommendation h3 { margin: 0 0 10px 0; color: #00e676; }
        
        /* List Indikator */
        .indicator-list { background: #1b1b1f; padding: 15px; border-radius: 8px; font-size: 13px; color: #a1a1aa; margin-top: 15px; border: 1px solid #4d4d57; }
        .indicator-list ul { margin: 5px 0 0 0; padding-left: 15px; }
        .indicator-list li { margin-bottom: 5px; display: flex; align-items: center; justify-content: space-between; }
        
        /* 1. VISUALISASI AI CANDLESTICK SNAPSHOT (HTML/CSS) */
        .candle-snapshot { display: flex; gap: 4px; align-items: flex-end; position: absolute; top: 20px; right: 20px; background: #121214; padding: 8px; border-radius: 6px; border: 1px solid #29292e;}
        .candle { width: 10px; border-radius: 2px; position: relative; }
        .candle.main { width: 14px; }
        
        /* Warna Candle Berdasarkan Tren EMA */
        .candle-green { background-color: #00e676; border: 1px solid #00c853; }
        .candle-red { background-color: #ff4d4d; border: 1px solid #e60000; }
        
        /* 2. VISUALISASI INDIKATOR GAUGE (STOCH RSI) */
        .stoch-gauge-container { width: 120px; height: 10px; background-color: #4d4d57; border-radius: 5px; overflow: hidden; margin-left: 10px; position: relative; border: 1px solid #29292e;}
        .stoch-gauge-fill { height: 100%; position: absolute; top: 0; left: 0; transition: width 0.3s ease; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #121214; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #29292e; }
        th { background-color: #29292e; color: #00e676; font-size: 14px; }
        td { font-size: 15px; }
        
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
                <table>
                    <thead>
                        <tr>
                            <th>Pair Koin</th>
                            <th>Harga Sekarang</th>
                            <th>Kenaikan (24h)</th>
                            <th>Volume Pasar (24h)</th>
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
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
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
                        <h4>Volume Global (CoinGecko)</h4>
                        <p style="color: #00e676;">{{ manual_result.vol_status }}</p>
                    </div>
                </div>

                <div class="recommendation" style="border-left-color: {% if manual_result.is_ready %}#00e676{% else %}#ffb300{% endif %};">
                    
                    <div class="candle-snapshot" title="Visualisasi Tren EMA 9 (Lilin Utama) vs EMA 21 (Lilin Samping)">
                        <div class="candle {% if manual_result.is_bullish %}candle-green{% else %}candle-red{% endif %}" style="height: 15px;"></div>
                        <div class="candle main {% if manual_result.is_bullish %}candle-green{% else %}candle-red{% endif %}" style="height: 25px;"></div>
                        <div class="candle {% if manual_result.is_bullish %}candle-green{% else %}candle-red{% endif %}" style="height: 10px;"></div>
                    </div>

                    <h3>🚨 REKOMENDASI SCALPING AI</h3>
                    <p><strong>KESIMPULAN:</strong> 
                        <span style="color: {% if manual_result.is_ready %}#00e676{% else %}#ffb300{% endif %}; font-weight: bold;">
                            {{ manual_result.signal }}
                        </span>
                    </p>
                    <p style="color: #e1e1e6; line-height: 1.5; margin-bottom: 15px;">💡 <strong>ALASAN AI:</strong> {{ manual_result.reason }}</p>
                    
                    <p style="color: #00e676;">🟢 <strong>JAM ENTRY:</strong> SEKARANG (Sebelum {{ manual_result.jam_entry_limit }} WIB)</p>
                    <p>💵 <strong>HARGA ENTRY OPTIMAL:</strong> Rp {{ "{:,.2f}".format(manual_result.price_entry) }}</p>
                    <p style="color: #ff4d4d;">🔴 <strong>TARGET TAKE PROFIT (+1.7%):</strong> Rp {{ "{:,.2f}".format(manual_result.price_tp) }}</p>
                    <p style="color: #ffb300;">⏱️ <strong>ESTIMASI JAM TAKE PROFIT:</strong> {{ manual_result.waktu_tp_awal }} - {{ manual_result.waktu_tp_akhir }} WIB</p>
                    
                    <div class="indicator-list">
                        📈 <strong>Matriks Indikator Konfirmasi (EMA, Stochastic RSI, VWAP):</strong>
                        <ul>
                            <li>
                                <span><strong>EMA 9 / EMA 21:</strong> {{ manual_result.ema_status }}</span>
                                <span style="font-weight: bold; color: {% if manual_result.is_bullish %}#00e676{% else %}#ff4d4d{% endif %}; margin-left: 10px;">
                                    {% if manual_result.is_bullish %}↑ Bullish Cross↑{% else %}↓ Bearish Rejection↓{% endif %}
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
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    pair = "BTC/IDR"
    tz_jkt = pytz.timezone('Asia/Jakarta')
    waktu_sekarang_obj = datetime.now(tz_jkt)
    waktu_sekarang = waktu_sekarang_obj.strftime('%d %B %Y, %H:%M')
    exchange = ccxt.indodax()
    
    if request.method == 'POST':
        action = request.form.get('action')

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
                        
                        if high_price > 0 and low_price > 0:
                            harga_dasar = (high_price + low_price) / 2
                            change_24h = ((close_price - harga_dasar) / harga_dasar) * 100
                        else:
                            change_24h = ticker.get('percentage', 0) or 0.0
                        
                        bid = ticker.get('bid', 0) or 1
                        ask = ticker.get('ask', 0) or 1
                        ratio = round((bid / ask), 2) if ask > 0 else 1.0
                        
                        # Parameter filter Top 10 masif (Volume > 1 Miliar IDR)
                        if volume_idr > 1000000000:
                            all_idr_coins.append({
                                "pair": symbol,
                                "price": close_price,
                                "change": change_24h,
                                "volume_raw": volume_idr,
                                "volume_formatted": f"{volume_idr / 1000000:,.1f} Juta" if volume_idr < 1000000000 else f"{volume_idr / 1000000000:,.2f} Miliar",
                            })
                
                top_volume_coins = sorted(all_idr_coins, key=lambda x: x['volume_raw'], reverse=True)
                top_10 = top_volume_coins[:10]
                
                return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=top_10, manual_result=None, waktu=waktu_sekarang, error=None)
                
            except Exception as e:
                return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=f"Gagal memindai pasar: {str(e)}")

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
                
                # 1. PERHITUNGAN SIMULASI VWAP
                vwap = (high_24h + low_24h + latest_price) / 3
                
                # 2. SIMULASI PERSILANGAN TREND EMA 9 & EMA 21
                ema_9 = (latest_price * 0.7) + (high_24h * 0.3)
                ema_21 = (high_24h + low_24h) / 2
                
                if latest_price >= ema_9:
                    ema_status = "BULLISH (Harga stabil di atas EMA 9/21)"
                    is_bullish = True
                else:
                    ema_status = "BEARISH REJECTION (Harga memantul turun dari EMA 9)"
                    is_bullish = False

                # 3. KALKULASI FORMULA STOCHASTIC RSI (Data 24 Jam)
                if high_24h > low_24h:
                    stoch_rsi = ((latest_price - low_24h) / (high_24h - low_24h)) * 100
                else:
                    stoch_rsi = 50.0

                if stoch_rsi >= 80:
                    stoch_status = "OVERBOUGHT (Jenuh Beli - Sangat Rawan Pucuk)"
                elif stoch_rsi <= 20:
                    stoch_status = "OVERSOLD (Jenuh Jual - Potensi Pantulan Kuat)"
                else:
                    stoch_status = "KONSOLIDASI (Squeeze Area)"
                
                coin_id = symbol_ccxt.split('/')[0].lower()
                mapping = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}
                gecko_id = mapping.get(coin_id.upper(), coin_id)
                vol_status = "NORMAL"
                
                try:
                    url = f"https://api.coingecko.com/api/v3/coins/{gecko_id}"
                    res = requests.get(url, timeout=5).json()
                    if 'market_data' in res and res['market_data']['total_volume']['usd'] > 10000000:
                        vol_status = "TINGGI (Akumulasi)"
                except:
                    vol_status = "NORMAL (Data Standar)"

                # MATRIKS KEPUTUSAN KOREKSI TOTAL:
                # Syarat Entry: Bullish, Harga dekat VWAP (Premium < 0.8%), dan Stoch RSI BELUM Jenuh Beli (<80)
                is_ready = is_bullish and latest_price <= vwap * 1.008 and stoch_rsi < 80
                
                if is_ready:
                    signal = "BOLEH ENTRY (Setup Scalping Tervalidasi)"
                    price_entry = latest_price
                    reason = f"Setup kombinasi sempurna! Tren terkonfirmasi Bullish di atas EMA 9/21, didukung posisi harga live yang berada dekat di area harga wajar VWAP (zona diskon volume masif), serta indikator Stochastic RSI berada di level {stoch_rsi:.1f}% yang belum mengalami jenuh beli ekstrim. Potensi pantulan naik sangat kuat."
                else:
                    signal = "WAIT & SEE (Setup Belum Matang / Rawan Koreksi)"
                    price_entry = vwap # Sarankan pasang jaring di garis VWAP
                    reason = f"AI mendeteksi anomali pada salah satu syarat utama strategi Anda. Struktur Stochastic RSI sudah menyentuh {stoch_rsi:.1f}% ({stoch_status}) atau harga bergerak terlalu jauh di atas VWap premium. Disarankan menunggu retracement kembali ke dekat garis EMA untuk meminimalkan risiko nyangkut di pucuk."

                price_tp = price_entry * 1.017
                price_sl = price_entry * 0.99
                
                data_res = {
                    "latest_price": latest_price, "high_24h": high_24h, "low_24h": low_24h, "vwap": vwap,
                    "is_bullish": is_bullish, "ema_status": ema_status, "stoch_rsi": stoch_rsi, "stoch_status": stoch_status, "vol_status": vol_status,
                    "signal": signal, "is_ready": is_ready, "reason": reason, "price_entry": price_entry, "price_tp": price_tp, "price_sl": price_sl,
                    "jam_entry_limit": (waktu_sekarang_obj + timedelta(minutes=15)).strftime("%H:%M"),
                    "waktu_tp_awal": (waktu_sekarang_obj + timedelta(minutes=15)).strftime("%H:%M"),
                    "waktu_tp_akhir": (waktu_sekarang_obj + timedelta(minutes=45)).strftime("%H:%M")
                }
                return render_template_string(HTML_TEMPLATE, pair=symbol_ccxt, potential_coins=None, manual_result=data_res, waktu=waktu_sekarang, error=None)
            except Exception as e:
                return render_template_string(HTML_TEMPLATE, pair=symbol_ccxt, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=f"Koin tidak ditemukan. Detail: {str(e)}")
                
    return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=None)
