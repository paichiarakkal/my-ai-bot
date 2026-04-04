import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- സൈഡ്ബാർ ബട്ടൺ കാണാനും ബാക്കി ഹൈഡ് ചെയ്യാനുമുള്ള ഫിക്സ്ഡ് സ്റ്റൈൽ ---
st.markdown("""
<style>
    /* 1. മുകളിലെ വെള്ള വര ഹൈഡ് ചെയ്യുന്നു */
    div[data-testid="stDecoration"] {display:none !important;}
    
    /* 2. 'Manage App' ബട്ടൺ ഹൈഡ് ചെയ്യുന്നു */
    .stDeployButton {display:none !important;}
    
    /* 3. സൈഡ്ബാർ ബട്ടൺ (Menu Icon) കറുപ്പ് നിറത്തിൽ വ്യക്തമായി കാണാൻ */
    header[data-testid="stHeader"] {
        visibility: visible !important;
        background-color: rgba(0,0,0,0) !important;
    }
    
    /* സൈഡ്ബാർ ഐക്കണിന്റെ നിറം മാറ്റുന്നു */
    button[data-testid="stBaseButton-headerNoPadding"] {
        color: black !important;
        background-color: white !important;
        border-radius: 50% !important;
        padding: 5px !important;
    }

    /* 4. ഫൂട്ടറും ടൂൾബാറും ഹൈഡ് ചെയ്യുന്നു */
    footer {visibility: hidden !important;}
    div[data-testid="stToolbar"] {display:none !important;}

    /* ആപ്പ് തീം */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background-color: #f0f2f6 !important; }
    .stButton>button { width: 100%; border-radius: 4px; background-color: #000 !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; font-weight: bold; }
    .main-title { color: #FFF; font-size: 24px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ലോഗിൻ ഫംഗ്ഷൻ ---
def login_section():
    st.markdown('<div style="background:white; padding:20px; border-radius:10px; text-align:center; color:black; border: 2px solid #BF953F;">', unsafe_allow_html=True)
    st.subheader("🔒 Faisal Pro Login")
    u = st.text_input("Username", key="u", placeholder="Enter Username")
    p = st.text_input("Password", type="password", key="p", placeholder="Enter Password")
    if st.button("Unlock Now"):
        if u == "faisal" and p == "trader123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("തെറ്റായ പാസ്‌വേഡ്!")
    st.markdown('</div>', unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_v_final_fix")
FILE_NAME = 'trade_history_v2.csv'

def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.header("🚀 Paichi Pro")
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()
    
    if st.session_state.logged_in:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.markdown('<p class="main-title">📈 LIVE MARKET DATA</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        nifty = get_live_price("^NSEI")
        st.metric("NIFTY 50", f"₹ {nifty:,.2f}")
    with col2:
        crude = get_live_price("CL=F")
        st.metric("CRUDE OIL", f"$ {crude:,.2f}")
    
    st.write("---")
    ex_rate = get_live_price("AEDINR=X")
    st.write(f"💰 **AED to INR:** ₹ {ex_rate:,.2f}")

elif mode == "JOURNAL" or mode == "DASHBOARD":
    if not st.session_state.logged_in:
        login_section()
    else:
        if mode == "JOURNAL":
            st.markdown('<p class="main-title">📝 TRADE JOURNAL</p>', unsafe_allow_html=True)
            # നിന്റെ പഴയ ജേണൽ കോഡ് ഇവിടെ ചേർക്കാം...
            st.info("ഇവിടെ നിനക്ക് ട്രേഡുകൾ സേവ് ചെയ്യാം.")
            
        elif mode == "DASHBOARD":
            st.markdown('<p class="main-title">📊 DASHBOARD</p>', unsafe_allow_html=True)
            if os.path.isfile(FILE_NAME):
                df = pd.read_csv(FILE_NAME)
                st.dataframe(df.iloc[::-1], use_container_width=True)
            else:
                st.warning("ഡാറ്റയൊന്നും ലഭ്യമല്ല!")

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
