import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
import plotly.express as px
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button { width: 100%; background-color: #000 !important; color: #BF953F !important; border: 1px solid #FFD700 !important; margin-bottom: 5px; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=10000, key="faisal_sidebar_btns")

FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def get_analysis(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        p = data['meta']['regularMarketPrice']
        close = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        ai_p = float(LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1,1)).predict([[5]])[0][0]) if len(close)>5 else p
        return {"p": p, "ai": ai_p}
    except: return None

# 4. സൈഡ് ബാർ (ബട്ടണുകൾ)
with st.sidebar:
    st.title("🚀 Paichi Menu")
    
    # കറൻസി കൺവെർട്ടർ
    aed_val = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_val * 22.75:.2f}")
    st.divider()

    # മെയിൻ സെക്ഷൻ സെലക്ഷൻ
    mode = st.radio("അടിസ്ഥാന വിഭാഗം:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()

    selected_item = None
    if mode == "MARKET":
        st.subheader("📊 ഇൻഡക്സ് സെലക്ട് ചെയ്യുക:")
        # ഓരോ ഇൻഡക്സിനും പ്രത്യേക ബട്ടണുകൾ
        if st.button("📈 NIFTY 50"): st.session_state.item = ("^NSEI", "NIFTY 50", 1)
        if st.button("🏦 BANK NIFTY"): st.session_state.item = ("^NSEBANK", "BANK NIFTY", 1)
        if st.button("💳 FIN NIFTY"): st.session_state.item = ("NIFTY_FIN_SERVICE.NS", "FIN NIFTY", 1)
        if st.button("📊 SENSEX"): st.session_state.item = ("^BSESN", "SENSEX", 1)
        if st.button("📉 MIDCAP 50"): st.session_state.item = ("^NSEMDCP50", "MIDCAP 50", 1)
        st.divider()
        st.subheader("🔥 കമ്മോഡിറ്റി:")
        if st.button("🛢️ CRUDE OIL MCX"): st.session_state.item = ("CL=F", "CRUDE OIL MCX", 93.5)
        if st.button("💰 GOLD 1 PAVAN"): st.session_state.item = ("GC=F", "GOLD 8 GRAM", 84.5 * 8)

# Default item സെറ്റ് ചെയ്യുക
if 'item' not in st.session_state:
    st.session_state.item = ("^NSEI", "NIFTY 50", 1)

# 5. മെയിൻ കണ്ടന്റ്
st.markdown(f'<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "MARKET":
    symbol, name, multi = st.session_state.item
    data = get_analysis(symbol)
    if data:
        st.subheader(f"📍 {name}")
        c1, c2 = st.columns(2)
        c1.metric("ലൈവ് വില", f"₹{data['p']*multi:.2f}")
        c2.metric("AI പ്രവചനം", f"₹{data['ai']*multi:.2f}")
        
        # ഗ്രാഫ് (ചെറുത്)
        df_chart = pd.DataFrame({"Price": [data['p']*multi]*10})
        st.line_chart(df_chart)

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ")
    # പഴയ ജേണൽ കോഡ് ഇവിടെ...
    with st.expander("പുതിയ ട്രേഡ് ചേർക്കുക", expanded=True):
        st.write("ഇവിടെ നിന്റെ ട്രേഡുകൾ സേവ് ചെയ്യാം.")

elif mode == "DASHBOARD":
    st.subheader("📊 വിൻ റേറ്റ് & പെർഫോമൻസ്")
    # പഴയ ഡാഷ്ബോർഡ് കോഡ് ഇവിടെ...
