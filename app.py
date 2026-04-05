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

# --- 2. വിഷ്വൽ ഫിക്സ് (എല്ലാം ഒരേസമയം കാണാൻ) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #1A1C24 !important; }
    
    /* സൈഡ്ബാറിലെ ടൈറ്റിൽ സ്റ്റൈൽ */
    .sidebar-brand {
        color: #00F900 !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        margin-bottom: 5px;
    }

    /* സൈഡ്ബാറിലെ എല്ലാ സെക്ഷനുകളും വെളുത്ത നിറത്തിൽ കാണാൻ */
    div[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: bold !important;
        opacity: 1 !important;
    }

    /* റേഡിയോ ബട്ടൺ സെലക്ഷൻ കളർ */
    div[data-testid="stWidgetLabel"] p {
        color: #FFD700 !important; /* ഗോൾഡ് കളർ */
    }

    /* ലൈവ് പ്രൈസ് & മെട്രിക്സ് */
    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* AI Prediction - മഞ്ഞ നിറം */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetricValue"] > div {
        color: #FFFF00 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ഡാറ്റ ഫംഗ്ഷൻ ---
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

# --- 4. സൈഡ് ബാർ (എല്ലാം ഒരുമിച്ച് കാണാൻ) ---
st.sidebar.markdown('<p class="sidebar-brand">🚀 Paichi Trader</p>', unsafe_allow_html=True)

# Durham to INR
st.sidebar.markdown("💰 **AED TO INR**")
aed_rate = 22.75 # ലൈവ് റേറ്റ് അനുസരിച്ച് മാറ്റാം
aed_val = st.sidebar.number_input("Durham (AED)", value=1.0, step=1.0)
st.sidebar.success(f"₹ {aed_val * aed_rate:.2f}")

st.sidebar.divider()

# മെയിൻ കാറ്റഗറി - ഒന്നിന് പുറകെ ഒന്നായി കാണും
st.sidebar.markdown("### 📊 CHOOSE CATEGORY")
main_cat = st.sidebar.radio("", ["INDEX", "COMMODITY", "GOLD"], label_visibility="collapsed")

selected = None
if main_cat == "INDEX":
    selected = st.sidebar.selectbox("Choose Index:", ["NIFTY 50", "BANK NIFTY", "GIFT NIFTY", "SENSEX"])
elif main_cat == "COMMODITY":
    selected = st.sidebar.selectbox("Choose Commodity:", ["CRUDE OIL MCX"])
elif main_cat == "GOLD":
    selected = st.sidebar.selectbox("Choose Gold Unit:", ["22K GOLD (1 Gram)", "22K GOLD (8 Gram)"])

# --- 5. മെയിൻ പേജ് ---
st.header("📈 Paichi AI Trader")

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

if selected == "NIFTY 50": display("^NSEI", "NIFTY 50")
elif selected == "BANK NIFTY": display("^NSEBANK", "BANK NIFTY")
elif selected == "GIFT NIFTY": display("INDF.NS", "GIFT NIFTY")
elif selected == "SENSEX": display("^BSESN", "SENSEX")
elif selected == "CRUDE OIL MCX": display("CL=F", "CRUDE OIL", mult=93.5)
elif selected == "22K GOLD (1 Gram)": display("GC=F", "GOLD 1G", mult=2.56)
elif selected == "22K GOLD (8 Gram)": display("GC=F", "GOLD 8G (PAVAN)", mult=20.5)
