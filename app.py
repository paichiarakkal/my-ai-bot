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

# ലൈവ് ഡാറ്റകൾ എടുക്കുന്നു
current_aed_rate = get_live_price("AEDINR=X")
n_total = get_live_price("^NSEI")
crude_usd = get_live_price("CL=F")
gold_oz = get_live_price("GC=F")

# കണക്കുകൂട്ടലുകൾ (INR)
crude_inr = crude_usd * current_aed_rate * 3.67 
gold_8g_inr = (gold_oz / 31.1035) * 8 * current_aed_rate * 1.15

# --- ഡിസൈൻ സ്റ്റൈൽ (Silver Sidebar & Live Ticker) ---
st.markdown(f"""
<style>
    /* മെയിൻ ഗോൾഡ് ബാക്ക്ഗ്രൗണ്ട് */
    .stApp {{ background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }}
    
    /* സിൽവർ സൈഡ്ബാർ */
    section[data-testid="stSidebar"] {{ 
        background: linear-gradient(180deg, #D3D3D3, #C0C0C0, #A9A9A9) !important; 
    }}
    
    /* ന്യൂസ് ടിക്കർ (Malayalam) */
    .ticker-wrap {{
        width: 100%; overflow: hidden; background: rgba(0, 0, 0, 0.9);
        padding: 10px 0; border-bottom: 2px solid #FFD700;
    }}
    .ticker {{
        display: inline-block; white-space: nowrap; padding-right: 100%;
        animation: ticker 25s linear infinite; color: #FFD700; font-weight: bold; font-size: 18px;
    }}
    @keyframes ticker {{
        0% {{ transform: translate3d(100%, 0, 0); }}
        100% {{ transform: translate3d(-100%, 0, 0); }}
    }}
    
    /* പ്രൈസ് കാർഡുകൾ */
    .price-card {{ 
        background: white; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #000; color: black; text-align: center; 
        box-shadow: 2px 2px 15px rgba(0,0,0,0.2); margin-top: 15px;
    }}
    
    /* സൈഡ്ബാർ ബട്ടണുകൾ */
    .stButton>button {{
        width: 100% !important; background-color: #000 !important; color: #FFD700 !important;
        border: 1px solid #FFD700 !important; border-radius: 10px !important; margin-bottom: 5px !important;
    }}
</style>
""", unsafe_allow_html=True)

# 1. മലയാളം ലൈവ് ന്യൂസ് ടിക്കർ
st.markdown(f"""
<div class="ticker-wrap"><div class="ticker">
    📢 ലൈവ് വാർത്തകൾ: നിഫ്റ്റി ഇപ്പോൾ ₹{n_total:,.2f} നിലവാരത്തിൽ.. 🟡 സ്വർണ്ണവില 8 ഗ്രാമിന് ₹{gold_8g_inr:,.0f}.. 💰 ദിർഹം നിരക്ക് ₹{current_aed_rate:.2f}.. 📈 ക്രൂഡ് ഓയിൽ വിപണിയിൽ മുന്നേറ്റം..
</div></div>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_final_production_v1")

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'market_idx' not in st.session_state:
    st.session_state.market_idx = "^NSEI"

# --- സൈഡ് ബാർ (Silver Side) ---
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
    main_menu = st.radio("MAIN MENU:", ["MARKET", "JOURNAL", "DASHBOARD", "AI ADVISOR"])
    
    st.divider()
    # MARKET ബട്ടണുകൾ സൈഡ്ബാറിൽ
    if main_menu == "MARKET":
        st.write("🎯 **ഇൻഡക്സ് തിരഞ്ഞെടുക്കുക:**")
        if st.button("📈 NIFTY 50"): st.session_state.market_idx = "^NSEI"
        if st.button("🏦 BANK NIFTY"): st.session_state.market_idx = "^NSEBANK"
        if st.button("💳 FIN NIFTY"): st.session_state.market_idx = "NIFTY_FIN_SERVICE.NS"
        if st.button("📊 SENSEX"): st.session_state.market_idx = "^BSESN"
        if st.button("📉 MIDCAP"): st.session_state.market_idx = "^NSEMDCP50"
    
    st.divider()
    st.write(f"🇦🇪 1 AED = ₹ {current_aed_rate:.2f}")
    if st.session_state.logged_in:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- മെയിൻ കണ്ടന്റ് ---
if main_menu == "MARKET":
    idx_names = {"^NSEI": "NIFTY 50", "^NSEBANK": "BANK NIFTY", "NIFTY_FIN_SERVICE.NS": "FIN NIFTY", "^BSESN": "SENSEX", "^NSEMDCP50": "MIDCAP 50"}
    price = get_live_price(st.session_state.market_idx)
    
    st.markdown(f"""
    <div class="price-card">
        <h2 style="margin:0;">{idx_names[st.session_state.market_idx]} LIVE</h2>
        <h1 style="font-size: 55px; color: #B38728; margin:10px 0;">₹ {price:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

    # Commodity Section (Crude & Gold INR)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="price-card" style="border-left: 10px solid #FF4B4B;">
            <h3>CRUDE OIL (INR)</h3>
            <h2 style="color: #FF4B4B;">₹ {crude_inr:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="price-card" style="border-left: 10px solid #FFD700;">
            <h3>GOLD 8G (INR)</h3>
            <h2 style="color: #B38728;">₹ {gold_8g_inr:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

elif main_menu == "AI ADVISOR":
    st.markdown('<h2 style="text-align:center; color:white; text-shadow: 2px 2px #000;">🤖 AI ADVISOR</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:black; color:#FFD700; padding:20px; border-radius:15px; border:1px solid #FFD700;">
        <h3>🎯 ഇന്നത്തെ മാർക്കറ്റ് നിരീക്ഷണം:</h3>
        <p>വിപണിയിൽ ബുല്ലിഷ് ട്രെൻഡ് തുടരാൻ സാധ്യതയുണ്ട്. ക്രൂഡ് ഓയിൽ ട്രേഡുകളിൽ ശ്രദ്ധിക്കുക. കൃത്യമായ സ്റ്റോപ്പ് ലോസ് ഉപയോഗിക്കുക.</p>
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
        st.success(f"ഹലോ ഫൈസൽ, നിന്റെ {main_menu} ഇവിടെ ലഭ്യമാണ്.")

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
