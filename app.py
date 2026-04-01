import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import os

st.set_page_config(page_title="AI Auto-Bot", layout="wide")

# --- 1. ഡാറ്റാ മാനേജ്‌മെന്റ് ---
DATA_FILE = 'auto_trade_log.csv'
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False

def log_auto_trade(sym, price, qty, t_type, reason):
    df = pd.DataFrame([{'Time': pd.Timestamp.now(), 'Sym': sym, 'Price': price, 'Qty': qty, 'Type': t_type, 'Reason': reason, 'Bal': st.session_state.balance}])
    df.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)

# --- 2. ബോട്ട് ലോജിക് ---
def get_bot_decision(df):
    close = df['Close']
    # RSI കണക്കാക്കുന്നു
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_series = 100 - (100 / (1 + rs))
    rsi = float(rsi_series.iloc[-1]) # ഇവിടെയാണ് മാറ്റം വരുത്തിയത്
    
    # EMA 20
    ema_series = close.ewm(span=20, adjust=False).mean()
    ema = float(ema_series.iloc[-1])
    last_price = float(close.iloc[-1])

    # കണ്ടീഷനുകൾ
    if rsi < 35 and last_price > ema:
        return "BUY", f"RSI: {rsi:.2f} (Oversold)"
    elif rsi > 65 or last_price < (ema * 0.98):
        return "SELL", f"RSI: {rsi:.2f} (Overbought)"
    return "HOLD", f"RSI: {rsi:.2f} | Waiting"

# --- 3. ഡിസ്‌പ്ലേ ---
st.sidebar.title("🤖 Faisal's AI Bot")
st.session_state.auto_mode = st.sidebar.toggle("Activate Auto-Mode", value=st.session_state.auto_mode)
asset = st.sidebar.selectbox("Select Asset", ["CL=F", "^NSEI", "GC=F"])

placeholder = st.empty()

# --- 4. ലൈവ് ലൂപ്പ് ---
if st.session_state.auto_mode:
    try:
        df = yf.download(asset, period="1d", interval="1m", progress=False)
        if not df.empty:
            decision, reason = get_bot_decision(df)
            price = float(df['Close'].iloc[-1])
            
            with placeholder.container():
                st.metric("Wallet Balance", f"₹{st.session_state.balance:,.2f}")
                
                # ബോട്ട് ട്രേഡ് എടുക്കുന്നു
                if decision == "BUY":
                    qty = 10
                    st.session_state.balance -= (price * qty)
                    log_auto_trade(asset, price, qty, "BUY", reason)
                    st.success(f"🤖 Bot Action: {decision} | {reason}")
                elif decision == "SELL":
                    qty = 10
                    st.session_state.balance += (price * qty)
                    log_auto_trade(asset, price, qty, "SELL", reason)
                    st.error(f"🤖 Bot Action: {decision} | {reason}")
                else:
                    st.info(f"🤖 Bot Status: {decision} | {reason}")

                # ചാർട്ട്
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)
                
            time.sleep(30) # 30 സെക്കൻഡിൽ അപ്‌ഡേറ്റ് ചെയ്യും
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("🤖 ബോട്ട് ഇപ്പോൾ ഓഫ് ആണ്. സൈഡ്‌ബാറിൽ നിന്ന് 'Activate' ചെയ്യുക.")

# ട്രേഡ് ഹിസ്റ്ററി കാണാൻ
if os.path.exists(DATA_FILE):
    st.divider()
    st.write("### 📜 Auto-Trade History")
    st.table(pd.read_csv(DATA_FILE).tail(5))
