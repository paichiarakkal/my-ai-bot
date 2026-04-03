import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Settings ---
st.set_page_config(
    page_title="Paichi AI Trader Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Gold Theme Background & Visual Fix (CSS) ---
st.markdown("""
<style>
    /* Main Background - Dark Gold/Bronze Shade */
    .stApp { 
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
        color: #000000 !important; 
    }
    
    /* Sidebar Fix */
    section[data-testid="stSidebar"] { 
        background-color: #1A1C24 !important; 
    }
    
    /* Main Title - Black color for better visibility on Gold */
    .main-title {
        color: #000000 !important;
        font-size: 40px !important;
        font-weight: 800 !important;
        text-align: center;
        text-shadow: 1px 1px 5px rgba(255, 255, 255, 0.5);
    }

    /* Metric Values - Black color */
    div[data-testid="stMetricValue"] > div {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 32px !important;
    }

    /* Prediction - Red/Green based on trend */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetricValue"] > div {
        color: #1B5E20 !important; /* Greenish for prediction visibility */
        background: rgba(255, 255, 255, 0.3);
        padding: 5px;
        border-radius: 5px;
    }

    /* Sidebar Labels - White color */
    div[data-testid="stSidebar"] label, div[data-testid="stSidebar"] p {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=2000, key="faisal_gold_theme_fix")

# --- 3. Data Logic ---
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

# --- 4. Sidebar ---
with st.sidebar:
    st.title("🚀 Paichi Trader")
    
    # AED to INR
    st.write("💰 **AED TO INR**")
    aed_rate = 22.75 
    aed_val = st.number_input("Durham (AED)", value=1.0)
    st.success(f"INR: ₹ {aed_val * aed_rate:.2f}")
    
    st.divider()
    
    # Category Selection
    main_cat = st.radio("CATEGORY:", ["INDEX", "COMMODITY", "GOLD"])
    
    selected = None
    if main_cat == "INDEX":
        selected = st.selectbox("Index:", ["NIFTY 50", "BANK NIFTY", "GIFT NIFTY", "SENSEX"])
    elif main_cat == "COMMODITY":
        selected = st.selectbox("Item:", ["CRUDE OIL MCX"])
    elif main_cat == "GOLD":
        selected = st.selectbox("Unit:", ["22K GOLD (1 Gram)", "22K GOLD (8 Gram)"])

# --- 5. Main Page ---
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

def display(symbol, name, mult=1):
    data = get_analysis(symbol)
    if data:
        p = data['price'] * mult
        ai_p = data['ai'] * mult
        st.subheader(f"📍 {name}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Price", f"₹{p:.2f}")
        
        t_color = "#1B5E20" if "BUY" in data['trend'] else "#B71C1C"
        c2.markdown(f"<div style='background-color:{t_color}; padding:10px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>{data['trend']}</div>", unsafe_allow_html=True)
        
        c3.metric("Status", "Active")
        diff = ai_p - p
        c4.metric("AI Prediction", f"₹{ai_p:.2f}", delta=f"{diff:.2f}")
        st.divider()

# Selection Logic
if selected == "NIFTY 50": display("^NSEI", "NIFTY 50")
elif selected == "BANK NIFTY": display("^NSEBANK", "BANK NIFTY")
elif selected == "GIFT NIFTY": display("INDF.NS", "GIFT NIFTY")
elif selected == "SENSEX": display("^BSESN", "SENSEX")
elif selected == "CRUDE OIL MCX": display("CL=F", "CRUDE OIL", mult=93.5)
elif selected == "22K GOLD (1 Gram)": display("GC=F", "GOLD 1G", mult=2.56)
elif selected == "22K GOLD (8 Gram)": display("GC=F", "GOLD 8G (PAVAN)", mult=20.5)
