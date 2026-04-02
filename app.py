import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

st.set_page_config(page_title="Faisal Paper Trader", layout="wide")

if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50
if 'position' not in st.session_state:
    st.session_state.position = None

def get_st(df):
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    hl2 = (df['High'] + df['Low']) / 2
    df['tr'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    atr = df['tr'].rolling(7).mean()
    upper = (hl2 + (3 * atr)).to_numpy()
    lower = (hl2 - (3 * atr)).to_numpy()
    close = df['Close'].to_numpy()
    st_vals = np.zeros(len(df))
    dirs = np.ones(len(df))
    for i in range(1, len(df)):
        if close[i] > upper[i-1]: dirs[i] = 1
        elif close[i] < lower[i-1]: dirs[i] = -1
        else: dirs[i] = dirs[i-1]
        st_vals[i] = lower[i] if dirs[i] == 1 else upper[i]
    df['ST'] = st_vals
    df['ST_DIR'] = dirs
    return df

st.sidebar.header("👤 Faisal Pro AI")
asset = st.sidebar.selectbox("Asset", ["Crude Oil (MCX)", "Nifty 50"])

placeholder = st.empty()
while True:
    ticker = "CL=F" if asset == "Crude Oil (MCX)" else "^NSEI"
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    if not df.empty:
        if asset == "Crude Oil (MCX)": df = df * 91.5
        try:
            df = get_st(df)
            curr_p = float(df['Close'].iloc[-1])
            with placeholder.container():
                c1, c2 = st.columns(2)
                c1.metric("Wallet", f"₹{st.session_state.balance:,.2f}")
                c2.metric("Price", f"₹{curr_p:,.2f}")
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='yellow')))
                fig.update_layout(template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e: st.error(f"Error: {e}")
    time.sleep(30)
