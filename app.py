import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. പേജ് സെറ്റിംഗ്സ് (Safe Mode - No Image) ---
st.set_page_config(page_title="Faisal AI Paper Trader", page_icon="💹", layout="wide")

# --- 2. വാലറ്റ് & ട്രേഡ് സെഷൻ സെറ്റപ്പ് ---
if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50
if 'position' not in st.session_state:
    st.session_state.position = None
if 'entry_price' not in st.session_state:
    st.session_state.entry_price = 0.0

# --- 3. സൂപ്പർട്രെൻഡ് ഫംഗ്‌ഷൻ ---
def get_supertrend(df, period=7, multiplier=3):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    hl2 = (df['High'] + df['Low']) / 2
    df['tr'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    atr = df['tr'].rolling(period).mean()
    upper = hl2 + (multiplier * atr)
    lower = hl2 - (multiplier * atr)
    st_vals, dirs = [0.0] * len(df), [1] * len(df)
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upper.iloc[i-1]: dirs[i] = 1
        elif df['Close'].iloc[i] < lower.iloc[i-1]: dirs[i] = -1
        else: dirs[i] = dirs[i-1]
        st_vals[i] = lower.iloc[i] if dirs[i] == 1 else upper.iloc[i]
    df['ST'], df['ST_DIR'] = st_vals, dirs
    return df

# --- 4. സൈഡ്‌ബാർ (എറർ വരാത്ത ഡിസൈൻ) ---
st.sidebar.markdown("<h2 style='color: #00FFA3; text-align: center;'>👤 Faisal Pro AI</h2>", unsafe_allow_html=True)

if st.sidebar.button("Reset Wallet"):
    st.session_state.balance = 471435.50
    st.session_state.position = None
    st.rerun()

asset = st.sidebar.selectbox("Asset", ["Crude Oil (MCX)", "Nifty 50"])
qty = st.sidebar.number_input("Quantity", min_value=1, value=10)

# --- 5. മെയിൻ ഡിസ്‌പ്ലേ ---
placeholder = st.empty()

while True:
    ticker = "CL=F" if asset == "Crude Oil (MCX)" else "^NSEI"
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    if not df.empty:
        if asset == "Crude Oil (MCX)": df = df * 91.5 
        df = get_supertrend(df)
        curr_p = float(df['Close'].iloc[-1])
        trend = df['ST_DIR'].iloc[-1]

        with placeholder.container():
            # സ്റ്റാറ്റസ് കാർഡുകൾ
            c1, c2, c3 = st.columns(3)
            c1.metric("Virtual Balance", f"₹{st.session_state.balance:,.2f}")
            c2.metric("Market Price", f"₹{curr_p:,.2f}")
            
            if st.session_state.position:
                pnl = (curr_p - st.session_state.entry_price) * qty
                c3.metric("Live P&L", f"₹{pnl:,.2f}", delta=f"{pnl:,.2f}")
            else:
                c3.metric("Live P&L", "No Trade")

            # പേപ്പർ ട്രേഡിംഗ് ബട്ടണുകൾ
            col_buy, col_exit = st.columns(2)
            if not st.session_state.position:
                if col_buy.button("🚀 PAPER BUY", use_container_width=True):
                    st.session_state.position = "LONG"
                    st.session_state.entry_price = curr_p
                    st.rerun()
            else:
                if col_exit.button("📉 EXIT TRADE", use_container_width=True):
                    profit = (curr_p - st.session_state.entry_price) * qty
                    st.session_state.balance += profit
                    st.session_state.position = None
                    st.rerun()

            # AI സിഗ്നൽ
            msg, color = ("BUY", "#00FFA3") if trend == 1 else ("SELL", "#FF3131")
            st.markdown(f'<div style="border:2px solid {color}; padding:10px; border-radius:10px; text-align:center;">AI Signal: <b style="color:{color};">{msg}</b></div>', unsafe_allow_html=True)

            # ചാർട്ട്
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market")])
            fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='yellow', width=2), name="Supertrend"))
            fig.update_layout(template="plotly_dark", height=450)
            st.plotly_chart(fig, use_container_width=True)

    time.sleep(30)
    st.rerun()
