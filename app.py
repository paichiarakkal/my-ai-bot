import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pytz

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="FTB AI Terminal", layout="wide")

# --- സൈഡ്‌ബാറിലെ വിവരങ്ങൾ ---
st.sidebar.markdown("## 📊 FTB SETTINGS")
uae_tz = pytz.timezone('Asia/Dubai')
st.sidebar.markdown(f"🕒 **UAE Time:** {datetime.now(uae_tz).strftime('%H:%M:%S')}")

# ഇൻഡിക്കേറ്റർ കൺട്രോൾ
st.sidebar.divider()
show_st = st.sidebar.checkbox("Show SuperTrend", value=True)
chart_int = st.sidebar.selectbox("Interval", ["1m", "5m", "15m"], index=0)

# --- SuperTrend Function ---
def get_st(df, period=10, mult=3):
    hl2 = (df['High'] + df['Low']) / 2
    tr = pd.concat([df['High'] - df['Low'], abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    up, lo = hl2 + (mult * atr), hl2 - (mult * atr)
    st_line = [lo[i] if df['Close'][i] > up[i-1] else up[i] for i in range(len(df))]
    return st_line

# --- മെയിൻ ഡാഷ്‌ബോർഡ് ---
st.markdown("<h1 style='text-align: center; color: #00E676;'>📊 FTB SMART AI TERMINAL</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📈 Trading Dashboard", "💬 FTB AI Chat"])

with tab1:
    # ക്രൂഡ് ഓയിൽ ലൈവ് ഡാറ്റ
    try:
        df = yf.Ticker("CL=F").history(period="1d", interval=chart_int)
        if not df.empty:
            curr_p = df['Close'].iloc[-1]
            st.subheader(f"CRUDEOIL FUT: {curr_p:.2f}")
            
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            if show_st:
                fig.add_trace(go.Scatter(x=df.index, y=get_st(df), line=dict(color='#FFEB3B', width=2), name='SuperTrend'))
            fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Buy/Sell ബട്ടണുകൾ (നീ കാണിച്ച ഫോട്ടോയിലെ പോലെ)
            c1, c2 = st.columns(2)
            if c1.button("🟢 BUY", use_container_width=True):
                st.success(f"Buy order placed at {curr_p:.2f}")
            if c2.button("🔴 SELL", use_container_width=True):
                st.error(f"Sell order placed at {curr_p:.2f}")
    except: st.error("Data error")

with tab2:
    st.subheader("🤖 FTB AI Assistant")
    
    # ചാറ്റ് ഹിസ്റ്ററി സൂക്ഷിക്കാൻ
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("ഇവിടെ ചോദിക്കൂ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI മറുപടി (ഇവിടെ നമുക്ക് പിന്നീട് കൂടുതൽ ഡാറ്റ ചേർക്കാം)
        ai_reply = f"ഫൈസൽ, നീ ചോദിച്ച '{prompt}' എന്നതിനെപ്പറ്റി ഞാൻ നോക്കുകയാണ്. മാർക്കറ്റിൽ ഇപ്പോൾ ക്രൂഡ് ഓയിൽ ശ്രദ്ധിക്കൂ!"
        
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        with st.chat_message("assistant"):
            st.markdown(ai_reply)
