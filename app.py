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

# --- 1. പേജ് സെറ്റിംഗ്സ് & ക്ലീൻ ഡിസൈൻ ---
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide", initial_sidebar_state="collapsed")

# നീ ആവശ്യപ്പെട്ടതുപോലെ മുകളിലെ Fork/Logo ഉം താഴെയുള്ള ഐക്കണുകളും നീക്കാനുള്ള CSS
st.markdown("""
<style>
    /* ഗോൾഡൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    
    /* സൈഡ് ബാർ തീം */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button { width: 100%; background-color: #000 !important; color: #BF953F !important; border: 1px solid #FFD700 !important; margin-bottom: 5px; font-weight: bold; }
    
    /* മുകളിലെ ഹെഡർ (Fork, GitHub) പൂർണ്ണമായി നീക്കാൻ */
    header, [data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }
    
    /* താഴെയുള്ള ഐക്കണുകൾ (Created by, Hosted with) നീക്കാൻ */
    footer {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    #MainMenu {visibility: hidden !important;}
    
    /* സ്ക്രീനിന്റെ ഏറ്റവും താഴെ കാണുന്ന ആ രണ്ട് ചിഹ്നങ്ങൾ ഒഴിവാക്കാൻ */
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stStatusWidget"] { visibility: hidden !important; }
    iframe { display: none !important; }

    /* ടൈറ്റിൽ & ന്യൂസ് ബോക്സ് */
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; margin-top: -60px; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 15 സെക്കൻഡിൽ ഓട്ടോ റിഫ്രഷ്
st_autorefresh(interval=15000, key="faisal_ultimate_clean_v80")

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

# --- 2. മലയാളം ലൈവ് വാർത്തകൾ ---
news_mal = get_live_news_malayalam()
st.markdown(f'<div class="news-box"><h4 style="color:#BF953F;text-align:center;">📰 മലയാളം ലൈവ് വാർത്തകൾ</h4><marquee scrollamount="5" style="color:#FFF;font-weight:bold;">📢 {news_mal}</marquee></div>', unsafe_allow_html=True)

# --- 3. സൈഡ് ബാർ ---
with st.sidebar:
    st.title("🚀 Paichi Pro")
    live_aed = get_live_aed_rate()
    st.subheader("💰 Live Currency")
    aed_in = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_in * live_aed:.2f} (INR)")
    st.divider()
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    if mode == "MARKET":
        if st.button("📈 NIFTY 50"): st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
        if st.button("🏦 BANK NIFTY"): st.session_state.sel = ("^NSEBANK", "BANK NIFTY", 1)
        if st.button("🛢️ CRUDE OIL MCX"): st.session_state.sel = ("CL=F", "CRUDE OIL MCX", 93.5)
        if st.button("💰 GOLD 8G"): st.session_state.sel = ("GC=F", "GOLD 8G", 84.5 * 8)

if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# --- 4. മെയിൻ കണ്ടന്റ് ---
st.markdown(f'<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    symbol, name, multi = st.session_state.sel
    data = get_analysis(symbol)
    if data:
        st.subheader(f"📍 {name}")
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{data['p']*multi:.2f}")
        c2.metric("AI പ്രവചനം", f"₹{data['ai']*multi:.2f}")
        st.line_chart(pd.DataFrame({"Price": [data['p']*multi]*10}))
    else: st.error("ഇന്റർനെറ്റ് കണക്ഷൻ പരിശോധിക്കുക.")

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ & SL Advisor")
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക", expanded=True):
        col1, col2 = st.columns(2)
        s = col1.text_input("Item", value=st.session_state.sel[1])
        a = col2.selectbox("Action", ["BUY", "SELL"])
        en, ex = col1.number_input("Entry Price", value=0.0), col2.number_input("Exit Price", value=0.0)
        if en > 0:
            sl = en * 0.99 if a == "BUY" else en * 1.01
            st.warning(f"💡 AI അഡ്വൈസ്: SL ₹{sl:.2f} | Target ₹{en*1.02 if a=='BUY' else en*0.98:.2f}")
        qty = col1.number_input("Qty", value=1, step=1)
        mood = col2.selectbox("മൂഡ്", ["Calm", "Happy", "Fear", "Greedy"])
        if st.button("Save Trade"):
            pnl = (ex - en) * qty if a == "BUY" else (en - ex) * qty
            save_trade(s, a, en, ex, qty, pnl, mood)
            st.success("സേവ് ചെയ്തു!"); st.rerun()
    if os.path.isfile(FILE_NAME):
        st.dataframe(pd.read_csv(FILE_NAME), use_container_width=True)

elif mode == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ്")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.metric("Win Rate 🎯", f"{(len(df[df['P&L']>0])/len(df)*100) if len(df)>0 else 0:.1f}%")
        st.plotly_chart(px.pie(df, names='Mood', title="Psychology Chart", hole=0.4))
