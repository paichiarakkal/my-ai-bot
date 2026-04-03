import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Trader", layout="wide")

# 2. വിസിബിലിറ്റി ശരിയാക്കാനുള്ള CSS
st.markdown("""
<style>
    /* ബാക്ക്ഗ്രൗണ്ട് കറുപ്പ് */
    .stApp { background-color: #0E1117; }
    
    /* എല്ലാ മെട്രിക്സ് നമ്പറുകളും ലേബലുകളും ശുദ്ധമായ വെളുപ്പ് നിറത്തിലാക്കാൻ */
    [data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
        font-size: 30px !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] > div {
        color: #FFFFFF !important;
        font-size: 16px !important;
    }
    [data-testid="stMetricDelta"] > div {
        font-weight: bold !important;
    }

    /* സൈഡ്ബാറിലെ അക്ഷരങ്ങൾ വെളുപ്പിക്കാൻ */
    section[data-testid="stSidebar"] .stText, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    /* ടൈറ്റിലുകൾ */
    h1, h2, h3 { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=2000, key="faisal_final_visibility")

# 3. ഡാറ്റ ഫെച്ചിംഗ്
def get_analysis(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        price = res['chart']['result'][0]['meta']['regularMarketPrice']
        return price
    except: return None

# 4. മെയിൻ ഡിസ്പ്ലേ
st.title("🚀 Paichi AI Trader")

col1, col2 = st.columns(2)

# NIFTY 50
nifty_p = get_analysis("^NSEI")
if nifty_p:
    col1.metric("NIFTY 50 - LIVE PRICE", f"₹{nifty_p:.2f}")

# CRUDE OIL
crude_p = get_analysis("CL=F")
if crude_p:
    col2.metric("CRUDE OIL - LIVE PRICE", f"₹{crude_p * 93.5:.2f}")

st.divider()
st.info("ഇപ്പോൾ അക്ഷരങ്ങൾ എല്ലാം നല്ല വെളുത്ത നിറത്തിൽ വ്യക്തമായി കാണാം!")
