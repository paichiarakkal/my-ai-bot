import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
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
gold_oz = get_live_price("GC=F") # അന്താരാഷ്ട്ര മാർക്കറ്റിലെ Gold per Ounce

# സ്വർണ്ണവില 8 ഗ്രാമിലേക്ക് മാറ്റുന്നു (Indian Price Approx)
# Formula: (Ounce Price / 31.1035) * 8 * Exchange Rate + Indian Taxes/Charges
gold_8g_inr = (gold_oz / 31.1035) * 8 * current_aed_rate * 1.15

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
</style>
""", unsafe_allow_html=True)

# ന്യൂസ് ടിക്കർ (ഇവിടെ സ്വർണ്ണവില 8 ഗ്രാമിന് എത്രയാണെന്ന് ലൈവ് ആയി കാണിക്കും)
st.markdown(f"""
<div class="ticker-wrap"><div class="ticker">
    📢 ലൈവ് വാർത്തകൾ: നിഫ്റ്റിയിൽ മുന്നേറ്റം തുടരുന്നു.. 🟡 ഇന്നത്തെ സ്വർണ്ണവില (8 ഗ്രാം): ₹{gold_8g_inr:,.0f}.. 💰 ദിർഹം വിനിമയ നിരക്ക് ഇപ്പോൾ ₹{current_aed_rate:.2f} ആണ്..
</div></div>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_gold_fix")

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("## 🚀 Paichi Pro")
    st.divider()
    st.write(f"🇦🇪 1 AED = ₹ {current_aed_rate:.2f}")
    st.write(f"🟡 Gold 8g = ₹ {gold_8g_inr:,.0f}")

# --- മെയിൻ ബോഡി ---
st.markdown(f"""
<div class="price-card" style="border-left: 15px solid #FFD700;">
    <h3 style="margin:0;">ഇന്നത്തെ സ്വർണ്ണവില (8 ഗ്രാം - പവൻ)</h3>
    <h1 style="font-size: 65px; color: #B38728; margin:10px 0;">₹ {gold_8g_inr:,.0f}</h1>
    <p style="color:gray;">അന്താരാഷ്ട്ര മാർക്കറ്റ് നിരക്ക് അനുസരിച്ചുള്ള ഏകദേശ വില</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
