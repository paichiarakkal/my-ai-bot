import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- Page Config ---
st.set_page_config(page_title="Faisal's AI Terminal", layout="wide")

# --- 1. വാലറ്റ് ബാലൻസ് ---
if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50 #

# --- 2. ലൈബ്രറി ഇല്ലാതെ സൂപ്പർട്രെൻഡ് കണക്കാക്കുന്ന ലോജിക് ---
def custom_supertrend(df, period=7, multiplier=3):
    # MultiIndex പ്രശ്നം ഒഴിവാക്കുന്നു
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    hl2 = (df['High'] + df['Low']) / 2
    # ATR കണക്കാക്കുന്നു
    df['tr'] = np.maximum(df['High'] - df['Low'], 
                          np.maximum(abs(df['High'] - df['Close'].shift(1)), 
                                     abs(df['Low'] - df['Close'].shift(1))))
    atr = df['tr'].rolling(period).mean()
    
    # Upper & Lower Bands
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    
    # സൂപ്പർട്രെൻഡ് ലോജിക്
    final_bands = pd.DataFrame(index=df.index)
    final_bands['upper'] = upperband
    final_bands['lower'] = lowerband
    
    supertrend = [0.0] * len(df)
    direction = [1] * len(df)
    
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > final_bands['upper'].iloc[i-1]:
            direction[i] = 1
        elif df['Close'].iloc[i] < final_bands['lower'].iloc[i-1]:
            direction[i] = -1
        else:
            direction[i] = direction[i-1]
            
        if direction[i] == 1:
            supertrend[i] = final_bands['lower'].iloc[i]
        else:
            supertrend[i] = final_bands['upper'].iloc[i]
            
    df['ST'] = supertrend
    df['ST_DIR'] = direction
    return df

# --- 3. സൈഡ്‌ബാർ & എക്സ്ചേഞ്ച് റേറ്റ് ---
st.sidebar.title("🤖 Faisal AI Terminal")
asset_choice = st.sidebar.selectbox("Select Asset", ["Crude Oil (MCX)", "Nifty 50", "Gold (Live)"])

# Exchange Calculator
try:
    inr_rate = float(yf.download("INR=X", period="1d", progress=False)['Close'].iloc[-1])
    st.sidebar.write(f"Current USD-INR: **₹{inr_rate:.2f}**")
except: pass

# --- 4. മെയിൻ ഡിസ്‌പ്ലേ ---
placeholder = st.empty()

while True:
    with placeholder.container():
        ticker_map = {"Crude Oil (MCX)": "CL=F", "Nifty 50": "^NSEI", "Gold (Live)": "GC=F"}
        df = yf.download(ticker_map[asset_choice], period="1d", interval="1m", progress=False)
        
        if not df.empty:
            # MCX പ്രൈസ് കൺവേർഷൻ (103 -> 9400)
            if asset_choice == "Crude Oil (MCX)":
                df = df * 91.5 
            
            # സൂപ്പർട്രെൻഡ് ലൈൻ ചേർക്കുന്നു
            df = custom_supertrend(df)
            
            last_p = float(df['Close'].iloc[-1])
            st_dir = df['ST_DIR'].iloc[-1]

            st.metric("Live Balance", f"₹{st.session_state.balance:,.2f}")

            # AI Advisor Signal
            if st_dir == 1:
                msg, col, bg = "🚀 AI BUY: ട്രെൻഡ് പോസിറ്റീവ് ആണ്!", "#00FFA3", "#003322"
            else:
                msg, col, bg = "📉 AI SELL: ട്രെൻഡ് താഴോട്ടാണ്!", "#FF3131", "#330000"

            st.markdown(f'<div style="background:{bg};padding:20px;border-radius:15px;border:2px solid {col};">'
                        f'<h3 style="color:{col};margin:0;">🚀 Faisal AI Advisor</h3>'
                        f'<p style="color:white;margin-top:10px;">{msg}</p></div>', unsafe_allow_html=True)

            # ലൈവ് ചാർട്ട്
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
            fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='yellow', width=2), name="Supertrend"))
            
            fig.update_layout(template="plotly_dark", height=450, title=f"{asset_choice} | Price: {last_p:,.2f}")
            st.plotly_chart(fig, use_container_width=True)

    time.sleep(30)
    st.rerun()
