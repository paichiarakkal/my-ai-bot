import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Faisal Pro Multi-Tool AI", layout="wide")

# വാലറ്റിലെ പണം സേവ് ചെയ്യാൻ (Initial 5 Lakhs)
if 'balance' not in st.session_state:
    st.session_state.balance = 500000.00
if 'position' not in st.session_state:
    st.session_state.position = None

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("💎 Faisal Pro Hub")
menu = st.sidebar.radio("മെനു തിരഞ്ഞെടുക്കുക:", 
    ["📈 Paper Trading", "💰 Currency & Gold", "🤖 AI Assistant", "📊 Market Indices"])

# --- 1. PAPER TRADING ---
if menu == "📈 Paper Trading":
    st.header("Live Trading Dashboard")
    asset = st.selectbox("തിരഞ്ഞെടുക്കുക:", ["Crude Oil (MCX)", "Nifty 50"])
    ticker = "CL=F" if asset == "Crude Oil (MCX)" else "^NSEI"
    
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    if not df.empty:
        curr_p = float(df['Close'].iloc[-1])
        if asset == "Crude Oil (MCX)": curr_p *= 91.5 # INR ഏകദേശ നിരക്ക്
        
        c1, c2 = st.columns(2)
        c1.metric("Wallet Balance", f"₹{st.session_state.balance:,.2f}")
        c2.metric(f"Live {asset} Price", f"₹{curr_p:,.2f}")
        
        # ബട്ടണുകൾ
        col_b1, col_b2 = st.columns(2)
        if col_b1.button("🟢 BUY"):
            st.success(f"Bought at ₹{curr_p}")
        if col_b2.button("🔴 SELL"):
            st.info(f"Sold at ₹{curr_p}")
        
        # ചാർട്ട്
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

# --- 2. CURRENCY & GOLD ---
elif menu == "💰 Currency & Gold":
    st.header("Live Rates (Exchange & Gold)")
    
    # Currency calculation (AED to INR)
    aed_rate = 22.78 # ഇത് നിനക്ക് ഇഷ്ടമുള്ള നിരക്കിലേക്ക് മാറ്റാം
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💵 Currency Converter")
        amt = st.number_input("Enter AED:", value=1.0)
        st.write(f"**{amt} AED = ₹{amt * aed_rate:.2f} INR**")
    
    with col2:
        st.subheader("🟡 Gold Price (India)")
        # 8 ഗ്രാം (1 പവൻ) ഏകദേശ വില
        gold_8g = 68450 
        st.write(f"**ഇന്നത്തെ സ്വർണ്ണവില (8g):** ₹{gold_8g:,}")
        st.caption("ശ്രദ്ധിക്കുക: ഇത് ഏകദേശ നിരക്കാണ്.")

# --- 3. AI ASSISTANT ---
elif menu == "🤖 AI Assistant":
    st.header("Ask Faisal AI")
    st.info("നിങ്ങളുടെ സംശയങ്ങൾ താഴെ ചോദിക്കാം. AI മറുപടി നൽകാൻ തയ്യാറാണ്!")
    user_input = st.chat_input("ഇവിടെ ടൈപ്പ് ചെയ്യൂ...")
    if user_input:
        st.chat_message("user").write(user_input)
        st.chat_message("assistant").write(f"നിങ്ങൾ ചോദിച്ചത്: '{user_input}'. ഇതിനെക്കുറിച്ച് കൂടുതൽ പഠിക്കാൻ ഞാൻ സഹായിക്കാം!")

# --- 4. MARKET INDICES ---
elif menu == "📊 Market Indices":
    st.header("Global Market Watch")
    indices = {"Nifty 50": "^NSEI", "Sensex": "^BSESN", "Dow Jones": "^DJI"}
    for name, tick in indices.items():
        data = yf.download(tick, period="1d", progress=False)
        if not data.empty:
            p = data['Close'].iloc[-1]
            st.write(f"**{name}:** {p:,.2f}")
