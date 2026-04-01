import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import urllib.parse
import numpy as np

# 1. AI Configuration
genai.configure(api_key="AIzaSyAVpgLWVDYglDw59PPADTrNM0_AYLT66Rc")
model = genai.GenerativeModel('gemini-pro')

# 2. Page Settings
st.set_page_config(page_title="FTB PRO TRADER", page_icon="📈", layout="wide")

# Custom CSS for UI Enhancement
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stSidebar { background-color: #FFFFFF; }
    .profile-img {
        border-radius: 50%;
        width: 120px;
        height: 120px;
        object-fit: cover;
        display: block;
        margin: 0 auto;
        border: 3px solid #2563EB;
    }
    .whatsapp-btn {
        background-color: #25D366; color: white; padding: 10px;
        border-radius: 10px; text-align: center; display: block;
        text-decoration: none; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ICON & PROFILE ---
# ഇവിടെ നിന്റെ ഫോട്ടോയുടെ ലിങ്ക് നൽകാം
USER_IMAGE = "https://www.w3schools.com/howto/img_avatar.png" 
APP_ICON = "🚀"

st.sidebar.markdown(f"<h1 style='text-align: center;'>{APP_ICON} FTB PRO</h1>", unsafe_allow_html=True)
st.sidebar.markdown(f'<img src="{USER_IMAGE}" class="profile-img">', unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center;'>Faisal FTB</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: gray;'>Intraday Trader</p>", unsafe_allow_html=True)

st.sidebar.divider()

# --- CURRENCY EXCHANGE (AED TO INR) ---
st.sidebar.subheader("💰 Currency Exchange")
try:
    rate = yf.Ticker("AEDINR=X").history(period="1d")['Close'].iloc[-1]
    st.sidebar.write(f"1 AED = **₹ {rate:.2f}**")
    val = st.sidebar.number_input("AED Amount", value=1.0)
    st.sidebar.success(f"₹ {val * rate:,.2f} INR")
except:
    st.sidebar.text("Exchange Rate Unavailable")

st.sidebar.divider()

# Navigation
page = st.sidebar.radio("MENU", ["📊 Trading Terminal", "🤖 AI Advisor", "💰 P&L Tracker"])

# --- HELPERS ---
def get_st(df):
    high, low, close = df['High'], df['Low'], df['Close']
    tr = pd.concat([high-low, abs(high-close.shift()), abs(low-close.shift())], axis=1).max(axis=1)
    atr = tr.rolling(7).mean()
    hl2 = (high + low) / 2
    upper, lower = hl2 + (3 * atr), hl2 - (3 * atr)
    st_val = np.where(close > upper.shift(), lower, upper)
    df['Supertrend'] = st_val
    return df

# --- PAGE 1: TERMINAL ---
if page == "📊 Trading Terminal":
    st.title("📉 Market Terminal")
    sym = st.text_input("Symbol", "Nifty")
    ticker = "^NSEI" if sym.upper() == "NIFTY" else (f"{sym.upper()}.NS" if "." not in sym else sym.upper())
    
    df = yf.download(ticker, period="5d", interval="15m", multi_level_index=False)
    if not df.empty:
        df = get_st(df)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['Supertrend'], name="ST", line=dict(color='orange')))
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Price", f"₹{df['Close'].iloc[-1]:,.2f}")

# --- PAGE 2: AI ADVISOR ---
elif page == "🤖 AI Advisor":
    st.title("🤖 AI Trading Assistant")
    q = st.chat_input("Ask about market...")
    if q:
        res = model.generate_content(f"I am Faisal, an intraday trader. Answer in Malayalam: {q}")
        st.write(res.text)

# --- PAGE 3: P&L TRACKER ---
elif page == "💰 P&L Tracker":
    st.title("💰 Profit & Loss Journal")
    note = st.text_input("Trade Note")
    pnl = st.number_input("Amount")
    if st.button("Save"): st.success("Trade Recorded!")
