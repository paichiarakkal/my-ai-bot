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
    /* ഗോൾഡൻ തീം */
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
        margin-bottom: 8px !important;
    }

    /* സൈഡ് ബാറിലെ ആ വലിയ ഓപ്പൺ ചാർട്ട് ബട്ടൺ */
    .sidebar-chart-button {
        display: block; width: 100%; padding: 15px 5px; background: #000; 
        color: #FFD700 !important; text-align: center; border-radius: 12px; 
        text-decoration: none; font-size: 18px; font-weight: bold; 
        border: 3px solid #FFD700; margin-top: 15px; transition: 0.3s;
    }
    .sidebar-chart-button:hover { background: #BF953F; color: #000 !important; }
    
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
    .main-title { color: #FFF; font-size: 26px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_sidebar_final")

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

# --- സൈഡ് ബാർ (Slide Bar) സെക്ഷൻ ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #000;'>🚀 Paichi Pro</h2>", unsafe_allow_html=True)
    
    # കറൻസി കൺവെർട്ടർ
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
        # ✨ ദാ ഇതാണ് നീ ചോദിച്ച സ്ലൈഡ് ബാറിലെ ചാർട്ട് ബട്ടൺ
        if 'url' in st.session_state:
            st.markdown(f'<a href="{st.session_state.url}" target="_blank" class="sidebar-chart-button">📈 OPEN {st.session_state.name}</a>', unsafe_allow_html=True)

# ഡിഫോൾട്ട് സെറ്റിംഗ്സ്
if 'url' not in st.session_state: 
    st.session_state.url = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY"
    st.session_state.name = "NIFTY 50"

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.markdown(f"<p class='main-title'>{st.session_state.name} Terminal ⚡</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.2); padding: 40px; border-radius: 20px; text-align: center; border: 1px solid rgba(0,0,0,0.1);">
        <h2 style="color: #000;">{st.session_state.name} വിശകലനം ചെയ്യാൻ തയ്യാറാണോ?</h2>
        <p style="color: #333; font-size: 18px;">സൈഡ് ബാറിലെ <b>'OPEN'</b> ബട്ടൺ അമർത്തുക. <br>അപ്പോൾ പുതിയ ടാബിൽ ചാർട്ട് പക്കാ ആയി തെളിയും.</p>
        <div style="font-size: 50px;">📈</div>
    </div>
    """, unsafe_allow_html=True)

elif mode == "JOURNAL":
    st.subheader("📝 Trading Journal")
    st.write("നിന്റെ ട്രേഡുകൾ ഇവിടെ രേഖപ്പെടുത്താം.")

elif mode == "DASHBOARD":
    st.subheader("📊 Performance")
    st.write("നിന്റെ ലാഭവിവരങ്ങൾ ഇവിടെ കാണാം.")
