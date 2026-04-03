import streamlit as st
import pandas as pd
import requests
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")
st_autorefresh(interval=1000, limit=1000, key="faisal_early_alert")

# --- ടെലിഗ്രാം ---
BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
CHAT_ID = "6091133068"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    try: requests.get(url)
    except: pass

# --- ഡാറ്റ അനാലിസിസ് ---
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

            # Supertrend
            df['tr'] = df['high'] - df['low']
            atr = df['tr'].rolling(window=10).mean().iloc[-1]
            mid = (df['high'].iloc[-1] + df['low'].iloc[-1]) / 2
            lower_band = mid - (3 * atr)
            upper_band = mid + (3 * atr)
            
            trend = "BUY 🟢" if price > lower_band else "SELL 🔴"
            
            # --- Early Warning Logic ---
            warning = ""
            if trend == "BUY 🟢" and last_rsi > 70:
                warning = "⚠️ *SELL വരാൻ സാധ്യതയുണ്ട്!* (RSI High)"
            elif trend == "SELL 🔴" and last_rsi < 30:
                warning = "⚠️ *BUY വരാൻ സാധ്യതയുണ്ട്!* (RSI Low)"

            return {"price": price, "rsi": last_rsi, "trend": trend, "warning": warning}
    except: return None

# --- മെയിൻ ഡിസ്പ്ലേ ---
if 'last_signal' not in st.session_state: st.session_state.last_signal = ""
if 'last_warning' not in st.session_state: st.session_state.last_warning = ""

st.title("🚀 Paichi Trader Pro (Advanced)")

def display_data(data, title, mult=1):
    if data:
        p = data['price'] * mult
        st.subheader(title)
        c1, c2, c3 = st.columns(3)
        c1.metric("Live Price", f"₹{p:.2f}")
        c2.metric("RSI (14)", f"{data['rsi']:.2f}")
        c3.metric("Trend", data['trend'])
        
        if data['warning']:
            st.warning(data['warning'])

        # അലേർട്ടുകൾ
        if title == "CRUDE OIL MCX":
            # 1. മെയിൻ സിഗ്നൽ അലേർട്ട്
            if data['trend'] != st.session_state.last_signal:
                send_telegram(f"⚡ *SIGNAL CHANGE!* \nTrend: {data['trend']}\nPrice: ₹{p:.2f}")
                st.session_state.last_signal = data['trend']
            
            # 2. മുൻകൂട്ടിയുള്ള മുന്നറിയിപ്പ് (Early Alert)
            if data['warning'] != st.session_state.last_warning and data['warning'] != "":
                send_telegram(f"🔔 *EARLY ALERT!* \n{data['warning']}\nPrice: ₹{p:.2f}")
                st.session_state.last_warning = data['warning']

display_data(get_analysis("CL=F"), "CRUDE OIL MCX", mult=93.5)
st.divider()
display_data(get_analysis("^NSEI"), "NIFTY 50")
