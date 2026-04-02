import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. പേജ് സെറ്റിംഗ്സ് ---
st.set_page_config(page_title="Faisal Paper Trader", page_icon="💹", layout="wide")

# --- 2. വാലറ്റ് & ട്രേഡ് സെഷൻ സെറ്റപ്പ് ---
if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50
if 'position' not in st.session_state:
    st.session_state.position = None
if 'entry_price' not in st.session_state:
    st.session_state.entry_price = 0.0

# --- 3. പരിഷ്കരിച്ച സൂപ്പർട്രെൻഡ് ഫംഗ്‌ഷൻ (ValueError ഒഴിവാക്കാൻ) ---
def get_st(df):
    df = df.copy()
    # Multi-index കളം ഉണ്ടെങ്കിൽ അത് ഒഴിവാക്കുന്നു
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # ഇൻഡക്സ് റീസെറ്റ് ചെയ്ത് സമയം കൃത്യമാക്കുന്നു
    df = df.reset_index()
    
    hl2 = (df['High'] + df['Low']) / 2
    df['tr'] = np.maximum(df['High'] - df['Low'], 
                          np.maximum(abs(df['High'] - df['Close'].shift(1)), 
                                     abs(df['Low'] - df['Close'].shift(1))))
    atr = df['tr'].rolling(7).mean()
    
    upper = hl2 + (3 * atr)
    lower = hl2 - (3 * atr)
    
    st_vals = np.zeros(len(df))
    dirs = np.ones(len(df))
    
    for i in range(1, len(df)):
        # iloc ഉപയോഗിച്ച് ഡാറ്റ കൃത്യമായി താരതമ്യം ചെയ്യുന്നു
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

# --- 4. സൈഡ്‌ബാർ ---
st.sidebar.markdown("<h2 style='color: #00FFA3;'>👤 Faisal Pro AI</h2>", unsafe_allow_html=True)
asset = st.sidebar.selectbox("Select Asset", ["Crude Oil (MCX)", "Nifty 50"])
qty = st.sidebar.number_input("Quantity", min_value=1, value=10)

if st.sidebar.button("Reset Wallet"):
    st.session_state.balance = 471435.50
    st.session_state.position = None
    st.rerun()

# --- 5. മെയിൻ ഡിസ്‌പ്ലേ ---
placeholder = st.empty()

while True:
    ticker = "CL=F" if asset == "Crude Oil (MCX)" else "^NSEI"
    # ലൈവ് ഡാറ്റ ഡൗൺലോഡ് ചെയ്യുന്നു
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    if not df.empty:
        # ക്രൂഡ് ഓയിൽ വില രൂപയിലേക്ക് മാറ്റുന്നു
        if asset == "Crude Oil (MCX)":
            df = df * 91.5
        
        try:
            df = get_st(df)
            curr_p = float(df['Close'].iloc[-1])
            trend = df['ST_DIR'].iloc[-1]
            
            with placeholder.container():
                # സ്റ്റാറ്റസ് കാർഡുകൾ
                c1, c2, c3 = st.columns(3)
                c1.metric("Wallet Balance", f"₹{st.session_state.balance:,.2f}")
                c2.metric("Market Price", f"₹{curr_p:,.2f}")
                
                if st.session_state.position:
                    pnl = (curr_p - st.session_state.entry_price) * qty
                    c3.metric("Live P&L", f"₹{pnl:,.2f}", delta=f"{pnl:,.2f}")
                    if st.button("📉 EXIT TRADE", use_container_width=True):
                        st.session_state.balance += pnl
                        st.session_state.position = None
                        st.rerun()
                else:
                    c3.metric("Status", "Waiting for Signal")
                    if st.button("🚀 PAPER BUY", use_container_width=True):
                        st.session_state.position = "LONG"
                        st.session_state.entry_price = curr_p
                        st.rerun()
                
                # AI സിഗ്നൽ ബോക്സ്
                msg, color = ("BUY SIGNAL", "#00FFA3") if trend == 1 else ("SELL SIGNAL", "#FF3131")
                st.markdown(f'<div style="border:2px solid {color}; padding:10px; border-radius:10px; text-align:center;">AI Indicator: <b style="color:{color};">{msg}</b></div>', unsafe_allow_html=True)
                
                # ചാർട്ട്
                fig = go.Figure(data=[go.Candlestick(
                    x=df['Datetime'] if 'Datetime' in df.columns else df.index,
                    open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    name="Market"
                )])
                fig.add_trace(go.Scatter(
                    x=df['Datetime'] if 'Datetime' in df.columns else df.index,
                    y=df['ST'], line=dict(color='yellow', width=2), name="Supertrend"
                ))
                fig.update_layout(template="plotly_dark", height=500, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error logic: {e}")
            
    time.sleep(30)
    st.rerun()
