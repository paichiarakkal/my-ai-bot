import streamlit as st
import requests
import pandas as pd
import numpy as np
import datetime
import os
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate
from PIL import Image

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Trader Pro", page_icon="image_7.png", layout="wide")

# ഗോൾഡൻ തീം സ്റ്റൈൽ
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button { width: 100%; background-color: #000 !important; color: #BF953F !important; border: 1px solid #FFD700 !important; margin-bottom: 5px; font-weight: bold; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=15000, key="faisal_final_fix")
FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def get_live_news_malayalam():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Crude%20Oil&newsCount=5"
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

# ഓപ്ഷൻ ചെയിൻ കൂടുതൽ മെച്ചപ്പെടുത്തിയത്
def get_option_chain(symbol):
    try:
        # Nifty-ക്ക് പകരം Yahoo-ൽ ഉപയോഗിക്കുന്നത് ^NSEI ആണ്
        url = f"https://query1.finance.yahoo.com/v7/finance/options/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers).json()
        
        if 'optionChain' in res and res['optionChain']['result']:
            options = res['optionChain']['result'][0]['options'][0]['calls']
            df = pd.DataFrame(options)[['strike', 'lastPrice', 'change', 'volume', 'openInterest']]
            return df.head(10)
        return None
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("image_7.png"):
        st.image(Image.open("image_7.png"), use_container_width=True)
    st.title("🚀 Paichi Pro")
    st.divider()
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "OPTION CHAIN", "JOURNAL"])
    if st.button("📈 NIFTY 50"): st.session_state.sel = ("^NSEI", "NIFTY 50")
    if st.button("🏦 BANK NIFTY"): st.session_state.sel = ("^NSEBANK", "BANK NIFTY")
    if st.button("🛢️ CRUDE OIL"): st.session_state.sel = ("CL=F", "CRUDE OIL")

if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50")

# --- MAIN ---
news_mal = get_live_news_malayalam()
st.markdown(f'<div class="news-box"><marquee scrollamount="5" style="color: #FFF; font-size: 18px; font-weight: bold;">📢 {news_mal}</marquee></div>', unsafe_allow_html=True)
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    symbol, name = st.session_state.sel
    data = get_analysis(symbol)
    if data:
        st.subheader(f"📍 {name}")
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{data['p']:.2f}")
        c2.metric("AI പ്രവചനം", f"₹{data['ai']:.2f}")
        
        # ഗ്രാഫിലെ വെള്ള ബോക്സ് ഒഴിവാക്കാൻ
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=[data['p']]*10, mode='lines', line=dict(color='#00008B', width=3), hoverinfo='none'))
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

elif mode == "OPTION CHAIN":
    symbol, name = st.session_state.sel
    st.subheader(f"📊 Option Chain - {name}")
    oc_df = get_option_chain(symbol)
    if oc_df is not None and not oc_df.empty:
        st.dataframe(oc_df, use_container_width=True)
    else:
        st.warning(f"നിലവിൽ {name} ഓപ്ഷൻ ഡാറ്റ ലഭ്യമല്ല. മാർക്കറ്റ് സമയങ്ങളിൽ വീണ്ടും ശ്രമിക്കുക.")

# --- FOOTER ---
st.markdown(f"""
    <hr style="border: 0.5px solid #BF953F;">
    <div style="text-align: center; color: #FFF; padding: 10px;">
        <p style="margin: 0; font-size: 14px;">Created by <b>Faisal Arakkal</b></p>
        <a href="https://my-ai-bot-kj4n8z6nvjusxwpts3kehs.streamlit.app/" target="_blank" style="color: #BF953F; text-decoration: none; font-weight: bold;">
            Visit My App 🔗
        </a>
    </div>
""", unsafe_allow_html=True)
