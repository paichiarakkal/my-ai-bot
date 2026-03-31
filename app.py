import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pytz

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="FTB PRO EXCHANGE", page_icon="📊", layout="wide")

# --- സൈഡ്‌ബാറിലെ വിവരങ്ങൾ ---
st.sidebar.markdown("## 📊 FTB SETTINGS")

# വാച്ച്‌ലിസ്റ്റ്
watchlist = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "CRUDE OIL": "CL=F"}
for name, sym in watchlist.items():
    try:
        p = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
        st.sidebar.markdown(f"**{name}**: ₹ {p:,.2f}")
    except: continue

st.sidebar.divider()

# കറൻസി കാൽക്കുലേറ്റർ
st.sidebar.markdown("### 💰 AED to INR")
try:
    rate = yf.Ticker("AEDINR=X").history(period="1d")['Close'].iloc[-1]
    aed = st.sidebar.number_input("Enter AED", value=1.0)
    st.sidebar.success(f"₹ {aed * rate:,.2f}")
except: pass

st.sidebar.divider()

# സ്മാർട്ട് സെർച്ച്
user_input = st.sidebar.text_input("Search Stock/Index", value="Nifty")

def get_ticker(name):
    name = name.lower().strip()
    mapping = {
        "nifty": "^NSEI", "bank nifty": "^NSEBANK",
        "crude": "CL=F", "crude oil": "CL=F",
        "gold": "GC=F", "reliance": "RELIANCE.NS"
    }
    if name in mapping: return mapping[name]
    if name.isalpha(): return f"{name.upper()}.NS"
    return name.upper()

search_ticker = get_ticker(user_input)
chart_int = st.sidebar.selectbox("Interval", ["1m", "5m", "15m"], index=0)

# --- മെയിൻ ടൈറ്റിൽ ---
st.markdown("<h1 style='color: #00E676;'>📊 FTB SMART TERMINAL</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 EXCHANGE VIEW", "💬 FTB AI CHAT"])

with tab1:
    try:
        data = yf.Ticker(search_ticker)
        df = data.history(period="1d", interval=chart_int)
        if not df.empty:
            curr_p = df['Close'].iloc[-1]
            st.subheader(f"LIVE: {user_input.upper()} (₹ {curr_p:,.2f})")
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False, yaxis=dict(side='right'))
            st.plotly_chart(fig, use_container_width=True)
            c1, c2 = st.columns(2)
            c1.button("🟢 BUY", use_container_width=True)
            c2.button("🔴 SELL", use_container_width=True)
        else:
            st.error("സ്റ്റോക്ക് കണ്ടെത്താനായില്ല.")
    except: st.error("Data error.")

with tab2:
    st.subheader("🤖 FTB AI Assistant")
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if prompt := st.chat_input("ഇവിടെ ചോദിക്കൂ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        reply = f"ഫൈസൽ, {user_input} ചാർട്ട് ഇപ്പോൾ നോക്കാം."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"): st.markdown(reply)
