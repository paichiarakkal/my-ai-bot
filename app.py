import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# --- 1. പേജ് സെറ്റിംഗ്സ് ---
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- 2. വിഷ്വൽസ് ശരിയാക്കാൻ (മഞ്ഞ നിറത്തിലുള്ള AI Prediction) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    
    /* മെട്രിക്സ് ലേബൽ വെളുപ്പ് */
    div[data-testid="stMetricLabel"] > div {
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }

    /* ലൈവ് പ്രൈസ് - ശുദ്ധമായ വെളുപ്പ് */
    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* --- AI PREDICTION പ്രത്യേകമായി മഞ്ഞ നിറമാക്കാൻ --- */
    /* നാലാമത്തെ കോളത്തിലെ (AI Prediction) വാല്യൂ മാത്രം ടാർഗെറ്റ് ചെയ്യുന്നു */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetricValue"] > div {
        color: #FFFF00 !important; /* Bright Yellow */
        text-shadow: 0px 0px 5px rgba(255, 255, 0, 0.5);
    }

    /* AI Prediction താഴെയുള്ള ഡെൽറ്റ നമ്പറുകൾ (ഉദാ: -8.85) തെളിച്ചമുള്ളതാക്കാൻ */
    div[data-testid="stMetricDelta"] > div {
        font-size: 18px !important;
        font-weight: bold !important;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 2px 5px;
        border-radius: 5px;
    }
    
    /* റെഡ് ഡെൽറ്റ */
    div[data-testid="stMetricDelta"] > div[data-font-color="red"] {
        color: #FF4B4B !important; 
    }
    
    /* ഗ്രീൻ ഡെൽറ്റ */
    div[data-testid="stMetricDelta"] > div[data-font-color="green"] {
        color: #00F900 !important;
    }

    section[data-testid="stSidebar"] { background-color: #1A1C24; }
    h1, h2, h3 { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=2000, key="faisal_yellow_prediction_v1")

# --- 3. ഡാറ്റ ലോജിക് ---
def predict_next_price(prices):
    if len(prices) > 10:
        y = np.array(prices[-10:]).reshape(-1, 1)
        x = np.arange(10).reshape(-1, 1)
        model = LinearRegression()
        model.fit(x, y)
        return float(model.predict([[10]])[0][0])
    return None

def get_analysis(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        result = res['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        df_close = [p for p in result['indicators']['quote'][0]['close'] if p is not None]
        if len(df_close) > 20:
            avg = sum(df_close[-10:]) / 10
            trend = "BUY 🟢" if price > avg else "SELL 🔴"
            ai_price = predict_next_price(df_close)
            return {"price": price, "trend": trend, "ai": ai_price}
    except: return None

def display_card(symbol, name, mult=1):
    data = get_analysis(symbol)
    if data:
        p = data['price'] * mult
        ai_p = data['ai'] * mult if data['ai'] else 0
        st.write(f"### {name}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Price", f"₹{p:.2f}")
        
        trend_color = "#1B5E20" if "BUY" in data['trend'] else "#B71C1C"
        c2.markdown(f"<div style='background-color:{trend_color}; padding:10px; border-radius:8px; color:white; font-weight:bold; text-align:center;'>{data['trend']}</div>", unsafe_allow_html=True)
        
        c3.metric("Status", "Active")
        
        # AI Prediction വിത്ത് ഡെൽറ്റ
        diff = ai_p - p
        c4.metric("AI Prediction", f"₹{ai_p:.2f}", delta=f"{diff:.2f}")
        st.divider()

# --- 4. മെയിൻ പേജ് ---
st.title("Paichi AI Trader")
display_card("^NSEI", "NIFTY 50")
display_card("^NSEBANK", "BANK NIFTY")
