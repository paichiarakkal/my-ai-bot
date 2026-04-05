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

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ + സിൽവർ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    /* മെയിൻ ബോഡി ഗോൾഡൻ തീം */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    
    /* സിൽവർ സൈഡ് ബാർ */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; 
    }
    
    /* സൈഡ് ബാറിലെ ബ്ലാക്ക് & ഗോൾഡ് ബട്ടണുകൾ */
    div[data-testid="stSidebar"] button {
        background-color: #000 !important; color: #BF953F !important;
        border: 2px solid #FFD700 !important; border-radius: 12px !important;
        height: 45px !important; font-weight: bold !important;
        margin-bottom: 10px !important; width: 100% !important;
        transition: 0.3s;
    }
    
    div[data-testid="stSidebar"] button:hover {
        background-color: #BF953F !important; color: #000 !important;
        transform: scale(1.03);
    }

    .main-title { color: #FFF; font-size: 30px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
</style>
""", unsafe_allow_html=True)

# 30 സെക്കൻഡിൽ ആപ്പ് ഓട്ടോ റിഫ്രഷ് ആകും
st_autorefresh(interval=30000, key="faisal_final_fix_v3")

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

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- ന്യൂസ് ടിക്കർ (TOP) ---
st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 വാർത്തകൾ: {get_live_news_malayalam()}</marquee></div>', unsafe_allow_html=True)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #000;'>🚀 Paichi Pro</h1>", unsafe_allow_html=True)
    
    # 💰 ലൈവ് ദിർഹം കൺവെർട്ടർ
    live_aed = get_live_aed_rate()
    aed_input = st.number_input("AED (Dirham) നൽകുക", value=1.0)
    st.success(f"₹ {aed_input * live_aed:,.2f} (INR)")
    
    st.divider()
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    
    if mode == "MARKET":
        st.subheader("🎯 Market Watch")
        if st.button("📊 NIFTY 50"): st.session_state.tv_sym = "NIFTY"
        if st.button("🏦 BANK NIFTY"): st.session_state.tv_sym = "BANKNIFTY"
        st.divider()
        # TradingView-ൽ എറർ വരാത്ത സിംബലുകൾ
        if st.button("🛢️ CRUDE OIL"): st.session_state.tv_sym = "TVC:USOIL" 
        if st.button("💰 GOLD"): st.session_state.tv_sym = "TVC:GOLD"

if 'tv_sym' not in st.session_state: st.session_state.tv_sym = "NIFTY"

# --- മെയിൻ ബോഡി ---
st.markdown("<p class='main-title'>Paichi AI Pro Terminal ⚡</p>", unsafe_allow_html=True)

if mode == "MARKET":
    # TradingView Advanced Widget
    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:550px;">
      <div id="tradingview_pro"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%",
        "height": 550,
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
    components.html(tradingview_html, height=570)

elif mode == "JOURNAL":
    st.subheader("📝 Trading Journal")
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക", expanded=True):
        col1, col2 = st.columns(2)
        item = col1.text_input("Item", value=st.session_state.tv_sym)
        act = col2.selectbox("Action", ["BUY", "SELL"])
        en = col1.number_input("Entry Price", value=0.0)
        ex = col2.number_input("Exit Price", value=0.0)
        q = col1.number_input("Qty", value=1)
        mood = col2.selectbox("Mood", ["Calm", "Happy", "Fear", "Greedy"])
        if st.button("Save Trade"):
            pnl = (ex - en) * q if act == "BUY" else (en - ex) * q
            save_trade(item, act, en, ex, q, pnl, mood)
            st.success(f"സേവ് ചെയ്തു! ലാഭം: ₹{pnl}")
            st.rerun()
    
    if os.path.isfile(FILE_NAME):
        st.dataframe(pd.read_csv(FILE_NAME), use_container_width=True)

elif mode == "DASHBOARD":
    st.subheader("📊 Performance Dashboard")
    if os.path.isfile(FILE_NAME):
        df_log = pd.read_csv(FILE_NAME)
        st.metric("Total P&L", f"₹{df_log['P&L'].sum():,.2f}")
        st.plotly_chart(px.bar(df_log, x='Date', y='P&L', color='P&L', title="P&L Trend"), use_container_width=True)
        st.plotly_chart(px.pie(df_log, names='Mood', title="Trading Mood Analysis"), use_container_width=True)
    else:
        st.info("ട്രേഡ് ഹിസ്റ്ററി ലഭ്യമല്ല.")
