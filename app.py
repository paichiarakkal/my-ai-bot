import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page Config
st.set_page_config(page_title="FTB ULTIMATE TERMINAL", layout="wide")

# Custom CSS for Dark Pro UI
st.markdown("""
    <style>
    .main { background-color: #0c0d10; color: white; }
    .stSidebar { background-color: #131722; border-right: 1px solid #2a2e39; }
    </style>
    """, unsafe_allow_html=True)

# --- INDICATOR CALCULATIONS ---
def add_indicators(df):
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Moving Average (SMA 20)
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # Supertrend
    high, low, close = df['High'], df['Low'], df['Close']
    atr = (high - low).rolling(10).mean()
    hl2 = (high + low) / 2
    df['ST_Upper'] = hl2 + (3 * atr)
    df['ST_Lower'] = hl2 - (3 * atr)
    return df

# --- SIDEBAR: SEARCH & WATCHLIST ---
st.sidebar.title("🔍 Search & Watchlist")
search_symbol = st.sidebar.text_input("Enter Symbol (eg: SBIN, TATAMOTORS)", "^NSEI")

st.sidebar.subheader("Quick Links")
quick_list = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "CRUDE OIL": "CL=F", "GOLD": "GC=F"}
selected_quick = st.sidebar.selectbox("Indices/Global", list(quick_list.keys()))

# --- MAIN DASHBOARD ---
ticker = search_symbol if search_symbol != "^NSEI" else quick_list[selected_quick]
if not ticker.endswith(".NS") and ticker not in ["CL=F", "GC=F", "^NSEI", "^NSEBANK"]:
    ticker = ticker.upper() + ".NS"

try:
    df = yf.download(ticker, period="5d", interval="15m", multi_level_index=False)
    if not df.empty:
        df = add_indicators(df)
        
        # Subplots: Price Chart & RSI
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        
        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        
        # Add SMA & Supertrend
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA 20", line=dict(color='yellow', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['ST_Upper'], name="ST Upper", line=dict(color='red', width=1, dash='dash')), row=1, col=1)
        
        # Add RSI
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='purple')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        fig.update_layout(template='plotly_dark', height=800, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Live Stats
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Price", f"₹ {df['Close'].iloc[-1]:,.2f}")
        c2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
        status = "BUY" if df['Close'].iloc[-1] > df['SMA20'].iloc[-1] else "SELL"
        c3.info(f"Trend Status: {status}")

except Exception as e:
    st.error(f"Symbol not found. Please try again.")
