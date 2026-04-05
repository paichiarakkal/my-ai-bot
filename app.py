import streamlit as st
import requests
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button {
        background-color: #000 !important; color: #BF953F !important;
        border: 2px solid #FFD700 !important; border-radius: 12px !important;
        height: 45px !important; font-weight: bold !important; width: 100% !important;
        margin-bottom: 8px !important;
    }
    .sidebar-chart-link {
        display: block; width: 100%; padding: 12px; background: #000; color: #FFD700 !important;
        text-align: center; border-radius: 10px; text-decoration: none; font-size: 16px; font-weight: bold; border: 2px solid #FFD700; margin-top: 10px;
    }
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
    .main-title { color: #FFF; font-size: 32px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .rule-card { background: rgba(0,0,0,0.8); color: #FFD700; padding: 15px; border-radius: 10px; border-left: 5px solid #FFD700; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_multi_page_v1")
FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def get_live_aed_rate():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        return res['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 22.75

def save_trade(symbol, action, entry, exit_p, qty, pnl):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry, exit_p, qty, pnl]], columns=['Date', 'Symbol', 'Action', 'Entry', 'Exit', 'Qty', 'P&L'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- സൈഡ് ബാർ (Navigation & Tools) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #000;'>🚀 Paichi Pro</h1>", unsafe_allow_html=True)
    
    # AED കൺവെർട്ടർ (എല്ലാ പേജിലും ഉണ്ടാകും)
    live_aed = get_live_aed_rate()
    aed_in = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_in * live_aed:,.2f} (INR)")
    st.divider()

    # മൾട്ടിപ്പിൾ പേജുകൾ (മൊത്തം 4 പേജുകൾ)
    page = st.radio("പേജ് മാറ്റാൻ തിരഞ്ഞെടുക്കുക:", ["🏠 HOME", "📈 MARKET", "📝 JOURNAL", "📊 DASHBOARD"])
    st.divider()

    # ചാർട്ട് ലിങ്ക് (Market പേജിൽ മാത്രം)
    if page == "📈 MARKET":
        st.subheader("🎯 Select Symbol")
        if st.button("📊 NIFTY 50"): st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY", "NIFTY 50"
        if st.button("🏦 BANK NIFTY"): st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY", "BANK NIFTY"
        if st.button("🛢️ CRUDE OIL"): st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=MCX:CRUDEOIL1!", "CRUDE OIL"
        
        if 'url' in st.session_state:
            st.markdown(f'<a href="{st.session_state.url}" target="_blank" class="sidebar-chart-link">📈 OPEN {st.session_state.name}</a>', unsafe_allow_html=True)

# ഡിഫോൾട്ട് സെറ്റിംഗ്സ്
if 'url' not in st.session_state: st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY", "NIFTY 50"

# --- പേജുകളുടെ പ്രവർത്തനം ---

# 1. HOME PAGE (Psychology Notes)
if page == "🏠 HOME":
    st.markdown(f"<p class='main-title'>Happy Trading, Faisal! 🦾</p>", unsafe_allow_html=True)
    
    # നിന്റെ ഫോട്ടോ
    my_photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png" 
    st.markdown(f'<div style="text-align: center;"><img src="{my_photo_url}" style="width: 150px; border-radius: 50%; border: 5px solid #FFD700;"></div>', unsafe_allow_html=True)
    
    st.markdown("### 🧠 Trading Psychology Rules")
    rules = [
        "1. അമിതമായ ആവേശം വേണ്ട, ക്ഷമയാണ് ട്രേഡിംഗിലെ വിജയം.",
        "2. ഒരു ദിവസം ഇത്ര നഷ്ടം വന്നാൽ നിർത്തും എന്ന് ഉറപ്പിക്കുക (Stop Loss).",
        "3. ലാഭം കിട്ടിയാൽ ഉടൻ അത് ലോക്ക് ചെയ്യാൻ പഠിക്കുക.",
        "4. ഒരിക്കലും റിവഞ്ച് ട്രേഡ് (നഷ്ടം നികത്താൻ വേണ്ടി മാത്രം ട്രേഡ് ചെയ്യൽ) ചെയ്യരുത്.",
        "5. മാർക്കറ്റ് എപ്പോഴും അവിടെത്തന്നെ കാണും, അവസരങ്ങൾ ഇനിയും വരും."
    ]
    for rule in rules:
        st.markdown(f'<div class="rule-card">{rule}</div>', unsafe_allow_html=True)

# 2. MARKET PAGE
elif page == "📈 MARKET":
    st.markdown(f"<p class='main-title'>{st.session_state.name} Terminal ⚡</p>", unsafe_allow_html=True)
    st.info("നിനക്ക് വേണ്ട സിംബൽ സൈഡ് ബാറിൽ നിന്ന് തിരഞ്ഞെടുക്കാം. അതിനുശേഷം 'OPEN' ബട്ടൺ അമർത്തുക.")
    st.markdown("<div style='text-align: center; font-size: 80px; margin-top: 50px;'>📈📉</div>", unsafe_allow_html=True)

# 3. JOURNAL PAGE
elif page == "📝 JOURNAL":
    st.markdown("<p class='main-title'>📝 Trade Journal</p>", unsafe_allow_html=True)
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കാം", expanded=True):
        c1, c2 = st.columns(2)
        sym = c1.text_input("Symbol", value=st.session_state.name)
        act = c2.selectbox("Action", ["BUY", "SELL"])
        en = c1.number_input("Entry Price")
        ex = c2.number_input("Exit Price")
        q = st.number_input("Quantity", value=1)
        if st.button("SAVE TRADE"):
            pnl = round((ex - en) * q if act == "BUY" else (en - ex) * q, 2)
            save_trade(sym, act, en, ex, q, pnl)
            st.success(f"സേവ് ചെയ്തു! P&L: ₹{pnl}")
            st.rerun()
    if os.path.isfile(FILE_NAME):
        st.dataframe(pd.read_csv(FILE_NAME).sort_index(ascending=False), use_container_width=True)

# 4. DASHBOARD PAGE
elif page == "📊 DASHBOARD":
    st.markdown("<p class='main-title'>📊 Performance Dashboard</p>", unsafe_allow_html=True)
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.metric("Total Net P&L", f"₹{df['P&L'].sum():,.2f}")
        st.bar_chart(df.set_index('Date')['P&L'])
    else:
        st.warning("ഡാറ്റ ലഭ്യമല്ല.")
