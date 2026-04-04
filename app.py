import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- സൈഡ്ബാർ തിരികെ വരാനുള്ള ഫിക്സഡ് സ്റ്റൈൽ ---
st.markdown("""
<style>
    /* 1. മുകളിലെ വെള്ള വര ഹൈഡ് ചെയ്യുന്നു */
    div[data-testid="stDecoration"] {display:none !important;}
    
    /* 2. 'Manage App' ബട്ടൺ മാത്രം ഹൈഡ് ചെയ്യുന്നു */
    .stDeployButton {display:none !important;}
    
    /* 3. താഴെ കാണുന്ന ടൂൾബാർ (Logs) ഹൈഡ് ചെയ്യുന്നു */
    footer {visibility: hidden !important;}
    div[data-testid="stToolbar"] {display:none !important;}

    /* സൈഡ്ബാർ ബട്ടൺ (Menu Icon) തെളിഞ്ഞു കാണാൻ */
    button[data-testid="stBaseButton-headerNoPadding"] {
        background-color: rgba(0,0,0,0.5) !important;
        color: white !important;
        border-radius: 50%;
    }

    /* ആപ്പ് തീം */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    .stButton>button { width: 100%; border-radius: 4px; background-color: #000 !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; font-weight: bold; }
    .main-title { color: #FFF; font-size: 24px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

# --- ലോഗിൻ സിസ്റ്റം ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_section():
    st.markdown('<div style="background:white; padding:20px; border-radius:10px; text-align:center;">', unsafe_allow_html=True)
    st.subheader("🔒 Faisal Pro Login")
    u = st.text_input("Username", key="u")
    p = st.text_input("Password", type="password", key="p")
    if st.button("Unlock"):
        if u == "faisal" and p == "trader123":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Wrong!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.header("🚀 Paichi Menu")
    mode = st.radio("Go to:", ["MARKET", "JOURNAL", "DASHBOARD"])
    if st.session_state.logged_in:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.markdown('<p class="main-title">📈 LIVE MARKET</p>', unsafe_allow_html=True)
    # ലൈവ് പ്രൈസ് കാണിക്കുന്ന വരികൾ...
    nifty = yf.Ticker("^NSEI").history(period='1d')['Close'].iloc[-1]
    st.metric("NIFTY 50", f"₹ {nifty:,.2f}")

elif mode == "JOURNAL" or mode == "DASHBOARD":
    if not st.session_state.logged_in:
        login_section()
    else:
        st.write(f"Welcome to {mode}!")
        # നിന്റെ പഴയ ജേണൽ കോഡ് ഇവിടെ വരും...
