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

# --- 1. പേജ് സെറ്റിംഗ്സ് (സൈഡ് ബാർ എപ്പോഴും കാണാൻ expanded ആക്കി) ---
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide", initial_sidebar_state="expanded")

# നിനക്ക് താല്പര്യമില്ലാത്ത എല്ലാം നീക്കം ചെയ്യാനുള്ള അൾട്ടിമേറ്റ് CSS
st.markdown("""
<style>
    /* ഗോൾഡൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    
    /* സൈഡ് ബാർ തിരികെ കൊണ്ടുവരാൻ */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; visibility: visible !important; width: 250px !important; }
    div[data-testid="stSidebar"] button { width: 100%; background-color: #000 !important; color: #BF953F !important; border: 1px solid #FFD700 !important; margin-bottom: 5px; font-weight: bold; }
    
    /* മുകളിലെ Fork, GitHub ഐക്കണുകൾ നീക്കാൻ */
    header, [data-testid="stHeader"] { display: none !important; }
    
    /* താഴെയുള്ള Created by, Hosted with, ചുവപ്പ് ലോഗോ എന്നിവ നീക്കാൻ */
    footer { visibility: hidden !important; display: none !important; }
    .stDeployButton { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    
    /* മൊബൈലിലെ മറ്റ് അനാവശ്യ ചിഹ്നങ്ങൾ (വയലറ്റ്/ചുവപ്പ് ഐക്കണുകൾ) */
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .st-emotion-cache-zq5wmm, .st-emotion-cache-15zrgzn {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* ടൈറ്റിൽ & ന്യൂസ് ബോക്സ് */
    .main-title { color: #FFF; font-size: 30px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; margin-top: -50px; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ഓട്ടോ റിഫ്രഷ്
st_autorefresh(interval=15000, key="faisal_sidebar_ultimate_v2")

FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---

def get_live_aed_rate():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        return res['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 22.75

def get_live_news_malayalam():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Crude%20Oil,Gold&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_list = [item['title'] for item in res['news']]
        return translate("  |  ".join(news_list), "ml", "en")
    except: return "വാർത്തകൾ അപ്‌ഡേറ്റ് ചെയ്യുന്നു..."

def get_analysis(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        p = data['meta']['regularMarketPrice']
        close = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        ai_p = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close)>5 else p
        return {"p": p, "ai": ai_p}
    except: return None

# --- 2. മലയാളം ലൈവ് വാർത്തകൾ ---
news_mal = get_live_news_malayalam()
st.markdown(f'<div class="news-box"><marquee scrollamount="5" style="color:#FFF;font-weight:bold;">📢 {news_mal}</marquee></div>', unsafe_allow_html=True)

# --- 3. സൈഡ് ബാർ (Sidebar Fixed) ---
with st.sidebar:
    st.title("🚀 Paichi Pro")
    live_aed = get_live_aed_rate()
    st.subheader("💰 Live Currency")
    aed_in = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_in * live_aed:.2f} (INR)") #
    st.divider()
    mode = st.radio("മെനു:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    if mode == "MARKET":
        if st.button("📈 NIFTY 50"): st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
        if st.button("🏦 BANK NIFTY"): st.session_state.sel = ("^NSEBANK", "BANK NIFTY", 1)
        if st.button("🛢️ CRUDE OIL MCX"): st.session_state.sel = ("CL=F", "CRUDE OIL MCX", 93.5)
        if st.button("💰 GOLD 8G"): st.session_state.sel = ("GC=F", "GOLD 8G", 84.5 * 8)

if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# --- 4. മെയിൻ കണ്ടന്റ് ---
st.markdown(f'<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    symbol, name, multi = st.session_state.sel
    data = get_analysis(symbol)
    if data:
        st.subheader(f"📍 {name}")
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{data['p']*multi:.2f}") #
        c2.metric("AI പ്രവചനം", f"₹{data['ai']*multi:.2f}")
        st.line_chart(pd.DataFrame({"Price": [data['p']*multi]*10}))
    else: st.error("ഇന്റർനെറ്റ് കണക്ഷൻ പരിശോധിക്കുക.")

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ")
    # പഴയ ജേണൽ കോഡ് ഇവിടെ വരും...

elif mode == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ്")
    # പഴയ ഡാഷ്ബോർഡ് കോഡ് ഇവിടെ വരും...
