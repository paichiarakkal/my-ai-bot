import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
import numpy as np
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    .stButton>button { width: 100%; border-radius: 4px; height: 2.2em; background-color: #000 !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; font-size: 14px !important; font-weight: bold; margin-bottom: 2px; }
    .main-title { color: #FFF; font-size: 26px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .info-box { background-color: #f8f9fa; padding: 10px; border-radius: 8px; color: #333; font-weight: bold; text-align: center; border: 1px solid #ddd; font-size: 14px; margin-bottom: 5px; }
    .buy-signal { background-color: #228B22; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; }
    .sell-signal { background-color: #B22222; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_supertrend_v1")
FILE_NAME = 'trade_history_v2.csv'

# --- സൂപ്പർട്രെൻഡ് ഫംഗ്ഷൻ (No extra libraries needed) ---
def get_supertrend(df, period=10, multiplier=3):
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # ATR കണക്കാക്കുന്നു
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    hl2 = (high + low) / 2
    final_upperband = hl2 + (multiplier * atr)
    final_lowerband = hl2 - (multiplier * atr)
    
    supertrend = [True] * len(df)
    for i in range(1, len(df)):
        if close[i] > final_upperband[i-1]:
            supertrend[i] = True
        elif close[i] < final_lowerband[i-1]:
            supertrend[i] = False
        else:
            supertrend[i] = supertrend[i-1]
            
    return supertrend, final_upperband, final_lowerband

def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1], data
    except: return 0.0, None

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'sel_ticker' not in st.session_state:
    st.session_state.sel_ticker = ("CL=F", "CRUDE OIL")

# --- 2. സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("### 🚀 Paichi Pro")
    st.markdown("[💬 Contact on WhatsApp](https://wa.me/918714752210)")
    
    st.divider()
    st.write("🔔 **Premium Alert**")
    alert_val = st.number_input("Alert Price", value=0.0)
    
    mode = st.radio("മെനു:", ["MARKET", "JOURNAL", "DASHBOARD"])
    
    if mode == "MARKET":
        st.write("🎯 **Indices:**")
        if st.button("⛽ CRUDE OIL"): st.session_state.sel_ticker = ("CL=F", "CRUDE OIL"); st.rerun()
        if st.button("📈 NIFTY 50"): st.session_state.sel_ticker = ("^NSEI", "NIFTY 50"); st.rerun()
        if st.button("🏦 BANK NIFTY"): st.session_state.sel_ticker = ("^NSEBANK", "BANK NIFTY"); st.rerun()

# --- 3. മെയിൻ കണ്ടന്റ് ---
if mode == "MARKET":
    symbol, name = st.session_state.sel_ticker
    price, hist_data = get_live_price(symbol)
    
    st.markdown(f'<p class="main-title">🚀 {name}</p>', unsafe_allow_html=True)
    st.metric(label=name, value=f"₹ {price:,.2f}")

    # സൂപ്പർട്രെൻഡ് അനാലിസിസ്
    if hist_data is not None and len(hist_data) > 15:
        st_trend, upper, lower = get_supertrend(hist_data)
        current_trend = st_trend[-1]
        
        if current_trend:
            st.markdown('<div class="buy-signal">🟢 SUPERTREND: BUY (Bullish)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sell-signal">🔴 SUPERTREND: SELL (Bearish)</div>', unsafe_allow_html=True)

        st.write("### 📈 Live Chart")
        st.line_chart(hist_data['Close'])
    else:
        st.warning("ഡാറ്റ ലോഡ് ആകുന്നു... ദയവായി കാത്തിരിക്കൂ.")

elif mode == "JOURNAL":
    st.markdown('<p class="main-title">📝 JOURNAL</p>', unsafe_allow_html=True)
    # പഴയ ജേണൽ കോഡ് ഇവിടെ വരും...
    st.info("നിന്റെ ട്രേഡുകൾ ഇവിടെ സേവ് ചെയ്യാം.")

st.markdown(f'<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
