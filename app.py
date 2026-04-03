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

st_autorefresh(interval=15000, key="faisal_final_v10")

FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def get_live_news_malayalam():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Crude%20Oil,Gold&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_list = [item['title'] for item in res['news']]
        full_news = "  |  ".join(news_list)
        return translate(full_news, "ml", "en")
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

# --- 1. മലയാളം വാർത്തകൾ (Top) ---
news_mal = get_live_news_malayalam()
st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 വാർത്തകൾ: {news_mal}</marquee></div>', unsafe_allow_html=True)

# 4. സൈഡ് ബാർ (ബട്ടണുകൾ)
with st.sidebar:
    st.title("🚀 Paichi Pro")
    
    # കറൻസി കൺവെർട്ടർ
    aed_val = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_val * 22.75:.2f} (INR)")
    st.divider()

    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()

    if mode == "MARKET":
        st.subheader("🎯 തിരഞ്ഞെടുക്കുക:")
        # ഇൻഡക്സുകൾ
        if st.button("📈 NIFTY 50"): st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
        if st.button("🏦 BANK NIFTY"): st.session_state.sel = ("^NSEBANK", "BANK NIFTY", 1)
        if st.button("💳 FIN NIFTY"): st.session_state.sel = ("NIFTY_FIN_SERVICE.NS", "FIN NIFTY", 1)
        if st.button("📊 SENSEX"): st.session_state.sel = ("^BSESN", "SENSEX", 1)
        if st.button("📉 MIDCAP 50"): st.session_state.sel = ("^NSEMDCP50", "MIDCAP 50", 1)
        st.divider()
        # കമ്മോഡിറ്റി & ഗോൾഡ്
        if st.button("🛢️ CRUDE OIL MCX"): st.session_state.sel = ("CL=F", "CRUDE OIL MCX", 93.5)
        if st.button("💰 GOLD 8G (INDIAN)"): st.session_state.sel = ("GC=F", "GOLD 8 GRAM (1 PAVAN)", 84.5 * 8)

# Default item
if 'sel' not in st.session_state:
    st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# 5. മെയിൻ കണ്ടന്റ്
st.markdown(f'<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    symbol, name, multi = st.session_state.sel
    data = get_analysis(symbol)
    if data:
        st.subheader(f"📍 {name}")
        live_p = data['p'] * multi
        ai_p = data['ai'] * multi
        
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{live_p:.2f}")
        c2.metric("AI പ്രവചനം", f"₹{ai_p:.2f}")
        
        # ഗ്രാഫ്
        chart_data = pd.DataFrame({"Price": [live_p] * 10})
        st.line_chart(chart_data)

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ & SL Advisor")
    # പഴയ ജേണൽ കോഡ് ഇവിടെ...
    with st.expander("ട്രേഡ് ചേർക്കുക", expanded=True):
        en = st.number_input("Entry Price", value=0.0)
        if en > 0:
            st.warning(f"💡 SL: ₹{en*0.99:.2f} | Target: ₹{en*1.02:.2f}")

elif mode == "DASHBOARD":
    st.subheader("📊 വിൻ റേറ്റ് & പെർഫോമൻസ്")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        wins = len(df[df['P&L'] > 0])
        st.metric("Win Rate 🎯", f"{(wins/len(df)*100) if len(df)>0 else 0:.1f}%")
        st.plotly_chart(px.pie(df, names='Mood', title="Psychology Chart")) #
