import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime

# 1. Gemini AI സെറ്റപ്പ്
genai.configure(api_key="AIzaSyCamT29LeVv_9031swUtfXQcS3FLPemi3A")
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="FTB SUPER APP", page_icon="🚀", layout="wide")

# --- സൈഡ്‌ബാറിലെ വിവരങ്ങൾ ---
st.sidebar.title("🚀 FTB NAVIGATION")
page = st.sidebar.radio("Go to", ["📈 Trading Terminal", "💰 Expense & Journal", "🤖 FTB AI Chat"])

user_input = st.sidebar.text_input("Stock Symbol (eg: Nifty, Crude)", value="Nifty")

def get_ticker(name):
    name = name.lower().strip()
    mapping = {"nifty": "^NSEI", "bank nifty": "^NSEBANK", "crude": "CL=F", "gold": "GC=F"}
    if name in mapping: return mapping[name]
    return f"{name.upper()}.NS"

search_ticker = get_ticker(user_input)

# --- PAGE 1: TRADING TERMINAL ---
if page == "📈 Trading Terminal":
    st.markdown("<h1 style='color: #00E676;'>📊 LIVE TRADING VIEW</h1>", unsafe_allow_html=True)
    interval = st.select_slider("Select Timeframe", options=["1m", "5m", "15m", "1h", "1d"])
    
    try:
        df = yf.Ticker(search_ticker).history(period="1d", interval=interval)
        if not df.empty:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(height=600, template='plotly_dark', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Simple AI Analysis Button
            if st.button("AI-യോട് ഈ ചാർട്ട് വിശകലനം ചെയ്യാൻ ആവശ്യപ്പെടുക"):
                last_price = df['Close'].iloc[-1]
                st.info(f"AI വിശകലനം ചെയ്യുന്നു: {user_input} ഇപ്പോൾ ₹{last_price:.2f} നിലവാരത്തിലാണ്.")
        else: st.error("ഡാറ്റ ലഭ്യമല്ല.")
    except: st.error("കണക്ഷൻ എറർ.")

# --- PAGE 2: EXPENSE & TRADING JOURNAL ---
elif page == "💰 Expense & Journal":
    st.header("📝 Expense Tracker & Trading Journal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Daily Expenses (AED/INR)")
        exp_item = st.text_input("Item Name")
        exp_amt = st.number_input("Amount", min_value=0.0)
        if st.button("Save Expense"):
            st.success(f"സേവ് ചെയ്തു: {exp_item} - {exp_amt}")
            
    with col2:
        st.subheader("📓 Trading Journal")
        trade_note = st.text_area("ഇന്നത്തെ ട്രേഡ് വിശേഷങ്ങൾ ഇവിടെ എഴുതാം...")
        if st.button("Save Journal"):
            st.success("നിന്റെ ട്രേഡിംഗ് ഡയറി അപ്‌ഡേറ്റ് ചെയ്തു!")

# --- PAGE 3: FTB AI CHAT ---
elif page == "🤖 FTB AI Chat":
    st.header("💬 FTB AI Assistant (Powered by Gemini)")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("ചോദിക്കൂ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            full_prompt = f"Faisal is a trader in Dubai. Help him: {prompt}"
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
