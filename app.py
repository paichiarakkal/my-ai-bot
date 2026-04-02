import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi Pro Hub", page_icon="💎", layout="wide")

# വാലറ്റ് ബാലൻസ്
if 'balance' not in st.session_state:
    st.session_state.balance = 500000.00

# 2. സൈഡ്‌ബാർ മെനു
st.sidebar.title("💎 Paichi Pro Menu")
menu = st.sidebar.radio("സേവനം തിരഞ്ഞെടുക്കുക:", 
    ["📈 Paper Trading", "📊 Nifty 50 Live", "🧮 Stock Calculator", "💰 Currency & Gold", "🤖 AI Assistant"])

# സഹായി (Helper Function) - എറർ ഒഴിവാക്കാൻ
def get_clean_price(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not data.empty:
            raw_p = data['Close'].iloc[-1]
            # ഇതാണ് എറർ പരിഹരിക്കുന്ന വരി
            return float(raw_p.iloc[0]) if hasattr(raw_p, "__len__") else float(raw_p)
    except:
        return None
    return None

# --- സെക്ഷൻ 1: PAPER TRADING ---
if menu == "📈 Paper Trading":
    st.header("Live Trading Dashboard")
    asset = st.selectbox("അസറ്റ് തിരഞ്ഞെടുക്കുക:", ["Crude Oil (MCX)", "Nifty 50"])
    t_sym = "CL=F" if asset == "Crude Oil (MCX)" else "^NSEI"
    
    curr_p = get_clean_price(t_sym)
    if curr_p:
        if asset == "Crude Oil (MCX)": curr_p *= 91.5
        c1, c2 = st.columns(2)
        c1.metric("Wallet Balance", f"₹{st.session_state.balance:,.2f}")
        c2.metric(f"Live {asset} Price", f"₹{curr_p:,.2f}")
        
        col_b1, col_b2 = st.columns(2)
        if col_b1.button("🟢 BUY"): st.success(f"Bought at ₹{curr_p:,.2f}")
        if col_b2.button("🔴 SELL"): st.info(f"Sold at ₹{curr_p:,.2f}")
    else:
        st.error("മാർക്കറ്റ് ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല.")

# --- സെക്ഷൻ 2: NIFTY 50 LIVE ---
elif menu == "📊 Nifty 50 Live":
    st.header("Nifty 50 Top Stocks")
    stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS"]
    for s in stocks:
        p = get_clean_price(s)
        if p: st.write(f"✅ **{s.replace('.NS','')}**: ₹{p:,.2f}")

# --- സെക്ഷൻ 3: STOCK CALCULATOR ---
elif menu == "🧮 Stock Calculator":
    st.header("Stock Profit/Loss Calculator")
    c_x, c_y = st.columns(2)
    buy = c_x.number_input("വാങ്ങിയ വില:", value=0.0)
    qty = c_x.number_input("എണ്ണം:", value=1)
    sell = c_y.number_input("വിറ്റ വില:", value=0.0)
    res = (sell * qty) - (buy * qty)
    st.divider()
    if res >= 0: st.success(f"ലാഭം: ₹{res:,.2f}")
    else: st.error(f"നഷ്ടം: ₹{abs(res):,.2f}")

# --- സെക്ഷൻ 4: CURRENCY & GOLD ---
elif menu == "💰 Currency & Gold":
    st.header("Live Rates")
    rate = get_clean_price("AEDINR=X")
    if rate:
        val = st.number_input("Enter AED:", value=1.0)
        st.write(f"**{val} AED = ₹{val * rate:.2f} INR**")
        st.info(f"Live Rate: 1 AED = ₹{rate:.4f}")
    st.write("**Gold (8g India):** ₹68,450 (Approx)")

# --- സെക്ഷൻ 5: AI ASSISTANT ---
elif menu == "🤖 AI Assistant":
    st.header("Ask Paichi AI")
    msg = st.chat_input("ചോദിക്കൂ...")
    if msg:
        st.chat_message("user").write(msg)
        st.chat_message("assistant").write(f"ഫൈസൽ, '{msg}' എന്നതിനെക്കുറിച്ച് ഞാൻ തിരയുകയാണ്!")
