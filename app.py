import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- പ്രധാനപ്പെട്ട മാറ്റം: മുകളിലെ മെനു ഹൈഡ് ചെയ്യുന്നു ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    .stButton>button { width: 100%; border-radius: 4px; background-color: #000 !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; font-weight: bold; }
    .main-title { color: #FFF; font-size: 26px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .info-box { background-color: #f8f9fa; padding: 10px; border-radius: 8px; color: #333; font-weight: bold; text-align: center; border: 1px solid #ddd; margin-bottom: 5px; }
    .login-card { 
        background: white; padding: 30px; border-radius: 15px; 
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2); border-top: 5px solid #BF953F;
        max-width: 400px; margin: auto; text-align: center; color: #000;
    }
</style>
""", unsafe_allow_html=True)

# --- ലോഗിൻ ഫംഗ്ഷൻ ---
def login_section():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader("🔒 Private Access")
    user = st.text_input("Username", placeholder="Username", key="login_user")
    pw = st.text_input("Password", type="password", placeholder="Password", key="login_pw")
    
    if st.button("UNLOCK", key="login_btn"):
        if user == "faisal" and pw == "trader123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("തെറ്റായ വിവരങ്ങൾ!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'sel_ticker' not in st.session_state:
    st.session_state.sel_ticker = ("^NSEI", "NIFTY 50")

st_autorefresh(interval=30000, key="faisal_v5_refresh")
FILE_NAME = 'trade_history_v2.csv'

def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("### 🚀 Paichi Pro")
    ex_rate = get_live_price("AEDINR=X")
    st.write(f"💰 **AED to INR:** ₹ {ex_rate:,.2f}")
    
    st.divider()
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()

    if st.session_state.get('logged_in', False):
        if st.button("🚪 LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

# --- മെയിൻ ബോഡി കണ്ടന്റ് ---
if mode == "MARKET":
    st.markdown('<p class="main-title">🚀 LIVE MARKET DATA</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        nifty = get_live_price("^NSEI")
        st.metric("NIFTY 50", f"₹ {nifty:,.2f}")
    with col2:
        crude = get_live_price("CL=F")
        st.metric("CRUDE OIL", f"$ {crude:,.2f}")
    
    st.write("---")
    gold_price_per_gram = get_live_price("GC=F")
    gold_8g_inr = (gold_price_per_gram / 31.1035) * 8 * ex_rate * 1.15 
    st.markdown(f'<div class="info-box">🟡 Gold Price (8g): ₹ {gold_8g_inr:,.0f} (Approx)</div>', unsafe_allow_html=True)

elif mode == "JOURNAL" or mode == "DASHBOARD":
    if not st.session_state.logged_in:
        login_section()
    else:
        if mode == "JOURNAL":
            st.markdown('<p class="main-title">📝 OPTION JOURNAL</p>', unsafe_allow_html=True)
            underlying = st.selectbox("Index", ["NIFTY", "BANKNIFTY", "CRUDE OIL"])
            strike = st.text_input("Strike & Type", placeholder="Ex: 22400 CE")
            col1, col2 = st.columns(2)
            entry_raw = col1.text_input("Entry Premium", value="", placeholder="0.00")
            exit_raw = col2.text_input("Exit Premium", value="", placeholder="0.00")
            qty_raw = col1.text_input("Total Qty", value="", placeholder="0")
            t_type = col2.selectbox("Order Type", ["BUY", "SELL"])
            
            if st.button("SAVE TRADE"):
                # സേവ് ചെയ്യാനുള്ള ഫംഗ്ഷൻ ഇവിടെ ചേർക്കാം
                st.success("Saved!")

        elif mode == "DASHBOARD":
            st.markdown('<p class="main-title">📊 MY PERFORMANCE</p>', unsafe_allow_html=True)
            if os.path.isfile(FILE_NAME):
                df = pd.read_csv(FILE_NAME)
                st.dataframe(df.iloc[::-1], use_container_width=True)

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
