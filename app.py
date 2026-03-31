import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai

# 1. Gemini AI Config
genai.configure(api_key="AIzaSyCanT29LeVv_9031swUtfXQcS3FLPemi3A")
model = genai.GenerativeModel('gemini-pro')

# 2. Page Config for Premium Look
st.set_page_config(page_title="FTB PRO", page_icon="📈", layout="wide")

# Custom CSS for Professional UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    .stSidebar { background-color: #0d1117; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h1 style='text-align: center; color: #00E676;'>🚀 FTB PRO</h1>", unsafe_allow_html=True)
page = st.sidebar.radio("NAVIGATION", ["📊 Trading Terminal", "🤖 FTB AI Assistant", "💰 Expense Manager"])

st.sidebar.divider()

# Currency Converter with Corrected Logic
st.sidebar.subheader("💰 Currency Converter")
try:
    # AED to INR rate fetch
    rate_data = yf.Ticker("AEDINR=X").history(period="1d")
    if not rate_data.empty:
        rate = rate_data['Close'].iloc[-1]
        aed_input = st.sidebar.number_input("Enter AED", value=1.0, step=1.0)
        st.sidebar.success(f"₹ {aed_input * rate:,.2f} INR")
    else:
        st.sidebar.info("Updating rates...")
except:
    st.sidebar.error("Service unavailable")

# --- SMART TICKER FUNCTION ---
def get_ticker(name):
    mapping = {"nifty": "^NSEI", "bank nifty": "^NSEBANK", "crude": "CL=F", "gold": "GC=F"}
    name = name.lower().strip()
    return mapping.get(name, f"{name.upper()}.NS")

# --- PAGE 1: TRADING TERMINAL ---
if page == "📊 Trading Terminal":
    st.markdown("<h2 style='color: #00E676;'>📉 Live Market View</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col2:
        search = st.text_input("Search (Nifty, Crude, etc.)", value="Nifty")
        interval = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"])
    ticker_sym = get_ticker(search)
    with col1:
        try:
            df = yf.download(ticker_sym, period="1d", interval=interval)
            if not df.empty:
                curr_p = df['Close'].iloc[-1]
                st.metric(label=f"{search.upper()} PRICE", value=f"₹ {curr_p:,.2f}")
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Data error")

# --- PAGE 2: AI ASSISTANT ---
elif page == "🤖 FTB AI Assistant":
    st.markdown("<h2 style='color: #00E676;'>🤖 FTB Smart AI</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if prompt := st.chat_input("Ask Faisal's AI..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            response = model.generate_content(f"Answer in Malayalam: {prompt}")
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# --- PAGE 3: EXPENSE MANAGER ---
elif page == "💰 Expense Manager":
    st.markdown("<h2 style='color: #00E676;'>📥 Expense Tracker</h2>", unsafe_allow_html=True)
    item = st.text_input("Item")
    amt = st.number_input("Amount", min_value=0.0)
    if st.button("Save"): st.success(f"Saved: {item} - ₹{amt}")
