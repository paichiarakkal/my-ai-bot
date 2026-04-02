import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")

# 1 second-il auto refresh akan
st_autorefresh(interval=1000, limit=1000, key="faisal_final_live")

st.sidebar.title("💎 Paichi Menu")
choice = st.sidebar.radio("Sēvanam thiraññeṭukkuka:", ["Indian Indices", "Commodities & Forex", "Quick Links"])

def get_live_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        result = data['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        prices = result['indicators']['quote'][0]['close']
        
        df = pd.Series(prices).dropna()
        if len(df) > 14:
            delta = df.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            last_rsi = float(rsi.iloc[-1])
        else:
            last_rsi = 50
        return {"price": price, "rsi": last_rsi}
    except:
        return None

def display_signal(data, title, mult=1):
    if data:
        p = data['price'] * mult
        rsi = data['rsi']
        st.metric(title, f"₹{p:.2f}")
        st.write(f"RSI: {rsi:.2f}")
        
        # BUY/SELL Signal Logic
        if rsi < 35:
            st.success("🟢 ACTION: BUY")
        elif rsi > 65:
            st.error("🔴 ACTION: SELL")
        else:
            st.warning("⏳ ACTION: WAIT")
    else:
        st.error(f"{title} data labhyamalla")

# --- Main Sections ---

if choice == "Indian Indices":
    st.title("📊 Indian Indices - Live Signals")
    col1, col2 = st.columns(2)
    with col1:
        display_signal(get_live_data("^NSEI"), "NIFTY 50")
        st.divider()
        display_signal(get_live_data("NIFTY_FIN_SERVICE.NS"), "FIN NIFTY")
    with col2:
        display_signal(get_live_data("^NSEBANK"), "BANK NIFTY")
        st.divider()
        display_signal(get_live_data("^BSESN"), "SENSEX")

elif choice == "Commodities & Forex":
    st.title("🛢️ Commodities & Gold")
    
    # Crude Oil
    c_data = get_live_data("CL=F")
    display_signal(c_data, "CRUDE OIL FUTURE (MCX)", mult=85.5)
    
    st.divider()
    
    # Gold 8 Gram
    g_data = get_live_data("GC=F")
    if g_data:
        g_price = ((g_data['price'] / 31.1) * 83.5 * 1.15) * 8
        st.metric("GOLD 8 GRAM (Approx)", f"₹{g_price:.0f}")
    
    st.divider()
    
    # Currency
    a_data = get_live_data("AEDINR=X")
    if a_data:
        st.metric("1 DIRHAM (AED)", f"₹{a_data['price']:.2f}")

else:
    st.title("🔗 Quick Access")
    st.markdown("### [🌐 Open Upstox Login](https://upstox.com/)")
    st.markdown("### [📊 TradingView Charts](https://www.tradingview.com/chart/)")
