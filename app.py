import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")

# ഓരോ 1 സെക്കൻഡിലും ഓട്ടോമാറ്റിക് റിഫ്രഷ്
st_autorefresh(interval=1000, limit=1000, key="faisal_live_gold")

# സൈഡ് ബാർ
st.sidebar.title("💎 Paichi Menu")
choice = st.sidebar.radio("സേവനം തിരഞ്ഞെടുക്കുക:", ["Indian Indices", "Commodities & Forex", "Quick Links"])

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

# --- മെയിൻ ഡിസ്‌പ്ലേ ---

if choice == "Indian Indices":
    st.title("📊 Live Market Signals")
    col1, col2 = st.columns(2)
    with col1:
        d = get_live_data("^NSEI")
        if d:
            st.metric("Nifty 50", f"{d['price']:.2f}")
            st.write(f"RSI: {d['rsi']:.2f}")
            if d['rsi'] < 35: st.success("ACTION: BUY 🟢")
            elif d['rsi'] > 65: st.error("ACTION: SELL 🔴")
            else: st.warning("ACTION: WAIT ⏳")
    with col2:
        db = get_live_data("^NSEBANK")
        if db:
            st.metric("Bank Nifty", f"{db['price']:.2f}")
            st.write(f"RSI: {db['rsi']:.2f}")

elif choice == "Commodities & Forex":
    st.title("🛢️ Commodities (Live)")
    
    # Crude Oil Section
    c_data = get_live_data("CL=F")
    if c_data:
        mcx_future = c_data['price'] * 85.5
        st.metric("Crude Oil Future (MCX)", f"₹{mcx_future:.2f}")
        st.write(f"RSI: {c_data['rsi']:.2f}")
    
    st.divider()
    
    # Gold Section (8 Gram INR)
    st.subheader("💰 Gold Price (India)")
    g_data = get_live_data("GC=F")
    if g_data:
        # ഗ്ലോബൽ ഗോൾഡ് പ്രൈസിനെ (USD/Ounce) 8 ഗ്രാം ഇന്ത്യൻ വിലയിലേക്ക് മാറ്റുന്നു
        # Formula: (Price/31.1) * 83.5 (USDINR) * 1.15 (Tax) * 8 Grams
        gold_8g = ((g_data['price'] / 31.1) * 83.5 * 1.15) * 8
        st.metric("Gold 8 Gram (Approx)", f"₹{gold_8g:.0f}")

    st.divider()
    
    # AED to INR
    a_data = get_live_data("AEDINR=X")
    if a_data: 
        st.metric("1 Dirham (AED)", f"₹{a_data['price']:.2f}")

else:
    st.title("🔗 Quick Access")
    st.markdown("### [🌐 Open Upstox Login](https://upstox.com/)")
    st.markdown("### [📊 Open TradingView Chart](https://www.tradingview.com/chart/)")
