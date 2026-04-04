import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# ലൈവ് പ്രൈസ് ഫംഗ്ഷൻ (Yahoo Finance-ൽ നിന്ന് നേരിട്ട് എടുക്കുന്നു)
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        if not data.empty:
            return data['Close'].iloc[-1]
        return 0.0
    except: return 0.0

# ലൈവ് ഡാറ്റകൾ ശേഖരിക്കുന്നു
aed_inr = get_live_price("AEDINR=X")
nifty_val = get_live_price("^NSEI")
crude_val = get_live_price("CL=F")
gold_val = get_live_price("GC=F")

# ലൈവ് സ്വർണ്ണവില കണക്കുകൂട്ടൽ (22K - 8 Gram)
gold_22k_8g = (gold_val / 31.1035) * 8 * aed_inr * 0.9167 * 1.05
# ക്രൂഡ് ഓയിൽ INR
crude_inr = crude_val * aed_inr * 3.67 

# --- ഡിസൈൻ സ്റ്റൈൽ (Silver Sidebar & Dynamic Ticker) ---
st.markdown(f"""
<style>
    .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }}
    section[data-testid="stSidebar"] {{ 
        background: linear-gradient(180deg, #D3D3D3, #C0C0C0, #A9A9A9) !important; 
    }}
    .ticker-wrap {{
        width: 100%; overflow: hidden; background: rgba(0, 0, 0, 0.9);
        padding: 12px 0; border-bottom: 2px solid #FFD700;
    }}
    .ticker {{
        display: inline-block; white-space: nowrap; padding-right: 100%;
        animation: ticker 30s linear infinite; color: #FFD700; font-weight: bold; font-size: 19px;
    }}
    @keyframes ticker {{
        0% {{ transform: translate3d(100%, 0, 0); }}
        100% {{ transform: translate3d(-100%, 0, 0); }}
    }}
    .price-card {{ 
        background: white; padding: 25px; border-radius: 15px; 
        border-left: 12px solid #000; color: black; text-align: center; 
        box-shadow: 2px 2px 15px rgba(0,0,0,0.2); margin-top: 15px;
    }}
    .stButton>button {{
        width: 100% !important; background-color: #000 !important; color: #FFD700 !important;
        border: 1px solid #FFD700 !important; border-radius: 10px !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- ഡൈനാമിക് ലൈവ് വാർത്താ ബാർ ---
st.markdown(f"""
<div class="ticker-wrap"><div class="ticker">
    📢 ലൈവ് മാർക്കറ്റ് അപ്ഡേറ്റ്സ്: &nbsp;&nbsp;&nbsp; 
    📊 NIFTY 50: ₹{nifty_val:,.2f} &nbsp;&nbsp;&nbsp; 
    🟡 GOLD 22K (8G): ₹{gold_22k_8g:,.0f} &nbsp;&nbsp;&nbsp; 
    💰 AED/INR: ₹{aed_inr:.2f} &nbsp;&nbsp;&nbsp; 
    🛢️ CRUDE OIL: ₹{crude_inr:,.0f} &nbsp;&nbsp;&nbsp; 
    🚀 പൈച്ചി പ്രോ ട്രേഡർ ലൈവ് ആണ്...
</div></div>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_live_ticker_v3")

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'market_idx' not in st.session_state: st.session_state.market_idx = "^NSEI"

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("## 🚀 Paichi Pro")
    st.markdown(f"""<div style="background:white; padding:10px; border-radius:10px; text-align:center; border:2px solid #000;">
        <h4 style="margin:0;">NIFTY LIVE</h4>
        <h2 style="margin:0; color:#B38728;">₹ {nifty_val:,.2f}</h2>
    </div>""", unsafe_allow_html=True)
    
    st.divider()
    main_menu = st.radio("MAIN MENU:", ["MARKET", "JOURNAL", "DASHBOARD", "AI ADVISOR"])
    
    if main_menu == "MARKET":
        st.write("🎯 **തിരഞ്ഞെടുക്കുക:**")
        if st.button("📈 NIFTY 50"): st.session_state.market_idx = "^NSEI"
        if st.button("🏦 BANK NIFTY"): st.session_state.market_idx = "^NSEBANK"
        if st.button("💳 FIN NIFTY"): st.session_state.market_idx = "NIFTY_FIN_SERVICE.NS"
        if st.button("📊 SENSEX"): st.session_state.market_idx = "^BSESN"
    
    st.divider()
    st.write(f"🇦🇪 1 AED = ₹ {aed_inr:.2f}")

# --- മെയിൻ ബോഡി ---
if main_menu == "MARKET":
    idx_names = {"^NSEI": "NIFTY 50", "^NSEBANK": "BANK NIFTY", "NIFTY_FIN_SERVICE.NS": "FIN NIFTY", "^BSESN": "SENSEX"}
    p_now = get_live_price(st.session_state.market_idx)
    
    st.markdown(f"""<div class="price-card">
        <h2 style="margin:0;">{idx_names.get(st.session_state.market_idx, "MARKET")}</h2>
        <h1 style="font-size: 55px; color: #B38728; margin:10px 0;">₹ {p_now:,.2f}</h1>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="price-card" style="border-left: 10px solid #FF4B4B;"><h3>CRUDE OIL (INR)</h3><h2>₹ {crude_inr:,.0f}</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="price-card" style="border-left: 10px solid #FFD700;"><h3>GOLD 22K (8G)</h3><h2>₹ {gold_22k_8g:,.0f}</h2></div>', unsafe_allow_html=True)

elif main_menu == "AI ADVISOR":
    st.markdown('<h2 style="text-align:center; color:white;">🤖 AI ADVISOR</h2>', unsafe_allow_html=True)
    st.markdown('<div class="price-card"><h3>Market Analysis</h3><p>Trend: Bullish | Support: 22,400</p></div>', unsafe_allow_html=True)

elif main_menu == "JOURNAL" or main_menu == "DASHBOARD":
    if not st.session_state.logged_in:
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("Login"):
            if u == "faisal" and p == "trader123":
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.success(f"ഹലോ ഫൈസൽ, നിന്റെ {main_menu} ഇവിടെ ലഭ്യമാണ്.")

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
