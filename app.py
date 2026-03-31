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
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pytz

# 1. ലോഗോയും പേജ് സെറ്റിംഗും
st.set_page_config(page_title="FTB PRO EXCHANGE", page_icon="📊", layout="wide")

# --- സൈഡ്‌ബാറിലെ വിവരങ്ങൾ ---
# ഒരു സ്റ്റാൻഡേർഡ് ട്രേഡിംഗ് ഐക്കൺ ലോഗോ ആയി നൽകുന്നു
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2620/2620582.png", width=120)
st.sidebar.markdown("## 📊 FTB SETTINGS")

# --- സ്മാർട്ട് സെർച്ച് ലോജിക് ---
user_input = st.sidebar.text_input("Search Stock/Index", value="Nifty")

# സെർച്ച് എളുപ്പമാക്കാനുള്ള മാപ്പിംഗ്
def get_ticker(name):
    name = name.lower().strip()
    # പ്രധാനപ്പെട്ടവ തനിയെ കൺവർട്ട് ചെയ്യും
    mapping = {
        "nifty": "^NSEI",
        "nifty 50": "^NSEI",
        "bank nifty": "^NSEBANK",
        "banknifty": "^NSEBANK",
        "crude": "CL=F",
        "crude oil": "CL=F",
        "gold": "GC=F",
        "silver": "SI=F",
        "bitcoin": "BTC-USD"
    }
    
    if name in mapping:
        return mapping[name]
    elif name.isalpha():
        # വെറും പേരാണെങ്കിൽ ഇന്ത്യൻ സ്റ്റോക്ക് ആണോ എന്ന് നോക്കും (eg: RELIANCE -> RELIANCE.NS)
        return f"{name.upper()}.NS"
    return name.upper()

search_ticker = get_ticker(user_input)
chart_int = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h"], index=0)

# --- കറൻസി കാൽക്കുലേറ്റർ ---
st.sidebar.divider()
try:
    rate = yf.Ticker("AEDINR=X").history(period="1d")['Close'].iloc[-1]
    aed = st.sidebar.number_input("AED to INR", value=1.0)
    st.sidebar.success(f"₹ {aed * rate:,.2f}")
except: pass

# --- മെയിൻ ടൈറ്റിൽ ---
st.markdown("<h1 style='color: #00E676;'>📊 FTB SMART TERMINAL</h1>", unsafe_allow_html=True)

# --- ചാർട്ട് ലോഡിംഗ് ---
try:
    data = yf.Ticker(search_ticker)
    df = data.history(period="1d", interval=chart_int)
    
    if not df.empty:
        curr_p = df['Close'].iloc[-1]
        name_display = data.info.get('shortName', user_input.upper())
        
        st.subheader(f"LIVE: {name_display} (₹ {curr_p:,.2f})")
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
        )])
        
        fig.update_layout(height=550, template='plotly_dark', xaxis_rangeslider_visible=False, yaxis=dict(side='right'))
        st.plotly_chart(fig, use_container_width=True)
        
        # Buy/Sell ബട്ടണുകൾ
        c1, c2 = st.columns(2)
        c1.button("🟢 BUY", use_container_width=True)
        c2.button("🔴 SELL", use_container_width=True)
    else:
        st.error(f"'{user_input}' എന്ന പേരിൽ സ്റ്റോക്ക് കണ്ടെത്താനായില്ല. ശരിയായ പേര് നൽകുക.")
except:
    st.error("മാർക്കറ്റ് ഡാറ്റ കണക്ഷൻ ലോസ് ആയി. ഒന്നുകൂടി ട്രൈ ചെയ്യൂ.")
