from flask import Flask, render_template_string, request
import ccxt
import pandas as pd
import pandas_ta as ta
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
        <p class="subtitle">Analisis Scalping Indodax (EMA, Stoch RSI, VWAP)</p>
        
        <form method="POST">
            <input type="text" name="pair" placeholder="Contoh: BTC/IDR" value="{{ pair }}" required>
            <button type="submit">Analisis</button>
        </form>

        {% if error %}
            <div class="error">⚠️ <strong>Error Analisis:</strong> {{ error }}</div>
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
                        <h4>Stoch RSI (%K / %D)</h4>
                        <p style="color: #fff;">{{ "{:.1f}".format(result.stoch_k) }} / {{ "{:.1f}".format(result.stoch_d) }}</p>
                    </div>
                    <div class="card">
                        <h4>Garis Jangkar VWAP</h4>
                        <p style="color: #fff;">Rp {{ "{:,.2f}".format(result.vwap) }}</p>
                    </div>
                    <div class="card">
                        <h4>Volume Global</h4>
                        <p style="color: #00e676;">{{ result.vol_status }}</p>
                    </div>
                </div>

                <div class="recommendation" style="border-left-color: {% if 'STRONG' in result.signal %}#00e676{% elif 'AMAN' in result.signal %}#2196f3{% else %}#ffeb3b{% endif %};">
                    <h3>🚨 REKOMENDASI SKENARIO</h3>
                    <p><strong>KESIMPULAN:</strong> {{ result.signal }}</p>
                    <p style="color: #00e676;">🟢 <strong>JAM ENTRY:</strong> SEKARANG (Sebelum {{ result.jam_entry_limit }} WIB)</p>
                    <p>💵 <strong>HARGA ENTRY:</strong> Rp {{ "{:,.2f}".format(result.price_entry) }}</p>
                    <p style="color: #f74040;">🔴 <strong>TARGET TAKE PROFIT (+1.7%):</strong> Rp {{ "{:,.2f}".format(result.price_tp) }}</p>
                    <p style="color: #ffb300;">⏱️ <strong>ESTIMASI JAM TAKE PROFIT:</strong> {{ result.waktu_tp_awal }} - {{ result.waktu_tp_akhir }} WIB</p>
                    <p style="color: #8d8d99; font-size: 14px;">❌ Stop Loss: Rp {{ "{:,.2f}".format(result.price_sl) }}</p>
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
        try:
            exchange = ccxt.indodax()
            ohlcv = exchange.fetch_ohlcv(pair, timeframe='5m', limit=100)
            
            if not ohlcv or len(ohlcv) < 30:
                return render_template_string(HTML_TEMPLATE, pair=pair, result=None, error="Data perdagangan dari Indodax tidak cukup untuk menghitung indikator.")
                
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Perhitungan Indikator Utama
            df['EMA_9'] = ta.ema(df['close'], length=9)
            df['EMA_21'] = ta.ema(df['close'], length=21)
            
            stoch_rsi = ta.stochrsi(df['close'], length=14, k=3, d=3)
            df['STOCHRSIk'] = stoch_rsi.iloc[:, 0]
            df['STOCHRSId'] = stoch_rsi.iloc[:, 1]
            
            df['VWAP'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])
            
            # Proteksi jika nilai VWAP atau EMA menghasilkan NaN kosong
            latest_price = float(df['close'].iloc[-1])
            ema9 = df['EMA_9'].iloc[-1] if not pd.isna(df['EMA_9'].iloc[-1]) else latest_price
            ema21 = df['EMA_21'].iloc[-1] if not pd.isna(df['EMA_21'].iloc[-1]) else latest_price
            stoch_k = df['STOCHRSIk'].iloc[-1] if not pd.isna(df['STOCHRSIk'].iloc[-1]) else 50.0
            stoch_d = df['STOCHRSId'].iloc[-1] if not pd.isna(df['STOCHRSId'].iloc[-1]) else 50.0
            vwap = df['VWAP'].iloc[-1] if not pd.isna(df['VWAP'].iloc[-1]) else latest_price
            
            # Pelacakan Volume Koin via CoinGecko
            coin_id = pair.split('/')[0].lower()
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

            # Logika Eksekusi Sinyal
            is_bullish_trend = float(ema9) > float(ema21)
            is_oversold = float(stoch_k) < 25.0 or float(stoch_d) < 25.0
            is_good_value = latest_price <= float(vwap) * 1.002
            
            if is_bullish_trend and is_oversold and is_good_value:
                signal = "SIAP ENTRY (STRONG BUY)"
                price_entry = min(latest_price, float(vwap))
            elif is_bullish_trend and is_good_value:
                signal = "BOLEH ENTRY (MENCARI PANTULAN)"
                price_entry = latest_price
            else:
                signal = "WAIT & SEE (TUNGGU MOMENTUM)"
                price_entry = latest_price * 0.995

            price_tp = price_entry * 1.017
            price_sl = price_entry * 0.99
            
            # Penyelarasan Waktu WIB Server secara Aman
            tz_jkt = pytz.timezone('Asia/Jakarta')
            waktu_sekarang = datetime.now(tz_jkt)
            
            data_res = {
                "latest_price": latest_price, "stoch_k": stoch_k, "stoch_d": stoch_d, "vwap": vwap, "vol_status": vol_status,
                "signal": signal, "price_entry": price_entry, "price_tp": price_tp, "price_sl": price_sl,
                "jam_entry_limit": (waktu_sekarang + timedelta(minutes=15)).strftime("%H:%M"),
                "waktu_tp_awal": (waktu_sekarang + timedelta(minutes=15)).strftime("%H:%M"),
                "waktu_tp_akhir": (waktu_sekarang + timedelta(minutes=45)).strftime("%H:%M")
            }
            return render_template_string(HTML_TEMPLATE, pair=pair, result=data_res, waktu=waktu_sekarang.strftime('%d %B %Y, %H:%M'), error=None)
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, pair=pair, result=None, waktu="", error=str(e))
            
    return render_template_string(HTML_TEMPLATE, pair=pair, result=None, waktu="", error=None)
