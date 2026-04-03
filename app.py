import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# --- 1. പേജ് സെറ്റിംഗ്സ് ---
st.set_page_config(
    page_title="Paichi AI Trader Pro",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. വിഷ്വൽസ് & ടെക്സ്റ്റ് ക്ലിയറിറ്റി (CSS) ---
st.markdown("""
<style>
    /* മെയിൻ പേജ് & ടെക്സ്റ്റ് */
    .stApp { background-color: #121212; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #1E1E1E; }
    
    /* മെട്രിക്സ് ബോക്സ് - നമ്പറുകൾ വ്യക്തമാക്കാൻ */
    div[data-testid="metric-container"] {
        background-color: #262626;
        border: 1px solid #444;
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: bold !important; font-size: 32px !important; }
    label[data-testid="stMetricLabel"] { color: #ADADAD !important; }
    
    h1, h2, h3 { color: #FFFFFF !important; font-weight: bold !important; }
    
    /* ഇൻപുട്ട് ബോക്സുകൾ */
    div.stNumberInput input, div.stSelectbox div[data-baseweb="select"] {
        color: white !important;
        background-color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=2000, limit=100, key="faisal_clear_nav_v13")

# --- ലൈവ് കറൻസി റേറ്റ് ---
def get_live_aed_rate():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        return response['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 25.22 

# --- സൈഡ് ബാർ (സബ് മെനു ഇവിടെ ശരിയാക്കിയിട്ടുണ്ട്) ---
st.sidebar.title("🚀 Paichi Trader")

# കറൻസി കാൽക്കുലേറ്റർ
st.sidebar.subheader("💰 Live Currency")
live_rate = get_live_aed_rate()
aed_val = st.sidebar.number_input("Enter AED", value=1.0)
st.sidebar.success(f"₹ {aed_val * live_rate:.2f}")
st.sidebar.caption(f"1 AED = ₹ {live_rate:.2f}")

st.sidebar.divider()

# മെയിൻ മെനു
st.sidebar.subheader("📊 Market Menu")
main_menu = st.sidebar.radio("Select Category:", ["📈 INDEX", "🔥 COMMODITY", "✨ GOLD"])

st.sidebar.divider() # മെനുവിന് താഴെ ഒരു വരി ഇട്ടു

# 3. ഉപമെനുകൾ (ഇവിടെയാണ് തിരുത്തൽ വരുത്തിയത്)
selected_item = None

# നമ്മൾ റേഡിയോ ബട്ടൺ ഞെക്കുമ്പോൾ അതിന്റെ താഴെത്തന്നെ selectbox വരാൻ st.sidebar.selectbox ഉപയോഗിച്ചു.
if main_menu == "📈 INDEX":
    selected_item = st.sidebar.selectbox("Choose Index:", 
        ["All Indices", "NIFTY 50", "BANK NIFTY", "SENSEX", "FIN NIFTY", "MIDCAP SELECT", "GIFT NIFTY"],
        key="index_select")

elif main_menu == "🔥 COMMODITY":
    selected_item = st.sidebar.selectbox("Choose Commodity:", ["All Commodities", "CRUDE OIL MCX"],
        key="commodity_select")

elif main_menu == "✨ GOLD":
    selected_item = st.sidebar.selectbox("Choose Gold Type:", ["22K GOLD 8 GRAM"],
        key="gold_select")

st.sidebar.divider()
st.sidebar.info("Al Barsha, Dubai Edition")

# --- AI Logic ---
def predict_next_price(prices):
    if len(prices) > 10:
        y = np.array(prices[-10:]).reshape(-1, 1)
        x = np.arange(10).reshape(-1, 1)
        model = LinearRegression()
        model.fit(x, y)
        return float(model.predict([[10]])[0][0])
    return None

def get_analysis(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        result = response['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        df_close = [p for p in result['indicators']['quote'][0]['close'] if p is not None]
        
        if len(df_close) > 20:
            avg = sum(df_close[-10:]) / 10
            trend = "BUY 🟢" if price > avg else "SELL 🔴"
            delta = pd.Series(df_close).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            ai_price = predict_next_price(df_close)
            return {"price": price, "rsi": rsi, "trend": trend, "ai": ai_price}
    except: return None

def display_card(symbol, name, mult=1):
    data = get_analysis(symbol)
    if data:
        p = data['price'] * mult
        ai_p = data['ai'] * mult if data['ai'] else 0
        st.write(f"## {name}") # ടൈറ്റിൽ വ്യക്തമാക്കാൻ
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Price", f"₹{p:.2f}")
        
        # ട്രെൻഡ് സിഗ്നൽ
        trend_color = "#2E7D32" if "BUY" in data['trend'] else "#C62828"
        c2.markdown(f"<div style='background-color:{trend_color}; padding:15px; border-radius:8px; color:white; font-weight:bold; text-align:center; font-size:20px; margin-top:10px;'>{data['trend']}</div>", unsafe_allow_html=True)
        
        c3.metric("RSI (14)", f"{data['rsi']:.2f}")
        diff = ai_p - p
        c4.metric("AI Prediction", f"₹{ai_p:.2f}", delta=f"{diff:.2f}")
        st.divider()

# --- മെയിൻ ഡിസ്പ്ലേ ---
st.title(f"Paichi AI: {selected_item}")

if selected_item in ["NIFTY 50", "All Indices"]: display_card("^NSEI", "NIFTY 50")
if selected_item in ["BANK NIFTY", "All Indices"]: display_card("^NSEBANK", "BANK NIFTY")
if selected_item in ["SENSEX", "All Indices"]: display_card("^BSESN", "SENSEX")
if selected_item in ["FIN NIFTY", "All Indices"]: display_card("NIFTY_FIN_SERVICE.NS", "FIN NIFTY")
if selected_item in ["MIDCAP SELECT", "All Indices"]: display_card("^NSEMDCP50", "MIDCAP SELECT")
if selected_item in ["GIFT NIFTY", "All Indices"]: display_card("INDF.NS", "GIFT NIFTY")

if selected_item in ["CRUDE OIL MCX", "All Commodities"]: display_card("CL=F", "CRUDE OIL MCX", mult=93.5)

if selected_item == "22K GOLD 8 GRAM":
    display_card("GC=F", "22K GOLD 8 GRAM (PAVAN)", mult=20.5)
