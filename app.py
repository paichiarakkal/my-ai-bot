import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. പേജ് സെറ്റിംഗ്സ് (Safe Mode - No Image) ---
st.set_page_config(page_title="Faisal AI Terminal", page_icon="📈", layout="wide")

# --- 2. വാലറ്റ് ബാലൻസ് അപ്‌ഡേറ്റ് ---
if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50

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

# --- 4. സൈഡ്‌ബാർ (Image ഒഴിവാക്കിയ പുതിയ ഡിസൈൻ) ---
st.sidebar.markdown("<h2 style='color: #00FFA3; text-align: center;'>👤 Faisal Pro AI</h2>", unsafe_allow_html=True)

# AI Chat Section
st.sidebar.divider()
query = st.sidebar.text_input("AI-യോട് ചോദിക്കാം:", placeholder="ക്രൂഡ് ഓയിൽ ട്രെൻഡ്?")
if query:
    st.sidebar.info("🤖: നിന്റെ ചോദ്യം ഞാൻ ശ്രദ്ധിച്ചു. ചാർട്ടിലെ മഞ്ഞ ലൈനിന് മുകളിൽ പ്രൈസ് നിൽക്കുമ്പോൾ ബൈ തുടരാം.")

# Currency Calc
st.sidebar.divider()
st.sidebar.subheader("💱 Currency Calc")
mode = st.sidebar.radio("Mode", ["INR to AED", "AED to INR"])
amt = st.sidebar.number_input("Amount", value=1.0)
try:
    rate = float(yf.download("AEDINR=X", period="1d", progress=False)['Close'].iloc[-1])
    res = amt / rate if mode == "INR to AED" else amt * rate
    st.sidebar.success(f"Result: {res:.2f}")
except: pass

asset = st.sidebar.selectbox("Asset", ["Crude Oil (MCX)", "Nifty 50", "Gold (Live)"])

# --- 5. മെയിൻ ഡിസ്‌പ്ലേ ---
placeholder = st.empty()

while True:
    with placeholder.container():
        ticker = {"Crude Oil (MCX)": "CL=F", "Nifty 50": "^NSEI", "Gold (Live)": "GC=F"}[asset]
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        if not df.empty:
            # ക്രൂഡ് ഓയിൽ പ്രൈസ് ലോജിക്
            if asset == "Crude Oil (MCX)":
                df = df * 91.5 
            
            df = get_supertrend(df)
            price = float(df['Close'].iloc[-1])
            trend = df['ST_DIR'].iloc[-1]

            # ബാലൻസ് ഡിസ്‌പ്ലേ
            st.metric("Live Wallet Balance", f"₹{st.session_state.balance:,.2f}")

            # AI Advisor Signal
            msg, col, bg = ("🚀 AI BUY: ട്രെൻഡ് പോസിറ്റീവ് ആണ്!", "#00FFA3", "#003322") if trend == 1 else ("📉 AI SELL: ട്രെൻഡ് നെഗറ്റീവ് ആണ്!", "#FF3131", "#330000")
            st.markdown(f'<div style="background:{bg};padding:20px;border-radius:15px;border:2px solid {col};"><h3 style="color:{col};margin:0;">🚀 Faisal AI Advisor</h3><p style="color:white;margin-top:10px;">{msg}</p></div>', unsafe_allow_html=True)

            # Chart
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market")])
            fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='yellow', width=2), name="Supertrend"))
            fig.update_layout(template="plotly_dark", height=480, title=f"{asset} | Price: {price:,.2f}")
            st.plotly_chart(fig, use_container_width=True)

    time.sleep(30)
    st.rerun()
