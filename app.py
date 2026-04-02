import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Paichi Trader", page_icon="📈")
st.title("📈 Paichi Trading Signals")

def get_data(ticker):
    try:
        # കഴിഞ്ഞ 5 ദിവസത്തെ ഡാറ്റ എടുക്കുന്നു
        df = yf.download(ticker, period="5d", interval="5m", progress=False)
        if df.empty: return None
        
        last_price = df['Close'].iloc[-1]
        
        # ലളിതമായ RSI കണക്കുകൂട്ടൽ
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return {"price": last_price, "rsi": rsi.iloc[-1]}
    except:
        return None

# ക്രൂഡ് ഓയിൽ
oil = get_data("CL=F")
if oil:
    st.metric("Crude Oil Price", f"${oil['price']:.2f}")
    st.write(f"RSI: {oil['rsi']:.2f}")
    if oil['rsi'] < 30: st.success("SIGNAL: BUY 🟢")
    elif oil['rsi'] > 70: st.error("SIGNAL: SELL 🔴")
    else: st.warning("SIGNAL: WAIT ⏳")

st.divider()

# നിഫ്റ്റി
nifty = get_data("^NSEI")
if nifty:
    st.metric("Nifty 50", f"{nifty['price']:.2f}")
    st.write(f"RSI: {nifty['rsi']:.2f}")
    if nifty['rsi'] < 30: st.success("SIGNAL: BUY 🟢")
    elif nifty['rsi'] > 70: st.error("SIGNAL: SELL 🔴")
    else: st.warning("SIGNAL: WAIT ⏳")
