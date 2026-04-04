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

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* ഗോൾഡൻ തീം ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    
    /* സൈഡ് ബാർ സ്റ്റൈൽ */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; min-width: 260px !important; }
    div[data-testid="stSidebar"] *, div[data-testid="stWidgetLabel"] p { color: #000 !important; font-weight: bold !important; }
    
    /* പ്രൊഫൈൽ ഫോട്ടോ സ്റ്റൈൽ */
    .profile-container { text-align: center; padding-bottom: 15px; }
    .profile-img {
        display: block; margin-left: auto; margin-right: auto;
        width: 120px; height: 120px;
        border-radius: 50%; border: 3px solid #000;
        object-fit: cover; box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
    .profile-name { color: #000; font-size: 20px; font-weight: bold; margin-top: 8px; text-align: center; }

    /* മെയിൻ ടൈറ്റിൽ & ടാർഗെറ്റ് അലേർട്ട് */
    .main-title { color: #FFF; font-size: 38px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; margin-top: -40px; }
    .target-hit { background-color: #1B5E20; color: white; padding: 15px; border-radius: 10px; text-align: center; font-size: 22px; font-weight: bold; border: 4px solid #FFD700; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    
    /* ഗിറ്റ്‌ഹബ് ബട്ടണുകൾ ഹൈഡ് ചെയ്യാൻ */
    header, [data-testid="stHeader"], footer, .stDeployButton, [data-testid="stDecoration"], #MainMenu { visibility: hidden !important; display: none !important; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=10000, key="faisal_final_v6")

FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def get_live_news_malayalam():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Crude%20Oil,Gold&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_list = [item['title'] for item in res['news']]
        return translate("  🔥  ".join(news_list), "ml", "en")
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

# --- ന്യൂസ് ടിക്കർ ---
st.markdown(f'<div style="background:#000;color:#BF953F;padding:10px;"><marquee scrollamount="6">📢 {get_live_news_malayalam()}</marquee></div>', unsafe_allow_html=True)

# 4. സൈഡ് ബാർ (ഫോട്ടോ, കറൻസി & സെറ്റിംഗ്സ്)
with st.sidebar:
    # നിന്റെ ഫോട്ടോ ലോഡ് ചെയ്യുന്ന ഭാഗം
    if os.path.exists("image_7.png"):
        img = Image.open("image_7.png")
        st.markdown('<div class="profile-container">', unsafe_allow_html=True)
        st.image(img, use_container_width=True)
        st.markdown('<div class="profile-name">Faisal @Paichi</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("image_7.png കണ്ടില്ല! ഫയൽ അപ്‌ലോഡ് ചെയ്തിട്ടുണ്ടോ എന്ന് നോക്കുക.")
    
    st.divider()
    st.subheader("💰 Currency Converter")
    aed_val = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_val * 22.75:.2f} (INR)")
    st.divider()
    cat = st.radio("MENU:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    target_p = st.number_input("Target Alert (₹)", value=0.0)

# 5. മെയിൻ കണ്ടന്റ്
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if cat == "MARKET":
    sub_cat = st.selectbox("വിഭാഗം:", ["INDEX", "COMMODITY", "GOLD"])
    
    opts = {
        "INDEX": [
            ("^NSEI", "NIFTY 50"), ("^NSEBANK", "BANK NIFTY"), 
            ("NIFTY_FIN_SERVICE.NS", "FIN NIFTY"), ("^BSESN", "SENSEX"), 
            ("^NSEMDCP50", "MIDCAP 50")
        ], 
        "COMMODITY": [("CL=F", "CRUDE OIL MCX", 93.5)], 
        "GOLD": [("GC=F", "GOLD 1 GRAM", 84.5), ("GC=F", "GOLD 8 GRAM (1 PAVAN)", 84.5 * 8)]
    }
    
    sel_name = st.selectbox("ഐറ്റം:", [i[1] for i in opts[sub_cat]])
    sel_data = next(i for i in opts[sub_cat] if i[1] == sel_name)
    
    data = get_analysis(sel_data[0])
    if data:
        m = sel_data[2] if len(sel_data) > 2 else 1
        live_price = data['p'] * m
        
        if target_p > 0 and live_price >= target_p:
            st.markdown(f'<div class="target-hit">🎉 ടാർഗെറ്റ് എത്തി! ₹{live_price:.2f}</div>', unsafe_allow_html=True)
            st.balloons()

        st.subheader(f"📍 {sel_name}")
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{live_price:.2f}")
        c2.metric("AI പ്രവചനം", f"₹{data['ai']*m:.2f}")
        
        # ലൈവ് ചാർട്ട് കാണിക്കാൻ
        st.line_chart(pd.DataFrame({"Price": [live_price]*10}))

elif cat == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ & SL Advisor")
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക", expanded=True):
        col1, col2 = st.columns(2)
        en = col1.number_input("Entry Price", value=0.0)
        if en > 0:
            st.warning(f"💡 SL: ₹{en*0.99:.2f} | Target: ₹{en*1.02:.2f}")

elif cat == "DASHBOARD":
    st.subheader("📊 വിൻ റേറ്റ് & ഹിസ്റ്ററി")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        wins = len(df[df['P&L'] > 0])
        st.metric("Win Rate 🎯", f"{(wins/len(df)*100) if len(df)>0 else 0:.1f}%")
        st.plotly_chart(px.bar(df, x='Date', y='P&L', title="P&L Trend"))
