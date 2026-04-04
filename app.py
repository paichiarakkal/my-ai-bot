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

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button { width: 100%; background-color: #000 !important; color: #BF953F !important; border: 1px solid #FFD700 !important; margin-bottom: 5px; font-weight: bold; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
    .trade-container { background: rgba(0,0,0,0.1); padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=15000, key="faisal_final_v1")
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

def get_analysis(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        p = data['meta']['regularMarketPrice']
        close = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        ai_p = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close)>5 else p
        return {"p": p, "ai": ai_p}
    except: return None

def get_option_chain(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/options/{symbol}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        options = res['optionChain']['result'][0]['options'][0]['calls']
        return pd.DataFrame(options)[['strike', 'lastPrice', 'volume', 'openInterest']].head(10)
    except: return None

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- 1. വാർത്തകൾ ---
news_mal = get_live_news_malayalam()
st.markdown(f'<div class="news-box"><marquee scrollamount="5" style="color: #FFF; font-size: 18px; font-weight: bold;">📢 {news_mal}</marquee></div>', unsafe_allow_html=True)

# --- 2. സൈഡ് ബാർ ---
with st.sidebar:
    st.title("🚀 Paichi Pro")
    live_aed = get_live_aed_rate()
    aed_in = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_in * live_aed:.2f} (INR)")
    st.divider()
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "OPTION CHAIN", "JOURNAL", "DASHBOARD"])
    if mode in ["MARKET", "OPTION CHAIN"]:
        if st.button("📈 NIFTY 50"): st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
        if st.button("🏦 BANK NIFTY"): st.session_state.sel = ("^NSEBANK", "BANK NIFTY", 1)
        if st.button("🛢️ CRUDE OIL"): st.session_state.sel = ("CL=F", "CRUDE OIL MCX", 93.5)

if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# --- 3. മെയിൻ കണ്ടന്റ് ---
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    symbol, name, multi = st.session_state.sel
    data = get_analysis(symbol)
    if data:
        st.subheader(f"📍 {name}")
        live_p, ai_p = data['p'] * multi, data['ai'] * multi
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{live_p:.2f}")
        c2.metric("AI പ്രവചനം", f"₹{ai_p:.2f}")

elif mode == "OPTION CHAIN":
    symbol, name, _ = st.session_state.sel
    st.subheader(f"📊 Option Chain - {name}")
    oc_data = get_option_chain(symbol)
    if oc_data is not None: st.table(oc_data)
    else: st.warning("ഡാറ്റ ലഭ്യമല്ല.")

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ & എഡിറ്റർ")
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക", expanded=False):
        col1, col2 = st.columns(2)
        s, a = col1.text_input("Item", value=st.session_state.sel[1]), col2.selectbox("Action", ["BUY", "SELL"])
        en, ex = col1.number_input("Entry", value=0.0), col2.number_input("Exit", value=0.0)
        q, mood = col1.number_input("Qty", value=1), col2.selectbox("മൂഡ്", ["Calm", "Happy", "Fear"])
        if st.button("Save Trade"):
            pnl = (ex - en) * q if a == "BUY" else (en - ex) * q
            save_trade(s, a, en, ex, q, pnl, mood)
            st.rerun()

    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.write("### സേവ് ചെയ്ത ട്രേഡുകൾ")
        for index, row in df.iterrows():
            with st.container():
                st.markdown(f'<div class="trade-container">', unsafe_allow_html=True)
                c1, c2 = st.columns([4, 1])
                c1.write(f"📅 {row['Date']} | **{row['Item']}** | {row['Type']} | P&L: **₹{row['P&L']}**")
                if c2.button("🗑️ Delete", key=f"del_{index}"):
                    df = df.drop(index)
                    df.to_csv(FILE_NAME, index=False)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

elif mode == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ്")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.plotly_chart(px.bar(df, x='Date', y='P&L', color='P&L'))
    else: st.info("ഹിസ്റ്ററി ലഭ്യമല്ല.")

# --- FOOTER ---
st.markdown(f"""
    <hr style="border: 0.5px solid #BF953F;">
    <p style="text-align: center; color: #FFF;">Created by <b>Faisal Arakkal</b></p>
""", unsafe_allow_html=True)
