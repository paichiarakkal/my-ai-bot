import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# --- 1. പേജ് സെറ്റിംഗ്സ് (ഇവിടെ സ്ലൈഡ് ബാർ എനേബിൾ ചെയ്തു) ---
st.set_page_config(
    page_title="Paichi AI Trader Pro",
    layout="wide",
    initial_sidebar_state="expanded" # സ്ലൈഡ് ബാർ എപ്പോഴും വരാൻ ഇത് സഹായിക്കും
)

# --- 2. സ്ലൈഡ് ബാർ & പ്രെഡിക്ഷൻ കളർ ശരിയാക്കാനുള്ള CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    
    /* സൈഡ് ബാർ ടെക്സ്റ്റ് വെളുപ്പിക്കാൻ */
    section[data-testid="stSidebar"] { 
        background-color: #1A1C24 !important; 
    }
    section[data-testid="stSidebar"] .stText, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* ലൈവ് പ്രൈസ് - ശുദ്ധമായ വെളുപ്പ് */
    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 35px !important;
    }

    /* --- AI PREDICTION പ്രത്യേകമായി മഞ്ഞ നിറമാക്കാൻ --- */
    /* 4-ാമത്തെ കോളത്തിലെ പ്രെഡിക്ഷൻ മാത്രം മഞ്ഞയാക്കുന്നു */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetricValue"] > div {
        color: #FFFF00 !important; 
        text-shadow: 0px 0px 8px rgba(255, 255, 0, 0.7);
    }

    /* ലേബലുകൾ (Live Price, AI Prediction) വെളുപ്പിക്കാൻ */
    div[data-testid="stMetricLabel"] > div {
        color: #FFFFFF !important;
        font-size: 16px !important;
    }

    /* ഡെൽറ്റ നമ്പറുകൾ വ്യക്തമാകാൻ */
    div[data-testid="stMetricDelta"] > div {
        font-weight: bold !important;
        font-size: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=2000, key="faisal_final_fix_v2")

# --- 3. ഡാറ്റ ഫെച്ചിംഗ് ---
def get_analysis(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        result = res['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        df_close = [p for p in result['indicators']['quote'][0]['close'] if p is not None]
        
        # Prediction Logic
        ai_price = 0
        if len(df_close) > 10:
            y = np.array(df_close[-10:]).reshape(-1, 1)
            x = np.arange(10).reshape(-1, 1)
            model = LinearRegression().fit(x, y)
            ai_price = float(model.predict([[10]])[0][0])
            
        trend = "BUY 🟢" if price > (sum(df_close[-10:])/10) else "SELL 🔴"
        return {"price": price, "trend": trend, "ai": ai_price}
    except: return None

# --- 4. സൈഡ് ബാർ (ഇപ്പോൾ ഇത് തിരിച്ചു വരും) ---
st.sidebar.title("🚀 Paichi Trader")
st.sidebar.subheader("💰 Live Currency")
# ദുബായ് കറൻസി റേറ്റ് (ഉദാഹരണത്തിന്)
aed_rate = 25.24 
aed_input = st.sidebar.number_input("Enter AED", value=1.0)
st.sidebar.success(f"Total INR: ₹{aed_input * aed_rate:.2f}")

st.sidebar.divider()
st.sidebar.subheader("Market Menu")
category = st.sidebar.radio("Select Category:", ["INDEX", "COMMODITY", "GOLD"])
st.sidebar.info("Al Barsha, Dubai Edition")

# --- 5. മെയിൻ ഡിസ്പ്ലേ ---
st.title(f"Paichi AI: {category}")

def show_data(symbol, name, mult=1):
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
        
        # AI Prediction - ഇവിടെ മഞ്ഞ നിറം വരും
        diff = ai_p - p
        c4.metric("AI Prediction", f"₹{ai_p:.2f}", delta=f"{diff:.2f}")
        st.divider()

if category == "INDEX":
    show_data("^NSEI", "NIFTY 50")
    show_data("^NSEBANK", "BANK NIFTY")
elif category == "COMMODITY":
    show_data("CL=F", "CRUDE OIL", mult=93.5)
