import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pytz

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="FTB PRO EXCHANGE", page_icon="📈", layout="wide")

# --- സൈഡ്‌ബാറിലെ വിവരങ്ങൾ ---
st.sidebar.markdown("## 📊 FTB SETTINGS")
watchlist = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "CRUDE OIL": "CL=F"}
for name, sym in watchlist.items():
    try:
        p = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
        st.sidebar.markdown(f"**{name}**: ₹ {p:,.2f}")
    except: continue

st.sidebar.divider()
user_input = st.sidebar.text_input("Search Stock/Index", value="Nifty")

def get_ticker(name):
    name = name.lower().strip()
    mapping = {"nifty": "^NSEI", "bank nifty": "^NSEBANK", "crude": "CL=F", "gold": "GC=F"}
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
        df = yf.Ticker(search_ticker).history(period="1d", interval=chart_int)
        if not df.empty:
            curr_p = df['Close'].iloc[-1]
            st.subheader(f"LIVE: {user_input.upper()} (₹ {curr_p:,.2f})")
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False, yaxis=dict(side='right'))
            st.plotly_chart(fig, use_container_width=True)
        else: st.error("Stock not found.")
    except: st.error("Connection Error.")

# --- AI CHAT SECTION (ഇവിടെയാണ് മാറ്റം വരുത്തിയത്) ---
with tab2:
    st.subheader("🤖 FTB SMART AI")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # പഴയ മെസേജുകൾ കാണിക്കുന്നു
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # യൂസർ ടൈപ്പ് ചെയ്യുന്നത് എടുക്കുന്നു
    if prompt := st.chat_input("ഇവിടെ ചോദിക്കൂ (eg: Crude Oil അടുത്ത മൂവ്മെന്റ് എങ്ങനെയുണ്ട്?)..."):
        # യൂസർ മെസേജ് സേവ് ചെയ്യുന്നു
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI മറുപടി ഉണ്ടാക്കുന്നു
        with st.chat_message("assistant"):
            # താൽക്കാലികമായി മാർക്കറ്റ് ഡാറ്റ വെച്ച് മറുപടി നൽകുന്നു
            # പിന്നീട് നമുക്ക് ഇവിടെ Gemini API കണക്ട് ചെയ്യാം
            response = f"ഫൈസൽ, നീ ചോദിച്ച '{prompt}' എന്നതിനെപ്പറ്റി ഞാൻ നോക്കി. നിലവിൽ {user_input} മാർക്കറ്റ് ട്രെൻഡ് നോക്കുമ്പോൾ സൂക്ഷിച്ചു ട്രേഡ് ചെയ്യുന്നതാണ് നല്ലത്."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
