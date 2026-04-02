import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")

# സൈഡ് ബാർ
st.sidebar.title("💎 Paichi Menu")
choice = st.sidebar.radio("സേവനം തിരഞ്ഞെടുക്കുക:", ["Market Signals", "Quick Links"])
st.sidebar.info("Intraday Trader Faisal, Al Barsha")

# ഡാറ്റ എടുക്കാനുള്ള പുതിയ രീതി (Yahoo Finance API)
def get_stock_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        
        # ലളിതമായ RSI കണക്കുകൂട്ടൽ
        df = pd.Series(prices).dropna()
        delta = df.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        return {"price": price, "rsi": rsi.iloc[-1] if not rsi.empty else 50}
    except:
        return None

if choice == "Market Signals":
    st.title("📈 Live Market & Signals")
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🛢️ Crude Oil"):
            with st.spinner('Loading...'):
                data = get_stock_data("CL=F")
                if data:
                    st.metric("Price (USD)", f"${data['price']:.2f}")
                    st.write(f"RSI: {data['rsi']:.2f}")
                    if data['rsi'] < 35: st.success("ACTION: BUY 🟢")
                    elif data['rsi'] > 65: st.error("ACTION: SELL 🔴")
                    else: st.warning("ACTION: WAIT ⏳")
                else: st.error("ഡാറ്റ ലഭ്യമല്ല. അല്പം കഴിഞ്ഞ് നോക്കൂ.")

        if st.button("💰 Gold (8 Gram INR)"):
            with st.spinner('Loading...'):
                data = get_stock_data("GC=F")
                if data:
                    # ഏകദേശ ഇന്ത്യൻ വില (INR)
                    price_inr_8g = ((data['price'] / 31.1) * 83.5 * 1.15) * 8
                    st.metric("Gold 8g (Approx)", f"₹{price_inr_8g:.0f}")

    with col2:
        if st.button("📊 Nifty 50 Index"):
            with st.spinner('Loading...'):
                data = get_stock_data("^NSEI")
                if data:
                    st.metric("Price", f"{data['price']:.2f}")
                    st.write(f"RSI: {data['rsi']:.2f}")
                    if data['rsi'] < 35: st.success("ACTION: BUY 🟢")
                    elif data['rsi'] > 65: st.error("ACTION: SELL 🔴")
                    else: st.warning("ACTION: WAIT ⏳")

        if st.button("🇦🇪 INR to Dirham"):
            with st.spinner('Loading...'):
                data = get_stock_data("AEDINR=X")
                if data:
                    st.metric("1 Dirham", f"₹{data['price']:.2f}")

else:
    st.title("🔗 Quick Access")
    st.markdown("### [🌐 Open Upstox Login](https://upstox.com/)")
    st.markdown("### [📊 Open TradingView Chart](https://www.tradingview.com/chart/)")
