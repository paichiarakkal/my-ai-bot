import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime

# 1. Gemini AI Config
genai.configure(api_key="AIzaSyCamT29LeVv_9031swUtfXQcS3FLPemi3A")
model = genai.GenerativeModel('gemini-pro')

# 2. Page Config
st.set_page_config(page_title="FTB SUPER APP", page_icon="🚀", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h1 style='text-align: center; color: #00E676;'>🚀 FTB PRO</h1>", unsafe_allow_html=True)
page = st.sidebar.radio("MAIN MENU", ["📊 Trading Terminal", "🤖 FTB AI Assistant", "💰 Expense Manager"])

st.sidebar.divider()

# Currency Converter in Sidebar
st.sidebar.subheader("💰 Currency")
try:
    rate = yf.Ticker("AEDINR=X").history(period="1d")['Close'].iloc[-1]
    aed_input = st.sidebar.number_input("AED Amount", value=1.0)
    st.sidebar.success(f"₹ {aed_input * rate:,.2f} INR")
except: pass

# --- SMART TICKER FUNCTION ---
def get_ticker(name):
    name = name.lower().strip()
    mapping = {"nifty": "^NSEI", "bank nifty": "^NSEBANK", "crude": "CL=F", "gold": "GC=F"}
    if name in mapping: return mapping[name]
    if name.isalpha(): return f"{name.upper()}.NS"
    return name.upper()

# --- PAGE 1: TRADING TERMINAL ---
if page == "📊 Trading Terminal":
    st.markdown("<h2 style='color: #00E676;'>📈 Live Market View</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        search = st.text_input("Search (eg: Nifty, Crude)", value="Nifty")
        interval = st.selectbox("Interval", ["1m", "5m", "15m", "1h"], index=0)
    
    ticker = get_ticker(search)
    
    with col1:
        try:
            data = yf.Ticker(ticker)
            df = data.history(period="1d", interval=interval)
            if not df.empty:
                curr_p = df['Close'].iloc[-1]
                st.metric(label=f"{search.upper()} PRICE", value=f"₹ {curr_p:,.2f}")
                
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)
            else: st.warning("Valid Symbol നൽകുക (eg: ^NSEI)")
        except: st.error("Data connection slow. Please wait.")

# --- PAGE 2: AI ASSISTANT ---
elif page == "🤖 FTB AI Assistant":
    st.markdown("<h2 style='color: #00E676;'>💬 FTB Smart AI</h2>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask anything to Gemini AI..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = model.generate_content(f"You are Faisal's personal trading assistant. Answer in simple Malayalam/English: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except: st.error("AI is busy. Try again.")

# --- PAGE 3: EXPENSE MANAGER ---
elif page == "💰 Expense Manager":
    st.markdown("<h2 style='color: #00E676;'>📥 Personal Expense Tracker</h2>", unsafe_allow_html=True)
    
    with st.expander("➕ Add New Expense", expanded=True):
        col_a, col_b = st.columns(2)
        item = col_a.text_input("Item Name")
        amt = col_b.number_input("Amount", min_value=0.0)
        if st.button("Save Entry", use_container_width=True):
            st.success(f"Saved: {item} - {amt}")
            st.info("Note: This is a preview. To save long-term, we can connect a database later.")
