import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- ഡിസൈൻ സ്റ്റൈൽ (Silver Sidebar, Gold Theme, Buttons) ---
st.markdown("""
<style>
    /* മെയിൻ ഗോൾഡൻ ബാക്ക്ഗ്രൗണ്ട് */
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    
    /* സിൽവർ സൈഡ്ബാർ */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #D3D3D3, #C0C0C0, #A9A9A9) !important; 
    }
    
    /* മുകളിലൂടെ നീങ്ങുന്ന മലയാളം വാർത്ത (Ticker) */
    .ticker-wrap {
        width: 100%; overflow: hidden; background: rgba(0, 0, 0, 0.9);
        padding: 10px 0; border-bottom: 2px solid #FFD700;
    }
    .ticker {
        display: inline-block; white-space: nowrap; padding-right: 100%;
        animation: ticker 30s linear infinite; color: #FFD700; font-weight: bold; font-size: 18px;
    }
    @keyframes ticker {
        0% { transform: translate3d(100%, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }

    /* മാർക്കറ്റ് ബട്ടണുകളുടെ സ്റ്റൈൽ */
    .stButton>button { 
        width: 100%; border-radius: 10px; background-color: #000 !important; 
        color: #FFD700 !important; font-weight: bold; border: 1px solid #FFD700;
        height: 45px; font-size: 16px; margin-bottom: 5px;
    }
    
    /* പ്രൈസ് കാർഡ് */
    .price-card { 
        background: white; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #000; color: black; text-align: center; 
        box-shadow: 2px 2px 15px rgba(0,0,0,0.2); margin-top: 10px;
    }
    
    /* സൈഡ്ബാർ നിഫ്റ്റി ഡിസ്‌പ്ലേ */
    .sidebar-nifty {
        background: white; color: black; padding: 15px; 
        border-radius: 10px; text-align: center; border: 2px solid #000;
    }
</style>
""", unsafe_allow_html=True)

# 1. മലയാളം ന്യൂസ് ടിക്കർ
st.markdown("""
<div class="ticker-wrap"><div class="ticker">
    📢 ലൈവ് വാർത്തകൾ: നിഫ്റ്റിയിൽ മുന്നേറ്റം തുടരുന്നു.. സ്വർണ്ണവില 8 ഗ്രാമിന് മാറ്റമില്ലാതെ തുടരുന്നു.. ക്രൂഡ് ഓയിൽ വിപണിയിൽ ബൈയിംഗ് ട്രെൻഡ്.. ദിർഹം വിനിമയ നിരക്ക് ഇന്ന് ₹22.68..
</div></div>
""", unsafe_allow_html=True)

# ലൈവ് പ്രൈസ് ഫംഗ്ഷൻ
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

# ഓട്ടോ റിഫ്രഷ് (30 സെക്കൻഡ്)
st_autorefresh(interval=30000, key="faisal_final_ui")

# --- സൈഡ് ബാർ (Silver Side) ---
with st.sidebar:
    st.markdown("## 🚀 Paichi Pro")
    
    # NIFTY TOTAL Display (Sidebar)
    nifty_total = get_live_price("^NSEI")
    st.markdown(f"""
    <div class="sidebar-nifty">
        <h4 style="margin:0;">NIFTY TOTAL</h4>
        <h2 style="margin:0; color:#B38728;">₹ {nifty_total:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "AI ADVISOR"])
    
    # AED to INR Rate
    aed_rate = get_live_price("AEDINR=X")
    st.write(f"🇦🇪 1 AED = ₹ {aed_rate:.2f}")

# --- മെയിൻ ബോഡി ---
if mode == "MARKET":
    st.markdown('<h1 style="text-align:center; color:white; text-shadow: 2px 2px #000;">📊 MARKET DASHBOARD</h1>', unsafe_allow_html=True)
    
    # മാർക്കറ്റ് ബട്ടണുകൾ (5 സെക്ഷൻ)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    if 'index_choice' not in st.session_state:
        st.session_state.index_choice = "^NSEI"

    if col1.button("NIFTY 50"): st.session_state.index_choice = "^NSEI"
    if col2.button("BANK NIFTY"): st.session_state.index_choice = "^NSEBANK"
    if col3.button("FIN NIFTY"): st.session_state.index_choice = "NIFTY_FIN_SERVICE.NS"
    if col4.button("SENSEX"): st.session_state.index_choice = "^BSESN"
    if col5.button("MIDCAP"): st.session_state.index_choice = "^NSEMDCP50"

    # സെലക്ട് ചെയ്ത ഇൻഡക്സ് വിവരങ്ങൾ
    idx_map = {
        "^NSEI": "NIFTY 50",
        "^NSEBANK": "BANK NIFTY",
        "NIFTY_FIN_SERVICE.NS": "FIN NIFTY",
        "^BSESN": "SENSEX",
        "^NSEMDCP50": "MIDCAP 50"
    }
    
    current_idx = st.session_state.index_choice
    price = get_live_price(current_idx)
    
    st.markdown(f"""
    <div class="price-card">
        <h3>{idx_map[current_idx]} LIVE</h3>
        <h1 style="font-size: 45px; color: #B38728;">₹ {price:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

    # സ്വർണ്ണവിലയും ക്രൂഡ് ഓയിലും
    st.write("---")
    g_oz = get_live_price("GC=F")
    gold_8g = (g_oz / 31.1035) * 8 * aed_rate * 1.15
    st.markdown(f'<div class="price-card" style="border-left: 10px solid #FFD700;">🟡 Gold 8g (Approx): ₹ {gold_8g:,.0f}</div>', unsafe_allow_html=True)

elif mode == "AI ADVISOR":
    st.markdown('<h2 style="text-align:center; color:white;">🤖 AI ADVISOR</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:black; color:#FFD700; padding:20px; border-radius:15px; border:1px solid #FFD700;">
        <h3>🎯 ഇന്നത്തെ ട്രേഡിംഗ് ടിപ്‌സ്:</h3>
        <p>നിഫ്റ്റി ഇപ്പോൾ സ്ട്രോങ്ങ് സപ്പോർട്ടിലാണ്. 22,450 സ്റ്റോപ്പ് ലോസ് വെച്ച് ലോങ്ങ് പൊസിഷൻ നോക്കാവുന്നതാണ്. ബാങ്ക് നിഫ്റ്റിയിൽ കരുതലോടെ ട്രേഡ് ചെയ്യുക.</p>
    </div>
    """, unsafe_allow_html=True)

elif mode == "JOURNAL":
    st.info("നിന്റെ ട്രേഡിംഗ് ഹിസ്റ്ററി ഇവിടെ ലഭ്യമാണ്.")

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
