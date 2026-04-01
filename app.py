import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. പേജ് സെറ്റിംഗ്സ് (Safe Mode - No Image Error) ---
st.set_page_config(page_title="Faisal AI Terminal", page_icon="👤", layout="wide")

# --- 2. വാലറ്റ് ബാലൻസ് അപ്‌ഡേറ്റ് ---
if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50

# --- 3. സൂപ്പർട്രെൻഡ് ഫംഗ്‌ഷൻ ---
def custom_supertrend(df, period=7, multiplier=3):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    hl2 = (df['High'] + df['Low']) / 2
    df['tr'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    atr = df['tr'].rolling(period).mean()
    upper = hl2 + (multiplier * atr)
    lower = hl2 - (multiplier * atr)
    st_list, dir_list = [0.0] * len(df), [1] * len(df)
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upper.iloc[i-1]: dir_list[i] = 1
        elif df['Close'].iloc[i] < lower.iloc[i-1]: dir_list[i] = -1
        else: dir_list[i] = dir_list[i-1]
        st_list[i] = lower.iloc[i] if dir_list[i] == 1 else upper.iloc[i]
    df['ST'], df['ST_DIR'] = st_list, dir_list
    return df

# --- 4. സൈഡ്‌ബാർ (AI Chat & Calc) ---
st.sidebar.markdown(f"<h1 style='text-align: center; color: #00FFA3;'>Faisal AI</h1>", unsafe_allow_html=True)

# AI Chat Box
st.sidebar.divider()
st.sidebar.subheader("💬 AI-യോട് ചോദിക്കുക")
user_query = st.sidebar.text_input("ചോദിക്കൂ:", placeholder="ഉദാ: ക്രൂഡ് ഓയിൽ ട്രെൻഡ്?")
if user_query:
    st.sidebar.info("🤖: ചാർട്ടിലെ മഞ്ഞ ലൈനിന് മുകളിൽ പ്രൈസ് നിൽക്കുന്നത് വരെ ബൈ ഹോൾഡ് ചെയ്യാം.")

# Exchange Calc
st.sidebar.divider()
st.sidebar.subheader("💱 Currency Calc")
mode = st.sidebar.radio("Mode", ["INR to AED", "AED to INR"])
amt = st.sidebar.number_input("Amount", value=1.0)
try:
    rate = float(yf.download("AEDINR=X", period="1d", progress=False)['Close'].iloc[-1])
    res = amt / rate if mode == "INR to AED" else amt * rate
    st.sidebar.success(f"Result: {res:.2f}")
except: pass

asset_choice = st.sidebar.selectbox("Asset", ["Crude Oil (MCX)", "Nifty 50", "Gold (Live)"])

# --- 5. മെയിൻ ഡിസ്‌പ്ലേ ---
placeholder = st.empty()

while True:
    with placeholder.container():
        ticker_map = {"Crude Oil (MCX)": "CL=F", "Nifty 50": "^NSEI", "Gold (Live)": "GC=F"}
        df = yf.download(ticker_map[asset_choice], period="1d", interval="1m", progress=False)
        
        if not df.empty:
            # ക്രൂഡ് ഓയിൽ പ്രൈസ് അപ്‌സ്റ്റോക്സിലെ പോലെ ശരിയാക്കുന്നു
            if asset_choice == "Crude Oil (MCX)":
                df = df * 91.5 
            
            df = custom_supertrend(df)
            last_p = float(df['Close'].iloc[-1])
            st_dir = df['ST_DIR'].iloc[-1]

            # വാലറ്റ് ബാലൻസ് ഡിസ്‌പ്ലേ
            st.metric("Live Wallet Balance", f"₹{st.session_state.balance:,.2f}")

            # AI Signal Box
            msg, col, bg = ("🚀 AI BUY: ട്രെൻഡ് പോസിറ്റീവ് ആണ്!", "#00FFA3", "#003322") if st_dir == 1 else ("📉 AI SELL: ട്രെൻഡ് നെഗറ്റീവ് ആണ്!", "#FF3131", "#330000")
            st.markdown(f'<div style="background:{bg};padding:20px;border-radius:15px;border:2px solid {col};"><h3 style="color:{col};margin:0;">🚀 Faisal AI Advisor</h3><p style="color:white;margin-top:10px;">{msg}</p></div>', unsafe_allow_html=True)

            # Chart
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market")])
            fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='yellow', width=2), name="Supertrend"))
            fig.update_layout(template="plotly_dark", height=450, title=f"{asset_choice} | Price: {last_p:,.2f}")
            st.plotly_chart(fig, use_container_width=True)

    time.sleep(30)
    st.rerun()
