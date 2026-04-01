import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

# 1. Page Config
st.set_page_config(page_title="FTB PRO - TradingView Style", layout="wide")

# Custom CSS for TradingView Look
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stSidebar { background-color: #f8f9fa; border-right: 1px solid #dee2e6; }
    [data-testid="stMetricValue"] { font-size: 20px; color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: WATCHLIST (TradingView Style) ---
st.sidebar.title("📑 Watchlist")
watchlist = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "CRUDE OIL": "CL=F",
    "RELIANCE": "RELIANCE.NS"
}
selected_stock = st.sidebar.radio("Select Asset", list(watchlist.keys()))
ticker = watchlist[selected_stock]

# --- INDICATOR LOGIC (Supertrend with Buy/Sell Signals) ---
def get_signals(df):
    high, low, close = df['High'], df['Low'], df['Close']
    # Supertrend Math
    tr = pd.concat([high-low, abs(high-close.shift()), abs(low-close.shift())], axis=1).max(axis=1)
    atr = tr.rolling(10).mean()
    hl2 = (high + low) / 2
    upper, lower = hl2 + (3 * atr), hl2 - (3 * atr)
    
    st_val = []
    current_st = True
    for i in range(len(df)):
        if close[i] > upper[i-1]: current_st = False
        elif close[i] < lower[i-1]: current_st = True
        st_val.append(lower[i] if not current_st else upper[i])
    
    df['ST'] = st_val
    df['Signal'] = np.where(close > df['ST'], 'Buy', 'Sell')
    return df

# --- MAIN TERMINAL ---
st.header(f"📊 {selected_stock} Dashboard")

try:
    df = yf.download(ticker, period="2d", interval="5m", multi_level_index=False)
    if not df.empty:
        df = get_signals(df)
        
        # Professional Chart with Buy/Sell Annotations
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price")])
        
        # Add Supertrend Line
        fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='gray', width=1, dash='dot'), name="Trend Line"))

        # Add BUY/SELL Markers (Like your TradingView screenshot)
        buy_signals = df[df['Signal'] != df['Signal'].shift(1)]
        for index, row in buy_signals.iterrows():
            color = "green" if row['Signal'] == "Buy" else "red"
            symbol = "triangle-up" if row['Signal'] == "Buy" else "triangle-down"
            text = "BUY" if row['Signal'] == "Buy" else "SELL"
            
            fig.add_annotation(x=index, y=row['Low'] if text=="BUY" else row['High'],
                               text=text, showarrow=True, arrowhead=1, 
                               bgcolor=color, font=dict(color="white"), yshift=10 if text=="SELL" else -10)

        fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Live Price Metric
        curr = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        st.metric("Current Price", f"₹ {curr:,.2f}", f"{curr-prev:.2f}")

except Exception as e:
    st.error(f"Error fetching data: {e}")
