import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- ഡിസൈൻ സ്റ്റൈൽ (Silver Sidebar & Gold Theme & News Ticker) ---
st.markdown("""
<style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    
    /* സിൽവർ സൈഡ്ബാർ */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #D3D3D3, #C0C0C0, #A9A9A9) !important; 
    }
    
    /* ന്യൂസ് ടിക്കർ (മുകളിലൂടെ നീങ്ങുന്ന വാർത്ത) */
    .ticker-wrap {
        width: 100%; overflow: hidden; background: rgba(0, 0, 0, 0.8);
        padding: 10px 0; border-bottom: 2px solid #FFD700;
    }
    .ticker {
        display: inline-block; white-space: nowrap; padding-right: 100%;
        animation: ticker 25s linear infinite; color: #FFD700; font-weight: bold; font-size: 18px;
    }
    @keyframes ticker {
        0% { transform: translate3d(0, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }

    /* കാർഡുകൾ */
    .price-card { background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #000; margin-bottom: 10px; color: black; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .ai-box { background: #000; color: #FFD700; padding: 15px; border-radius: 12px; margin-top: 15px; border: 1px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ (Live News)
st.markdown("""
<div class="ticker-wrap">
    <div class="ticker">
        📢 ബ്രേക്കിംഗ്: ക്രൂഡ് ഓയിൽ വിലയിൽ നേരിയ വർദ്ധനവ് രേഖപ്പെടുത്തി. 📈 നിഫ്റ്റി 22,700 നിലവാരത്തിൽ തുടരുന്നു. 🟡 സ്വർണ്ണവിലയിൽ മാറ്റമില്ല. 💰 ദിർഹം രൂപ വിനിമയ നിരക്ക് ഇന്ന് 25.23 ആണ്.
    </div>
</div>
""", unsafe_allow_html=True)

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st_autorefresh(interval=30000, key="faisal_final_v1")

# ലൈവ് പ്രൈസ് ഫംഗ്ഷൻ
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# --- സൈഡ് ബാർ (Silver Side) ---
with st.sidebar:
    st.markdown("## 🚀 Paichi Pro")
    
    # AED to INR Converter
    st.write("### 🇦🇪 AED (Dirham) Converter")
    aed_input = st.number_input("Enter AED", value=1.0, step=1.0)
    current_aed_rate = get_live_price("AEDINR=X")
    st.success(f"₹ {aed_input * current_aed_rate:.2f} (INR)")
    
    st.divider()
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "AI ADVISOR"])
    
    if st.session_state.logged_in:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.markdown('<h1 style="text-align:center; color:white; text-shadow: 2px 2px #000;">📈 LIVE MARKET</h1>', unsafe_allow_html=True)
    
    nifty = get_live_price("^NSEI")
    crude = get_live_price("CL=F")
    gold_oz = get_live_price("GC=F")
    
    # Gold calculation (Approx for 8g Indian price)
    gold_8g = (gold_oz / 31.1035) * 8 * current_aed_rate * 1.15
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="price-card"><h3>NIFTY 50</h3><h2>₹ {nifty:,.2f}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="price-card"><h3>CRUDE OIL</h3><h2>$ {crude:,.2f}</h2></div>', unsafe_allow_html=True)
        
    st.markdown(f'<div class="price-card" style="border-left: 5px solid #FFD700;">🟡 Gold Price (8 Gram): ₹ {gold_8g:,.0f} (Approx)</div>', unsafe_allow_html=True)

elif mode == "AI ADVISOR":
    st.markdown('<h1 style="text-align:center; color:white; text-shadow: 2px 2px #000;">🤖 AI ADVISOR</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="ai-box">
        <h3>🎯 ഇന്നത്തെ ട്രേഡിംഗ് നിർദ്ദേശം:</h3>
        <p>മാർക്കറ്റ് ഇപ്പോൾ സൈഡ്‌വേയ്‌സ് (Sideways) മൂവ്‌മെന്റിലാണ്. 22,800 കടന്നാൽ മാത്രം നിഫ്റ്റിയിൽ ലോങ്ങ് പൊസിഷൻ എടുക്കുന്നതാണ് ഉചിതം. ക്രൂഡ് ഓയിൽ ബൈയിംഗ് സോണിലാണ് (Buying Zone).</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Prediction
    crude_val = get_live_price("CL=F")
    st.metric("AI പ്രവചനം (Crude)", f"$ {crude_val + 0.50:.2f}", delta="Bullish")

elif mode == "JOURNAL":
    if not st.session_state.logged_in:
        # Simple login card inside Journal
        st.markdown('<div class="price-card">', unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Unlock Journal"):
            if u == "faisal" and p == "trader123":
                st.session_state.logged_in = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success("ഹലോ ഫൈസൽ, നിന്റെ ജേണൽ ഇവിടെ കാണാം.")

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
