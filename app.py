import streamlit as st
import requests
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

st_autorefresh(interval=30000, key="faisal_final_upstox_style")
FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
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
    except: return "വാർത്തകൾ അപ്‌ഡേറ്റ് ചെയ്യുന്നു..."

# --- ന്യൂസ് ടിക്കർ ---
st.markdown(f'<div class="news-ticker"><marquee>📢 {get_live_news_malayalam()}</marquee></div>', unsafe_allow_html=True)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #000;'>🚀 Paichi Pro</h2>", unsafe_allow_html=True)
    live_aed = get_live_aed_rate()
    aed_in = st.number_input("AED", value=1.0)
    st.success(f"₹ {aed_in * live_aed:,.2f} (INR)")
    st.divider()
    mode = st.radio("Menu:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    if mode == "MARKET":
        if st.button("📊 NIFTY 50"): st.session_state.chart_url = "https://kitecharts.zerodha.com/charts/NIFTY50"
        if st.button("🏦 BANK NIFTY"): st.session_state.chart_url = "https://kitecharts.zerodha.com/charts/BANKNIFTY"
        if st.button("🛢️ CRUDE OIL"): st.session_state.chart_url = "https://kitecharts.zerodha.com/charts/CRUDEOIL"

if 'chart_url' not in st.session_state: st.session_state.chart_url = "https://s.tradingview.com/widgetembed/?symbol=NSE:NIFTY&interval=5&theme=dark"

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    # ഈ ഐഫ്രെയിം രീതി ഉപയോഗിച്ചാൽ ബ്ലോക്ക് ആവാതെ ചാർട്ട് വരാൻ സാധ്യത കൂടുതലാണ്
    components.iframe(st.session_state.chart_url, height=600, scrolling=True)

elif mode == "JOURNAL":
    st.subheader("📝 Trading Journal")
    # പഴയ ജേണൽ കോഡ് ഇവിടെ...
    if os.path.isfile(FILE_NAME): st.dataframe(pd.read_csv(FILE_NAME))

elif mode == "DASHBOARD":
    st.subheader("📊 Performance")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.metric("Total Profit", f"₹{df['P&L'].sum()}")
