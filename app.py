import streamlit as st
import requests
import pandas as pd
import datetime
import os
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    /* ഗോൾഡൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    
    /* സിൽവർ സൈഡ് ബാർ */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; 
    }
    
    /* ബ്ലാക്ക് & ഗോൾഡ് ബട്ടണുകൾ */
    div[data-testid="stSidebar"] button {
        background-color: #000 !important; color: #BF953F !important;
        border: 2px solid #FFD700 !important; border-radius: 12px !important;
        height: 45px !important; font-weight: bold !important; width: 100% !important;
    }
    
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
    .main-title { color: #FFF; font-size: 26px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    
    /* സ്പെഷ്യൽ ചാർട്ട് ബട്ടൺ */
    .chart-link {
        display: block; width: 100%; padding: 20px; background: #000; color: #FFD700;
        text-align: center; border-radius: 15px; text-decoration: none; font-size: 20px;
        font-weight: bold; border: 3px solid #FFD700; margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_stable_final")

# --- ഡാറ്റ ഫംഗ്ഷനുകൾ ---
def get_live_aed_rate():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        return res['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 22.75

def get_live_news_malayalam():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Crude%20Oil&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_list = [item['title'] for item in res['news']]
        return translate("  |  ".join(news_list), "ml", "en")
    except: return "വാർത്തകൾ ലോഡ് ചെയ്യുന്നു..."

# --- ടോപ്പ് ടിക്കർ ---
st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 {get_live_news_malayalam()}</marquee></div>', unsafe_allow_html=True)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #000;'>🚀 Paichi Pro</h1>", unsafe_allow_html=True)
    live_aed = get_live_aed_rate()
    aed_in = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_in * live_aed:,.2f} (INR)")
    
    st.divider()
    mode = st.radio("Menu:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    
    if mode == "MARKET":
        if st.button("📊 NIFTY 50"): 
            st.session_state.url = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY"
            st.session_state.name = "NIFTY 50"
        if st.button("🏦 BANK NIFTY"): 
            st.session_state.url = "https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY"
            st.session_state.name = "BANK NIFTY"
        if st.button("🛢️ CRUDE OIL"): 
            st.session_state.url = "https://in.tradingview.com/chart/?symbol=MCX:CRUDEOIL1!"
            st.session_state.name = "CRUDE OIL"

if 'url' not in st.session_state: 
    st.session_state.url = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY"
    st.session_state.name = "NIFTY 50"

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.markdown(f"<p class='main-title'>{st.session_state.name} Live Terminal</p>", unsafe_allow_html=True)
    
    st.write("പഴയതുപോലെ എറർ വരാതിരിക്കാൻ താഴെ കാണുന്ന ബട്ടൺ അമർത്തുക. ചാർട്ട് പക്കാ ആയി തെളിയും. 👇")
    
    # സ്പെഷ്യൽ ലിങ്ക് ബട്ടൺ
    st.markdown(f'<a href="{st.session_state.url}" target="_blank" class="chart-link">📈 OPEN {st.session_state.name} CHART</a>', unsafe_allow_html=True)
    
    st.info("ഈ ബട്ടൺ അമർത്തിയാൽ ചാർട്ട് പുതിയ വിൻഡോയിൽ ലോഡ് ആകും. അവിടെ നിനക്ക് എല്ലാ ഇൻഡിക്കേറ്ററുകളും ഒരു തടസ്സവുമില്ലാതെ ഉപയോഗിക്കാം.")

elif mode == "JOURNAL":
    st.subheader("📝 Trading Journal")
    st.info("നിന്റെ ട്രേഡുകൾ ഇവിടെ റെക്കോർഡ് ചെയ്യാം.")

elif mode == "DASHBOARD":
    st.subheader("📊 Performance")
    st.info("നിന്റെ ലാഭവും നഷ്ടവും ഇവിടെ കാണാം.")
