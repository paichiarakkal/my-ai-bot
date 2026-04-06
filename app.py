import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
import plotly.express as px
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
import yfinance as yf

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button { width: 100%; background-color: #000 !important; color: #BF953F !important; border: 1px solid #FFD700 !important; margin-bottom: 5px; font-weight: bold; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 30 സെക്കൻഡിൽ ആപ്പ് ഓട്ടോ റിഫ്രഷ് (API calls കുറയ്ക്കാൻ)
st_autorefresh(interval=30000, key="paichi_trader_fixed")

FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---

def get_live_aed_rate():
    try:
        ticker = yf.Ticker("AEDINR=X")
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return data['Close'].iloc[-1]
        else:
            return 22.75
    except:
        return 22.75

def get_live_news_malayalam():
    try:
        # Yahoo Finance news API (free, no key)
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Crude%20Oil,Gold&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = res.json()
        news_titles = [item['title'] for item in data.get('news', [])]
        if not news_titles:
            return "വാർത്തകൾ ലഭ്യമല്ല."
        # ഇംഗ്ലീഷ് വാർത്തകൾ മലയാളത്തിലേക്ക് translate ചെയ്യാൻ ശ്രമിക്കുക
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='en', target='ml')
            translated = " | ".join([translator.translate(title) for title in news_titles[:3]])
            return translated
        except:
            # translate ലൈബ്രറി ഇല്ലെങ്കിൽ ഇംഗ്ലീഷിൽ തന്നെ കാണിക്കുക
            return " | ".join(news_titles[:3])
    except Exception as e:
        return f"വാർത്തകൾ ലഭ്യമല്ല: {str(e)}"

def get_analysis(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # 1 മിനിറ്റ് ഇടവിട്ടുള്ള 10 ഡാറ്റ പോയിൻ്റുകൾ
        data = ticker.history(period="5m", interval="1m")
        if data.empty:
            return None
        last_price = data['Close'].iloc[-1]
        # ലളിതമായ Linear Regression പ്രവചനം (അവസാന 5 വിലകൾ ഉപയോഗിച്ച്)
        close_prices = data['Close'].values[-5:]
        if len(close_prices) < 5:
            return {"p": last_price, "ai": last_price}
        X = np.arange(len(close_prices)).reshape(-1, 1)
        y = close_prices.reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, y)
        next_x = np.array([[len(close_prices)]])
        predicted = model.predict(next_x)[0][0]
        return {"p": last_price, "ai": predicted}
    except Exception as e:
        st.error(f"Data fetch error: {e}")
        return None

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME):
        df_new.to_csv(FILE_NAME, index=False)
    else:
        df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- 1. മലയാളം ലൈവ് വാർത്തകൾ (TOP) ---
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
    st.title("🚀 Paichi Pro")
    
    # ലൈവ് ദിർഹം കൺവെർട്ടർ
    live_aed = get_live_aed_rate()
    st.subheader("💰 Live Currency")
    aed_in = st.number_input("AED (Dirham)", value=1.0, step=0.1)
    st.success(f"₹ {aed_in * live_aed:.2f} (INR)")
    st.caption(f"Current Rate: 1 AED = ₹{live_aed:.2f}")
    st.divider()

    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()

    if mode == "MARKET":
        st.subheader("🎯 തിരഞ്ഞെടുക്കുക:")
        # Stock/Index buttons
        if st.button("📈 NIFTY 50"): st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
        if st.button("🏦 BANK NIFTY"): st.session_state.sel = ("^NSEBANK", "BANK NIFTY", 1)
        if st.button("💳 FIN NIFTY"): st.session_state.sel = ("NIFTY_FIN_SERVICE.NS", "FIN NIFTY", 1)
        if st.button("📊 SENSEX"): st.session_state.sel = ("^BSESN", "SENSEX", 1)
        if st.button("📉 MIDCAP 50"): st.session_state.sel = ("^NSEMDCP50", "MIDCAP 50", 1)
        st.divider()
        if st.button("🛢️ CRUDE OIL MCX"): st.session_state.sel = ("CL=F", "CRUDE OIL MCX", 93.5)
        if st.button("💰 GOLD 8G (INDIAN)"): st.session_state.sel = ("GC=F", "GOLD 8 GRAM (1 PAVAN)", 84.5 * 8)

if 'sel' not in st.session_state:
    st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# --- 3. മെയിൻ കണ്ടന്റ് ---
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
        c2.metric("AI പ്രവചനം (1 min)", f"₹{ai_p:.2f}")
        # ഒരു ചെറിയ line chart (കഴിഞ്ഞ 10 മിനിറ്റ്)
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="10m", interval="1m")
        if not hist.empty:
            st.line_chart(hist['Close'])
    else:
        st.error("ഡാറ്റ ലഭ്യമല്ല. ഇൻ്റർനെറ്റ് കണക്ഷൻ പരിശോധിക്കുക.")

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ & SL Advisor")
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക", expanded=True):
        col1, col2 = st.columns(2)
        s = col1.text_input("Item", value=st.session_state.sel[1])
        a = col2.selectbox("Action", ["BUY", "SELL"])
        en = col1.number_input("Entry Price", value=0.0, format="%.2f")
        ex = col2.number_input("Exit Price", value=0.0, format="%.2f")
        if en > 0:
            sl = en * 0.99 if a == "BUY" else en * 1.01
            target = en * 1.02 if a == "BUY" else en * 0.98
            st.warning(f"💡 AI അഡ്വൈസ്: SL ₹{sl:.2f} | Target ₹{target:.2f}")
        q = col1.number_input("Qty", value=1, step=1)
        mood = col2.selectbox("മൂഡ്", ["Calm", "Happy", "Fear", "Greedy"])
        if st.button("Save Trade"):
            if en > 0 and ex > 0:
                pnl = (ex - en) * q if a == "BUY" else (en - ex) * q
                save_trade(s, a, en, ex, q, pnl, mood)
                st.success("സേവ് ചെയ്തു!")
                st.rerun()
            else:
                st.error("Entry, Exit price നൽകുക.")
    
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("ഇതുവരെ ട്രേഡുകളൊന്നുമില്ല.")

elif mode == "DASHBOARD":
    st.subheader("📊 പെർഫോമൻസ് & വിൻ റേറ്റ്")
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        wins = len(df[df['P&L'] > 0])
        total = len(df)
        win_rate = (wins/total*100) if total > 0 else 0
        st.metric("Win Rate 🎯", f"{win_rate:.1f}%")
        if not df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(px.pie(df, names='Mood', title="Psychology Chart", hole=0.4), use_container_width=True)
            with col2:
                st.plotly_chart(px.bar(df, x='Date', y='P&L', color='P&L', title="P&L Trend"), use_container_width=True)
    else:
        st.info("ഹിസ്റ്ററി ലഭ്യമല്ല.")
