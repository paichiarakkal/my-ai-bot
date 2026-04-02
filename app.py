import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- പേജ് സെറ്റിംഗ്സ് ---
st.set_page_config(page_title="Faisal Paper Trader", layout="wide")

# --- ബാലൻസ് സെറ്റപ്പ് ---
if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50
if 'position' not in st.session_state:
    st.session_state.position = None
if 'entry_price' not in st.session_state:
    st.session_state.entry_price = 0.0

# --- പരിഷ്കരിച്ച സൂപ്പർട്രെൻഡ് ഫംഗ്‌ഷൻ (No ValueError) ---
def get_st(df):
    # ലേബലുകൾ ക്ലീൻ ചെയ്യുന്നു
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    hl2 = (df['High'] + df['Low']) / 2
    # ട്രൂ റേഞ്ച് കണക്കാക്കുന്നു
    df['tr'] = np.maximum(df['High'] - df['Low'], 
                          np.maximum(abs(df['High'] - df['Close'].shift(1)), 
                                     abs(df['Low'] - df['Close'].shift(1))))
    atr = df['tr'].rolling(7).mean()
    
    upper = hl2 + (3 * atr)
    lower = hl2 - (3 * atr)
    
    st_vals = np.zeros(len(df))
    dirs = np.ones(len(df))
    
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upper.iloc[i-1]:
            dirs[i] = 1
        elif df['Close'].iloc[i] < lower.iloc[i-1]:
            dirs[i] = -1
        else:
            dirs[i] = dirs[i-1]
            
        if dirs[i] == 1:
            st_vals[i] = lower.iloc[i]
        else:
            st_vals[i] = upper.iloc[i]
            
    df['ST'] = st_vals
    df['ST_DIR'] = dirs
    return df

# --- സൈഡ്‌ബാർ ---
st.sidebar.header("👤 Faisal Pro AI")
asset = st.sidebar.selectbox("Asset", ["Crude Oil (MCX)", "Nifty 50"])
if st.sidebar.button("Reset Wallet"):
    st.session_state.balance = 471435.50
    st.session_state.position = None

# --- മെയിൻ ആപ്പ് ---
placeholder = st.empty()
while True:
    ticker = "CL=F" if asset == "Crude Oil (MCX)" else "^NSEI"
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    if not df.empty:
        if asset == "Crude Oil (MCX)":
            df = df * 91.5
        
        try:
            df = get_st(df)
            curr_p = float(df['Close'].iloc[-1])
            trend = df['ST_DIR'].iloc[-1]
            
            with placeholder.container():
                c1, c2, c3 = st.columns(3)
                c1.metric("Wallet", f"₹{st.session_state.balance:,.2f}")
                c2.metric("Price", f"₹{curr_p:,.2f}")
                
                if st.session_state.position:
                    pnl = (curr_p - st.session_state.entry_price) * 10
                    c3.metric("Live P&L", f"₹{pnl:,.2f}", delta=f"{pnl:,.2f}")
                    if st.button("📉 EXIT TRADE", use_container_width=True):
                        st.session_state.balance += pnl
                        st.session_state.position = None
                        st.rerun()
                else:
                    c3.metric("Status", "No Trade")
                    if st.button("🚀 PAPER BUY", use_container_width=True):
                        st.session_state.position = "LONG"
                        st.session_state.entry_price = curr_p
                        st.rerun()
                
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='yellow'), name="Supertrend"))
                fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
            
    time.sleep(30)
