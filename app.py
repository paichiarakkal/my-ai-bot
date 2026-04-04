import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- സൈഡ്ബാർ ഐക്കൺ തിരികെ വരാനും ബാക്കി ഹൈഡ് ചെയ്യാനുമുള്ള ഫിക്സ് ---
st.markdown("""
<style>
    /* മുകളിലെ വെള്ള വര ഹൈഡ് ചെയ്യുന്നു */
    div[data-testid="stDecoration"] {display:none !important;}
    
    /* 'Manage App' ബട്ടൺ ഹൈഡ് ചെയ്യുന്നു */
    .stDeployButton {display:none !important;}
    
    /* ഫൂട്ടർ ഹൈഡ് ചെയ്യുന്നു */
    footer {visibility: hidden !important;}

    /* സൈഡ്ബാർ ഐക്കൺ കൃത്യമായി കാണാൻ (This is the Fix) */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        visibility: visible !important;
    }

    /* ആപ്പ് തീം */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    .stButton>button { width: 100%; border-radius: 4px; background-color: #000 !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; font-weight: bold; }
    .main-title { color: #FFF; font-size: 24px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ലോഗിൻ ഫംഗ്ഷൻ ---
def login_section():
    st.markdown('<div style="background:white; padding:20px; border-radius:10px; text-align:center; color:black;">', unsafe_allow_html=True)
    st.subheader("🔒 Private Access")
    u = st.text_input("Username", key="u")
    p = st.text_input("Password", type="password", key="p")
    if st.button("Unlock"):
        if u == "faisal" and p == "trader123":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Wrong!")
    st.markdown('</div>', unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_v_recovery")

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.header("🚀 Paichi Pro")
    mode = st.radio("മെനു:", ["MARKET", "JOURNAL", "DASHBOARD"])
    if st.session_state.logged_in:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- മെയിൻ കണ്ടന്റ് ---
if mode == "MARKET":
    st.markdown('<p class="main-title">📈 LIVE MARKET</p>', unsafe_allow_html=True)
    try:
        nifty_price = yf.Ticker("^NSEI").history(period='1d')['Close'].iloc[-1]
        st.metric("NIFTY 50", f"₹ {nifty_price:,.2f}")
    except:
        st.write("Market data loading...")

elif mode == "JOURNAL" or mode == "DASHBOARD":
    if not st.session_state.logged_in:
        login_section()
    else:
        st.write(f"Welcome to {mode} Section!")
