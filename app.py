import streamlit as st
import pandas as pd
import requests
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")

# 1 Second Auto Refresh
st_autorefresh(interval=1000, limit=1000, key="faisal_final_telegram")

# --- TELEGRAM SETTINGS ---
BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
CHAT_ID = "6091133068" # നിന്റെ ID ഇവിടെ അപ്ഡേറ്റ് ചെയ്തു

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    try:
        requests.get(url)
    except:
        pass

# --- TRADING LOGIC ---
def get_analysis(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        result = data['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        ohlc = result['indicators']['quote'][0]
        
        df = pd.DataFrame({'close': ohlc['close'], 'high': ohlc['high'], 'low': ohlc['low']}).dropna()

        if len(df) > 20:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            last_rsi = float(rsi.iloc[-1])

            df['tr'] = df['high'] - df['low']
            atr = df['tr'].rolling(window=10).mean().iloc[-1]
            mid = (df['high'].iloc[-1] + df['low'].iloc[-1]) / 2
            lower_band = mid - (3 * atr)
            
            trend = "BUY 🟢" if price > lower_band else "SELL 🔴"
            return {"price": price, "rsi": last_rsi, "trend": trend}
    except:
        return None

# --- UI & LOGIC ---
st.sidebar.title("💎 Paichi Menu")
choice = st.sidebar.radio("സേവനം:", ["Commodities & Forex", "Indian Indices"])

if 'last_signal' not in st.session_state:
    st.session_state.last_signal = ""

def display_data(data, title, mult=1):
    if data:
        p = data['price'] * mult
        st.subheader(title)
        c1, c2, c3 = st.columns(3)
        c1.metric("Price", f"₹{p:.2f}")
        c2.metric("RSI", f"{data['rsi']:.2f}")
        c3.metric("Supertrend", data['trend'])
        
        if title == "CRUDE OIL MCX":
            if data['trend'] != st.session_state.last_signal:
                msg = f"🚀 *CRUDE OIL ALERT!* \nTrend: {data['trend']}\nPrice: ₹{p:.2f}"
                send_telegram(msg)
                st.session_state.last_signal = data['trend']

if choice == "Indian Indices":
    display_data(get_analysis("^NSEI"), "NIFTY 50")
    st.divider()
    display_data(get_analysis("^NSEBANK"), "BANK NIFTY")

elif choice == "Commodities & Forex":
    display_data(get_analysis("CL=F"), "CRUDE OIL MCX", mult=93.5)
    st.divider()
    a_data = get_analysis("AEDINR=X")
    if a_data: st.metric("1 AED to INR", f"₹{a_data['price']:.2f}")
