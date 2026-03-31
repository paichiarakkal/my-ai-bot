import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import urllib.parse

# 1. Gemini AI Config
genai.configure(api_key="AIzaSyCanT29LeVv_9031swUtfXQcS3FLPemi3A")
model = genai.GenerativeModel('gemini-pro')

# 2. Page Config
st.set_page_config(page_title="FTB PRO TRADER", page_icon="📈", layout="wide")

# Custom CSS for Light Professional Theme
st.markdown("""
    <style>
    .main { background-color: #F0F2F6; color: #1F2937; } 
    div[data-testid="stMetric"] { 
        background-color: #FFFFFF; 
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #E5E7EB;
    }
    .stSidebar { background-color: #FFFFFF; border-right: 1px solid #E5E7EB; }
    .whatsapp-btn {
        background-color: #25D366;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        display: block;
        text-align: center;
        font-weight: bold;
        text-decoration: none;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h1 style='text-align: center; color: #2563EB;'>🚀 FTB PRO</h1>", unsafe_allow_html=True)
page = st.sidebar.radio("MENU", ["📊 Trading Terminal", "🤖 FTB AI Assistant", "💰 Expense Manager"])

st.sidebar.divider()

# Currency Converter
st.sidebar.subheader("💰 Currency Converter")
try:
    rate_data = yf.Ticker("AEDINR=X").history(period="1d")
    if not rate_data.empty:
        rate = rate_data['Close'].iloc[-1]
        aed_input = st.sidebar.number_input("Enter AED", value=1.0, step=1.0)
        st.sidebar.success(f"₹ {aed_input * rate:,.2f} INR")
except:
    st.sidebar.error("Rates offline")

# --- SMART TICKER FUNCTION ---
def get_ticker(name):
    mapping = {"nifty": "^NSEI", "bank nifty": "^NSEBANK", "crude": "CL=F", "gold": "GC=F"}
    name = name.lower().strip()
    return mapping.get(name, f"{name.upper()}.NS")

# --- PAGE 1: TRADING TERMINAL ---
if page == "📊 Trading Terminal":
    st.markdown("<h2 style='color: #2563EB;'>📉 Live Market View</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col2:
        search = st.text_input("Symbol", value="Nifty")
        interval = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"], index=1)
        ma_period = st.slider("MA Period", 5, 50, 20)
        app_url = "https://upqvdh.streamlit.app"
        share_text = f"FTB Analysis for {search}: {app_url}"
        whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📲 Share on WhatsApp</a>', unsafe_allow_html=True)
    ticker_sym = get_ticker(search)
    with col1:
        try:
            df = yf.download(ticker_sym, period="5d", interval=interval, multi_level_index=False)
            if not df.empty:
                df['MA'] = df['Close'].rolling(window=ma_period).mean()
                curr_p = df['Close'].iloc[-1]
                if curr_p > df['MA'].iloc[-1]:
                    st.sidebar.success("🚀 SIGNAL: BUY")
                else:
                    st.sidebar.error("🔻 SIGNAL: SELL")
                st.metric(label=f"{search.upper()} PRICE", value=f"₹ {curr_p:,.2f}")
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
                fig.add_trace(go.Scatter(x=df.index, y=df['MA'], line=dict(color='#2563EB', width=1.5), name=f"MA {ma_period}"))
                fig.update_layout(height=550, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Data error")

# --- PAGE 2: AI ASSISTANT ---
elif page == "🤖 FTB AI Assistant":
    st.markdown("<h2 style='color: #2563EB;'>🤖 AI Support</h2>", unsafe_allow_html=True)
    prompt = st.chat_input("Ask Faisal's AI...")
    if prompt:
        with st.chat_message("assistant"):
            response = model.generate_content(f"Answer in Malayalam: {prompt}")
            st.write(response.text)

# --- PAGE 3: EXPENSE MANAGER ---
elif page == "💰 Expense Manager":
    st.markdown("<h2 style='color: #2563EB;'>📥 Expense Tracker</h2>", unsafe_allow_html=True)
    item = st.text_input("Item Name")
    amt = st.number_input("Amount", min_value=0.0)
    if st.button("Save"):
        st.success(f"Saved: {item} - ₹{amt}")
