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
from PIL import Image

# 1. പേജ് സെറ്റിംഗ്സ് (Icon ആയി നിന്റെ ഫോട്ടോ വരാൻ)
st.set_page_config(
    page_title="Paichi AI Trader Pro", 
    page_icon="image_7.png", 
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button { width: 100%; background-color: #000 !important; color: #BF953F !important; border: 1px solid #FFD700 !important; margin-bottom: 5px; font-weight: bold; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 15 സെക്കൻഡിൽ ആപ്പ് ഓട്ടോ റിഫ്രഷ് ആകും
st_autorefresh(interval=15000, key="faisal_ultimate_fixed_v20")

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

# --- 1. മലയാളം ലൈവ് വാർത്തകൾ ---
news_mal = get_live_news_malayalam()
st.markdown(f"""
    <div class="news-box">
        <h4 style="color: #BF953F; margin: 0; font-size: 16px; text-align: center;">📰 മലയാളം ലൈവ് വാർത്തകൾ</h4>
        <marquee scrollamount="5" style="color: #FFF; font-size: 18px; font-weight: bold; padding-top: 5px;">
            📢 {news_mal}
        </marquee>
    </div>
""", unsafe_allow_html=True)

# --- 2. സൈഡ് ബാർ ---
with st.sidebar:
    # സൈഡ് ബാറിൽ നിന്റെ ഫോട്ടോ വരാൻ താഴെ വരികൾ
    if os.path.exists("image_7.png"):
        img = Image.open("image_7.png")
        st.image(img, use_container_width=True)
    
    st.title("🚀 Paichi Pro")
    
    live_aed = get_live_aed_rate()
    st.subheader("💰 Live Currency")
    aed_in = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_in * live_aed:.2f} (INR)")
    st.divider()

    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])

# --- 3. മെയിൻ കണ്ടന്റ് ---
st.markdown(f'<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
    symbol, name, multi = st.session_state.sel
    data = get_analysis(symbol)
    if data:
        st.subheader(f"📍 {name}")
        live_p, ai_p = data['p'] * multi, data['ai'] * multi
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{live_p:.2f}")
        c2.metric("AI പ്രവചനം", f"₹{ai_p:.2f}")
        st.line_chart(pd.DataFrame({"Price": [live_p]*10}))

# ബാക്കി കോഡുകൾ (Journal, Dashboard) ഇതിന് താഴെ പഴയതുപോലെ തന്നെ തുടരും.
