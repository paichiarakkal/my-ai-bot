import streamlit as st
import requests
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
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
    .sidebar-chart-button {
        display: block; width: 100%; padding: 12px; background: #000; 
        color: #FFD700 !important; text-align: center; border-radius: 12px; 
        text-decoration: none; font-size: 16px; font-weight: bold; 
        border: 2px solid #FFD700; margin-top: 10px;
    }
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_complete_v1")
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
    except: return "വാർത്തകൾ ലോഡ് ചെയ്യുന്നു..."

def save_trade(symbol, action, entry, exit_p, qty, pnl):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry, exit_p, qty, pnl]], 
                          columns=['Date', 'Symbol', 'Action', 'Entry', 'Exit', 'Qty', 'P&L'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- ന്യൂസ് ടിക്കർ ---
st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 {get_live_news_malayalam()}</marquee></div>', unsafe_allow_html=True)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #000;'>🚀 Paichi Pro</h2>", unsafe_allow_html=True)
    live_aed = get_live_aed_rate()
    aed_in = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_in * live_aed:,.2f} (INR)")
    st.divider()
    
    mode = st.radio("Menu:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    
    if mode == "MARKET":
        if st.button("📊 NIFTY 50"): 
            st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY", "NIFTY 50"
        if st.button("🏦 BANK NIFTY"): 
            st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY", "BANK NIFTY"
        if st.button("🛢️ CRUDE OIL"): 
            st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=MCX:CRUDEOIL1!", "CRUDE OIL"
        
        if 'url' in st.session_state:
            st.markdown(f'<a href="{st.session_state.url}" target="_blank" class="sidebar-chart-button">📈 OPEN {st.session_state.name}</a>', unsafe_allow_html=True)

if 'url' not in st.session_state: st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY", "NIFTY 50"

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.header(f"📈 {st.session_state.name} Terminal")
    st.info("ചാർട്ട് കാണാൻ സൈഡ് ബാറിലെ 'OPEN' ബട്ടൺ അമർത്തുക.")

elif mode == "JOURNAL":
    st.header("📝 Trading Journal")
    with st.expander("Add New Trade"):
        c1, c2 = st.columns(2)
        sym = c1.text_input("Symbol", value=st.session_state.name)
        act = c2.selectbox("Type", ["BUY", "SELL"])
        en = c1.number_input("Entry")
        ex = c2.number_input("Exit")
        q = st.number_input("Qty", value=1)
        if st.button("Save Trade"):
            pnl = (ex - en) * q if act == "BUY" else (en - ex) * q
            save_trade(sym, act, en, ex, q, pnl)
            st.success(f"സേവ് ചെയ്തു! P&L: ₹{pnl}")
    
    if os.path.isfile(FILE_NAME):
        st.dataframe(pd.read_csv(FILE_NAME), use_container_width=True)

elif mode == "DASHBOARD":
    st.header("📊 Performance Dashboard")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.metric("Total P&L", f"₹{df['P&L'].sum():,.2f}")
        st.bar_chart(df.set_index('Date')['P&L'])
    else: st.warning("ട്രേഡ് ഹിസ്റ്ററി ലഭ്യമല്ല.")
