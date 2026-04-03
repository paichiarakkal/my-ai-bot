import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# --- 1. പേജ് സെറ്റിംഗ്സ് ---
st.set_page_config(
    page_title="Paichi AI Trader Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. അൾട്രാ വിസിബിലിറ്റി & കളർ ഫിക്സ് (CSS) ---
st.markdown("""
<style>
    /* ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #1A1C24 !important; }
    
    /* സൈഡ്ബാറിലെ ടൈറ്റിൽ (Paichi Trader) */
    .sidebar-title {
        color: #00F900 !important; /* പച്ച നിറം */
        font-size: 26px !important;
        font-weight: 800 !important;
        margin-bottom: 20px;
    }

    /* സൈഡ്ബാറിലെ ഓപ്ഷനുകൾ (INDEX, COMMODITY, GOLD) */
    div[data-testid="stSidebar"] label {
        color: #FFD700 !important; /* സ്വർണ്ണ നിറം (മഞ്ഞ) */
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 10px 0px;
    }
    
    /* സൈഡ്ബാറിലെ ബാക്കി അക്ഷരങ്ങൾ */
    div[data-testid="stSidebar"] p, div[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* മെയിൻ ടൈറ്റിൽ */
    .main-title {
        color: #FFFFFF !important;
        font-size: 40px !important;
        font-weight: 800 !important;
        text-align: center;
        text-shadow: 2px 2px 10px rgba(255, 255, 255, 0.2);
    }

    /* ലൈവ് പ്രൈസ് & AI പ്രെഡിക്ഷൻ */
    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
        font-size: 38px !important;
        font-weight: 800 !important;
    }
    
    /* AI Prediction - പ്രത്യേകമായി മഞ്ഞ നിറം */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetricValue"] > div {
        color: #FFFF00 !important;
    }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=2000, key="faisal_sidebar_color_fix")

# --- 3. ഡാറ്റ ലോജിക് ---
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

# --- 4. സൈഡ് ബാർ (പവർഫുൾ കളേഴ്സ്) ---
st.sidebar.markdown('<p class="sidebar-title">🚀 Paichi Trader</p>', unsafe_allow_html=True)

# Durham to INR
st.sidebar.write("💰 **AED TO INR**")
aed_rate = 25.24 
aed_val = st.sidebar.number_input("Durham (AED)", value=1.0)
st.sidebar.success(f"₹ {aed_val * aed_rate:.2f}")

st.sidebar.divider()

# മെയിൻ സെലക്ഷൻ
main_cat = st.sidebar.radio("CHOOSE CATEGORY:", ["INDEX", "COMMODITY", "GOLD"])

selected = None
if main_cat == "INDEX":
    selected = st.sidebar.selectbox("Choose Index:", ["NIFTY 50", "BANK NIFTY", "GIFT NIFTY", "SENSEX"])
elif main_cat == "COMMODITY":
    selected = st.sidebar.selectbox("Choose:", ["CRUDE OIL MCX"])
elif main_cat == "GOLD":
    selected = st.sidebar.selectbox("Choose:", ["22K GOLD (1 Gram)", "22K GOLD (8 Gram)"])

# --- 5. മെയിൻ പേജ് ഡിസ്പ്ലേ ---
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

def display(symbol, name, mult=1):
    data = get_analysis(symbol)
    if data:
        p = data['price'] * mult
        ai_p = data['ai'] * mult
        st.subheader(f"📊 {name}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Price", f"₹{p:.2f}")
        t_color = "#1B5E20" if "BUY" in data['trend'] else "#B71C1C"
        c2.markdown(f"<div style='background-color:{t_color}; padding:10px; border-radius:8px; color:white; text-align:center; font-weight:bold; margin-top:10px;'>{data['trend']}</div>", unsafe_allow_html=True)
        c3.metric("Status", "Active")
        diff = ai_p - p
        c4.metric("AI Prediction", f"₹{ai_p:.2f}", delta=f"{diff:.2f}")
        st.divider()

if selected == "NIFTY 50": display("^NSEI", "NIFTY 50")
elif selected == "BANK NIFTY": display("^NSEBANK", "BANK NIFTY")
elif selected == "GIFT NIFTY": display("INDF.NS", "GIFT NIFTY")
elif selected == "SENSEX": display("^BSESN", "SENSEX")
elif selected == "CRUDE OIL MCX": display("CL=F", "CRUDE OIL", mult=93.5)
elif selected == "22K GOLD (1 Gram)": display("GC=F", "GOLD 1G", mult=2.56)
elif selected == "22K GOLD (8 Gram)": display("GC=F", "GOLD 8G (PAVAN)", mult=20.5)
