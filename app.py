import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. Page Configuration (Icon Set to Faisal's Photo) ---
st.set_page_config(
    page_title="Faisal's AI Terminal", 
    # ഇവിടെ നമ്മൾ നിന്റെ ഫോട്ടോ തന്നെ ഐക്കൺ ആയി നൽകുന്നു
    page_icon="my_photo.jpg",
    layout="wide"
)

# --- 2. വാലറ്റ് ബാലൻസ് അപ്‌ഡേറ്റ് ---
if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50 # നിന്റെ വാലറ്റിലെ ബാലൻസ്

# --- 3. സൂപ്പർട്രെൻഡ് ലോജിക് (No Library Required) ---
def custom_supertrend(df, period=7, multiplier=3):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    hl2 = (df['High'] + df['Low']) / 2
    df['tr'] = np.maximum(df['High'] - df['Low'], 
                          np.maximum(abs(df['High'] - df['Close'].shift(1)), 
                                     abs(df['Low'] - df['Close'].shift(1))))
    atr = df['tr'].rolling(period).mean()
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
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
        supertrend[i] = final_bands['lower'].iloc[i] if direction[i] == 1 else final_bands['upper'].iloc[i]
    df['ST'] = supertrend
    df['ST_DIR'] = direction
    return df

# --- 4. സൈഡ്‌ബാർ (Faisal's Photo & Calculator Fix) ---
try:
    # നിന്റെ ഫോട്ടോ സൈഡ്‌ബാറിൽ മുകളിലായി കാണിക്കുന്നു
    st.sidebar.image("my_photo.jpg", caption="Faisal's Bot", width=150)
except:
    st.sidebar.error("📷 ഫോൾഡറിൽ 'my_photo.jpg' കാണുന്നില്ല. അത് ചേർത്താൽ നിന്റെ ചിത്രം ഇവിടെ വരും.")

st.sidebar.title("🤖 Faisal AI terminal")

# INR to AED (Dirham) Calculator
st.sidebar.subheader("💱 Currency Converter")
calc_mode = st.sidebar.selectbox("Conversion", ["INR to AED (Dirham)", "AED to INR"])
input_amt = st.sidebar.number_input("Amount", value=1.0)

try:
    rates = yf.download("AEDINR=X", period="1d", progress=False)
    if isinstance(rates.columns, pd.MultiIndex): rates.columns = rates.columns.get_level_values(0)
    live_rate = float(rates['Close'].iloc[-1])
    
    if calc_mode == "INR to AED (Dirham)":
        res = input_amt / live_rate
        st.sidebar.success(f"₹{input_amt} = **{res:.2f} AED**")
    else:
        res = input_amt * live_rate
        st.sidebar.success(f"{input_amt} AED = **₹{res:.2f}**")
    st.sidebar.write(f"Live Rate: 1 AED = ₹{live_rate:.2f}")
except:
    st.sidebar.error("Rate fetch failed")

st.sidebar.divider()
asset_choice = st.sidebar.selectbox("Select Asset", ["Crude Oil (MCX)", "Nifty 50", "Gold (Live)"])

# --- 5. മെയിൻ ഡിസ്‌പ്ലേ ലൂപ്പ് ---
placeholder = st.empty()

while True:
    with placeholder.container():
        ticker_map = {"Crude Oil (MCX)": "CL=F", "Nifty 50": "^NSEI", "Gold (Live)": "GC=F"}
        df = yf.download(ticker_map[asset_choice], period="1d", interval="1m", progress=False)
        
        if not df.empty:
            # MCX പ്രൈസ് കൺവേർഷൻ
            if asset_choice == "Crude Oil (MCX)":
                df = df * 91.5 
            
            df = custom_supertrend(df)
            last_p = float(df['Close'].iloc[-1])
            st_dir = df['ST_DIR'].iloc[-1]

            st.metric("Live Wallet Balance", f"₹{st.session_state.balance:,.2f}") #

            # AI Advisor Signal
            if st_dir == 1:
                msg, col, bg = "🚀 AI BUY: മാർക്കറ്റ് പോസിറ്റീവ് ആണ്!", "#00FFA3", "#003322"
            else:
                msg, col, bg = "📉 AI SELL: മാർക്കറ്റ് നെഗറ്റീവ് ആണ്!", "#FF3131", "#330000"

            st.markdown(f'<div style="background:{bg};padding:20px;border-radius:15px;border:2px solid {col};">'
                        f'<h3 style="color:{col};margin:0;">🚀 Faisal AI Advisor</h3>'
                        f'<p style="color:white;margin-top:10px;font-size:18px;">{msg}</p></div>', unsafe_allow_html=True)

            # ചാർട്ട്
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
            fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='yellow', width=2), name="Supertrend"))
            fig.update_layout(template="plotly_dark", height=450, title=f"{asset_choice} Live")
            st.plotly_chart(fig, use_container_width=True)

    time.sleep(30)
    st.rerun()
