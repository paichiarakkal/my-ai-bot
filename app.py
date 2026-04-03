import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression

# --- 1. പേജ് സെറ്റിംഗ്സ് ---
st.set_page_config(
    page_title="Paichi AI Trader Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. അൾട്രാ ക്ലിയർ വിഷ്വൽ ഫിക്സ് (CSS) ---
# ഇവിടെയാണ് ഗോൾഡും സിൽവറും നമ്മൾ സെറ്റ് ചെയ്യുന്നത്
st.markdown("""
<style>
    /* മെയിൻ ബാക്ക്ഗ്രൗണ്ട് - ഗോൾഡ് ഗ്രേഡിയന്റ് */
    .stApp { 
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
        color: #000000 !important; 
    }
    
    /* സ്ലൈഡ് ബാർ - സിൽവർ ഗ്രേഡിയന്റ് */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; 
        border-right: 1px solid #444;
    }
    
    /* സൈഡ്ബാറിലെ അക്ഷരങ്ങൾ കറുപ്പ് നിറത്തിൽ തെളിഞ്ഞു കാണാൻ */
    div[data-testid="stSidebar"] label, 
    div[data-testid="stSidebar"] p, 
    div[data-testid="stSidebar"] span,
    div[data-testid="stWidgetLabel"] p {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }

    /* മെയിൻ ടൈറ്റിൽ വെളുപ്പ് നിറത്തിൽ */
    .main-title {
        color: #FFFFFF !important;
        font-size: 38px !important;
        font-weight: 800 !important;
        text-align: center;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.4);
        margin-top: -30px;
    }

    /* ലൈവ് പ്രൈസ് വെളുപ്പ് നിറത്തിൽ */
    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* AI Prediction മഞ്ഞ നിറത്തിൽ */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetricValue"] > div {
        color: #FFFF00 !important;
    }

    /* മെട്രിക്സ് ലേബലുകൾ (Live Price, Status) */
    div[data-testid="stMetricLabel"] > div {
        color: #000000 !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ഡാറ്റ ഫെച്ചിംഗ് ലോജിക് ---
def get_analysis(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        result = res['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        df_close = [p for p in result['indicators']['quote'][0]['close'] if p is not None]
        
        ai_p = 0
        if len(df_close) > 10:
            y = np.array(df_close[-10:]).reshape(-1, 1)
            x = np.arange(10).reshape(-1, 1)
            model = LinearRegression().fit(x, y)
            ai_p = float(model.predict([[10]])[0][0])
            
        trend = "BUY 🟢" if price > (sum(df_close[-10:])/10) else "SELL 🔴"
        return {"price": price, "trend": trend, "ai": ai_p}
    except: return None

# --- 4. സ്ലൈഡ് ബാർ (സിൽവർ ലുക്ക്) ---
# ഇതിനുള്ളിലെ അക്ഷരങ്ങളെല്ലാം നമ്മൾ കറുപ്പ് നിറത്തിലാക്കി
with st.sidebar:
    st.markdown('<p style="font-size:24px; font-weight:bold; color:black;">🚀 Paichi Trader</p>', unsafe_allow_html=True)
    
    # AED to INR കൺവെർട്ടർ
    st.write("💰 **AED TO INR**")
    aed_rate = 22.75 # ലൈവ് റേറ്റ് അനുസരിച്ച് മാറ്റാം
    aed_input = st.number_input("Enter Durham (AED)", value=1.0, step=1.0)
    st.success(f"₹ {aed_input * aed_rate:.2f}")
    
    st.divider()
    
    # കാറ്റഗറി സെലക്ഷൻ
    st.write("📊 **CHOOSE CATEGORY**")
    main_cat = st.radio("", ["INDEX", "COMMODITY", "GOLD"], label_visibility="collapsed")
    
    selected = None
    if main_cat == "INDEX":
        selected = st.selectbox("Choose Index:", ["NIFTY 50", "BANK NIFTY", "GIFT NIFTY", "SENSEX"])
    elif main_cat == "COMMODITY":
        selected = st.selectbox("Choose:", ["CRUDE OIL MCX"])
    elif main_cat == "GOLD":
        selected = st.selectbox("Choose Unit:", ["22K GOLD (1 Gram)", "22K GOLD (8 Gram)"])

# --- 5. മെയിൻ പേജ് (ഗോൾഡ് ലുക്ക്) ---
# ടൈറ്റിൽ വെളുപ്പ് നിറത്തിൽ കൊടുത്തിരിക്കുന്നു
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

def display(symbol, name, mult=mult=1):
    data = get_analysis(symbol)
    if data:
        p = data['price'] * mult
        ai = data['ai'] * mult
        st.subheader(f"📍 {name}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Price", f"₹{p:.2f}")
        t_color = "#1B5E20" if "BUY" in data['trend'] else "#B71C1C"
        c2.markdown(f"<div style='background-color:{t_color}; padding:10px; border-radius:8px; color:white; text-align:center; font-weight:bold;'>{data['trend']}</div>", unsafe_allow_html=True)
        c3.metric("Status", "Active")
        diff = ai - p
        c4.metric("AI Prediction", f"₹{ai:.2f}", delta=f"{diff:.2f}")
        st.divider()

if selected == "NIFTY 50": display("^NSEI", "NIFTY 50")
elif selected == "BANK NIFTY": display("^NSEBANK", "BANK NIFTY")
elif selected == "GIFT NIFTY": display("INDF.NS", "GIFT NIFTY")
elif selected == "SENSEX": display("^BSESN", "SENSEX")
elif selected == "CRUDE OIL MCX": display("CL=F", "CRUDE OIL", mult=mult=93.5)
elif selected == "22K GOLD (1 Gram)": display("GC=F", "GOLD 1G", mult=mult=2.56)
elif selected == "22K GOLD (8 Gram)": display("GC=F", "GOLD 8G (PAVAN)", mult=mult=20.5)
