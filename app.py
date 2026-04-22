import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. Page Settings & Golden Theme
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    .stButton>button { width: 100%; border-radius: 4px; height: 2.2em; background-color: #000 !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; font-size: 14px !important; font-weight: bold; }
    .main-title { color: #FFF; font-size: 26px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .signal-box { padding: 15px; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; color: white; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_final_v2")

# --- Optimized Supertrend Function ---
def get_supertrend_simple(df, period=10, multiplier=3):
    df = df.copy()
    hl2 = (df['High'] + df['Low']) / 2
    # Simple ATR calculation
    df['tr'] = (df['High'] - df['Low'])
    df['atr'] = df['tr'].rolling(period).mean()
    
    df['upper'] = hl2 + (multiplier * df['atr'])
    df['lower'] = hl2 - (multiplier * df['atr'])
    
    # Trend Logic
    df['trend'] = True
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['upper'].iloc[i-1]:
            df.at[df.index[i], 'trend'] = True
        elif df['Close'].iloc[i] < df['lower'].iloc[i-1]:
            df.at[df.index[i], 'trend'] = False
        else:
            df.at[df.index[i], 'trend'] = df['trend'].iloc[i-1]
    return df['trend'].iloc[-1], df

def get_data(ticker):
    try:
        d = yf.download(ticker, period='1d', interval='5m')
        if d.empty: return None, 0.0
        return d, d['Close'].iloc[-1]
    except: return None, 0.0

# --- Sidebar ---
if 'sel_ticker' not in st.session_state:
    st.session_state.sel_ticker = ("CL=F", "CRUDE OIL")

with st.sidebar:
    st.markdown("### 🚀 Paichi Pro")
    st.markdown("[💬 WhatsApp](https://wa.me/918714752210)")
    st.divider()
    mode = st.radio("മെനു:", ["MARKET", "JOURNAL"])
    if mode == "MARKET":
        st.write("🎯 **Indices:**")
        if st.button("⛽ CRUDE OIL"): st.session_state.sel_ticker = ("CL=F", "CRUDE OIL"); st.rerun()
        if st.button("📈 NIFTY 50"): st.session_state.sel_ticker = ("^NSEI", "NIFTY 50"); st.rerun()
        if st.button("🏦 BANK NIFTY"): st.session_state.sel_ticker = ("^NSEBANK", "BANK NIFTY"); st.rerun()

# --- Main Content ---
if mode == "MARKET":
    symbol, name = st.session_state.sel_ticker
    hist, price = get_data(symbol)
    
    st.markdown(f'<p class="main-title">🚀 {name}</p>', unsafe_allow_html=True)
    st.metric(label="Current Price", value=f"₹ {float(price):,.2f}")

    if hist is not None and len(hist) > 10:
        trend, full_df = get_supertrend_simple(hist)
        
        if trend:
            st.markdown('<div class="signal-box" style="background-color: #28a745;">🟢 SUPERTREND: BUY</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="signal-box" style="background-color: #dc3545;">🔴 SUPERTREND: SELL</div>', unsafe_allow_html=True)
        
        st.write("### 📈 Live Chart")
        st.area_chart(full_df['Close'])
    else:
        st.error("Data loading error. Please wait...")

elif mode == "JOURNAL":
    st.markdown('<p class="main-title">📝 JOURNAL</p>', unsafe_allow_html=True)
    st.write("ഈ സെക്ഷനിൽ നിന്റെ ട്രേഡുകൾ റെക്കോർഡ് ചെയ്യാം.")
