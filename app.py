import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# ലൈവ് പ്രൈസ് ഫംഗ്ഷൻ
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# ലൈവ് ഡാറ്റ എടുക്കുന്നു
current_aed_rate = get_live_price("AEDINR=X")
n_total = get_live_price("^NSEI")

# --- ഡിസൈൻ സ്റ്റൈൽ (Silver Sidebar & Live Ticker) ---
st.markdown(f"""
<style>
    .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }}
    section[data-testid="stSidebar"] {{ 
        background: linear-gradient(180deg, #D3D3D3, #C0C0C0, #A9A9A9) !important; 
    }}
    .ticker-wrap {{
        width: 100%; overflow: hidden; background: rgba(0, 0, 0, 0.9);
        padding: 10px 0; border-bottom: 2px solid #FFD700;
    }}
    .ticker {{
        display: inline-block; white-space: nowrap; padding-right: 100%;
        animation: ticker 30s linear infinite; color: #FFD700; font-weight: bold; font-size: 18px;
    }}
    @keyframes ticker {{
        0% {{ transform: translate3d(100%, 0, 0); }}
        100% {{ transform: translate3d(-100%, 0, 0); }}
    }}
    .price-card {{ 
        background: white; padding: 25px; border-radius: 15px; 
        border-left: 10px solid #000; color: black; text-align: center; 
        box-shadow: 2px 2px 15px rgba(0,0,0,0.2); margin-top: 15px;
    }}
    .stButton>button {{
        width: 100% !important; background-color: #000 !important; color: #FFD700 !important;
        border: 1px solid #FFD700 !important; border-radius: 10px !important; margin-bottom: 5px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ (Live AED Rate)
st.markdown(f"""
<div class="ticker-wrap"><div class="ticker">
    📢 ലൈവ് വാർത്തകൾ: നിഫ്റ്റിയിൽ മുന്നേറ്റം തുടരുന്നു.. സ്വർണ്ണവില 8 ഗ്രാമിന് മാറ്റമില്ലാതെ തുടരുന്നു.. 💰 ദിർഹം വിനിമയ നിരക്ക് ഇപ്പോൾ ₹{current_aed_rate:.2f} ആണ്..
</div></div>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_full_app_v2")

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'market_idx' not in st.session_state:
    st.session_state.market_idx = "^NSEI"

# --- സൈഡ് ബാർ (ബട്ടണുകൾ ഇവിടെ) ---
with st.sidebar:
    st.markdown("## 🚀 Paichi Pro")
    
    # NIFTY TOTAL Display
    st.markdown(f"""
    <div style="background:white; padding:10px; border-radius:10px; text-align:center; border:2px solid #000;">
        <h4 style="margin:0;">NIFTY TOTAL</h4>
        <h2 style="margin:0; color:#B38728;">₹ {n_total:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    # പ്രധാന മെനു
    main_menu = st.radio("MAIN MENU:", ["MARKET", "JOURNAL", "DASHBOARD", "AI ADVISOR"])
    
    st.divider()
    # മാർക്കറ്റ് ബട്ടണുകൾ (MARKET സെലക്ട് ചെയ്താൽ മാത്രം)
    if main_menu == "MARKET":
        st.write("🎯 **തിരഞ്ഞെടുക്കുക:**")
        if st.button("📈 NIFTY 50"): st.session_state.market_idx = "^NSEI"
        if st.button("🏦 BANK NIFTY"): st.session_state.market_idx = "^NSEBANK"
        if st.button("💳 FIN NIFTY"): st.session_state.market_idx = "NIFTY_FIN_SERVICE.NS"
        if st.button("📊 SENSEX"): st.session_state.market_idx = "^BSESN"
    
    st.divider()
    if st.session_state.logged_in:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- മെയിൻ ബോഡി ---
if main_menu == "MARKET":
    idx_names = {"^NSEI": "NIFTY 50", "^NSEBANK": "BANK NIFTY", "NIFTY_FIN_SERVICE.NS": "FIN NIFTY", "^BSESN": "SENSEX"}
    current_price = get_live_price(st.session_state.market_idx)
    
    st.markdown(f"""
    <div class="price-card">
        <h2 style="margin:0;">{idx_names[st.session_state.market_idx]} LIVE</h2>
        <h1 style="font-size: 55px; color: #B38728; margin:10px 0;">₹ {current_price:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

    # Gold Calculation
    g_oz = get_live_price("GC=F")
    gold_8g = (g_oz / 31.1035) * 8 * current_aed_rate * 1.15
    st.markdown(f'<div class="price-card" style="border-left: 10px solid #FFD700;">🟡 Gold Price (8g Approx): ₹ {gold_8g:,.0f}</div>', unsafe_allow_html=True)

elif main_menu == "AI ADVISOR":
    st.markdown('<h2 style="text-align:center; color:white;">🤖 AI ADVISOR</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:black; color:#FFD700; padding:20px; border-radius:15px; border:1px solid #FFD700;">
        <h3>🎯 ഇന്നത്തെ ട്രേഡിംഗ് നിർദ്ദേശം:</h3>
        <p>വിപണി ഇപ്പോൾ സ്ട്രോങ്ങ് ബുല്ലിഷ് ട്രെൻഡിലാണ്. സ്റ്റോപ്പ് ലോസ് കൃത്യമായി പാലിച്ചു മാത്രം ട്രേഡ് ചെയ്യുക.</p>
    </div>
    """, unsafe_allow_html=True)

elif main_menu == "JOURNAL" or main_menu == "DASHBOARD":
    if not st.session_state.logged_in:
        st.markdown('<div class="price-card">', unsafe_allow_html=True)
        st.subheader("🔒 ലോഗിൻ ചെയ്യുക")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Unlock"):
            if u == "faisal" and p == "trader123":
                st.session_state.logged_in = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success(f"ഹലോ ഫൈസൽ, നീ ഇപ്പോൾ {main_menu} സെക്ഷനിലാണ്.")
        if main_menu == "DASHBOARD":
             st.write("ട്രേഡിംഗ് ഡാറ്റ ഇവിടെ ലഭ്യമാണ്.")

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
