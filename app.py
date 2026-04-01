import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

# 1. Page Config (Mobile Optimization)
st.set_page_config(page_title="FTB PRO - Mobile", layout="wide")

# Custom CSS for TradingView Dark Mobile UI
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    .stSidebar { background-color: #171b26; border-right: 1px solid #2a2e39; }
    .stMetric { background-color: #1e222d; border-radius: 10px; padding: 10px; }
    /* Bottom Navigation Simulation */
    .nav-bar {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #171b26; display: flex; justify-content: space-around;
        padding: 10px; border-top: 1px solid #2a2e39; z-index: 100;
    }
    .nav-item { color: #848e9c; font-size: 12px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- APP DATA & LOGIC ---
watchlist_symbols = {
    "NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", 
    "CRUDE OIL": "CL=F", "RELIANCE": "RELIANCE.NS", "ADANI PORTS": "ADANIPORTS.NS"
}

def get_st_signals(df):
    high, low, close = df['High'], df['Low'], df['Close']
    tr = pd.concat([high-low, abs(high-close.shift()), abs(low-close.shift())], axis=1).max(axis=1)
    atr = tr.rolling(10).mean()
    hl2 = (high + low) / 2
    upper, lower = hl2 + (3 * atr), hl2 - (3 * atr)
    st_val = []
    curr = True
    for i in range(len(df)):
        if close[i] > upper[i-1]: curr = False
        elif close[i] < lower[i-1]: curr = True
        st_val.append(lower[i] if not curr else upper[i])
    df['ST'] = st_val
    df['Signal'] = np.where(close > df['ST'], 'BUY', 'SELL')
    return df

# --- SIDEBAR: WATCHLIST ---
st.sidebar.title("📑 Watchlist")
for name, sym in watchlist_symbols.items():
    try:
        data = yf.Ticker(sym).history(period="1d")
        price = data['Close'].iloc[-1]
        change = ((price - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100
        color = "#00ff00" if change >= 0 else "#ff0000"
        st.sidebar.markdown(f"**{name}**: <span style='color:{color}'>{price:,.2f} ({change:.2f}%)</span>", unsafe_allow_html=True)
    except: pass

selected = st.sidebar.selectbox("Select Target", list(watchlist_symbols.keys()))

# --- MAIN INTERFACE ---
st.markdown(f"### {selected} Chart")

try:
    df = yf.download(watchlist_symbols[selected], period="1d", interval="5m", multi_level_index=False)
    if not df.empty:
        df = get_st_signals(df)
        
        # Dark Theme Chart
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1, dash='dot')))
        
        # Buy/Sell Labels
        signals = df[df['Signal'] != df['Signal'].shift(1)]
        for idx, row in signals.iterrows():
            st.write() # Spacer
            fig.add_annotation(x=idx, y=row['Close'], text=row['Signal'], 
                               bgcolor="green" if row['Signal']=="BUY" else "red",
                               font=dict(color="white"), showarrow=False)

        fig.update_layout(template='plotly_dark', paper_bgcolor='#131722', plot_bgcolor='#131722', 
                          xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

except:
    st.error("Connection lost.")

# --- BOTTOM NAV SIMULATION ---
st.markdown("""
    <div class="nav-bar">
        <div class="nav-item">📊<br>Watchlist</div>
        <div class="nav-item" style="color:#2962ff">📈<br>Chart</div>
        <div class="nav-item">🌍<br>Explore</div>
        <div class="nav-item">👤<br>Menu</div>
    </div>
    """, unsafe_allow_html=True)
