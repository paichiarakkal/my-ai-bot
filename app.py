import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. പേജ് സെറ്റിംഗ്സ് (നിന്റെ പേരും ഐക്കണും)
st.set_page_config(
    page_title="Paichi Pro Hub",
    page_icon="💎",
    layout="wide"
)

# വാലറ്റ് ബാലൻസ് സേവ് ചെയ്യാൻ
if 'balance' not in st.session_state:
    st.session_state.balance = 500000.00

# 2. സൈഡ്‌ബാർ മെനു (എല്ലാ ബട്ടണുകളും ഇവിടെയുണ്ട്)
st.sidebar.title("💎 Paichi Pro Menu")
menu = st.sidebar.radio("സേവനം തിരഞ്ഞെടുക്കുക:", 
    ["📈 Paper Trading", "📊 Nifty 50 Live", "🧮 Stock Calculator", "💰 Currency & Gold", "🤖 AI Assistant"])

# --- സെക്ഷൻ 1: PAPER TRADING ---
if menu == "📈 Paper Trading":
    st.header("Live Trading Dashboard")
    asset = st.selectbox("അസറ്റ് തിരഞ്ഞെടുക്കുക:", ["Crude Oil (MCX)", "Nifty 50"])
    ticker = "CL=F" if asset == "Crude Oil (MCX)" else "^NSEI"
    
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    if not df.empty:
        curr_p = float(df['Close'].iloc[-1])
        if asset == "Crude Oil (MCX)": curr_p *= 91.5
        
        c1, c2 = st.columns(2)
        c1.metric("Wallet Balance", f"₹{st.session_state.balance:,.2f}")
        c2.metric(f"Live {asset} Price", f"₹{curr_p:,.2f}")
        
        col_b1, col_b2 = st.columns(2)
        if col_b1.button("🟢 BUY"): st.success(f"Bought at ₹{curr_p}")
        if col_b2.button("🔴 SELL"): st.info(f"Sold at ₹{curr_p}")
        
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

# --- സെക്ഷൻ 2: NIFTY 50 LIVE STOCKS ---
elif menu == "📊 Nifty 50 Live":
    st.header("Nifty 50 Top Stocks")
    # പ്രധാനപ്പെട്ട ചില ഇന്ത്യൻ സ്റ്റോക്കുകൾ
    stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS", "BHARTIARTL.NS"]
    
    for s in stocks:
        s_data = yf.download(s, period="1d", progress=False)
        if not s_data.empty:
            p = s_data['Close'].iloc[-1]
            st.write(f"✅ **{s.replace('.NS','')}**: ₹{p:,.2f}")

# --- സെക്ഷൻ 3: STOCK CALCULATOR ---
elif menu == "🧮 Stock Calculator":
    st.header("Stock Profit/Loss Calculator")
    col_x, col_y = st.columns(2)
    buy = col_x.number_input("വാങ്ങിയ വില (Buy Price):", value=0.0)
    qty = col_x.number_input("എണ്ണം (Quantity):", value=1)
    sell = col_y.number_input("വിറ്റ വില (Sell Price):", value=0.0)
    
    cost = buy * qty
    revenue = sell * qty
    res = revenue - cost
    
    st.divider()
    st.subheader(f"ആകെ ഇൻവെസ്റ്റ്‌മെന്റ്: ₹{cost:,.2f}")
    if res > 0:
        st.success(f"ലാഭം: ₹{res:,.2f}")
    else:
        st.error(f"നഷ്ടം: ₹{abs(res):,.2f}")

# --- സെക്ഷൻ 4: CURRENCY & GOLD (LIVE) ---
elif menu == "💰 Currency & Gold":
    st.header("Live Rates")
    # Live AED to INR
    cur = yf.download("AEDINR=X", period="1d", progress=False)
    rate = float(cur['Close'].iloc[-1]) if not cur.empty else 22.78
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💵 Currency")
        val = st.number_input("Enter AED:", value=1.0)
        st.write(f"**{val} AED = ₹{val * rate:.2f} INR**")
        st.info(f"Live Rate: 1 AED = ₹{rate:.2f}")
    
    with col2:
        st.subheader("🟡 Gold (India)")
        st.write("**ഇന്നത്തെ സ്വർണ്ണവില (8g):** ₹68,450 (Approx)")

# --- സെക്ഷൻ 5: AI ASSISTANT ---
elif menu == "🤖 AI Assistant":
    st.header("Ask Paichi AI")
    msg = st.chat_input("എന്താണ് ചോദിക്കേണ്ടത്?")
    if msg:
        st.chat_message("user").write(msg)
        st.chat_message("assistant").write(f"ഹലോ ഫൈസൽ, '{msg}' എന്നതിനെക്കുറിച്ച് ഞാൻ പഠിക്കുകയാണ്!")
