import streamlit as st
import requests, numpy as np, pandas as pd, datetime, os, time
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# --- 1. CONFIG & GOLDEN THEME ---
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button { width: 100%; background-color: #000 !important; color: #BF953F !important; border: 1px solid #FFD700 !important; margin-bottom: 5px; font-weight: bold; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=15000, key="faisal_fixed_v5")
FILE_NAME = 'trade_history_v2.csv'

# --- 2. CORE FUNCTIONS ---
def get_live_data(symbol):
    try:
        # Yahoo Finance API calling
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        p = data['meta']['regularMarketPrice']
        close = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        ai_p = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close)>5 else p
        return {"p": p, "ai": ai_p}
    except: return None

def get_live_aed_rate():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        return res['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 22.75

def get_malayalam_news():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Gold,Crude&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_titles = "  |  ".join([item['title'] for item in res['news']])
        return translate(news_titles, "ml", "en")
    except: return "വാർത്തകൾ അപ്‌ഡേറ്റ് ചെയ്യുന്നു..."

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- 3. TOP NEWS BAR ---
st.markdown(f'<div class="news-box"><marquee scrollamount="5" style="color: #FFF; font-size: 18px; font-weight: bold;">📢 {get_malayalam_news()}</marquee></div>', unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🚀 Paichi Pro")
    live_aed = get_live_aed_rate()
    st.metric("1 AED to INR", f"₹{live_aed:.2f}")
    st.divider()
    mode = st.radio("മെനു:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()

    if mode == "MARKET":
        st.subheader("📊 Watchlist")
        # Nifty, Crude, Gold Buttons with Live Prices
        def sb_btn(sym, lbl, mult=1):
            d = get_live_data(sym)
            price = (d['p'] * mult) if d else 0
            btn_lbl = f"{lbl}: ₹{price:,.0f}" if price > 0 else lbl
            if st.button(btn_lbl):
                st.session_state.sel = (sym, lbl, mult)
                st.session_state.last_price = price

        sb_btn("^NSEI", "📈 NIFTY 50")
        sb_btn("CL=F", "🛢️ CRUDE OIL", 84.5 * 10) # Crude Price Correction
        sb_btn("GC=F", "💰 GOLD 8G", 8.45 * 8 * 84.5) # Gold Price Correction

if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# --- 5. MAIN CONTENT ---
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    # Rocket Animation
    p_holder = st.empty()
    for i in range(1, 15):
        p_holder.markdown(f"### {'&nbsp;' * i} 🚀 *AI Analyzing...*")
        time.sleep(0.06)
    p_holder.empty()

    sym, name, multi = st.session_state.sel
    data = get_live_data(sym)
    if data:
        st.subheader(f"📍 {name}")
        lp, ap = data['p'] * multi, data['ai'] * multi
        st.session_state.last_price = lp # Store for Journal

        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{lp:,.2f}")
        c2.metric("AI പ്രവചനം", f"₹{ap:,.2f}")

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ")
    # Automatic Price from Market Section
    auto_p = st.session_state.get('last_price', 0.0)
    
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക", expanded=True):
        col1, col2 = st.columns(2)
        s = col1.text_input("Item", value=st.session_state.sel[1])
        a = col2.selectbox("Action", ["BUY", "SELL"])
        en = col1.number_input("Entry Price", value=float(auto_p))
        ex = col2.number_input("Exit Price", value=0.0)
        q = col1.number_input("Qty", value=1, step=1)
        mood = col2.selectbox("മൂഡ്", ["Calm", "Happy", "Fear", "Greedy"])
        if st.button("Save Trade"):
            pnl = (ex - en) * q if a == "BUY" else (en - ex) * q
            save_trade(s, a, en, ex, q, pnl, mood)
            st.success("സേവ് ചെയ്തു!")
            st.rerun()

    if os.path.isfile(FILE_NAME):
        st.dataframe(pd.read_csv(FILE_NAME), use_container_width=True)

elif mode == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ്")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.plotly_chart(px.bar(df, x='Date', y='P&L', color='P&L', title="P&L Trend"))

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)

