import streamlit as st
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ് & സ്റ്റൈൽ (Gold & Silver Theme)
st.set_page_config(page_title="Paichi AI Trader", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] *, div[data-testid="stWidgetLabel"] p { color: #000 !important; font-weight: bold !important; }
    .main-title { color: #FFF; font-size: 38px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    div[data-testid="stMetricValue"] > div { color: #FFF !important; font-weight: 800; }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetricValue"] > div { color: #FFFF00 !important; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=2000, key="faisal_refresh")

# 2. ഡാറ്റ എടുക്കാനുള്ള ഫംഗ്ഷൻ (Simplified)
def get_analysis(symbol):
    try:
        res = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        data = res['chart']['result'][0]
        price = data['meta']['regularMarketPrice']
        close = [p for p in data['indicators']['quote'][0]['close'] if p is not None]
        
        ai_p = 0
        if len(close) > 5:
            model = LinearRegression().fit(np.arange(5).reshape(-1, 1), np.array(close[-5:]).reshape(-1, 1))
            ai_p = float(model.predict([[5]])[0][0])
        
        return {"p": price, "t": "BUY 🟢" if price > np.mean(close[-5:]) else "SELL 🔴", "ai": ai_p}
    except: return None

# 3. സ്ലൈഡ് ബാർ (Silver Sidebar)
with st.sidebar:
    st.title("🚀 Paichi Trader")
    aed = st.number_input("AED to INR", value=1.0)
    st.success(f"₹ {aed * 22.75:.2f}")
    st.divider()
    cat = st.radio("CATEGORY:", ["INDEX", "COMMODITY", "GOLD"])
    
    # ഓരോ കാറ്റഗറിയിലെയും ഓപ്ഷനുകൾ
    opts = {
        "INDEX": [("^NSEI", "NIFTY 50"), ("^NSEBANK", "BANK NIFTY"), ("INDF.NS", "GIFT NIFTY")],
        "COMMODITY": [("CL=F", "CRUDE OIL MCX", 93.5)],
        "GOLD": [("GC=F", "GOLD 1G", 2.56), ("GC=F", "GOLD 8G", 20.5)]
    }
    sel_name = st.selectbox("Select Item:", [i[1] for i in opts[cat]])
    sel_data = next(i for i in opts[cat] if i[1] == sel_name)

# 4. മെയിൻ പേജ് ഡിസ്പ്ലേ (Gold Main Page)
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

data = get_analysis(sel_data[0])
if data:
    m = sel_data[2] if len(sel_data) > 2 else 1
    st.subheader(f"📍 {sel_data[1]}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Price", f"₹{data['p']*m:.2f}")
    c2.markdown(f"<div style='background:{'#1B5E20' if 'BUY' in data['t'] else '#B71C1C'};padding:10px;border-radius:8px;color:#FFF;text-align:center;font-weight:bold;'>{data['t']}</div>", unsafe_allow_html=True)
    c3.metric("Status", "Active")
    c4.metric("AI Prediction", f"₹{data['ai']*m:.2f}", delta=f"{(data['ai']-data['p'])*m:.2f}")
    
