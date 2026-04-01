import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import os

st.set_page_config(page_title="Faisal's Pro Terminal", layout="wide")

# --- 1. ഡാറ്റാ മാനേജ്‌മെന്റ് ---
DATA_FILE = 'faisal_pro_log.csv'
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False

def log_trade(sym, price, qty, t_type, reason):
    df = pd.DataFrame([{'Time': pd.Timestamp.now().strftime('%H:%M:%S'), 'Asset': sym, 'Price': price, 'Qty': qty, 'Type': t_type, 'Reason': reason, 'Bal': round(st.session_state.balance, 2)}])
    df.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)

# --- 2. ലൈവ് എക്സ്ചേഞ്ച് റേറ്റ് എടുക്കുന്നു ---
def get_live_inr_rate():
    try:
        data = yf.download("INR=X", period="1d", progress=False)
        return float(data['Close'].iloc[-1])
    except: return 83.0 # താൽക്കാലിക റേറ്റ്

# --- 3. ബോട്ട് ലോജിക് (RSI & EMA) ---
def get_bot_decision(df):
    close = df['Close']
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = float((100 - (100 / (1 + rs))).iloc[-1])
    ema = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
    last_price = float(close.iloc[-1])

    if rsi < 35 and last_price > ema: return "BUY", f"RSI: {rsi:.2f}"
    elif rsi > 65 or last_price < (ema * 0.98): return "SELL", f"RSI: {rsi:.2f}"
    return "HOLD", f"RSI: {rsi:.2f}"

# --- 4. സൈഡ്‌ബാർ ---
st.sidebar.title("🤖 Faisal's AI Bot")
st.session_state.auto_mode = st.sidebar.toggle("Activate Auto-Trading", value=st.session_state.auto_mode)
asset_choice = st.sidebar.selectbox("Select Asset", ["Gold (INR)", "Nifty 50", "Crude Oil"])

# എക്സ്ചേഞ്ച് കാൽക്കുലേറ്റർ
st.sidebar.divider()
st.sidebar.subheader("💱 Currency Converter")
conv_amt = st.sidebar.number_input("Amount (USD)", value=1.0)
inr_rate = get_live_inr_rate()
st.sidebar.success(f"1 USD = ₹{inr_rate:.2f}")
st.sidebar.write(f"Total: ₹{conv_amt * inr_rate:,.2f}")

# --- 5. മെയിൻ ഡിസ്‌പ്ലേ ---
placeholder = st.empty()

asset_map = {"Gold (INR)": "GC=F", "Nifty 50": "^NSEI", "Crude Oil": "CL=F"}
ticker = asset_map[asset_choice]

if st.session_state.auto_mode:
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            decision, reason = get_bot_decision(df)
            last_p = float(df['Close'].iloc[-1])
            
            # ഗോൾഡ് ആണെങ്കിൽ INR-ലേക്ക് മാറ്റുന്നു
            display_price = last_p * inr_rate if asset_choice == "Gold (INR)" else last_p
            price_label = "Price (₹)" if asset_choice != "Crude Oil" else "Price ($)"

            with placeholder.container():
                st.metric("Live Balance", f"₹{st.session_state.balance:,.2f}")
                st.info(f"**Asset:** {asset_choice} | **{price_label}:** {display_price:,.2f}")
                
                if decision != "HOLD":
                    qty = 10
                    trade_cost = last_p * qty
                    if decision == "BUY": st.session_state.balance -= trade_cost
                    else: st.session_state.balance += trade_cost
                    log_trade(asset_choice, display_price, qty, decision, reason)
                    st.toast(f"Bot {decision} {asset_choice}")

                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=450, title=f"{asset_choice} Live Chart")
                st.plotly_chart(fig, use_container_width=True)

            time.sleep(30)
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")
else:
    st.warning("🤖 ബോട്ട് ഓഫ് ആണ്. ഓൺ ചെയ്യാൻ സൈഡ്‌ബാർ നോക്കുക.")
    if os.path.exists(DATA_FILE):
        st.write("### 📜 History")
        st.table(pd.read_csv(DATA_FILE).tail(10))
