import streamlit as st
import pandas as pd
import requests
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")

# 1 second auto refresh
st_autorefresh(interval=1000, limit=1000, key="faisal_final_v3")

st.sidebar.title("💎 Paichi Menu")
choice = st.sidebar.radio("സേവനം തിരഞ്ഞെടുക്കുക:", ["Indian Indices", "Commodities & Forex", "Quick Links"])

def get_supertrend_analysis(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        result = data['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        ohlc = result['indicators']['quote'][0]
        
        df = pd.DataFrame({
            'close': ohlc['close'],
            'high': ohlc['high'],
            'low': ohlc['low']
        }).dropna()

        if len(df) > 20:
            # RSI (14)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            last_rsi = float(rsi.iloc[-1])

            # ATR for Supertrend (10, 3 settings)
            df['tr'] = df['high'] - df['low']
            atr = df['tr'].rolling(window=10).mean().iloc[-1]
            mid_price = (df['high'].iloc[-1] + df['low'].iloc[-1]) / 2
            lower_band = mid_price - (3 * atr)
            
            # Trend Logic
            trend = "BUY 🟢" if price > lower_band else "SELL 🔴"
            color = "green" if price > lower_band else "red"

            return {"price": price, "rsi": last_rsi, "trend": trend, "color": color}
    except:
        return None

def display_dashboard(data, title, mult=1):
    if data:
        p = data['price'] * mult
        with st.container():
            st.subheader(title)
            c1, c2, c3 = st.columns(3)
            c1.metric("Live Price", f"₹{p:.2f}")
            c2.metric("RSI (14)", f"{data['rsi']:.2f}")
            c3.metric("Supertrend", data['trend'])
            
            if data['color'] == "green": st.success(f"🔥 {title}: BUY SIGNAL")
            else: st.error(f"💥 {title}: SELL SIGNAL")
    else:
        st.error(f"{title} data ലഭ്യമല്ല")

# --- Main Dashboard ---

if choice == "Indian Indices":
    st.title("📊 Indian Markets - Supertrend")
    display_dashboard(get_supertrend_analysis("^NSEI"), "NIFTY 50")
    st.divider()
    display_dashboard(get_supertrend_analysis("^NSEBANK"), "BANK NIFTY")
    st.divider()
    display_dashboard(get_supertrend_analysis("NIFTY_FIN_SERVICE.NS"), "FIN NIFTY")

elif choice == "Commodities & Forex":
    st.title("🛢️ Commodities & Currency")
    
    # Crude Oil (Multiplier 93.5 to match your Upstox price)
    display_dashboard(get_supertrend_analysis("CL=F"), "CRUDE OIL MCX", mult=93.5)
    
    st.divider()
    
    # Gold 8 Gram
    g_data = get_supertrend_analysis("GC=F")
    if g_data:
        g_price = ((g_data['price'] / 31.1) * 83.5 * 1.15) * 8
        st.metric("GOLD 8 GRAM (Approx)", f"₹{g_price:.0f}")

    st.divider()
    
    # 🇦🇪 INR to Dirham (AED) - ഇതാണ് നീ ചോദിച്ചത്
    st.subheader("🇦🇪 Dirham (AED) to INR")
    a_data = get_supertrend_analysis("AEDINR=X")
    if a_data:
        st.metric("1 AED", f"₹{a_data['price']:.2f}")

else:
    st.title("🔗 Quick Access")
    st.markdown("### [🌐 Open Upstox Login](https://upstox.com/)")
