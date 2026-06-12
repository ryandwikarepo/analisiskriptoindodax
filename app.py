@app.route('/', methods=['GET', 'POST'])
def home():
    pair = "BTC/IDR"
    if request.method == 'POST':
        pair = request.form['pair'].upper()
        try:
            exchange = ccxt.indodax()
            
            # --- PROTEKSI TIMEFRAME INDODAX ---
            # Kita coba ambil data 5 menit terlebih dahulu. 
            # Jika Indodax menolak, sistem otomatis beralih ke format '5' atau '1h' agar tidak crash.
            ohlcv = None
            for tf in ['5m', '5', '1h']:
                try:
                    ohlcv = exchange.fetch_ohlcv(pair, timeframe=tf, limit=100)
                    if ohlcv and len(ohlcv) >= 30:
                        break
                except:
                    continue
            
            if not ohlcv or len(ohlcv) < 30:
                return render_template_string(HTML_TEMPLATE, pair=pair, result=None, waktu="", error="API Indodax menolak memberikan data candlestick untuk pair ini. Coba koin besar lain seperti BTC/IDR atau ETH/IDR.")
                
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
