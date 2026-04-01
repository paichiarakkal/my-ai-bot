import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import os

# പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Faisal's AI Auto-Terminal", layout="wide")

# --- 1. ഡാറ്റാ മാനേജ്‌മെന്റ് (Persistence) ---
DATA_FILE = 'faisal_auto_trades.csv'
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False

def log_auto_trade(sym, price, qty, t_type, reason):
    df = pd.DataFrame([{
        'Time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Asset': sym,
        'Price': price,
        'Qty': qty,
        'Type': t_type,
        'Reason': reason,
        'Wallet': round(st.session_state.balance, 2)
    }])
    df.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)

# --- 2. ബോട്ട് സ്ട്രാറ്റജി ലോജിക് (RSI & EMA) ---
def get_bot_decision(df):
    close = df['Close']
    # RSI കണക്കാക്കുന്നു
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_series = 100 - (100 / (1 + rs))
    rsi = float(rsi_series.iloc[-1]) # Error Fix: float ആക്കി മാറ്റി
    
    # EMA 20 (Trend)
    ema_series = close.ewm(span=20, adjust=False).mean()
    ema = float(ema_series.iloc[-1])
    last_price = float(close.iloc[-1])

    # AI തീരുമാനങ്ങൾ
    if rsi < 35 and last_price > ema:
        return "BUY", f"RSI: {rsi:.2f} (Oversold)"
    elif rsi > 65 or last_price < (ema * 0.99):
        return "SELL", f"RSI: {rsi:.2f} (Overbought)"
    return "HOLD", f"RSI: {rsi:.2f} | Waiting for Signal"

# --- 3. സൈഡ്‌ബാർ കൺട്രോൾസ് ---
st.sidebar.title("🤖 Faisal's AI Bot")
st.session_state.auto_mode = st.sidebar.toggle("Activate Auto-Mode", value=st.session_state.auto_mode)

# പേര് മാറ്റം (Display Names for Ease)
asset_display = st.sidebar.selectbox("Select Asset", ["Nifty 50", "Crude Oil", "Gold"])
asset_map = {"Nifty 50": "^NSEI", "Crude Oil": "CL=F", "Gold": "GC=F"}
ticker = asset_map[asset_display]

placeholder = st.empty()

# --- 4. ലൈവ് എക്സിക്യൂഷൻ ലൂപ്പ് ---
if st.session_state.auto_mode:
    try:
        # ഡാറ്റ ഡൗൺലോഡ് (1 മിനിറ്റ് ഇന്റർവെൽ)
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        if not df.empty:
            decision, reason = get_bot_decision(df)
            price = float(df['Close'].iloc[-1])
            
            with placeholder.container():
                st.metric("Live Wallet Balance", f"₹{st.session_state.balance:,.2f}")
                
                # ബോട്ട് ആക്ഷൻ (Auto Trading)
                if decision == "BUY":
                    qty = 10
                    st.session_state.balance -= (price * qty)
                    log_auto_trade(asset_display, price, qty, "BUY", reason)
                    st.success(f"🤖 Bot Action: {decision} | {reason}")
                elif decision == "SELL":
                    qty = 10
                    st.session_state.balance += (price * qty)
                    log_auto_trade(asset_display, price, qty, "SELL", reason)
                    st.error(f"🤖 Bot Action: {decision} | {reason}")
                else:
                    st.info(f"🤖 Bot Status: {decision} | {reason}")

                # പ്രൊഫഷണൽ ചാർട്ട്
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(title=f"{asset_display} Live Chart", template="plotly_dark", height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            time.sleep(30) # 30 സെക്കൻഡിൽ അപ്‌ഡേറ്റ് ചെയ്യും
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("🤖 ബോട്ട് ഇപ്പോൾ ഓഫ് ആണ്. സൈഡ്‌ബാറിൽ നിന്ന് 'Activate' ചെയ്യുക.")
    st.info("നിഫ്റ്റി കാണാൻ സൈഡ്‌ബാറിലെ ലിസ്റ്റിൽ നിന്ന് 'Nifty 50' സെലക്ട് ചെയ്യുക.")

# ട്രേഡ് ഹിസ്റ്ററി (History)
st.divider()
if os.path.exists(DATA_FILE):
    st.write("### 📜 Auto-Trade History")
    history_df = pd.read_csv(DATA_FILE)
    st.table(history_df.tail(10))
