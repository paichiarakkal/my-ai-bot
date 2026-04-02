import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")

# സൈഡ് ബാർ സെറ്റിംഗ്സ്
st.sidebar.title("💎 Paichi Menu")
choice = st.sidebar.radio("സേവനം തിരഞ്ഞെടുക്കുക:", ["Market Rates & Signals", "Quick Links"])
st.sidebar.info("Intraday Trader Faisal, Al Barsha")

def get_data(ticker):
    try:
        df = yf.download(ticker, period="5d", interval="5m", progress=False)
        if df.empty: return None
        last_price = float(df['Close'].iloc[-1])
        
        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        last_rsi = float(rsi.iloc[-1])
        
        return {"price": last_price, "rsi": last_rsi}
    except: return None

if choice == "Market Rates & Signals":
    st.title("📈 Live Market & Signals")
    st.write("ബട്ടൺ അമർത്തി തത്സമയ നിരക്കുകളും സിഗ്നലുകളും കാണുക.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🛢️ Crude Oil (Global)"):
            data = get_data("CL=F")
            if data:
                st.metric("Price (USD)", f"${data['price']:.2f}")
                st.write(f"RSI: {data['rsi']:.2f}")
                if data['rsi'] < 35: st.success("ACTION: BUY 🟢")
                elif data['rsi'] > 65: st.error("ACTION: SELL 🔴")
                else: st.warning("ACTION: WAIT ⏳")

        if st.button("💰 Gold (8 Gram - INR)"):
            data = get_data("GC=F") # Global Gold
            if data:
                # 8 Gram Indian Price Approx Calculation
                price_inr_1g = (data['price'] / 31.1) * 83.5 * 1.15 # Approx with tax
                st.metric("Gold 8g (Approx)", f"₹{price_inr_1g * 8:.0f}")
                st.caption("ശ്രദ്ധിക്കുക: ഇത് ഏകദേശ വിലയാണ്.")

    with col2:
        if st.button("📊 Nifty 50 Index"):
            data = get_data("^NSEI")
            if data:
                st.metric("Price", f"{data['price']:.2f}")
                st.write(f"RSI: {data['rsi']:.2f}")
                if data['rsi'] < 35: st.success("ACTION: BUY 🟢")
                elif data['rsi'] > 65: st.error("ACTION: SELL 🔴")
                else: st.warning("ACTION: WAIT ⏳")

        if st.button("💵 INR to AED (Dirham)"):
            data = get_data("AEDINR=X")
            if data:
                st.metric("1 Dirham", f"₹{data['price']:.2f}")

else:
    st.title("🔗 Quick Links")
    st.markdown("[🌐 Open Upstox Login](https://upstox.com/)")
    st.markdown("[📊 Open TradingView Chart](https://www.tradingview.com/chart/)")
