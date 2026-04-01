import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. Page Settings (Mobile Friendly)
st.set_page_config(page_title="FTB PRO TERMINAL", layout="wide")

# Dark Theme CSS
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    .stSidebar { background-color: #171b26; border-right: 1px solid #2a2e39; }
    div[data-testid="stMetricValue"] { color: #2962ff; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ALL STOCKS & INDICES ---
st.sidebar.title("📑 Watchlist")

# Nifty 50 പ്രധാന സ്റ്റോക്കുകളുടെ ലിസ്റ്റ്
nifty50_stocks = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "ICICI BANK": "ICICIBANK.NS",
    "INFY": "INFY.NS",
    "SBIN": "SBIN.NS",
    "ADANI PORTS": "ADANIPORTS.NS",
    "CRUDE OIL": "CL=F"
}

selected_name = st.sidebar.selectbox("Select Asset", list(nifty50_stocks.keys()))
ticker = nifty50_stocks[selected_name]

# Timeframe Selection
interval = st.sidebar.select_slider("Timeframe", options=["1m", "5m", "15m", "1h", "1d"], value="5m")

# --- MAIN CHART LOGIC ---
st.header(f"📈 {selected_name} Live Chart")

try:
    # Fetching Data
    df = yf.download(ticker, period="2d", interval=interval, multi_level_index=False)
    
    if not df.empty:
        # Professional Candlestick Chart
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price"
        )])

        # Update Chart Layout to match TradingView Style
        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=600,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='#131722',
            plot_bgcolor='#131722'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Current Stats
        c1, c2 = st.columns(2)
        curr_price = df['Close'].iloc[-1]
        change = curr_price - df['Open'].iloc[0]
        c1.metric("Live Price", f"₹ {curr_price:,.2f}", f"{change:.2f}")
        c2.info(f"Market: {'OPEN' if not df.empty else 'CLOSED'}")

except Exception as e:
    st.error(f"Error loading {selected_name}. Please try a different timeframe.")

st.sidebar.divider()
st.sidebar.caption("FTB PRO - Advanced Trading Terminal")
