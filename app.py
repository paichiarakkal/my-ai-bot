import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")
st_autorefresh(interval=1000, limit=100, key="faisal_v7")

# --- സൈഡ് ബാർ (Side Bar Menu) ---
st.sidebar.title("🚀 Paichi Trader")

# 1. കറൻസി കൺവേർട്ടർ
st.sidebar.subheader("💰 Currency")
aed_input = st.sidebar.number_input("AED to INR", value=1.0)
inr_result = aed_input * 22.75
st.sidebar.success(f"₹ {inr_result:.2f}")

st.sidebar.divider()

# 2. മെയിൻ മെനു (ബട്ടണുകൾക്ക് പകരം സെലക്ഷൻ)
st.sidebar.subheader("📊 Market Menu")
menu = st.sidebar.radio("Select Category:", ["📈 INDEX", "🔥 COMMODITY", "✨ GOLD"])

st.sidebar.divider()
st.sidebar.info("Al Barsha, Dubai Edition")

# --- AI & Analysis Logic ---
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
        response = requests.get(url, headers=headers)
        data = response.json()
        result = data['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        ohlc = result['indicators']['quote'][0]['close']
        df_close = [p for p in ohlc if p is not None]
        
        if len(df_close) > 20:
            delta = pd.Series(df_close).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            trend = "BUY 🟢" if price > (sum(df_close[-10:]) / 10) else "SELL 🔴"
            ai_price = predict_next_price(df_close)
            return {"price": price, "rsi": rsi, "trend": trend, "ai": ai_price}
    except: return None

def display_card(symbol, name, mult=1):
    data = get_analysis(symbol)
    if data:
        p = data['price'] * mult
        ai_p = data['ai'] * mult if data['ai'] else 0
        st.write(f"## {name}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Price", f"₹{p:.2f}")
        c2.metric("Trend", data['trend'])
        c3.metric("RSI", f"{data['rsi']:.2f}")
        diff = ai_p - p
        c4.metric("AI Prediction", f"₹{ai_p:.2f}", delta=f"{diff:.2f}")
        st.divider()

# --- മെയിൻ പേജ് (മെനുവിൽ സെലക്ട് ചെയ്യുന്നത് അനുസരിച്ച് മാറും) ---
st.title(f"Market Data: {menu}")

if menu == "📈 INDEX":
    display_card("^NSEI", "NIFTY 50")
    display_card("^NSEBANK", "BANK NIFTY")
    display_card("^BSESN", "SENSEX")
    display_card("NIFTY_FIN_SERVICE.NS", "FIN NIFTY")
    display_card("^NSEMDCP50", "MIDCAP SELECT")
    display_card("INDF.NS", "GIFT NIFTY")

elif menu == "🔥 COMMODITY":
    display_card("CL=F", "CRUDE OIL MCX", mult=93.5)

elif menu == "✨ GOLD":
    display_card("GC=F", "22K GOLD 8 GRAM (PAVAN)", mult=20.5)
