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

# --- 1. പേജ് സെറ്റിംഗ്സ് ---
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide", initial_sidebar_state="expanded")

# ഗോൾഡൻ തീം & ക്ലീൻ ഡിസൈൻ
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    [data-testid="stSidebar"] { background-color: #f0f2f6 !important; }
    .main-title { color: #FFF; font-size: 32px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; margin-top: -40px; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
    header, footer { visibility: visible; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_v45_update")
FILE_NAME = 'trade_history_v3.csv'

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
    except: return "വാർത്തകൾ ലോഡ് ചെയ്യുന്നു..."

def get_market_data(symbol, period="1d", interval="5m"):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={period}", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        prices = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        return prices, data['meta']['regularMarketPrice']
    except: return [], 0

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood, notes):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood, notes]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood', 'Notes'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- 2. ലൈവ് വാർത്തകൾ ---
news_mal = get_live_news_malayalam()
st.markdown(f'<div class="news-box"><marquee scrollamount="5" style="color:#FFF;font-weight:bold;">📢 {news_mal}</marquee></div>', unsafe_allow_html=True)

# --- 3. സൈഡ് ബാർ ---
with st.sidebar:
    st.title("🚀 Paichi Pro")
    live_aed = get_live_aed_rate()
    st.success(f"1 AED = ₹ {live_aed:.2f} (INR)")
    st.divider()
    mode = st.radio("മെനു:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    if mode == "MARKET":
        if st.button("📈 NIFTY 50"): st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
        if st.button("🏦 BANK NIFTY"): st.session_state.sel = ("^NSEBANK", "BANK NIFTY", 1)
        if st.button("🛢️ CRUDE OIL"): st.session_state.sel = ("CL=F", "CRUDE OIL", 93.5)

if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# --- 4. മെയിൻ കണ്ടന്റ് ---
st.markdown(f'<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    symbol, name, multi = st.session_state.sel
    prices_1d, live_p = get_market_data(symbol, "1d", "5m")
    prices_5d, _ = get_market_data(symbol, "5d", "60m")
    
    if live_p > 0:
        st.subheader(f"📍 {name} - ₹{live_p*multi:.2f}")
        
        # മൾട്ടിപ്പിൾ ടൈംഫ്രെയിം ചാർട്ടുകൾ
        col1, col2 = st.columns(2)
        with col1:
            st.write("📊 **Today's Trend (5m)**")
            st.line_chart(np.array(prices_1d)*multi)
        with col2:
            st.write("📈 **Last 5 Days (1h)**")
            st.line_chart(np.array(prices_5d)*multi)
    else: st.error("ഡാറ്റ ലഭ്യമല്ല.")

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ & നോട്ട്സ്")
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക", expanded=True):
        c1, c2 = st.columns(2)
        s = c1.text_input("Item", value=st.session_state.sel[1])
        a = c2.selectbox("Action", ["BUY", "SELL"])
        en, ex = c1.number_input("Entry Price"), c2.number_input("Exit Price")
        qty = c1.number_input("Qty", value=1)
        mood = c2.selectbox("മൂഡ്", ["Calm", "Happy", "Fear", "Greedy"])
        notes = st.text_area("ഈ ട്രേഡിൽ നിന്ന് പഠിച്ച കാര്യങ്ങൾ (Notes):") #
        if st.button("Save Trade"):
            pnl = (ex - en) * qty if a == "BUY" else (en - ex) * qty
            save_trade(s, a, en, ex, qty, pnl, mood, notes)
            st.success("സേവ് ചെയ്തു!"); st.rerun()
    
    if os.path.isfile(FILE_NAME):
        st.dataframe(pd.read_csv(FILE_NAME), use_container_width=True)

elif mode == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ്")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.metric("Total P&L", f"₹ {df['P&L'].sum():.2f}")
        st.plotly_chart(px.bar(df, x='Date', y='P&L', color='P&L', title="Daily P&L"))
