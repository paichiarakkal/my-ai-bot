import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")

# സൈഡ് ബാർ (Sidebar Menu)
st.sidebar.title("💎 Paichi Menu")
choice = st.sidebar.radio("സേവനം തിരഞ്ഞെടുക്കുക:", ["Indian Indices", "Commodities & Forex", "Quick Links"])
st.sidebar.info("Intraday Trader Faisal, Al Barsha")

# ലൈവ് ഡാറ്റ എടുക്കാനുള്ള ഫംഗ്ഷൻ
def get_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
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
        else: last_rsi = 50
        return {"price": price, "rsi": last_rsi}
    except: return None

# --- മെയിൻ ആപ്പ് ഭാഗം ---

if choice == "Indian Indices":
    st.title("📊 Indian Stock Market")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 Nifty 50"):
            d = get_data("^NSEI")
            if d:
                st.metric("Nifty 50", f"{d['price']:.2f}")
                st.write(f"RSI: {d['rsi']:.2f}")
                if d['rsi'] < 35: st.success("SIGNAL: BUY 🟢")
                elif d['rsi'] > 65: st.error("SIGNAL: SELL 🔴")
                else: st.warning("SIGNAL: WAIT ⏳")
        
        if st.button("🏦 Bank Nifty"):
            d = get_data("^NSEBANK")
            if d: st.metric("Bank Nifty", f"{d['price']:.2f}")

    with col2:
        if st.button("🚀 Fin Nifty"):
            d = get_data("NIFTY_FIN_SERVICE.NS")
            if d: st.metric("Fin Nifty", f"{d['price']:.2f}")
            
        if st.button("🏛️ Sensex"):
            d = get_data("^BSESN")
            if d: st.metric("Sensex", f"{d['price']:.2f}")

elif choice == "Commodities & Forex":
    st.title("🛢️ Commodities & Currency")
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("🇮🇳 Crude Oil Future (MCX)"):
            d = get_data("CL=F")
            if d:
                # ഫ്യൂച്ചർ വിലയ്ക്കുള്ള മൾട്ടിപ്ലയർ (1.25)
                mcx_future = d['price'] * 83.5 * 1.25
                st.metric("Crude Oil Future", f"₹{mcx_future:.2f}")
                st.write(f"Global RSI: {d['rsi']:.2f}")
                if d['rsi'] < 35: st.success("SIGNAL: BUY 🟢")
                elif d['rsi'] > 65: st.error("SIGNAL: SELL 🔴")
                else: st.warning("SIGNAL: WAIT ⏳")

        if st.button("💰 Gold (8 Gram INR)"):
            d = get_data("GC=F")
            if d:
                p_8g = ((d['price'] / 31.1) * 83.5 * 1.15) * 8
                st.metric("Gold 8g Approx", f"₹{p_8g:.0f}")

    with c2:
        if st.button("🇦🇪 INR to Dirham (AED)"):
            d = get_data("AEDINR=X")
            if d: st.metric("1 Dirham (AED)", f"₹{d['price']:.2f}")

else:
    st.title("🔗 Quick Access")
    st.markdown("### [🌐 Open Upstox](https://upstox.com/)")
    st.markdown("### [📊 TradingView](https://www.tradingview.com/chart/)")
