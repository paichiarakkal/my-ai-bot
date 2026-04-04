import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ് (നോർമൽ സെറ്റിംഗ്‌സ്)
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- സാധാരണ ഡിസൈൻ (ഹൈഡ് ചെയ്യുന്ന കോഡുകൾ ഒഴിവാക്കി) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; }
    .stButton>button { width: 100%; border-radius: 4px; background-color: #000 !important; color: #FFD700 !important; font-weight: bold; }
    .main-title { color: #FFF; font-size: 26px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ലോഗിൻ സെക്ഷൻ ---
def login_section():
    st.markdown('<div style="background:white; padding:20px; border-radius:10px; border:2px solid #BF953F; color:black; text-align:center;">', unsafe_allow_html=True)
    st.subheader("🔒 Login Access")
    u = st.text_input("Username", key="u_user")
    p = st.text_input("Password", type="password", key="p_pass")
    if st.button("Unlock"):
        if u == "faisal" and p == "trader123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong Password!")
    st.markdown('</div>', unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_v_original")
FILE_NAME = 'trade_history_v2.csv'

def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# --- സൈഡ് ബാർ (പഴയതുപോലെ) ---
with st.sidebar:
    st.header("🚀 Paichi Pro")
    mode = st.radio("SELECT:", ["MARKET", "JOURNAL", "DASHBOARD"])
    if st.session_state.logged_in:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.markdown('<p class="main-title">📈 LIVE MARKET DATA</p>', unsafe_allow_html=True)
    nifty = get_live_price("^NSEI")
    crude = get_live_price("CL=F")
    st.metric("NIFTY 50", f"₹ {nifty:,.2f}")
    st.metric("CRUDE OIL", f"$ {crude:,.2f}")

elif mode == "JOURNAL" or mode == "DASHBOARD":
    if not st.session_state.logged_in:
        login_section()
    else:
        if mode == "JOURNAL":
            st.markdown('<p class="main-title">📝 JOURNAL</p>', unsafe_allow_html=True)
            st.write("Welcome Faisal! നിനക്ക് ഇവിടെ ട്രേഡുകൾ കാണാം.")
        elif mode == "DASHBOARD":
            st.markdown('<p class="main-title">📊 DASHBOARD</p>', unsafe_allow_html=True)
            if os.path.isfile(FILE_NAME):
                df = pd.read_csv(FILE_NAME)
                st.dataframe(df.iloc[::-1], use_container_width=True)

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
