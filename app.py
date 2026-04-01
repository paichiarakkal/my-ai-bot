import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

# 1. Page Config
st.set_page_config(page_title="FTB PRO - TradingView Clone", layout="wide")

# Custom CSS for TradingView Dark Mobile UI
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    .stSidebar { background-color: #171b26; }
    div[data-testid="stMetricValue"] { color: #00ff00; font-size: 18px; }
    .nav-item { padding: 10px; border-radius: 5px; margin-bottom: 5px; cursor: pointer; }
    .nav-item:hover { background-color: #2a2e39; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION (Bottom Nav Simulation) ---
st.sidebar.title("FTB PRO 🚀")
menu = st.sidebar.radio("Go to", ["📑 Watchlist", "📈 Chart", "🔍 Explore", "👥 Community", "👤 Profile"])

# --- DATA HELPERS ---
def get_chart(ticker):
    df = yf.download(ticker, period="2d", interval="5m", multi_level_index=False)
    # Simple Supertrend Logic
    high, low, close = df['High'], df['Low'], df['Close']
    atr = (high - low).rolling(10).mean()
    hl2 = (high + low) / 2
    df['ST'] = hl2 + (3 * atr) # Upper band simulation
    df['Signal'] = np.where(close > df['ST'].shift(), 'BUY', 'SELL')
    return df

# --- 1. WATCHLIST PAGE (43632.jpg) ---
if menu == "📑 Watchlist":
    st.header("Watchlist")
    stocks = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "CRUDE OIL": "CL=F", "ADANI PORTS": "ADANIPORTS.NS"}
    for name, sym in stocks.items():
        col1, col2 = st.columns([3, 1])
        data = yf.Ticker(sym).history(period="1d")
        price = data['Close'].iloc[-1]
        col1.markdown(f"### {name}")
        col2.metric("", f"{price:,.2f}", f"{price - data['Open'].iloc[-1]:.2f}")
        st.divider()

# --- 2. CHART PAGE (43633.jpg) ---
elif menu == "📈 Chart":
    st.header("Advanced Chart")
    target = st.selectbox("Select Asset", ["^NSEI", "CL=F", "^NSEBANK"])
    df = get_chart(target)
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    
    # Add Buy/Sell Markers
    signals = df[df['Signal'] != df['Signal'].shift(1)]
    for idx, row in signals.iterrows():
        fig.add_annotation(x=idx, y=row['Close'], text=row['Signal'], bgcolor="green" if row['Signal']=="BUY" else "red")
        
    fig.update_layout(template='plotly_dark', paper_bgcolor='#131722', plot_bgcolor='#131722', height=600)
    st.plotly_chart(fig, use_container_width=True)

# --- 3. EXPLORE PAGE (43636.jpg) ---
elif menu == "🔍 Explore":
    st.header("Global Markets")
    indices = {"S&P 500": "^GSPC", "Dow 30": "^DJI", "Nasdaq": "^IXIC"}
    cols = st.columns(3)
    for i, (name, sym) in enumerate(indices.items()):
        val = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
        cols[i].metric(name, f"{val:,.2f}", "Live")
    st.subheader("Top Stories")
    st.info("EUR/USD: Euro Chases $1.16 as Dollar Drops")
    st.warning("NIKE Stock Crashes 9% as Outlook Dims")

# --- 4. COMMUNITY PAGE (43635.jpg) ---
elif menu == "👥 Community":
    st.header("Community Ideas")
    st.markdown("""
    **@TradingShot** - *BITCOIN The 8-year Megaphone reveals Bear Cycle*
    🚀 91 | 💬 11
    """)
    st.divider()
    st.markdown("**@Path_Of_Hanzo** - *USD/JPY Analysis*")

# --- 5. PROFILE PAGE (43634.jpg) ---
elif menu == "👤 Profile":
    st.header("My Profile")
    st.subheader("Faisal FTB")
    st.text("Account: BASIC")
    col1, col2, col3 = st.columns(3)
    col1.metric("Ideas", "0")
    col2.metric("Followers", "1")
    col3.metric("Following", "0")
    st.button("Sign Out")
