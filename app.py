import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression

# --- 1. പേജ് സെറ്റിംഗ്സ് ---
st.set_page_config(
    page_title="Paichi AI Trader Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. അൾട്രാ ക്ലിയർ വിഷ്വൽസ് (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #1A1C24 !important; }
    
    .main-title {
        color: #FFFFFF !important;
        font-size: 35px !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 20px;
    }

    div[data-testid="stSidebar"] label, 
    div[data-testid="stSidebar"] p, 
    div[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* AI PREDICTION - മഞ്ഞ നിറം */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetricValue"] > div {
        color: #FFFF00 !important; 
        text-shadow: 0px 0px 10px rgba(255, 255, 0, 0.8);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ലൈവ് ഡാറ്റ ഫംഗ്ഷൻ ---
def get_analysis(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers).json()
        result = res['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        df_close = [p for p in result['indicators']['quote'][0]['close'] if p is not None]
        
        ai_price = 0
        if len(df_close) > 10:
            y = np.array(df_close[-10:]).reshape(-1, 1)
            x = np.arange(10).reshape(-1, 1)
            model = LinearRegression().fit(x, y)
            ai_price = float(model.predict([[10]])[0][0])
            
        trend = "BUY 🟢" if price > (sum(df_close[-10:])/10) else "SELL 🔴"
        return {"price": price, "trend": trend, "ai": ai_price}
    except: return None

# --- 4. സൈഡ് ബാർ (AED to INR & Gold) ---
st.sidebar.title("🚀 Paichi Trader")

# AED to INR കൺവെർട്ടർ
st.sidebar.subheader("💰 Dubai Currency")
def get_aed_to_inr():
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d").json()
        return r['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 22.75 # Default rate

live_aed = get_aed_to_inr()
aed_amount = st.sidebar.number_input("Enter Durham (AED)", value=1.0)
st.sidebar.success(f"₹ {aed_amount * live_aed:.2f}")
st.sidebar.caption(f"Live Rate: 1 AED = ₹ {live_aed:.2f}")

st.sidebar.divider()

# മാർക്കറ്റ് സെലക്ഷൻ
main_cat = st.sidebar.radio("Select Category:", ["INDEX", "COMMODITY", "GOLD"])

selected = None
if main_cat == "INDEX":
    selected = st.sidebar.selectbox("Choose Index:", ["NIFTY 50", "BANK NIFTY", "GIFT NIFTY"])
elif main_cat == "COMMODITY":
    selected = st.sidebar.selectbox("Choose:", ["CRUDE OIL MCX"])
elif main_cat == "GOLD":
    selected = st.sidebar.selectbox("Choose Gold:", ["22K GOLD (1 Gram)", "22K GOLD (8 Gram/Pavan)"])

# --- 5. മെയിൻ ഡിസ്പ്ലേ ---
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

def display(symbol, name, mult=1):
    data = get_analysis(symbol)
    if data:
        p = data['price'] * mult
        ai_p = data['ai'] * mult
        st.subheader(name)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Price", f"₹{p:.2f}")
        t_color = "#1B5E20" if "BUY" in data['trend'] else "#B71C1C"
        c2.markdown(f"<div style='background-color:{t_color}; padding:10px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>{data['trend']}</div>", unsafe_allow_html=True)
        c3.metric("Status", "Active")
        diff = ai_p - p
        c4.metric("AI Prediction", f"₹{ai_p:.2f}", delta=f"{diff:.2f}")
        st.divider()

# സെലക്ഷൻ അനുസരിച്ചുള്ള ഡിസ്പ്ലേ
if selected == "NIFTY 50": display("^NSEI", "NIFTY 50")
elif selected == "BANK NIFTY": display("^NSEBANK", "BANK NIFTY")
elif selected == "GIFT NIFTY": display("INDF.NS", "GIFT NIFTY")
elif selected == "CRUDE OIL MCX": display("CL=F", "CRUDE OIL", mult=93.5)

# ഗോൾഡ് പ്രൈസ് കാൽക്കുലേഷൻ
elif selected == "22K GOLD (1 Gram)": 
    display("GC=F", "22K GOLD (1 Gram)", mult=2.56) # ഏകദേശ ഇന്ത്യൻ റേറ്റ്
elif selected == "22K GOLD (8 Gram/Pavan)": 
    display("GC=F", "22K GOLD (8 Gram/Pavan)", mult=20.5)
