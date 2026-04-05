import streamlit as st
import requests
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    
    /* സിൽവർ സൈഡ് ബാർ */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; 
    }
    
    /* സൈഡ് ബാർ ബട്ടണുകൾ */
    div[data-testid="stSidebar"] button {
        background-color: #000 !important; color: #BF953F !important;
        border: 2px solid #FFD700 !important; border-radius: 12px !important;
        height: 45px !important; font-weight: bold !important; width: 100% !important;
        margin-bottom: 5px !important;
    }

    /* സ്ലൈഡ് ബാറിലെ സ്പെഷ്യൽ ചാർട്ട് ലിങ്ക് */
    .sidebar-chart-link {
        display: block; width: 100%; padding: 12px; background: #000; color: #FFD700 !important;
        text-align: center; border-radius: 10px; text-decoration: none; font-size: 16px;
        font-weight: bold; border: 2px solid #FFD700; margin-top: 10px;
    }
    
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
    .main-title { color: #FFF; font-size: 26px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_sidebar_stable")

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

# --- ന്യൂസ് ടിക്കർ ---
st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 {get_live_news_malayalam()}</marquee></div>', unsafe_allow_html=True)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #000;'>🚀 Paichi Pro</h2>", unsafe_allow_html=True)
    
    # കൺവെർട്ടർ
    live_aed = get_live_aed_rate()
    aed_in = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_in * live_aed:,.2f} (INR)")
    st.divider()
    
    mode = st.radio("Menu:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    
    if mode == "MARKET":
        st.subheader("🎯 Select Symbol")
        if st.button("📊 NIFTY 50"): 
            st.session_state.url = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY"
            st.session_state.name = "NIFTY 50"
        if st.button("🏦 BANK NIFTY"): 
            st.session_state.url = "https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY"
            st.session_state.name = "BANK NIFTY"
        if st.button("🛢️ CRUDE OIL"): 
            st.session_state.url = "https://in.tradingview.com/chart/?symbol=MCX:CRUDEOIL1!"
            st.session_state.name = "CRUDE OIL"

        st.divider()
        # സ്ലൈഡ് ബാറിൽ ചാർട്ട് ബട്ടൺ വരുന്നു
        st.markdown(f'<a href="{st.session_state.url}" target="_blank" class="sidebar-chart-link">📈 OPEN {st.session_state.name}</a>', unsafe_allow_html=True)

# സെഷൻ സ്റ്റേറ്റ് സെറ്റിംഗ്സ്
if 'url' not in st.session_state: 
    st.session_state.url = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY"
    st.session_state.name = "NIFTY 50"

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.markdown(f"<p class='main-title'>{st.session_state.name} Terminal</p>", unsafe_allow_html=True)
    st.info("നിനക്ക് വേണ്ട Symbol സൈഡ് ബാറിൽ നിന്ന് തിരഞ്ഞെടുക്കാം. അതിനുശേഷം 'OPEN' ബട്ടൺ അമർത്തുക.")
    
    # മെയിൻ സ്ക്രീനിലും ഒരു വലിയ ബട്ടൺ വേണമെങ്കിൽ:
    st.markdown(f"""
    <div style="background: rgba(0,0,0,0.1); padding: 30px; border-radius: 15px; text-align: center;">
        <h3>{st.session_state.name} ചാർട്ട് കാണാൻ താഴെ അമർത്തുക</h3>
        <a href="{st.session_state.url}" target="_blank" style="text-decoration: none;">
            <button style="background: #000; color: #FFD700; padding: 15px 30px; border: 2px solid #FFD700; border-radius: 10px; cursor: pointer; font-weight: bold;">
                CLICK TO ANALYZE 📈
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

elif mode == "JOURNAL":
    st.subheader("📝 Trading Journal")
    st.write("ട്രേഡുകൾ ഇവിടെ സേവ് ചെയ്യാം.")

elif mode == "DASHBOARD":
    st.subheader("📊 Performance")
    st.write("നിന്റെ പ്രകടനം ഇവിടെ കാണാം.")
