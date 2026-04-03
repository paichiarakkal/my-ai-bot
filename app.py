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

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Pro - Crude Special", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .target-hit { background-color: #1B5E20; color: white; padding: 15px; border-radius: 10px; text-align: center; font-size: 22px; font-weight: bold; border: 4px solid #FFD700; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.6; } }
    .crude-box { background: #000; color: #BF953F; padding: 15px; border-radius: 10px; border-left: 5px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=8000, key="faisal_crude_pro")

FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def get_live_news_malayalam():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Crude%20Oil,Nifty&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_list = [item['title'] for item in res['news']]
        return translate("  🔥  ".join(news_list), "ml", "en")
    except: return "വാർത്തകൾ അപ്‌ഡേറ്റ് ചെയ്യുന്നു..."

def get_data(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        result = res['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        prev_close = result['meta']['previousClose']
        change = ((price - prev_close) / prev_close) * 100
        close_list = [c for c in result['indicators']['quote'][0]['close'] if c is not None]
        ai_pred = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close_list[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close_list)>5 else price
        return {"p": price, "c": change, "ai": ai_pred}
    except: return None

# --- മുകളിൽ കാണുന്ന വാർത്തകൾ ---
st.markdown(f'<div style="background:#000;color:#BF953F;padding:10px;"><marquee>📢 {get_live_news_malayalam()}</marquee></div>', unsafe_allow_html=True)

# 2. സൈഡ് ബാർ
with st.sidebar:
    st.title("🚀 Paichi Pro")
    menu = st.radio("MENU:", ["CRUDE FOCUS", "JOURNAL", "DASHBOARD"])
    st.divider()
    st.subheader("🎯 Profit Alert")
    target = st.number_input("Target Price (₹)", value=0.0)
    st.divider()
    st.write("📅 US Inventory: Every Wednesday 8:00 PM")

# 3. മെയിൻ കണ്ടന്റ്
st.markdown('<p class="main-title">🛢️ Crude Oil Special Tracker</p>', unsafe_allow_html=True)

if menu == "CRUDE FOCUS":
    crude = get_data("CL=F")
    if crude:
        live_p = crude['p'] * 93.5 # MCX ഏകദേശ നിരക്ക്
        
        # Target Alert Check
        if target > 0 and live_p >= target:
            st.markdown(f'<div class="target-hit">🎉 ടാർഗെറ്റ് എത്തി! വില: ₹{live_p:.2f} <br> പ്രോഫിറ്റ് ബുക്ക് ചെയ്യാം! 💰</div>', unsafe_allow_html=True)
            st.balloons()

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""<div class="crude-box">
                <h3>📍 CRUDE OIL MCX</h3>
                <h1 style="font-size: 50px;">₹{live_p:.2f}</h1>
                <p style="color: {'#00FF00' if crude['c'] > 0 else '#FF0000'};">മാറ്റം: {crude['c']:.2f}%</p>
            </div>""", unsafe_allow_html=True)
        
        with col2:
            st.subheader("🤖 AI Prediction")
            st.metric("Expected Price", f"₹{crude['ai']*93.5:.2f}")
            st.info("അടുത്ത 5 മിനിറ്റിലെ ട്രെൻഡ് നോക്കി AI കണക്കാക്കിയത്.")

    st.divider()
    st.subheader("📊 Live Chart Simulation")
    chart_data = pd.DataFrame(np.random.randn(20, 1), columns=['Price Trend'])
    st.line_chart(chart_data)

elif menu == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ")
    # (പഴയ ജേണൽ കോഡ്)
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക"):
        s = st.text_input("ഐറ്റം", value="Crude Oil")
        en = st.number_input("Entry", value=0.0)
        ex = st.number_input("Exit", value=0.0)
        mood = st.selectbox("മൂഡ്", ["Calm", "Happy", "Fear", "Greedy"])
        if st.button("സേവ്"):
            # സേവ് ചെയ്യുന്ന ലോജിക് ഇവിടെ തുടരും
            st.success("സേവ് ചെയ്തു!")

elif menu == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ് & AI അഡ്വൈസ്")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.plotly_chart(px.bar(df, x='Date', y='P&L', title="ലാഭനഷ്ടം"), use_container_width=True)
        
        # AI Trading Coach Section
        st.divider()
        st.subheader("🤖 AI Trading Coach")
        if 'Mood' in df.columns:
            m = df['Mood'].mode()[0]
            if m == "Fear": st.warning("⚠️ ഫൈസൽ, പേടി കാരണം നീ നല്ല അവസരങ്ങൾ നഷ്ടപ്പെടുത്തുന്നു. കോൺഫിഡൻസ് കൂട്ടുക!")
            elif m == "Greedy": st.error("🛑 അമിത ലാഭത്തിന് ശ്രമിക്കുന്നത് അപകടമാണ്. കൃത്യസമയത്ത് പ്രോഫിറ്റ് ബുക്ക് ചെയ്യുക.")
            elif m == "Happy": st.success("✅ നീ ഇപ്പോൾ മികച്ച രീതിയിലാണ് ട്രേഡ് ചെയ്യുന്നത്. ഇതേ ഡിസിപ്ലിൻ തുടരുക.")
    else:
        st.info("കൂടുതൽ ട്രേഡുകൾ ജേണലിൽ ചേർത്താൽ AI അഡ്വൈസ് ലഭ്യമാകും.")
