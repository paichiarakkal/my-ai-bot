import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import os

st.set_page_config(page_title="Faisal's Dubai Terminal", layout="wide")

# --- 1. ഡാറ്റാ മാനേജ്‌മെന്റ് ---
DATA_FILE = 'faisal_pro_log.csv'
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False

def log_trade(sym, price, qty, t_type, reason):
    df = pd.DataFrame([{'Time': pd.Timestamp.now().strftime('%H:%M:%S'), 'Asset': sym, 'Price': price, 'Qty': qty, 'Type': t_type, 'Reason': reason, 'Bal': round(st.session_state.balance, 2)}])
    df.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)

# --- 2. ലൈവ് എക്സ്ചേഞ്ച് റേറ്റുകൾ ---
def get_exchange_rates():
    try:
        inr_data = yf.download("INR=X", period="1d", progress=False)
        aed_data = yf.download("AED=X", period="1d", progress=False)
        return float(inr_data['Close'].iloc[-1]), float(aed_data['Close'].iloc[-1])
    except: return 83.0, 3.67

# --- 3. ബോട്ട് ലോജിക് ---
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

# --- 4. സൈഡ്‌ബാർ & കറൻസി ---
st.sidebar.title("🤖 Faisal's AI Bot")
st.session_state.auto_mode = st.sidebar.toggle("Activate Auto-Trading", value=st.session_state.auto_mode)
asset_choice = st.sidebar.selectbox("Select Asset", ["Gold (Dubai/AED)", "Nifty 50", "Crude Oil"])

inr_rate, aed_rate = get_exchange_rates()

st.sidebar.divider()
st.sidebar.subheader("🌍 Live Exchange Rates")
st.sidebar.write(f"1 USD = **₹{inr_rate:.2f}**")
st.sidebar.write(f"1 USD = **{aed_rate:.2f} AED**")

# --- 5. മെയിൻ ഡിസ്‌പ്ലേ ---
placeholder = st.empty()
asset_map = {"Gold (Dubai/AED)": "GC=F", "Nifty 50": "^NSEI", "Crude Oil": "CL=F"}
ticker = asset_map[asset_choice]

if st.session_state.auto_mode:
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            decision, reason = get_bot_decision(df)
            last_p = float(df['Close'].iloc[-1]) # അന്താരാഷ്ട്ര വില (USD per Ounce)
            
            with placeholder.container():
                st.metric("Live Balance", f"₹{st.session_state.balance:,.2f}")
                
                # ഗോൾഡ് കാൽക്കുലേഷൻ (1 Ounce = 31.1035 Grams)
                if "Gold" in asset_choice:
                    price_per_gram_usd = last_p / 31.1035
                    price_per_gram_aed = price_per_gram_usd * aed_rate
                    price_8gram_aed = price_per_gram_aed * 8
                    
                    st.success(f"**Gold Price (Dubai):**")
                    c1, c2 = st.columns(2)
                    c1.metric("1 Gram (AED)", f"{price_per_gram_aed:.2f}")
                    c2.metric("8 Gram / 1 Pavan (AED)", f"{price_8gram_aed:.2f}")
                
                # ട്രേഡിംഗ് ആക്ഷൻ
                if decision != "HOLD":
                    qty = 10
                    if decision == "BUY": st.session_state.balance -= (last_p * qty)
                    else: st.session_state.balance += (last_p * qty)
                    log_trade(asset_choice, last_p, qty, decision, reason)
                    st.toast(f"Bot {decision} {asset_choice}")

                # ചാർട്ട്
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=450, title=f"{asset_choice} Live Tracker")
                st.plotly_chart(fig, use_container_width=True)

            time.sleep(30)
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")
