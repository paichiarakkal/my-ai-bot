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

# --- 2. ബോട്ട് ലോജിക് (Decision Making) ---
def get_bot_decision(df):
    close = df['Close']
    # RSI കണക്കാക്കുന്നു
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
    
    # EMA 20
    ema = close.ewm(span=20, adjust=False).mean().iloc[-1]
    last_price = close.iloc[-1]

    # കണ്ടീഷനുകൾ:
    if rsi < 30 and last_price > ema:
        return "BUY", f"RSI: {rsi:.2f} (Oversold) & Price > EMA"
    elif rsi > 70 or last_price < (ema * 0.99):
        return "SELL", f"RSI: {rsi:.2f} (Overbought) or Price Drop"
    return "HOLD", "Waiting for Signal"

# --- 3. മെയിൻ ഡിസ്‌പ്ലേ ---
st.sidebar.title("🤖 AI Bot Control")
st.session_state.auto_mode = st.sidebar.toggle("Activate Auto-Trading", value=st.session_state.auto_mode)
asset = st.sidebar.selectbox("Select Asset", ["CL=F", "^NSEI", "GC=F"])

placeholder = st.empty()

# --- 4. ഓട്ടോമാറ്റിക് ലൂപ്പ് ---
while st.session_state.auto_mode:
    with placeholder.container():
        try:
            df = yf.download(asset, period="1d", interval="1m", progress=False)
            if not df.empty:
                decision, reason = get_bot_decision(df)
                price = float(df['Close'].iloc[-1])
                
                # ബോട്ട് ട്രേഡ് എടുക്കുന്നു
                if decision == "BUY":
                    qty = 10
                    st.session_state.balance -= (price * qty)
                    log_auto_trade(asset, price, qty, "BUY", reason)
                    st.toast(f"🤖 Bot Bought {asset} at {price}")
                
                elif decision == "SELL":
                    qty = 10
                    st.session_state.balance += (price * qty)
                    log_auto_trade(asset, price, qty, "SELL", reason)
                    st.toast(f"🤖 Bot Sold {asset} at {price}")

                # ലൈവ് സ്റ്റാറ്റസ് കാണിക്കുന്നു
                st.metric("Wallet Balance", f"₹{st.session_state.balance:,.2f}")
                st.info(f"**Bot Status:** {decision} | **Reason:** {reason}")
                
                # ചാർട്ട് അപ്‌ഡേറ്റ്
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)

            time.sleep(60) # ഓരോ മിനിറ്റിലും ചെക്ക് ചെയ്യും
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
            break

if not st.session_state.auto_mode:
    st.warning("🤖 ബോട്ട് ഇപ്പോൾ ഓഫ് ആണ്. സൈഡ്‌ബാറിൽ നിന്ന് 'Activate' ചെയ്യുക.")
    if os.path.exists(DATA_FILE):
        st.write("### 📜 Last Auto-Trades")
        st.table(pd.read_csv(DATA_FILE).tail(5))
