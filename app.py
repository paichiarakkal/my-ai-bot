import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    
    /* ബട്ടണുകളുടെ വലിപ്പം കുറയ്ക്കാനുള്ള സ്റ്റൈൽ */
    .stButton>button { 
        width: 100%; 
        border-radius: 4px; 
        height: 2.2em; /* വലിപ്പം കുറച്ചു */
        background-color: #000 !important; 
        color: #FFD700 !important; 
        border: 1px solid #FFD700 !important; 
        font-size: 14px !important; /* അക്ഷരങ്ങൾ ചെറുതാക്കി */
        font-weight: bold; 
        margin-bottom: 2px; 
    }
    .main-title { color: #FFF; font-size: 24px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .conv-box { background-color: #d1e7dd; padding: 10px; border-radius: 8px; color: #0f5132; font-weight: bold; text-align: center; border: 1px solid #badbcc; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_sidebar_v4")
FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'sel_ticker' not in st.session_state:
    st.session_state.sel_ticker = ("^NSEI", "NIFTY 50")

# --- 2. സൈഡ് ബാർ (വലിപ്പം കുറഞ്ഞ ബട്ടണുകൾ) ---
with st.sidebar:
    st.markdown("### 🚀 Paichi Pro")
    
    # Currency Converter (AED to INR)
    st.write("AED (Dirham)")
    aed_amount = st.number_input("", min_value=0.0, value=1.0, step=1.0, key="aed_val")
    ex_rate = get_live_price("AEDINR=X")
    if ex_rate > 0:
        inr_val = aed_amount * ex_rate
        st.markdown(f'<div class="conv-box">₹ {inr_val:,.2f} (INR)</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # പ്രധാന മെനു മാത്രം
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()

    if mode == "MARKET":
        st.write("🎯 **ഇൻഡക്സ് തിരഞ്ഞെടുക്കുക:**")
        # ചെറിയ ബട്ടണുകൾ
        if st.button("📈 NIFTY 50"): st.session_state.sel_ticker = ("^NSEI", "NIFTY 50"); st.rerun()
        if st.button("🏦 BANK NIFTY"): st.session_state.sel_ticker = ("^NSEBANK", "BANK NIFTY"); st.rerun()
        if st.button("💳 FIN NIFTY"): st.session_state.sel_ticker = ("NIFTY_FIN_SERVICE.NS", "FIN NIFTY"); st.rerun()
        if st.button("📊 SENSEX"): st.session_state.sel_ticker = ("^BSESN", "SENSEX"); st.rerun()
        if st.button("⛽ CRUDE OIL"): st.session_state.sel_ticker = ("CL=F", "CRUDE OIL"); st.rerun()
        if st.button("📉 MIDCAP"): st.session_state.sel_ticker = ("^NSEMDCP50", "MIDCAP 50"); st.rerun()

# --- 3. മെയിൻ കണ്ടന്റ് ---
if mode == "MARKET":
    st.markdown(f'<p class="main-title">🚀 {st.session_state.sel_ticker[1]}</p>', unsafe_allow_html=True)
    symbol, name = st.session_state.sel_ticker
    current_p = get_live_price(symbol)
    if current_p > 0:
        st.write(f"### ലൈവ് വില")
        st.metric(label=name, value=f"₹ {current_p:,.2f}")
    else: st.error("Data Fetching...")

elif mode == "JOURNAL":
    st.markdown(f'<p class="main-title">📝 TRADING JOURNAL</p>', unsafe_allow_html=True)
    # ജേണൽ എൻട്രി കോഡ് (പഴയത് പോലെ തന്നെ)
    st.info("ട്രേഡുകൾ ഇവിടെ നൽകാം.")

elif mode == "DASHBOARD":
    st.markdown(f'<p class="main-title">📊 DASHBOARD</p>', unsafe_allow_html=True)
    # ഡാഷ്ബോർഡ് ഹിസ്റ്ററി
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.dataframe(df)
    else:
        st.warning("ഡാറ്റ ലഭ്യമല്ല.")

st.markdown(f'<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
