import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pytz

# 1. പേജ് സെറ്റിംഗ്സ് & ലോഗോ സെറ്റപ്പ്
LOGO_URL = "https://i.ibb.co/v4m0YmX/FTB-Logo.png"

st.set_page_config(
    page_title="FTB PRO EXCHANGE",
    page_icon=LOGO_URL,
    layout="wide"
)

# --- ലോഗോയും മെയിൻ ടൈറ്റിലും ---
col_logo, col_title = st.columns([0.1, 0.9])
with col_logo:
    st.image(LOGO_URL, width=70)
with col_title:
    st.markdown("<h1 style='color: #00E676; margin-top: -10px;'>FTB SMART TERMINAL</h1>", unsafe_allow_html=True)

# --- SIDEBAR: MARKET WATCH & TOOLS ---
st.sidebar.image(LOGO_URL, width=120)
st.sidebar.markdown("## 🏛️ MARKET WATCH")

# വാച്ച്‌ലിസ്റ്റ് (Live Prices in Sidebar)
watchlist = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "CRUDE OIL": "CL=F",
    "RELIANCE": "RELIANCE.NS",
    "GOLD": "GC=F"
}

for name, sym in watchlist.items():
    try:
        p_data = yf.Ticker(sym).history(period="1d")
        price = p_data['Close'].iloc[-1]
        change = price - p_data['Open'].iloc[-1]
        color = "#00E676" if change > 0 else "#FF5252"
        st.sidebar.markdown(f"**{name}**: <span style='color:{color};'>₹ {price:,.2f}</span>", unsafe_allow_html=True)
    except: continue

st.sidebar.divider()

# കറൻസി കാൽക്കുലേറ്റർ (AED to INR)
st.sidebar.markdown("### 💰 CURRENCY CONVERTER")
try:
    rate = yf.Ticker("AEDINR=X").history(period="1d")['Close'].iloc[-1]
    aed_val = st.sidebar.number_input("Enter AED", value=1000.0, step=100.0)
    st.sidebar.success(f"{aed_val} AED = **₹ {aed_val * rate:,.2f}**")
except: st.sidebar.text("Rates unavailable")

st.sidebar.divider()

# സെർച്ച് സെക്ഷൻ
search_ticker = st.sidebar.text_input("Search Stock/Index", value="CL=F")
chart_int = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h"], index=0)
show_st = st.sidebar.checkbox("Show SuperTrend", value=True)

# --- FUNCTIONS ---
def get_st(df, period=10, mult=3):
    hl2 = (df['High'] + df['Low']) / 2
    tr = pd.concat([df['High'] - df['Low'], abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    up, lo = hl2 + (mult * atr), hl2 - (mult * atr)
    return [lo[i] if df['Close'][i] > up[i-1] else up[i] for i in range(len(df))]

# --- MAIN DASHBOARD TABS ---
tab1, tab2 = st.tabs(["📊 EXCHANGE VIEW", "💬 FTB AI CHAT"])

with tab1:
    col_main, col_info = st.columns([3, 1])
    
    with col_main:
        try:
            # ഡാറ്റ ലോഡിംഗ്
            df = yf.Ticker(search_ticker).history(period="1d", interval=chart_int)
            if not df.empty:
                curr_p = df['Close'].iloc[-1]
                st.subheader(f"LIVE: {search_ticker} - {curr_p:,.2f}")
                
                # ചാർട്ട് നിർമ്മാണം
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                if show_st:
                    fig.add_trace(go.Scatter(x=df.index, y=get_st(df), line=dict(color='#FFEB3B', width=1.5), name='ST'))
                
                fig.update_layout(height=550, template='plotly_dark', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0), yaxis=dict(side='right'))
                st.plotly_chart(fig, use_container_width=True)
                
                # BUY/SELL ബട്ടണുകൾ
                btn1, btn2 = st.columns(2)
                if btn1.button("🟢 BUY", use_container_width=True): st.success(f"Buy Placed at {curr_p:.2f}")
                if btn2.button("🔴 SELL", use_container_width=True): st.error(f"Sell Placed at {curr_p:.2f}")
            else: st.warning("Please enter a valid symbol (e.g., ^NSEI, RELIANCE.NS)")
        except: st.error("Connection Error. Try again.")

    with col_info:
        st.markdown("### 📑 Market Depth")
        st.caption("Auto-refreshing live orders...")
        st.divider()
        st.markdown("### 🔔 Alerts")
        st.info(f"Watching {search_ticker} for breakout")

with tab2:
    st.subheader("🤖 FTB AI Assistant")
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("ഇവിടെ ചോദിക്കൂ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        reply = f"ഫൈസൽ, {search_ticker} ചാർട്ട് പ്രകാരം മാർക്കറ്റ് ഇപ്പോൾ ശ്രദ്ധിക്കണം! {prompt} എന്നതിനെപ്പറ്റി ഞാൻ നോക്കാം."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"): st.markdown(reply)
