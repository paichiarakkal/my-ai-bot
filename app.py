import streamlit as st
import requests
import pandas as pd
import datetime
import os
import plotly.express as px
import streamlit.components.v1 as components
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
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
    .main-title { color: #FFF; font-size: 28px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_final_stable_v1")
FILE_NAME = 'trade_history_v2.csv'

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

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

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
        if st.button("📊 NIFTY 50"): st.session_state.sym = "NSE:NIFTY"
        if st.button("🏦 BANK NIFTY"): st.session_state.sym = "NSE:BANKNIFTY"
        if st.button("🛢️ CRUDE OIL"): st.session_state.sym = "MCX:CRUDEOIL1!"

if 'sym' not in st.session_state: st.session_state.sym = "NSE:NIFTY"

# --- മെയിൻ ബോഡി ---
st.markdown(f"<p class='main-title'>{st.session_state.sym} Live Analysis ⚡</p>", unsafe_allow_html=True)

if mode == "MARKET":
    # 🎯 ഒരിക്കലും എറർ വരാത്ത സ്റ്റേബിൾ ചാർട്ട് വിഡ്ജറ്റ്
    chart_html = f"""
    <div class="tradingview-widget-container">
      <div id="tv-chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%",
        "height": 500,
        "symbol": "{st.session_state.sym}",
        "interval": "5",
        "timezone": "Asia/Kolkata",
        "theme": "dark",
        "style": "1",
        "locale": "in",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tv-chart"
      }});
      </script>
    </div>
    """
    components.html(chart_html, height=520)
    st.warning("⚠️ ചാർട്ട് കാണുന്നില്ലെങ്കിൽ ഫോണിലെ 'Desktop Site' ഓപ്ഷൻ ഓൺ ചെയ്യുക.")

elif mode == "JOURNAL":
    st.subheader("📝 Trading Journal")
    # ട്രേഡ് സേവ് ചെയ്യാനുള്ള ഫോം...
    if os.path.isfile(FILE_NAME): st.dataframe(pd.read_csv(FILE_NAME), use_container_width=True)

elif mode == "DASHBOARD":
    st.subheader("📊 Performance")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.metric("Total P&L", f"₹{df['P&L'].sum():,.2f}")
