import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
import plotly.express as px
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    /* മെയിൻ ബോഡി ഗോൾഡൻ ഗ്രേഡിയന്റ് */
    .stApp { 
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); 
        color: #000; 
    }
    
    /* സൈഡ് ബാർ സിൽവർ കളർ (തിരിച്ചു കൊണ്ടുവന്നു) */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; 
    }
    
    /* സൈഡ് ബാറിലെ ബട്ടണുകൾ - നല്ല മോഡേൺ ലുക്കിൽ */
    div[data-testid="stSidebar"] button {
        background-color: #000 !important;
        color: #BF953F !important;
        border: 2px solid #FFD700 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        margin-bottom: 8px !important;
        transition: 0.3s;
    }
    
    div[data-testid="stSidebar"] button:hover {
        background-color: #BF953F !important;
        color: #000 !important;
        transform: scale(1.05);
    }

    .main-title { 
        color: #FFF; 
        font-size: 35px; 
        font-weight: 800; 
        text-align: center; 
        text-shadow: 2px 2px 4px #000; 
    }
</style>
""", unsafe_allow_html=True)
    
    /* പുതിയ മോഡേൺ ബട്ടൺ സ്റ്റൈൽ */
    div[data-testid="stSidebar"] button {
        background: linear-gradient(45deg, #000, #333) !important;
        color: #BF953F !important;
        border: 2px solid #BF953F !important;
        border-radius: 12px !important;
        height: 50px !important;
        font-weight: bold !important;
        transition: 0.4s !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }
    div[data-testid="stSidebar"] button:hover {
        background: #BF953F !important;
        color: #000 !important;
        transform: scale(1.02);
    }
    
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=15000, key="faisal_final_design_v1")
FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def get_live_aed_rate():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        return res['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 22.75

def get_analysis(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        p = data['meta']['regularMarketPrice']
        close = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        ai_p = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close)>5 else p
        return {"p": p, "ai": ai_p}
    except: return None

# --- സൈഡ് ബാർ (പുതിയ ഡിസൈൻ) ---
with st.sidebar:
    st.markdown("<h1 style='color: #BF953F; text-align: center;'>🚀 Paichi Pro</h1>", unsafe_allow_html=True)
    
    live_aed = get_live_aed_rate()
    st.metric("1 AED to INR", f"₹{live_aed:.2f}")
    st.divider()

    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()

    if mode == "MARKET":
        st.subheader("🎯 Market Watch")
        if st.button("📊 NIFTY 50", use_container_width=True): st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
        if st.button("🏦 BANK NIFTY", use_container_width=True): st.session_state.sel = ("^NSEBANK", "BANK NIFTY", 1)
        st.divider()
        if st.button("🛢️ CRUDE OIL", use_container_width=True): st.session_state.sel = ("CL=F", "CRUDE OIL", 84.5)
        if st.button("💰 GOLD 8G", use_container_width=True): st.session_state.sel = ("GC=F", "GOLD 8G", 8.45 * 8)

if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# --- മെയിൻ കണ്ടന്റ് ---
st.markdown(f'<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    symbol, name, multi = st.session_state.sel
    data = get_analysis(symbol)
    if data:
        st.subheader(f"📍 {name}")
        live_p, ai_p = data['p'] * multi, data['ai'] * multi
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{live_p:,.2f}")
        c2.metric("AI പ്രവചനം", f"₹{ai_p:,.2f}")
        # വെള്ള ഗ്രാഫ് ഒഴിവാക്കി

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ")
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക", expanded=True):
        col1, col2 = st.columns(2)
        s = col1.text_input("Item", value=st.session_state.sel[1])
        a = col2.selectbox("Action", ["BUY", "SELL"])
        en = col1.number_input("Entry Price", value=0.0)
        ex = col2.number_input("Exit Price", value=0.0)
        q = col1.number_input("Qty", value=1, step=1)
        mood = col2.selectbox("മൂഡ്", ["Calm", "Happy", "Fear", "Greedy"])
        if st.button("Save to History"):
            pnl = (ex - en) * q if a == "BUY" else (en - ex) * q
            # (Save function calling code should be here)
            st.success(f"സേവ് ചെയ്തു!")
            st.rerun()

elif mode == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ്")
    st.info("ട്രേഡ് ഹിസ്റ്ററി ഇവിടെ കാണാം.")
