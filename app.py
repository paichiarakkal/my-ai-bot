import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")
st_autorefresh(interval=1000, limit=100, key="faisal_final_v5")

# --- സൈഡ് ബാർ (INR to AED Converter) ---
st.sidebar.title("💰 Currency Converter")
st.sidebar.subheader("INR to AED")
inr_input = st.sidebar.number_input("Enter Amount (INR)", value=1000.0)
aed_rate = 0.044 # ഏകദേശ ദുർഹം റേറ്റ് (ഇത് മാറ്റാം)
aed_result = inr_input * aed_rate
st.sidebar.success(f"AED: {aed_result:.2f}")

st.sidebar.divider()
st.sidebar.info("Paichi AI Trader - Dubai Edition")

# --- ടെലിഗ്രാം ---
BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
CHAT_ID = "6091133068"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    try: requests.get(url)
    except: pass

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

# --- മെയിൻ പേജ് ഡിസ്പ്ലേ ---
if 'last_signal' not in st.session_state: st.session_state.last_signal = ""

st.title("🚀 Paichi AI Trader Pro")

def display_card(symbol, name, mult=1):
    data = get_analysis(symbol)
    if data:
        p = data['price'] * mult
        ai_p = data['ai'] * mult if data['ai'] else 0
        st.subheader(f"📊 {name}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Live Price", f"₹{p:.2f}")
        col2.metric("Trend", data['trend'])
        col3.metric("RSI (14)", f"{data['rsi']:.2f}")
        diff = ai_p - p
        col4.metric("AI Prediction", f"₹{ai_p:.2f}", delta=f"{diff:.2f}")

        if name == "CRUDE OIL MCX" and data['trend'] != st.session_state.last_signal:
            send_telegram(f"⚡ *SIGNAL CHANGE!*\n{name}\nTrend: {data['trend']}\nPrice: ₹{p:.2f}")
            st.session_state.last_signal = data['trend']

# --- എല്ലാ ബട്ടണുകളും മെയിൻ പേജിൽ വരാൻ ---
display_card("CL=F", "CRUDE OIL MCX", mult=93.5)
st.divider()
display_card("^NSEI", "NIFTY 50")
st.divider()
display_card("^NSEBANK", "BANK NIFTY")
st.divider()
display_card("GC=F", "22K GOLD 8 GRAM (PAVAN)", mult=20.5)
