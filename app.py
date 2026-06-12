from flask import Flask, render_template_string, request
import ccxt
import requests
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Scalping AI Analyzer</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121214; color: #e1e1e6; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { max-width: 600px; width: 100%; background: #202024; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        h1 { text-align: center; color: #00e676; margin-bottom: 5px; }
        p.subtitle { text-align: center; color: #8d8d99; margin-top: 0; margin-bottom: 25px; }
        form { display: flex; gap: 10px; margin-bottom: 25px; }
        input[type="text"] { flex: 1; padding: 12px; border-radius: 6px; border: 1px solid #4d4d57; background: #121214; color: white; font-size: 16px; text-transform: uppercase; }
        button { padding: 12px 20px; border: none; background-color: #00e676; color: #121214; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #00c853; }
        .result-box { border-top: 2px solid #4d4d57; padding-top: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .card { background: #121214; padding: 15px; border-radius: 8px; border: 1px solid #29292e; }
        .card h4 { margin: 0 0 5px 0; color: #8d8d99; font-size: 14px; }
        .card p { margin: 0; font-size: 18px; font-weight: bold; }
        .recommendation { background: #29292e; padding: 20px; border-radius: 8px; border-left: 5px solid #00e676; }
        .recommendation h3 { margin: 0 0 10px 0; color: #00e676; }
        .error { color: #f74040; background: #3a1a1a; padding: 15px; border-radius: 6px; border-left: 5px solid #f74040; word-break: break-all; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Crypto AI Analyzer</h1>
        <p class="subtitle">Analisis Scalping Indodax Instant Mode</p>
        
        <form method="POST">
            <input type="text" name="pair" placeholder="Contoh: BTC/IDR" value="{{ pair }}" required>
            <button type="submit">Analisis</button>
        </form>

        {% if error %}
            <div class="error">⚠️ <strong>Sinyal Terbatas:</strong> {{ error }}</div>
        {% endif %}

        {% if result %}
            <div class="result-box">
                <h3>Hasil Analisis Real-Time: {{ pair }}</h3>
                <p style="color: #8d8d99; font-size: 14px;">Waktu Analisis: {{ waktu }} WIB</p>
                
                <div class="grid">
                    <div class="card">
                        <h4>Harga Terakhir</h4>
                        <p style="color: #fff;">Rp {{ "{:,.2f}".format(result.latest_price) }}</p>
                    </div>
                    <div class="card">
                        <h4>Harga Tertinggi (24h)</h4>
                        <p style="color: #ff4d4d;">Rp {{ "{:,.2f}".format(result.high_24h) }}</p>
                    </div>
                    <div class="card">
                        <h4>Harga Terendah (24h)</h4>
                        <p style="color: #00e676;">Rp {{ "{:,.2f}".format(result.low_24h) }}</p>
                    </div>
                    <div class="card">
                        <h4>Volume Global (CoinGecko)</h4>
                        <p style="color: #00e676;">{{ result.vol_status }}</p>
                    </div>
                </div>

                <div class="recommendation" style="border-left-color: #2196f3;">
                    <h3>🚨 REKOMENDASI SKENARIO</h3>
                    <p><strong>KESIMPULAN:</strong> {{ result.signal }}</p>
                    <p style="color: #00e676;">🟢 <strong>JAM ENTRY:</strong> SEKARANG (Sebelum {{ result.jam_entry_limit }} WIB)</p>
                    <p>💵 <strong>HARGA ENTRY OPTIMAL:</strong> Rp {{ "{:,.2f}".format(result.price_entry) }}</p>
                    <p style="color: #f74040;">🔴 <strong>TARGET TAKE PROFIT (+1.7%):</strong> Rp {{ "{:,.2f}".format(result.price_tp) }}</p>
                    <p style="color: #ffb300;">⏱️ <strong>ESTIMASI JAM TAKE PROFIT:</strong> {{ result.waktu_tp_awal }} - {{ result.waktu_tp_akhir }} WIB</p>
                    <p style="color: #8d8d99; font-size: 14px;">❌ Stop Loss (Proteksi): Rp {{ "{:,.2f}".format(result.price_sl) }}</p>
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
    if request.method == 'POST':
        pair = request.form['pair'].upper()
        
        # Penyesuaian nama simbol agar ramah terhadap API Indodax murni
        symbol_ccxt = pair
        if '/' not in symbol_ccxt and '_' in symbol_ccxt:
            symbol_ccxt = symbol_ccxt.replace('_', '/')
        elif '/' not in symbol_ccxt:
            # Jika user ketik btcidr langsung, ubah jadi BTC/IDR
            if symbol_ccxt.endswith("IDR"):
                symbol_ccxt = symbol_ccxt[:-3] + "/IDR"
            elif symbol_ccxt.endswith("USDT"):
                symbol_ccxt = symbol_ccxt[:-4] + "/USDT"

        try:
            exchange = ccxt.indodax()
            
            # Menggunakan fetch_ticker untuk bypass error 'invalid TimeFrame' 
            ticker = exchange.fetch_ticker(symbol_ccxt)
            
            latest_price = float(ticker['last'])
            high_24h = float(ticker['high'])
            low_24h = float(ticker['low'])
            
            # Hitung titik tengah dinamis (Rata-rata transaksi sebagai pengganti jangkar VWAP)
            mid_price = (high_24h + low_24h + latest_price) / 3
            
            # Pelacakan Volume Koin via CoinGecko
            coin_id = symbol_ccxt.split('/')[0].lower()
            mapping = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "XRP": "ripple"}
            gecko_id = mapping.get(coin_id, coin_id)
            vol_status = "NORMAL"
            try:
                url = f"https://api.coingecko.com/api/v3/coins/{gecko_id}"
                res = requests.get(url, timeout=5).json()
                if 'market_data' in res and res['market_data']['total_volume']['usd'] > 10000000:
                    vol_status = "TINGGI (Akumulasi)"
            except:
                vol_status = "NORMAL (Data Standar)"

            # Logika keputusan scalping aman tanpa perlu chart saingan
            if latest_price <= mid_price * 1.005:
                signal = "BOLEH ENTRY (Harga Berada Di Area Transaksi Murah)"
                price_entry = latest_price
            else:
                signal = "WAIT & SEE (Harga Agak Tinggi, Tunggu Koreksi Kecil)"
                price_entry = mid_price

            price_tp = price_entry * 1.017
            price_sl = price_entry * 0.99
            
            # Penyelarasan Waktu WIB Server
            tz_jkt = pytz.timezone('Asia/Jakarta')
            waktu_sekarang = datetime.now(tz_jkt)
            
            data_res = {
                "latest_price": latest_price, "high_24h": high_24h, "low_24h": low_24h, "vol_status": vol_status,
                "signal": signal, "price_entry": price_entry, "price_tp": price_tp, "price_sl": price_sl,
                "jam_entry_limit": (waktu_sekarang + timedelta(minutes=15)).strftime("%H:%M"),
                "waktu_tp_awal": (waktu_sekarang + timedelta(minutes=15)).strftime("%H:%M"),
                "waktu_tp_akhir": (waktu_sekarang + timedelta(minutes=45)).strftime("%H:%M")
            }
            return render_template_string(HTML_TEMPLATE, pair=symbol_ccxt, result=data_res, waktu=waktu_sekarang.strftime('%d %B %Y, %H:%M'), error=None)
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, pair=symbol_ccxt, result=None, waktu="", error=f"Koin tidak ditemukan atau koneksi API Indodax sedang sibuk. Detail: {str(e)}")
            
    return render_template_string(HTML_TEMPLATE, pair=pair, result=None, waktu="", error=None)
