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
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
</style>
""", unsafe_allow_html=True)

# 15 സെക്കൻഡിൽ ആപ്പ് ഓട്ടോ റിഫ്രഷ് ആകും
st_autorefresh(interval=15000, key="faisal_final_no_chart_v1")

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

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- ന്യൂസ് ടിക്കർ (TOP) ---
news_mal = get_live_news_malayalam()
st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 വാർത്തകൾ: {news_mal}</marquee></div>', unsafe_allow_html=True)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.title("🚀 Paichi Pro")
    
    # ലൈവ് ദിർഹം കൺവെർട്ടർ
    live_aed = get_live_aed_rate()
    st.subheader("💰 Live Currency")
    aed_in = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_in * live_aed:.2f} (INR)")
    st.caption(f"1 AED = ₹{live_aed:.2f}")
    st.divider()

    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()

    if mode == "MARKET":
        st.subheader("🎯 തിരഞ്ഞെടുക്കുക:")
        if st.button("📈 NIFTY 50"): st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
        if st.button("🏦 BANK NIFTY"): st.session_state.sel = ("^NSEBANK", "BANK NIFTY", 1)
        if st.button("💳 FIN NIFTY"): st.session_state.sel = ("NIFTY_FIN_SERVICE.NS", "FIN NIFTY", 1)
        if st.button("📊 SENSEX"): st.session_state.sel = ("^BSESN", "SENSEX", 1)
        if st.button("📉 MIDCAP 50"): st.session_state.sel = ("^NSEMDCP50", "MIDCAP 50", 1)
        st.divider()
        # Crude & Gold Symbols Updated for Live Price
        if st.button("🛢️ CRUDE OIL"): st.session_state.sel = ("CL=F", "CRUDE OIL", 84.5)
        if st.button("💰 GOLD 8G"): st.session_state.sel = ("GC=F", "GOLD 8G", 8.45 * 8)

if 'sel' not in st.session_state:
    st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# --- മെയിൻ കണ്ടന്റ് ---
st.markdown(f'<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    symbol, name, multi = st.session_state.sel
    data = get_analysis(symbol)
    if data:
        st.subheader(f"📍 {name}")
        live_p, ai_p = data['p'] * multi, data['ai'] * multi
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{live_p:,.2f}")
        c2.metric("AI പ്രവചനം", f"₹{ai_p:,.2f}")
        # വെള്ള ഗ്രാഫ് ഇവിടെ നിന്ന് ഒഴിവാക്കി

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ & SL Advisor")
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക", expanded=True):
        col1, col2 = st.columns(2)
        s = col1.text_input("Item", value=st.session_state.sel[1])
        a = col2.selectbox("Action", ["BUY", "SELL"])
        en = col1.number_input("Entry Price", value=0.0)
        ex = col2.number_input("Exit Price", value=0.0)
        if en > 0:
            sl = en * 0.99 if a == "BUY" else en * 1.01
            st.warning(f"💡 AI അഡ്വൈസ്: SL ₹{sl:.2f} | Target ₹{en*1.02 if a=='BUY' else en*0.98:.2f}")
        q = col1.number_input("Qty", value=1, step=1)
        mood = col2.selectbox("മൂഡ്", ["Calm", "Happy", "Fear", "Greedy"])
        if st.button("Save to History"):
            pnl = (ex - en) * q if a == "BUY" else (en - ex) * q
            save_trade(s, a, en, ex, q, pnl, mood)
            st.success(f"സേവ് ചെയ്തു! P&L: ₹{pnl}")
            st.rerun()
    
    if os.path.isfile(FILE_NAME):
        st.dataframe(pd.read_csv(FILE_NAME), use_container_width=True)

elif mode == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ് & വിൻ റേറ്റ്")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        wins = len(df[df['P&L'] > 0])
        total = len(df)
        st.metric("Win Rate 🎯", f"{(wins/total*100) if total > 0 else 0:.1f}%")
        st.plotly_chart(px.pie(df, names='Mood', title="സൈക്കോളജി ചാർട്ട്", hole=0.4))
        st.plotly_chart(px.bar(df, x='Date', y='P&L', color='P&L', title="P&L Trend"))
    else:
        st.info("ഹിസ്റ്ററി ലഭ്യമല്ല. ട്രേഡുകൾ സേവ് ചെയ്യുക.")
