import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(
    page_title="Paichi Pro Hub",
    page_icon="💎",
    layout="wide"
)

# വാലറ്റ് ബാലൻസ്
if 'balance' not in st.session_state:
    st.session_state.balance = 500000.00

# 2. സൈഡ്‌ബാർ മെനു
st.sidebar.title("💎 Paichi Pro Menu")
menu = st.sidebar.radio("സേവനം തിരഞ്ഞെടുക്കുക:", 
    ["📈 Paper Trading", "📊 Nifty 50 Live", "🧮 Stock Calculator", "💰 Currency & Gold", "🤖 AI Assistant"])

# --- സെക്ഷൻ 1: PAPER TRADING (ERROR FIXED) ---
if menu == "📈 Paper Trading":
    st.header("Live Trading Dashboard")
    asset = st.selectbox("അസറ്റ് തിരഞ്ഞെടുക്കുക:", ["Crude Oil (MCX)", "Nifty 50"])
    ticker = "CL=F" if asset == "Crude Oil (MCX)" else "^NSEI"
    
    # ഡാറ്റ എടുക്കുന്നു
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    if not df.empty:
        try:
            # TypeError പരിഹരിക്കാൻ ഇവിടെ മാറ്റം വരുത്തി
            raw_price = df['Close'].iloc[-1]
            curr_p = float(raw_price.iloc[0]) if hasattr(raw_price, "__len__") else float(raw_price)
            
            if asset == "Crude Oil (MCX)": curr_p *= 91.5
            
            c1, c2 = st.columns(2)
            c1.metric("Wallet Balance", f"₹{st.session_state.balance:,.2f}")
            c2.metric(f"Live {asset} Price", f"₹{curr_p:,.2f}")
            
            col_b1, col_b2 = st.columns(2)
            if col_b1.button("🟢 BUY"): st.success(f"Bought at ₹{curr_p:,.2f}")
            if col_b2.button("🔴 SELL"): st.info(f"Sold at ₹{curr_p:,.2f}")
            
            # ചാർട്ട്
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"ഡാറ്റ ലോഡ് ചെയ്യുന്നതിൽ പ്രശ്നം: {e}")
    else:
        st.warning("നിലവിൽ മാർക്കറ്റ് ഡാറ്റ ലഭ്യമല്ല. അല്പസമയത്തിന് ശേഷം ശ്രമിക്കൂ.")

# --- സെക്ഷൻ 2: NIFTY 50 LIVE STOCKS ---
elif menu == "📊 Nifty 50 Live":
    st.header("Nifty 50 Top Stocks")
    stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS", "BHARTIARTL.NS"]
    for s in stocks:
        s_data = yf.download(s, period="1d", progress=False)
        if not s_data.empty:
            p = float(s_data['Close'].iloc[-1])
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

# --- സെക്ഷൻ 4: CURRENCY & GOLD (LIVE AED to INR) ---
elif menu == "💰 Currency & Gold":
    st.header("Live Rates")
    with st.spinner('Fetching live rates...'):
        cur = yf.download("AEDINR=X", period="1d", progress=False)
        rate = float(cur['Close'].iloc[-1]) if not cur.empty else 22.78
    
    col1, col2 = st.columns(2)
    val = col1.number_input("Enter AED:", value=1.0)
    col1.write(f"**{val} AED = ₹{val * rate:.2f} INR**")
    col1.info(f"Live Rate: 1 AED = ₹{rate:.4f}")
    col2.write("**സ്വർണ്ണവില (8g India):** ₹68,450 (Approx)")

# --- സെക്ഷൻ 5: AI ASSISTANT ---
elif menu == "🤖 AI Assistant":
    st.header("Ask Paichi AI")
    msg = st.chat_input("എന്താണ് ചോദിക്കേണ്ടത്?")
    if msg:
        st.chat_message("user").write(msg)
        st.chat_message("assistant").write(f"ഹലോ ഫൈസൽ, '{msg}' എന്നതിനെക്കുറിച്ച് കൂടുതൽ വിവരങ്ങൾ ഞാൻ തരാം!")
