import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import urllib.parse

# 1. വാട്സ്ആപ്പ് അയക്കാനുള്ള ഫങ്ക്ഷൻ
def send_algo_alert(message_text):
    phone = "971551347989"
    apikey = "7463030"
    encoded_message = urllib.parse.quote(message_text)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_message}&apikey={apikey}"
    try:
        requests.get(url)
        st.success("📲 സിഗ്നൽ വാട്സ്ആപ്പിലേക്ക് അയച്ചു!")
    except Exception as e:
        st.error(f"Error: {e}")

# 2. സ്വന്തമായി RSI കണക്കാക്കുന്ന ഫങ്ക്ഷൻ
def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 3. സ്വന്തമായി Supertrend കണക്കാക്കുന്ന ഫങ്ക്ഷൻ
def calculate_supertrend(df, period=7, multiplier=3):
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # ATR കണക്കാക്കുന്നു
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    
    hl2 = (high + low) / 2
    final_upperband = hl2 + (multiplier * atr)
    final_lowerband = hl2 - (multiplier * atr)
    
    # ട്രെൻഡ് കണ്ടുപിടിക്കുന്നു
    supertrend = np.zeros(len(df))
    direction = np.zeros(len(df)) # 1 = BUY, -1 = SELL
    
    for i in range(1, len(df)):
        if close.iloc[i] > final_upperband.iloc[i-1]:
            direction[i] = 1
        elif close.iloc[i] < final_lowerband.iloc[i-1]:
            direction[i] = -1
        else:
            direction[i] = direction[i-1]
            
    return direction

# --- Streamlit UI ---
st.title("🤖 Algo Trading Bot")

ticker = st.text_input("Stock Ticker", "TATAMOTORS.NS")

if st.button("Check Signal"):
    df = yf.download(ticker, period="5d", interval="5m", progress=False)
    
    if not df.empty:
        # ഇൻഡിക്കേറ്ററുകൾ കണക്കാക്കുന്നു
        df['RSI'] = calculate_rsi(df)
        df['ST_Direction'] = calculate_supertrend(df)
        
        last_row = df.iloc[-1]
        current_close = float(last_row['Close'])
        current_rsi = float(last_row['RSI'])
        current_trend = int(last_row['ST_Direction'])
        
        st.write(f"📊 **വില:** {round(current_close, 2)} | **RSI:** {round(current_rsi, 2)}")
        
        # കണ്ടീഷൻ ചെക്കിങ്
        if current_trend == 1 and current_rsi > 50:
            st.success("🟢 STRONG BUY SIGNAL Generated!")
            msg = f"🔥 ALGO ALERT: {ticker} 🔥\n\n🟢 STRONG BUY SIGNAL\n📈 Price: {round(current_close, 2)}\n📊 RSI: {round(current_rsi, 2)}"
            send_algo_alert(msg)
        elif current_trend == -1 and current_rsi < 40:
            st.error("🔴 STRONG SELL SIGNAL Generated!")
            msg = f"📉 ALGO ALERT: {ticker} 📉\n\n🔴 STRONG SELL SIGNAL\n📉 Price: {round(current_close, 2)}\n📊 RSI: {round(current_rsi, 2)}"
            send_algo_alert(msg)
        else:
            st.info("⌛ നിലവിൽ സ്ട്രോങ്ങ് സിഗ്നലുകൾ ഇല്ല. Waiting...")
    else:
        st.error("ഡാറ്റ ലഭ്യപ്പമല്ല!")
