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
    
    /* സിൽവർ സൈഡ് ബാർ */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; 
    }
    
    /* ബ്ലാക്ക് & ഗോൾഡ് ബട്ടണുകൾ */
    div[data-testid="stSidebar"] button {
        background-color: #000 !important; color: #BF953F !important;
        border: 2px solid #FFD700 !important; border-radius: 12px !important;
        height: 45px !important; font-weight: bold !important; width: 100% !important;
        margin-bottom: 5px !important;
    }
    
    /* സൈഡ് ബാറിലെ സ്പെഷ്യൽ ഓപ്പൺ ചാർട്ട് ബട്ടൺ */
    .sidebar-chart-link {
        display: block; width: 100%; padding: 12px; background: #000; color: #FFD700 !important;
        text-align: center; border-radius: 10px; text-decoration: none; font-size: 16px;
        font-weight: bold; border: 2px solid #FFD700; margin-top: 10px;
    }
    
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
    .main-title { color: #FFF; font-size: 32px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_pro_terminal_final")
FILE_NAME = 'trade_history_v2.csv'

# --- ഡാറ്റ ഫംഗ്ഷനുകൾ ---
def get_live_aed_rate():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        return res['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 25.24

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

# --- ടോപ്പ് ന്യൂസ് ടിക്കർ ---
st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 {get_live_news_malayalam()}</marquee></div>', unsafe_allow_html=True)

# --- സൈഡ് ബാർ (SLIDE BAR) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #000;'>🚀 Paichi Pro</h1>", unsafe_allow_html=True)
    
    # 💰 AED Converter
    live_aed = get_live_aed_rate()
    aed_in = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_in * live_aed:,.2f} (INR)")
    st.divider()
    
    # 📱 Navigation
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

        # ✨ സൈഡ് ബാറിലെ ചാർട്ട് ലിങ്ക്
        if 'url' in st.session_state:
            st.markdown(f'<a href="{st.session_state.url}" target="_blank" class="sidebar-chart-link">📈 OPEN {st.session_state.name}</a>', unsafe_allow_html=True)

# ഡിഫോൾട്ട് വാല്യൂസ്
if 'url' not in st.session_state: 
    st.session_state.url = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY"
    st.session_state.name = "NIFTY 50"

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.markdown(f"<p class='main-title'>{st.session_state.name} Live Analysis ⚡</p>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 60px; margin-top: 50px;'>📈</div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>വിശകലനത്തിനായി സൈഡ് ബാറിലെ ബട്ടൺ ഉപയോഗിക്കുക.</h3>", unsafe_allow_html=True)

elif mode == "JOURNAL":
    st.markdown("<p class='main-title'>📝 Trading Journal</p>", unsafe_allow_html=True)
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കാം", expanded=True):
        c1, c2 = st.columns(2)
        sym = c1.text_input("Symbol", value=st.session_state.name)
        act = c2.selectbox("Action", ["BUY", "SELL"])
        en = c1.number_input("Entry Price", min_value=0.0)
        ex = c2.number_input("Exit Price", min_value=0.0)
        q = st.number_input("Quantity", value=1, min_value=1)
        if st.button("SAVE TRADE"):
            pnl = round((ex - en) * q if act == "BUY" else (en - ex) * q, 2)
            save_trade(sym, act, en, ex, q, pnl)
            st.success(f"ട്രേഡ് സേവ് ചെയ്തു! ലാഭം/നഷ്ടം: ₹{pnl}")
            st.rerun()
    
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)

elif mode == "DASHBOARD":
    st.markdown("<p class='main-title'>📊 Performance Dashboard</p>", unsafe_allow_html=True)
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        total_pnl = df['P&L'].sum()
        col_metric, _ = st.columns([1, 2])
        col_metric.metric("Total Net P&L", f"₹{total_pnl:,.2f}")
        
        st.subheader("P&L Chart")
        st.bar_chart(df.set_index('Date')['P&L'])
    else:
        st.info("നിങ്ങൾ ഇതുവരെ ട്രേഡുകളൊന്നും രേഖപ്പെടുത്തിയിട്ടില്ല.")
