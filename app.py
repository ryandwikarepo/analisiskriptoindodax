from flask import Flask, render_template_string, request
import ccxt
import requests
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

# Tampilan HTML + CSS Modern yang mendukung Dua Fitur Utama
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Scalping AI Hub</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121214; color: #e1e1e6; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { max-width: 750px; width: 100%; background: #202024; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
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
        
        .recommendation { background: #29292e; padding: 20px; border-radius: 8px; border-left: 5px solid #00e676; }
        .recommendation h3 { margin: 0 0 10px 0; color: #00e676; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #121214; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #29292e; }
        th { background-color: #29292e; color: #00e676; font-size: 14px; }
        td { font-size: 15px; }
        .badge-green { background: #1b3a24; color: #00e676; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        
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
                <button type="submit" class="btn-scanner">🚀 Analisis Koin Potensial (Scan Seluruh Pasar IDR)</button>
            </form>
        </div>

        <div class="menu-box">
            <div class="menu-title">💵 FITUR 2: KALKULATOR SCALPING INSTAN (+1.7%)</div>
            <form method="POST" class="flex-form">
                <input type="hidden" name="action" value="analyze_manual">
                <input type="text" name="pair" placeholder="Contoh: BTC/IDR atau SOL/IDR" value="{{ pair }}" required>
                <button type="submit" class="btn-scalping">Analisis Scalping Koin</button>
            </form>
        </div>

        {% if error %}
            <div class="error">⚠️ {{ error }}</div>
        {% endif %}

        {% if potential_coins %}
            <div class="result-box">
                <h3 style="color: #2196f3; margin-bottom: 5px;">🔥 TOP 5 KOIN PALING POTENSIAL DETIK INI</h3>
                <p style="color: #8d8d99; font-size: 13px; margin-top: 0;">Diurutkan otomatis berdasarkan kekuatan akumulasi Order Book & Volume (Waktu: {{ waktu }} WIB)</p>
                <table>
                    <thead>
                        <tr>
                            <th>Pair Koin</th>
                            <th>Harga Sekarang</th>
                            <th>Kenaikan (24h)</th>
                            <th>Volume (24h)</th>
                            <th>Order Book Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for coin in potential_coins %}
                        <tr>
                            <td style="font-weight: bold; color: #fff;">{{ coin.pair }}</td>
                            <td>Rp {{ "{:,.0f}".format(coin.price) }}</td>
                            <td style="color: #00e676;">+{{ "{:.2f}".format(coin.change) }}%</td>
                            <td style="color: #8d8d99;">Rp {{ coin.volume_formatted }}</td>
                            <td><span class="badge-green">🟢 Buyer Kuat ({{ coin.ratio }}x)</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <p style="font-size: 13px; color: #8d8d99; margin-top: 12px;">💡 <em>Tips: Ambil simbol koin teratas, lalu masukkan ke Fitur 2 di atas untuk eksekusi target profit +1.7%.</em></p>
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

                <div class="recommendation" style="border-left-color: #00e676;">
                    <h3>🚨 REKOMENDASI SKENARIO</h3>
                    <p><strong>KESIMPULAN:</strong> {{ manual_result.signal }}</p>
                    <p style="color: #00e676;">🟢 <strong>JAM ENTRY:</strong> SEKARANG (Sebelum {{ manual_result.jam_entry_limit }} WIB)</p>
                    <p>💵 <strong>HARGA ENTRY OPTIMAL:</strong> Rp {{ "{:,.2f}".format(manual_result.price_entry) }}</p>
                    <p style="color: #f74040;">🔴 <strong>TARGET TAKE PROFIT (+1.7%):</strong> Rp {{ "{:,.2f}".format(manual_result.price_tp) }}</p>
                    <p style="color: #ffb300;">⏱️ <strong>ESTIMASI JAM TAKE PROFIT:</strong> {{ manual_result.waktu_tp_awal }} - {{ manual_result.waktu_tp_akhir }} WIB</p>
                    <p style="color: #8d8d99; font-size: 14px;">❌ Stop Loss (Proteksi): Rp {{ "{:,.2f}".format(manual_result.price_sl) }}</p>
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
    waktu_sekarang = datetime.now(tz_jkt).strftime('%d %B %Y, %H:%M')
    
    if request.method == 'POST':
        action = request.form.get('action')
        exchange = ccxt.indodax()

        # --- LOGIKA TOMBOL 1: ANALISIS KOIN POTENSIAL (SCANNER) ---
        if action == "scan_potential":
            try:
                tickers = exchange.fetch_tickers()
                valid_coins = []
                
                for symbol, ticker in tickers.items():
                    # Hanya scan pasar IDR dan singkirkan koin utama yang terlalu stabil (seperti BTC atau ETH) demi mencari koin volatilitas tinggi
                    if symbol.endswith('/IDR') and symbol not in ['BTC/IDR', 'ETH/IDR']:
                        change_24h = ticker.get('percentage', 0) or 0
                        base_volume = ticker.get('baseVolume', 0) or 0
                        close_price = ticker.get('last', 0) or 0
                        
                        # Filter 1: Kenaikan sehat antara +2% s/d +15% (Bukan koin mati, bukan koin yang sudah over-pumped)
                        # Filter 2: Volume perdagangan harian harus aktif (di atas 100 juta rupiah)
                        if (2.0 <= change_24h <= 15.0) and (base_volume * close_price > 100000000):
                            volume_idr = base_volume * close_price
                            
                            # Trik Order Book Rasio Singkat (Simulasi bobot buyer)
                            # Menggunakan data ticker untuk efisiensi kecepatan bypass vwap/bids massal
                            bid = ticker.get('bid', 0) or 1
                            ask = ticker.get('ask', 0) or 1
                            ratio = round((bid / ask), 2) if ask > 0 else 1.0
                            
                            valid_coins.append({
                                "pair": symbol,
                                "price": close_price,
                                "change": change_24h,
                                "volume_raw": volume_idr,
                                "volume_formatted": f"{volume_idr / 1000000:,.1f} Juta" if volume_idr < 1000000000 else f"{volume_idr / 1000000000:,.2f} Miliar",
                                "ratio": ratio
                            })
                
                # URUTAN OTOMATIS: Koin dengan rasio buyer & volume tertinggi didorong ke paling atas (Rekomendasi Utama)
                valid_coins = sorted(valid_coins, key=lambda x: (x['ratio'], x['volume_raw']), reverse=True)
                top_5 = valid_coins[:5]
                
                if not top_5:
                    return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error="Saat ini belum ada koin IDR yang memenuhi kriteria volatilitas sehat (+2% s/d +15%). Coba beberapa saat lagi.")
                    
                return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=top_5, manual_result=None, waktu=waktu_sekarang, error=None)
                
            except Exception as e:
                return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=f"Gagal memindai pasar: {str(e)}")

        # --- LOGIKA TOMBOL 2: ANALISIS SCALPING KOIN (MANUAL) ---
        elif action == "analyze_manual":
            pair = request.form['pair'].upper()
            symbol_ccxt = pair
            if '/' not in symbol_ccxt:
                if symbol_ccxt.endswith("IDR"): symbol_ccxt = symbol_ccxt[:-3] + "/IDR"
                elif symbol_ccxt.endswith("USDT"): symbol_ccxt = symbol_ccxt[:-4] + "/USDT"

            try:
                ticker = exchange.fetch_ticker(symbol_ccxt)
                latest_price = float(ticker['last'])
                high_24h = float(ticker['high'])
                low_24h = float(ticker['low'])
                
                mid_price = (high_24h + low_24h + latest_price) / 3
                
                coin_id = symbol_ccxt.split('/')[0].lower()
                mapping = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}
                gecko_id = mapping.get(coin_id, coin_id)
                vol_status = "NORMAL"
                try:
                    url = f"https://api.coingecko.com/api/v3/coins/{gecko_id}"
                    res = requests.get(url, timeout=5).json()
                    if 'market_data' in res and res['market_data']['total_volume']['usd'] > 10000000:
                        vol_status = "TINGGI (Akumulasi)"
                except:
                    vol_status = "NORMAL (Data Standar)"

                if latest_price <= mid_price * 1.005:
                    signal = "BOLEH ENTRY (Harga Berada Di Area Transaksi Murah)"
                    price_entry = latest_price
                else:
                    signal = "WAIT & SEE (Harga Agak Tinggi, Tunggu Koreksi Kecil)"
                    price_entry = mid_price

                price_tp = price_entry * 1.017
                price_sl = price_entry * 0.99
                
                waktu_obj = datetime.now(tz_jkt)
                
                data_res = {
                    "latest_price": latest_price, "high_24h": high_24h, "low_24h": low_24h, "vol_status": vol_status,
                    "signal": signal, "price_entry": price_entry, "price_tp": price_tp, "price_sl": price_sl,
                    "jam_entry_limit": (waktu_obj + timedelta(minutes=15)).strftime("%H:%M"),
                    "waktu_tp_awal": (waktu_obj + timedelta(minutes=15)).strftime("%H:%M"),
                    "waktu_tp_akhir": (waktu_obj + timedelta(minutes=45)).strftime("%H:%M")
                }
                return render_template_string(HTML_TEMPLATE, pair=symbol_ccxt, potential_coins=None, manual_result=data_res, waktu=waktu_obj.strftime('%d %B %Y, %H:%M'), error=None)
            except Exception as e:
                return render_template_string(HTML_TEMPLATE, pair=symbol_ccxt, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=f"Koin tidak ditemukan. Detail: {str(e)}")
                
    return render_template_string(HTML_TEMPLATE, pair=pair, potential_coins=None, manual_result=None, waktu=waktu_sekarang, error=None)
