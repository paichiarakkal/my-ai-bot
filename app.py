import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- ഡിസൈൻ സ്റ്റൈൽ (Silver Sidebar & News Ticker) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #D3D3D3, #C0C0C0, #A9A9A9) !important; 
    }
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
    /* സൈഡ്ബാർ ബട്ടൺ സ്റ്റൈൽ */
    div[data-testid="stSidebarNav"] + div button {
        width: 100% !important; background-color: #000 !important; color: #FFD700 !important;
        border: 1px solid #FFD700 !important; border-radius: 10px !important; margin-bottom: 5px !important;
    }
    .price-card { 
        background: white; padding: 30px; border-radius: 20px; 
        border-left: 15px solid #000; color: black; text-align: center; 
        box-shadow: 2px 2px 20px rgba(0,0,0,0.3); margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ
st.markdown('<div class="ticker-wrap"><div class="ticker">📢 ലൈവ് വാർത്തകൾ: വിപണിയിൽ മുന്നേറ്റം തുടരുന്നു.. സ്വർണ്ണവിലയിൽ മാറ്റമില്ല.. ക്രൂഡ് ഓയിൽ വിപണി നിരീക്ഷണത്തിൽ.. ദിർഹം നിരക്ക് ₹22.68..</div></div>', unsafe_allow_html=True)

# ലൈവ് പ്രൈസ് ഫംഗ്ഷൻ
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

st_autorefresh(interval=30000, key="faisal_sidebar_update")

# --- സൈഡ് ബാർ (ബട്ടണുകൾ ഇവിടെ) ---
with st.sidebar:
    st.markdown("## 🚀 Paichi Pro")
    
    # NIFTY TOTAL (Sidebari Main Bari)
    n_total = get_live_price("^NSEI")
    st.markdown(f"""
    <div style="background:white; padding:10px; border-radius:10px; text-align:center; border:2px solid #000;">
        <h4 style="margin:0;">NIFTY TOTAL</h4>
        <h2 style="margin:0; color:#B38728;">₹ {n_total:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # മാർക്കറ്റ് സെലക്ഷൻ ബട്ടണുകൾ സൈഡ്ബാറിൽ
    st.write("🎯 **തിരഞ്ഞെടുക്കുക:**")
    if st.button("📈 NIFTY 50"): st.session_state.market_idx = "^NSEI"
    if st.button("🏦 BANK NIFTY"): st.session_state.market_idx = "^NSEBANK"
    if st.button("💳 FIN NIFTY"): st.session_state.market_idx = "NIFTY_FIN_SERVICE.NS"
    if st.button("📊 SENSEX"): st.session_state.market_idx = "^BSESN"
    if st.button("📉 MIDCAP"): st.session_state.market_idx = "^NSEMDCP50"
    
    if 'market_idx' not in st.session_state:
        st.session_state.market_idx = "^NSEI"
    
    st.divider()
    # Currency
    aed_rate = get_live_price("AEDINR=X")
    st.write(f"🇦🇪 1 AED = ₹ {aed_rate:.2f}")

# --- മെയിൻ ബോഡി ---
idx_names = {
    "^NSEI": "NIFTY 50",
    "^NSEBANK": "BANK NIFTY",
    "NIFTY_FIN_SERVICE.NS": "FIN NIFTY",
    "^BSESN": "SENSEX",
    "^NSEMDCP50": "MIDCAP 50"
}

st.markdown(f'<h1 style="text-align:center; color:white; text-shadow: 2px 2px #000;">MARKET DASHBOARD</h1>', unsafe_allow_html=True)

current_price = get_live_price(st.session_state.market_idx)

# സെലക്ട് ചെയ്ത ഐറ്റത്തിന്റെ വലിയ ഡിസ്‌പ്ലേ
st.markdown(f"""
<div class="price-card">
    <h2 style="margin:0;">{idx_names[st.session_state.market_idx]} LIVE</h2>
    <h1 style="font-size: 60px; color: #B38728; margin:10px 0;">₹ {current_price:,.2f}</h1>
    <p style="color:gray;">Last Updated: {datetime.datetime.now().strftime('%H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

# സ്വർണ്ണവില (Common Info)
g_oz = get_live_price("GC=F")
gold_8g = (g_oz / 31.1035) * 8 * aed_rate * 1.15
st.markdown(f'<div class="price-card" style="border-left: 15px solid #FFD700; padding:15px;">🟡 Gold 8g (Approx): ₹ {gold_8g:,.0f}</div>', unsafe_allow_html=True)

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
