import streamlit as st
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# 1 സെക്കൻഡ് ഓട്ടോ റിഫ്രഷ്
st_autorefresh(interval=1000, limit=100, key="faisal_ai_v4")

# --- ടെലിഗ്രാം സെറ്റിംഗ്സ് ---
BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
CHAT_ID = "6091133068"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    try: requests.get(url)
    except: pass

# --- AI പ്രൈസ് പ്രെഡിക്ഷൻ ലോജിക് ---
def predict_next_price(prices):
    if len(prices) > 10:
        y = np.array(prices[-10:]).reshape(-1, 1)
        x = np.arange(10).reshape(-1, 1)
        model = LinearRegression()
        model.fit(x, y)
        prediction = model.predict([[10]])
        return float(prediction[0][0])
    return None

# --- ഡാറ്റ അനാലിസിസ് ---
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
            # RSI Calculation
            delta = pd.Series(df_close).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
            
            # Trend Logic (Simple)
            avg = sum(df_close[-10:]) / 10
            trend = "BUY 🟢" if price > avg else "SELL 🔴"
            
            # AI Prediction
            ai_price = predict_next_price(df_close)
            
            return {"price": price, "rsi": rsi, "trend": trend, "ai": ai_price}
    except: return None

# --- മെയിൻ ഡിസ്പ്ലേ ---
if 'last_signal' not in st.session_state: st.session_state.last_signal = ""

st.title("🚀 Paichi AI Trader Pro")
st.write("AI ഉപയോഗിച്ച് ക്രൂഡ് ഓയിൽ, നിഫ്റ്റി പ്രവചനങ്ങൾ തത്സമയം കാണുക.")

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
        
        # AI പ്രവചനം കാണിക്കുന്നു
        diff = ai_p - p
        color = "normal" if diff > 0 else "inverse"
        col4.metric("AI Predicted (1m)", f"₹{ai_p:.2f}", delta=f"{diff:.2f}", delta_color=color)

        # ടെലിഗ്രാം അലേർട്ട്
        if name == "CRUDE OIL MCX":
            if data['trend'] != st.session_state.last_signal:
                msg = f"⚡ *SIGNAL CHANGE!*\n{name}\nTrend: {data['trend']}\nPrice: ₹{p:.2f}\nAI Forecast: ₹{ai_p:.2f}"
                send_telegram(msg)
                st.session_state.last_signal = data['trend']

# --- റീഡർ ---
display_card("CL=F", "CRUDE OIL MCX", mult=93.5)
st.divider()
display_card("^NSEI", "NIFTY 50")
st.divider()
display_card("^NSEBANK", "BANK NIFTY")
# --- 22K GOLD 8 GRAM (1 PAVAN) INDIAN PRICE ---
# ഇവിടെ mult=52.5 എന്നത് ഡോളർ വിലയെ ഏകദേശം ഇന്ത്യൻ 22K പവൻ വിലയിലേക്ക് മാറ്റാനുള്ളതാണ്.
display_card("GC=F", "22K GOLD 8 GRAM (PAVAN)", mult=52.5) 
