import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import urllib.parse
import numpy as np

# AI Config
genai.configure(api_key="AIzaSyAVpgLWVDYglDw59PPADTrNM0_AYLT66Rc")
model = genai.GenerativeModel('gemini-pro')

# Page Settings
st.set_page_config(page_title="FTB PRO TRADER", page_icon="🚀", layout="wide")

# Custom CSS for Professional Design
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    div[data-testid="stMetric"] { 
        background-color: #FFFFFF; border-radius: 12px; padding: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #2563EB;
    }
    .profile-img {
        border-radius: 50%; width: 120px; height: 120px;
        object-fit: cover; display: block; margin: 0 auto;
        border: 3px solid #2563EB;
    }
    </style>
    """, unsafe_allow_html=True)

# Supertrend Calculation without extra library
def calculate_st(df):
    high, low, close = df['High'], df['Low'], df['Close']
    tr = pd.concat([high-low, abs(high-close.shift()), abs(low-close.shift())], axis=1).max(axis=1)
    atr = tr.rolling(7).mean()
    hl2 = (high + low) / 2
    upper = hl2 + (3 * atr)
    lower = hl2 - (3 * atr)
    st_val = np.where(close > upper.shift(), lower, upper)
    df['Supertrend'] = st_val
    return df

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='text-align: center;'>🚀 FTB PRO</h1>", unsafe_allow_html=True)
# Profile Image (Example link)
st.sidebar.markdown('<img src="https://www.w3schools.com/howto/img_avatar.png" class="profile-img">', unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center;'>Faisal FTB</h3>", unsafe_allow_html=True)

st.sidebar.divider()

# Currency Exchange
st.sidebar.subheader("💰 Currency")
try:
    rate = yf.Ticker("AEDINR=X").history(period="1d")['Close'].iloc[-1]
    st.sidebar.write(f"1 AED = **₹ {rate:.2f}**")
except: st.sidebar.text("Exchange Offline")

st.sidebar.divider()
page = st.sidebar.radio("MENU", ["📊 Terminal", "🤖 AI Advisor", "💰 P&L"])

# --- PAGES ---
if page == "📊 Terminal":
    st.title("📉 Market Terminal")
    sym = st.text_input("Symbol", "Nifty")
    ticker = "^NSEI" if sym.upper() == "NIFTY" else (f"{sym.upper()}.NS" if "." not in sym else sym.upper())
    
    df = yf.download(ticker, period="5d", interval="15m", multi_level_index=False)
    if not df.empty:
        df = calculate_st(df)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['Supertrend'], name="Supertrend", line=dict(color='orange')))
        st.plotly_chart(fig, use_container_width=True)
        st.metric(f"Price ({sym})", f"₹{df['Close'].iloc[-1]:,.2f}")

elif page == "🤖 AI Advisor":
    st.title("🤖 AI Assistant")
    q = st.chat_input("Ask something...")
    if q:
        res = model.generate_content(f"Answer in Malayalam: {q}")
        st.write(res.text)

elif page == "💰 P&L":
    st.title("💰 Profit & Loss")
    st.success("Trade recording ready!")
