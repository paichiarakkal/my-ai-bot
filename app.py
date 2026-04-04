import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ് - സൈഡ്ബാർ എപ്പോഴും തുറന്നു വെക്കാൻ (Expanded)
st.set_page_config(
    page_title="Paichi AI Trader Pro", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- ഐക്കൺ നിർബന്ധമായും കാണിക്കാനുള്ള സ്റ്റൈൽ ---
st.markdown("""
<style>
    /* 1. ആപ്പ് ബാറുകൾ ക്ലീൻ ആക്കുന്നു */
    header[data-testid="stHeader"] {
        visibility: visible !important;
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* 2. സൈഡ്ബാർ ഐക്കൺ (Menu) കറുപ്പ് നിറത്തിൽ ഹൈലൈറ്റ് ചെയ്യുന്നു */
    button[data-testid="stBaseButton-headerNoPadding"] {
        color: #000 !important;
        background-color: #FFD700 !important; /* ഗോൾഡൻ ബട്ടൺ */
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        border: 2px solid #000 !important;
        display: block !important;
        z-index: 999999 !important;
    }

    /* 3. 'Manage App' ബട്ടൺ ഹൈഡ് ചെയ്യുന്നു */
    .stDeployButton {display:none !important;}
    footer {visibility: hidden !important;}
    div[data-testid="stToolbar"] {display:none !important;}

    /* 4. ആപ്പ് തീം (Gold Gradient) */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    
    /* 5. സൈഡ്ബാർ വൈറ്റ് ബാക്ക്ഗ്രൗണ്ട് */
    section[data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        min-width: 250px !important;
    }
    
    .main-title { 
        color: #FFF; font-size: 24px; font-weight: 800; 
        text-align: center; text-shadow: 2px 2px 4px #000;
        background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ലോഗിൻ സെക്ഷൻ ---
def login_section():
    st.markdown('<div style="background:#f9f9f9; padding:20px; border-radius:15px; border:2px solid #BF953F; color:black;">', unsafe_allow_html=True)
    st.subheader("🔒 Faisal Pro Login")
    u = st.text_input("Username", key="f_user")
    p = st.text_input("Password", type="password", key="f_pass")
    if st.button("UNLOCK"):
        if u == "faisal" and p == "trader123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong Password!")
    st.markdown('</div>', unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_v9_refresh")

def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("## 🚀 Paichi Pro")
    st.write("---")
    mode = st.radio("SELECT MENU:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.write("---")
    
    if st.session_state.logged_in:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- മെയിൻ കണ്ടന്റ് ---
if mode == "MARKET":
    st.markdown('<p class="main-title">📈 LIVE MARKET DATA</p>', unsafe_allow_html=True)
    
    nifty = get_live_price("^NSEI")
    crude = get_live_price("CL=F")
    aed_inr = get_live_price("AEDINR=X")
    
    col1, col2 = st.columns(2)
    col1.metric("NIFTY 50", f"₹ {nifty:,.2f}")
    col2.metric("CRUDE OIL", f"$ {crude:,.2f}")
    
    st.info(f"💰 AED to INR: ₹ {aed_inr:,.2f}")

elif mode == "JOURNAL" or mode == "DASHBOARD":
    if not st.session_state.logged_in:
        login_section()
    else:
        st.success(f"Hello Faisal! You are in {mode} section.")

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
