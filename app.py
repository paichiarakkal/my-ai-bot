import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
import plotly.express as px
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button {
        background-color: #000 !important; color: #BF953F !important;
        border: 2px solid #FFD700 !important; border-radius: 12px !important;
        height: 45px !important; font-weight: bold !important; width: 100% !important;
    }
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_final_fix_v4")

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

# --- ന്യൂസ് ടിക്കർ ---
st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 വാർത്തകൾ: {get_live_news_malayalam()}</marquee></div>', unsafe_allow_html=True)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #000;'>🚀 Paichi Pro</h1>", unsafe_allow_html=True)
    live_aed = get_live_aed_rate()
    aed_input = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_input * live_aed:,.2f} (INR)")
    st.divider()
    mode = st.radio("മെനു:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    
    if mode == "MARKET":
        if st.button("📊 NIFTY 50"): st.session_state.tv_sym = "NIFTY"
        if st.button("🏦 BANK NIFTY"): st.session_state.tv_sym = "BANKNIFTY"
        if st.button("🛢️ CRUDE OIL"): st.session_state.tv_sym = "FX:USOIL" 
        if st.button("💰 GOLD"): st.session_state.tv_sym = "OANDA:XAUUSD"

if 'tv_sym' not in st.session_state: st.session_state.tv_sym = "NIFTY"

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    # ⚠️ ഇവിടെയാണ് മാറ്റം! NSE സിംബലുകൾ വരാൻ "exchange" ഒഴിവാക്കി നോക്കുന്നു.
    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:600px;">
      <div id="tradingview_pro"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%",
        "height": 600,
        "symbol": "{st.session_state.tv_sym}",
        "interval": "5",
        "timezone": "Asia/Kolkata",
        "theme": "dark",
        "style": "1",
        "locale": "in",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_pro"
      }});
      </script>
    </div>
    """
    components.html(tradingview_html, height=620)
    st.info("നിഫ്റ്റി കാണുന്നില്ലെങ്കിൽ ചാർട്ടിലെ സെർച്ച് ബോക്സിൽ 'NIFTY' എന്ന് ടൈപ്പ് ചെയ്ത് NSE തിരഞ്ഞെടുക്കുക.")

elif mode == "JOURNAL":
    st.subheader("📝 Trading Journal")
    st.info("നിന്റെ ട്രേഡുകൾ ഇവിടെ സേവ് ചെയ്യാം.")

elif mode == "DASHBOARD":
    st.subheader("📊 Performance Dashboard")
