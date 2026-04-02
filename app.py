import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Paichi Trader Pro", page_icon="📈", layout="wide")

st.title("📈 Paichi Smart Trading Signals")

def get_signal(ticker):
    try:
        # 5 മിനിറ്റ് ചാർട്ട് ഡാറ്റ എടുക്കുന്നു
        df = yf.download(ticker, period="2d", interval="5m", progress=False)
        if len(df) < 25: return None, None, None

        # 1. RSI (14) Manual Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 2. Moving Average (SMA 20)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        
        last_price = float(df['Close'].iloc[-1])
        last_rsi = float(df['RSI'].iloc[-1])
        last_sma = float(df['SMA_20'].iloc[-1])

        # സിഗ്നൽ നിയമം (Logic)
        signal = "WAIT ⏳"
        if last_rsi < 35 and last_price > last_sma:
            signal = "BUY 🟢"
        elif last_rsi > 65 and last_price < last_sma:
            signal = "SELL 🔴"
            
        return last_price, signal, last_rsi
    except Exception as e:
        return None, None, None

# ഡിസ്‌പ്ലേ ഭാഗം
col1, col2 = st.columns(2)

# ക്രൂഡ് ഓയിൽ സിഗ്നൽ
p_oil, s_oil, r_oil = get_signal("CL=F")
with col1:
    st.info("🛢️ Crude Oil")
    if p_oil:
        st.metric("Price", f"${p_oil:.2f}")
        st.write(f"RSI: {r_oil:.2f}")
        st.subheader(f"Action: {s_oil}")

# നിഫ്റ്റി സിഗ്നൽ
p_nifty, s_nifty, r_nifty = get_signal("^NSEI")
with col2:
    st.info("📊 Nifty 50")
    if p_nifty:
        st.metric("Price", f"{p_nifty:.2f}")
        st.write(f"RSI: {r_nifty:.2f}")
        st.subheader(f"Action: {s_nifty}")

st.divider()
st.warning("ഇത് ലളിതമായ RSI/SMA സിഗ്നൽ മാത്രമാണ്. നിന്റെ സ്വന്തം പ്ലാൻ കൂടി നോക്കി മാത്രം ട്രേഡ് ചെയ്യുക.")
