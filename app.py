import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")

# ഓരോ 1 സെക്കൻഡിലും ഓട്ടോമാറ്റിക് റിഫ്രഷ്
st_autorefresh(interval=1000, limit=1000, key="faisal_live_signals")

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
        
        # RSI കണക്കുകൂട്ടൽ
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

def show_signal(data, name, multiplier=1):
    if data:
        price = data['price'] * multiplier
        st.metric(name, f"₹{price:.2f}")
        st.write(f"RSI: {data['rsi']:.2f}")
        if data['rsi'] < 35: st.success("ACTION: BUY 🟢")
        elif data['rsi'] > 65: st.error("ACTION: SELL 🔴")
        else: st.warning("ACTION: WAIT ⏳")
    else:
        st.error(f"{name} ഡാറ്റ ലഭ്യമല്ല")

# --- മെയിൻ ഡിസ്‌പ്ലേ ---

if choice == "Indian Indices":
    st.title("📊 Live Market Signals")
    col1, col2 = st.columns(2)
    with col1:
        show_signal(get_live_data("^NSEI"), "Nifty 50")
    with col2:
        show_signal(get_live_data("^NSEBANK"), "Bank Nifty")

elif choice == "Commodities & Forex":
    st.title("🛢️ Commodities (Live)")
    # Crude Oil Future Calculation
    c_data = get_live_data("CL=F")
    show_signal(c_data, "Crude Oil Future (MCX)", multiplier=85.5)
    
    st.divider()
    a_data = get_live_data("AEDINR=X")
    if a_data: st.metric("1 Dirham (AED)", f"₹{a_data['price']:.2f}")

else:
    st.title("🔗 Quick Access")
    st.markdown("### [🌐 Open Upstox Login](https://upstox.com/)")
    st.markdown("### [📊 Open TradingView Chart](https://www.tradingview.com/chart/)")
