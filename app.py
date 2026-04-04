import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser # ഇപ്പോൾ ഇത് വർക്ക് ആകും!
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# ലൈവ് പ്രൈസ് ഫംഗ്ഷൻ
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1] if not data.empty else 0.0
    except: return 0.0

# ലൈവ് വാർത്തകൾ ശേഖരിക്കാനുള്ള ഫംഗ്ഷൻ (Malayalam News)
def get_latest_news():
    try:
        # ഗൂഗിൾ ന്യൂസ് മലയാളം ഫീഡ്
        feed = feedparser.parse("https://news.google.com/rss/search?q=kerala+news+in+malayalam&hl=ml&gl=IN&ceid=IN:ml")
        news_titles = [entry.title for entry in feed.entries[:5]]
        return " | ".join(news_titles)
    except:
        return "വാർത്തകൾ ലഭ്യമാക്കുന്നതിൽ തടസ്സം നേരിടുന്നു.."

# ലൈവ് ഡാറ്റകൾ ശേഖരിക്കുന്നു
aed_inr = get_live_price("AEDINR=X")
nifty_val = get_live_price("^NSEI")
crude_usd = get_live_price("CL=F")
gold_spot = get_live_price("GC=F")
external_news = get_latest_news() # പുറത്തെ വാർത്തകൾ ഇവിടെ വരും

# സ്വർണ്ണവില കറക്റ്റ് കണക്കുകൂട്ടൽ (22K - 8 Gram) - ₹70k+ റേഞ്ച്
gold_8g_inr = (gold_spot / 31.1035) * 8 * aed_inr * 0.9167 * 1.15
# ക്രൂഡ് ഓയിൽ INR
crude_inr = crude_usd * aed_inr * 3.67 

# --- ഡിസൈൻ സ്റ്റൈൽ (Silver Sidebar & Gold Theme) ---
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
        animation: ticker 40s linear infinite; color: #FFD700; font-weight: bold; font-size: 18px;
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
</style>
""", unsafe_allow_html=True)

# ലൈവ് വാർത്താ ബാർ (വാർത്തകളും വിലകളും ഒരേ ടിക്കറിൽ)
st.markdown(f"""
<div class="ticker-wrap"><div class="ticker">
    🔴 ലൈവ് വാർത്തകൾ: {external_news} &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; 
    📊 NIFTY 50: ₹{nifty_val:,.2f} &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; 
    🟡 22K GOLD (8G): ₹{gold_8g_inr:,.0f} &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; 
    💰 AED/INR: ₹{aed_inr:.2f} &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; 
    🛢️ CRUDE: ₹{crude_inr:,.0f}
</div></div>
""", unsafe_allow_html=True)

st_autorefresh(interval=60000, key="faisal_news_ready_v5")

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("## 🚀 Paichi Pro")
    st.divider()
    menu = st.radio("MENU:", ["MARKET", "JOURNAL", "DASHBOARD", "AI ADVISOR"])
    st.divider()
    st.write(f"🇦🇪 1 AED = ₹ {aed_inr:.2f}")

# --- മെയിൻ ബോഡി ---
if menu == "MARKET":
    st.markdown(f"""<div class="price-card">
        <h2 style="margin:0;">NIFTY 50 LIVE</h2>
        <h1 style="font-size: 55px; color: #B38728; margin:10px 0;">₹ {nifty_val:,.2f}</h1>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="price-card" style="border-left: 10px solid #FF4B4B;"><h3>CRUDE OIL (INR)</h3><h2>₹ {crude_inr:,.0f}</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="price-card" style="border-left: 10px solid #FFD700;"><h3>GOLD 22K (8G)</h3><h2>₹ {gold_8g_inr:,.0f}</h2></div>', unsafe_allow_html=True)

elif menu == "AI ADVISOR":
    st.markdown('<div class="price-card"><h3>🤖 AI Advisor</h3><p>വിപണി ഇപ്പോൾ സജീവമാണ്. ട്രെൻഡ് നോക്കി ട്രേഡ് ചെയ്യുക.</p></div>', unsafe_allow_html=True)

else:
    st.markdown(f'<div class="price-card"><h3>📂 {menu}</h3><p>സെക്ഷൻ റെഡി ആണ്.</p></div>', unsafe_allow_html=True)

st.markdown('<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
