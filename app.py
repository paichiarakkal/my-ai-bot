import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(
    page_title="Paichi AI Trader",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. വിഷ്വൽസ് ശരിയാക്കാനുള്ള CSS (ലിങ്കുകൾ ഒഴിവാക്കി)
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #1A1C24; }
    
    /* സൈഡ്ബാറിലെ മങ്ങിയ അക്ഷരങ്ങൾ വെളുപ്പിക്കാൻ */
    div[data-testid="stSidebar"] p, 
    div[data-testid="stSidebar"] span, 
    div[data-testid="stSidebar"] label,
    div[data-testid="stSidebar"] .st-emotion-cache-17l243g {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* മെയിൻ പേജിലെ ലേബലുകൾ */
    div[data-testid="stMetricLabel"] > div {
        color: #D1D1D1 !important;
    }

    /* വലിയ നമ്പറുകൾ */
    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
    }

    /* ചുവപ്പ് ഡെൽറ്റ തെളിച്ചമുള്ളതാക്കാൻ */
    div[data-testid="stMetricDelta"] > div[data-font-color="red"] {
        color: #FF4B4B !important;
    }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=2000, limit=100, key="faisal_final_fix")

# 3. ലൈവ് കറൻസി റേറ്റ് (ദുബായ്)
def get_aed_rate():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        return r['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 25.24

# 4. സൈഡ് ബാർ ഡിസൈൻ
st.sidebar.title("🚀 Paichi Trader")

st.sidebar.subheader("💰 Live Currency")
live_rate = get_aed_rate()
aed_val = st.sidebar.number_input("Enter AED", value=1.0)
st.sidebar.success(f"Total INR: ₹{aed_val * live_rate:.2f}")
st.sidebar.caption(f"Rate: 1 AED = ₹{live_rate:.2f}")

st.sidebar.divider()

st.sidebar.subheader("📊 Market Menu")
main_menu = st.sidebar.radio("Select Category:", ["INDEX", "COMMODITY", "GOLD"])

selected_item = None
if main_menu == "INDEX":
    selected_item = st.sidebar.selectbox("Choose Index:", 
        ["All Indices", "NIFTY 50", "BANK NIFTY", "SENSEX", "FIN NIFTY"])
elif main_menu == "COMMODITY":
    selected_item = st.sidebar.selectbox("Choose:", ["All Commodities", "CRUDE OIL MCX"])
elif main_menu == "GOLD":
    selected_item = st.sidebar.selectbox("Choose:", ["22K GOLD 8 GRAM"])

st.sidebar.divider()
st.sidebar.info("Al Barsha, Dubai Edition")

# 5. ട്രേഡിംഗ് ലോജിക്
def get_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        price = res['chart']['result'][0]['meta']['regularMarketPrice']
        closes = [c for c in res['chart']['result'][0]['indicators']['quote'][0]['close'] if c is not None]
        
        if len(closes) > 10:
            avg = sum(closes[-10:]) / 10
            trend = "BUY 🟢" if price > avg else "SELL 🔴"
            # RSI Calculation
            diffs = np.diff(closes)
            up = diffs[diffs > 0].sum() if any(diffs > 0) else 0.1
            down = abs(diffs[diffs < 0].sum()) if any(diffs < 0) else 0.1
            rsi = 100 - (100 / (1 + (up/down)))
            return {"price": price, "rsi": rsi, "trend": trend}
    except: return None

def show_market(symbol, name, mult=1):
    info = get_data(symbol)
    if info:
        p = info['price'] * mult
        st.write(f"### {name}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Live Price", f"₹{p:.2f}")
        c2.metric("RSI (14)", f"{info['rsi']:.2f}")
        
        btn_color = "#1B5E20" if "BUY" in info['trend'] else "#B71C1C"
        c3.markdown(f"<div style='background-color:{btn_color}; padding:10px; border-radius:5px; text-align:center; font-weight:bold;'>{info['trend']}</div>", unsafe_allow_html=True)
        st.divider()

# 6. മെയിൻ പേജ് ഡിസ്പ്ലേ
st.title(f"Paichi AI: {selected_item}")

if selected_item in ["NIFTY 50", "All Indices"]: show_market("^NSEI", "NIFTY 50")
if selected_item in ["BANK NIFTY", "All Indices"]: show_market("^NSEBANK", "BANK NIFTY")
if selected_item in ["SENSEX", "All Indices"]: show_market("^BSESN", "SENSEX")
if selected_item in ["CRUDE OIL MCX", "All Commodities"]: show_market("CL=F", "CRUDE OIL MCX", mult=93.5)
if selected_item == "22K GOLD 8 GRAM": show_market("GC=F", "22K GOLD 8 GRAM", mult=20.5)
