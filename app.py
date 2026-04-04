import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- ഡിസൈൻ സ്റ്റൈൽ (Silver Sidebar & Gold Theme) ---
st.markdown("""
<style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    
    /* സിൽവർ സൈഡ്ബാർ */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #D3D3D3, #C0C0C0, #A9A9A9) !important; 
    }
    
    /* ബട്ടൺ സ്റ്റൈൽ */
    .stButton>button { width: 100%; border-radius: 8px; background-color: #000 !important; color: #FFD700 !important; font-weight: bold; border: 1px solid #FFD700; }
    
    /* ടൈറ്റിൽ സ്റ്റൈൽ */
    .main-title { color: #FFF; font-size: 26px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    
    /* ഇൻഫോ ബോക്സ് */
    .info-box { background-color: white; padding: 15px; border-radius: 10px; color: black; font-weight: bold; text-align: center; margin: 10px 0; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st_autorefresh(interval=30000, key="faisal_v10_refresh")

# --- ലൈവ് പ്രൈസ് ഫംഗ്ഷൻ ---
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# --- സൈഡ് ബാർ (Silver Side) ---
with st.sidebar:
    st.markdown("## 🚀 Paichi Pro")
    st.write(f"📅 {datetime.datetime.now().strftime('%Y-%m-%d')}")
    st.divider()
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "NEWS"])
    st.divider()
    
    if not st.session_state.logged_in:
        st.subheader("🔒 Login")
        u = st.text_input("User", key="u")
        p = st.text_input("Pass", type="password", key="p")
        if st.button("Unlock"):
            if u == "faisal" and p == "trader123":
                st.session_state.logged_in = True
                st.rerun()
    else:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.markdown('<p class="main-title">🚀 LIVE MARKET DATA</p>', unsafe_allow_html=True)
    
    # നിരക്കുകൾ എടുക്കുന്നു
    nifty = get_live_price("^NSEI")
    crude = get_live_price("CL=F")
    aed_inr = get_live_price("AEDINR=X")
    gold_oz = get_live_price("GC=F") # Gold per Ounce
    
    # കറൻസി & ഗോൾഡ് കണക്കുകൂട്ടൽ
    gold_8g_inr = (gold_oz / 31.1035) * 8 * aed_inr * 1.15 # Approx with tax/margin
    
    col1, col2 = st.columns(2)
    col1.metric("NIFTY 50", f"₹ {nifty:,.2f}")
    col2.metric("CRUDE OIL", f"$ {crude:,.2f}")
    
    st.markdown(f'<div class="info-box">💰 AED to INR: ₹ {aed_inr:.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-box">🟡 Gold Price (8g): ₹ {gold_8g_inr:,.0f} (Approx)</div>', unsafe_allow_html=True)

elif mode == "NEWS":
    st.markdown('<p class="main-title">📰 ലൈവ് വാർത്തകൾ</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="text-align: left;">
    <p>🔹 ക്രൂഡ് ഓയിൽ വിലയിൽ നേരിയ മാറ്റം.</p>
    <p>🔹 ഇന്ത്യൻ വിപണിയിൽ മുന്നേറ്റം തുടരുന്നു.</p>
    <p>🔹 ദുബായ് സ്വർണ്ണ വിപണിയിൽ തിരക്ക് വർദ്ധിക്കുന്നു.</p>
    </div>
    """, unsafe_allow_html=True)

elif mode == "JOURNAL":
    if not st.session_state.logged_in:
        st.warning("ഈ ഭാഗം കാണാൻ സൈഡ്ബാറിൽ ലോഗിൻ ചെയ്യുക!")
    else:
        st.markdown('<p class="main-title">📝 ട്രേഡിംഗ് ജേണൽ</p>', unsafe_allow_html=True)
        st.write("സ്വാഗതം ഫൈസൽ, നിന്റെ ട്രേഡുകൾ ഇവിടെ രേഖപ്പെടുത്താം.")

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
