import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import requests
from datetime import datetime, timedelta

# Pengaturan Judul Website
st.set_page_config(page_title="Crypto Scalping AI Analyzer", layout="centered")
st.title("📊 Crypto Scalping AI Analyzer (Indodax)")
st.write("Masukkan pair kripto Indodax untuk analisis berbasis EMA Cross, Stochastic RSI, dan VWAP.")

# Input dari User
pair_input = st.text_input("Ketik Pair Kripto (Contoh: BTC/IDR atau SOL/USDT):", "BTC/IDR").upper()

if st.button("Jalankan Skenario Analisis"):
    try:
        exchange = ccxt.indodax()
        ohlcv = exchange.fetch_ohlcv(pair_input, timeframe='5m', limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Hitung Indikator Teknikal
        df['EMA_9'] = ta.ema(df['close'], length=9)
        df['EMA_21'] = ta.ema(df['close'], length=21)
        stoch_rsi = ta.stochrsi(df['close'], length=14, k=3, d=3)
        df['STOCHRSIk'] = stoch_rsi.iloc[:, 0]
        df['STOCHRSId'] = stoch_rsi.iloc[:, 1]
        df['VWAP'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])
        
        latest_price = df['close'].iloc[-1]
        ema9 = df['EMA_9'].iloc[-1]
        ema21 = df['EMA_21'].iloc[-1]
        stoch_k = df['STOCHRSIk'].iloc[-1]
        stoch_d = df['STOCHRSId'].iloc[-1]
        vwap = df['VWAP'].iloc[-1]
        
        # Estimasi Volume via CoinGecko
        coin_id = pair_input.split('/')[0].lower()
        mapping = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "XRP": "ripple", "DOGE": "dogecoin"}
        gecko_id = mapping.get(coin_id, coin_id)
        
        vol_status = "NORMAL"
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{gecko_id}"
            res = requests.get(url).json()
            vol_change_24h = res['market_data']['total_volume']['usd']
            if vol_change_24h > 10000000: 
                vol_status = "TINGGI (Terindikasi Akumulasi)"
        except:
            vol_status = "TIDAK TERDETEKSI"

        # Logika Skenario Rekomendasi
        is_bullish_trend = ema9 > ema21
        is_oversold = stoch_k < 25 or stoch_d < 25
        is_good_value = latest_price <= vwap * 1.002 
        
        if is_bullish_trend and is_oversold and is_good_value:
            signal_conclusion = "🚨 KONDISI IDEAL: SIAP ENTRY (STRONG BUY)"
            price_entry = round(min(latest_price, vwap), 2)
        elif is_bullish_trend and is_good_value:
            signal_conclusion = "🟢 KONDISI AMAN: BOLEH ENTRY (MENCARI PANTULAN)"
            price_entry = round(latest_price, 2)
        else:
            signal_conclusion = "⏳ KONDISI WAIT & SEE: TUNGGU MOMENTUM DASAR"
            price_entry = round(latest_price * 0.995, 2)

        price_tp = round(price_entry * 1.017, 2)
        price_sl = round(price_entry * 0.99, 2)
        
        waktu_sekarang = datetime.now() + timedelta(hours=7) # Waktu WIB
        waktu_tp_awal = (waktu_sekarang + timedelta(minutes=15)).strftime("%H:%M")
        waktu_tp_akhir = (waktu_sekarang + timedelta(minutes=45)).strftime("%H:%M")

        # Tampilkan Hasil di Web
        st.subheader(f"📊 HASIL ANALISIS REAL-TIME: {pair_input}")
        st.write(f"*Waktu Analisis: {waktu_sekarang.strftime('%d %B %Y, %H:%M')} WIB*")
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Harga Terakhir", value=f"{latest_price:,.2f}")
            st.write(f"🐳 **Volume Global:** {vol_status}")
        with col2:
            st.metric(label="Stoch RSI (%K / %D)", value=f"{stoch_k:.1f} / {stoch_d:.1f}")
            st.write("📈 **Status:** Oversold" if is_oversold else "⏳ **Status:** Normal")
        with col3:
            st.metric(label="Garis Jangkar VWAP", value=f"{vwap:,.2f}")
            st.write("🔥 **EMA Trend:** Bullish" if is_bullish_trend else "❄️ **EMA Trend:** Bearish/Sideways")
            
        st.markdown("---")
        st.subheader("🚨 REKOMENDASI SKENARIO SCALPING")
        st.info(f"**KESIMPULAN SISTEM:** {signal_conclusion}")
        st.success(f"🟢 **JAM ENTRY (Beli):** SEKARANG (Sebelum { (waktu_sekarang + timedelta(minutes=15)).strftime('%H:%M') } WIB)")
        st.info(f"💵 **HARGA ENTRY RECOMMENDED:** Rp {price_entry:,.2f}")
        st.error(f"🔴 **HARGA TAKE PROFIT (+1.7%):** Rp {price_tp:,.2f}")
        st.warning(f"⏱️ **ESTIMASI JAM TAKE PROFIT:** Antara pukul {waktu_tp_awal} - {waktu_tp_akhir} WIB")
        st.text(f"❌ Stop Loss: Rp {price_sl:,.2f}")

    except Exception as e:
        st.error(f"Format pair salah atau bursa gangguan. Error: {e}")
