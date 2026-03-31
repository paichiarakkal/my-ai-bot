import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import os

# 1. Gemini AI Config
genai.configure(api_key="AIzaSyCanT29LeVv_9031swUtfXQcS3FLPemi3A")
model = genai.GenerativeModel('gemini-pro')

# 2. Page Config
st.set_page_config(page_title="FTB SUPER APP", page_icon="🚀", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h1 style='text-align: center; color: #00E676;'>🚀 FTB PRO</h1>", unsafe_allow_html=True)
page = st.sidebar.radio("MAIN MENU", ["📊 Trading Terminal", "🤖 FTB AI Assistant", "💰 Expense Manager"])

st.sidebar.divider()

# Currency Converter in Sidebar
st.sidebar.subheader("💰 Currency Converter")
try:
    rate_data = yf.download("AEDINR=X", period="1d", interval="1m")
    if not rate_data.empty:
        rate = rate_data['Close'].iloc[-1]
        aed_input = st.sidebar.number_input("Enter AED", value=1.0)
        st.sidebar.success(f"₹ {aed_input * rate:,.2f} INR")
    else:
        st.sidebar.info("Updating rates...")
except Exception as e:
    st.sidebar.error("Currency rates unavailable")

# --- SMART TICKER FUNCTION ---
def get_ticker(name):
    name = name.lower().strip()
    mapping = {
        "nifty": "^NSEI",
        "bank nifty": "^NSEBANK",
        "crude": "CL=F",
        "crude oil": "CL=F",
        "gold": "GC=F"
    }
    if name in mapping:
        return mapping[name]
    if name.isalpha():
        return f"{name.upper()}.NS"
    return name.upper()

# --- PAGE 1: TRADING TERMINAL ---
if page == "📊 Trading Terminal":
    st.markdown("<h2 style='color: #00E676;'>📉 Live Market View</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        search = st.text_input("Search (eg: Nifty, Crude)", value="Nifty")
        interval = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"], index=0)
    
    ticker_sym = get_ticker(search)
    
    with col1:
        try:
            stock = yf.Ticker(ticker_sym)
            df = stock.history(period="1d", interval=interval)
            
            if not df.empty:
                curr_p = df['Close'].iloc[-1]
                st.metric(label=f"{search.upper()} LIVE PRICE", value=f"₹ {curr_p:,.2f}")
                
                fig = go.Figure(data=[go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close']
                )])
                fig.update_layout(height=550, template='plotly_dark', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"'{search}' എന്നതിന് ഡാറ്റ ലഭ്യമല്ല. ശരിയായ സിംബൽ നൽകുക.")
        except:
            st.error("Market data load ചെയ്യാൻ കഴിയുന്നില്ല. ഇന്റർനെറ്റ് ചെക്ക് ചെയ്യൂ.")

# --- PAGE 2: AI ASSISTANT ---
elif page == "🤖 FTB AI Assistant":
    st.markdown("<h2 style='color: #00E676;'>🤖 FTB Smart AI</h2>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Ask anything to Gemini AI..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            try:
                response = model.generate_content(f"You are Faisal's personal trading assistant. Answer in simple Malayalam: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except:
                st.error("AI is busy. Try again.")

# --- PAGE 3: EXPENSE MANAGER ---
elif page == "💰 Expense Manager":
    st.markdown("<h2 style='color: #00E676;'>📥 Personal Expense Tracker</h2>", unsafe_allow_html=True)
    
    with st.expander("➕ Add New Expense", expanded=True):
        col_a, col_b = st.columns(2)
        item = col_a.text_input("Item Name")
        amt = col_b.number_input("Amount", min_value=0.0)
        if st.button("Save Entry", use_container_width=True):
            st.success(f"Saved: {item} - ₹{amt}")
            st.info("Note: This is a preview. To save long-term, we can connect a database later.")
# --- PAGE 3: EXPENSE MANAGER ---
elif page == "💰 Expense Manager":
    st.markdown("<h2 style='color: #00E676;'>📥 Daily Expense Tracker</h2>", unsafe_allow_html=True)
    
    with st.expander("➕ Add New Entry", expanded=True):
        col_a, col_b = st.columns(2)
        item = col_a.text_input("Item/Reason")
        amt = col_b.number_input("Amount (AED/INR)", min_value=0.0)
        if st.button("Save Entry", use_container_width=True):
            st.success(f"സേവ് ചെയ്തു: {item} - {amt}")
            st.info("ഇത് താൽക്കാലികമാണ്. ഡാറ്റാബേസ് കണക്ട് ചെയ്താൽ കൂടുതൽ കാലം സൂക്ഷിക്കാം.")
