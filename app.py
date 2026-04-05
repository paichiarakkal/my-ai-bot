import streamlit as st
import requests, numpy as np, pandas as pd, datetime, os, time
import plotly.express as px
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=15000, key="faisal_pro_v22")
FILE_NAME = 'trade_history_v2.csv'

# --- 2. CORE FUNCTIONS ---
def get_live_data(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        p = data['meta']['regularMarketPrice']
        close = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        ai_p = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close)>5 else p
        return {"p": p, "ai": ai_p}
    except: return None

def get_malayalam_news():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Gold&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_titles = "  |  ".join([item['title'] for item in res['news']])
        return translate(news_titles, "ml", "en")
    except: return "വാർത്തകൾ അപ്‌ഡേറ്റ് ചെയ്യുന്നു..."

# --- 3. UI COMPONENTS ---
# Top News Bar
st.markdown(f'<div class="news-box"><marquee scrollamount="5" style="color: #FFF; font-size: 18px; font-weight: bold;">📢 {get_malayalam_news()}</marquee></div>', unsafe_allow_html=True)

# Sidebar Menu
with st.sidebar:
    st.title("🚀 Paichi Pro")
    mode = st.radio("മെനു:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    if mode == "MARKET":
        if st.button("📈 NIFTY 50"): st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
        if st.button("🛢️ CRUDE MCX"): st.session_state.sel = ("CL=F", "CRUDE OIL", 93.5)
        if st.button("💰 GOLD 8G"): st.session_state.sel = ("GC=F", "GOLD 8G", 84.5 * 8)

if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# Main Display logic
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
        # Rocket Animation (Slower & Longer)
    p_holder = st.empty()
    for i in range(1, 30):
        # '&nbsp;' ഓരോ ലൂപ്പിലും കൂടുമ്പോൾ റോക്കറ്റ് നീങ്ങും
        p_holder.markdown(f"### {'&nbsp;' * i} 🚀 *AI Analyzing Market...*")
        time.sleep(0.1) # വേഗത കുറച്ചു (0.1 സെക്കൻഡ് ഗ്യാപ്പ്)
    p_holder.empty()

    symbol, name, multi = st.session_state.sel
    data = get_live_data(symbol)
    if data:
        st.subheader(f"📍 {name}")
        lp, ap = data['p'] * multi, data['ai'] * multi
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{lp:,.2f}")
        c2.metric("AI പ്രവചനം", f"₹{ap:,.2f}")
        st.line_chart(pd.DataFrame({"Price": [lp, ap, lp*1.001]}))

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ")
    # നിന്റെ പഴയ ജേണൽ സേവിംഗ് ലോജിക് ഇവിടെ തുടരാം...
    if os.path.isfile(FILE_NAME):
        st.dataframe(pd.read_csv(FILE_NAME), use_container_width=True)

elif mode == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ്")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.plotly_chart(px.bar(df, x='Date', y='P&L', color='P&L', title="P&L Trend"))

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
