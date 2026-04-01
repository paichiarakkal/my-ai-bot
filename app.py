import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import os

# --- Page Config ---
st.set_page_config(page_title="Faisal's AI Terminal", layout="wide")

# --- 1. വാലറ്റ് ബാലൻസ് ---
if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50 # നിന്റെ വാലറ്റിലെ ബാലൻസ്

# --- 2. ലൈവ് ഡാറ്റാ ഫംഗ്‌ഷൻ ---
def get_exchange_rates():
    try:
        inr_rate = float(yf.download("INR=X", period="1d", progress=False)['Close'].iloc[-1])
        aed_rate = float(yf.download("AED=X", period="1d", progress=False)['Close'].iloc[-1])
        gold_spot = float(yf.download("GC=F", period="1d", progress=False)['Close'].iloc[-1])
        return inr_rate, aed_rate, gold_spot
    except:
        return 83.30, 3.67, 2300.0

# --- 3. AI അസിസ്റ്റന്റ് ലോജിക് (TypeError Fixed) ---
def get_ai_advice(rsi_series, price, ema):
    # RSI ഡാറ്റ ഉണ്ടോ എന്ന് ഉറപ്പുവരുത്തുന്നു
    if rsi_series is None or len(rsi_series) == 0:
        return "⚖️ SYNCING: ഡാറ്റ ശേഖരിക്കുന്നു. അല്പസമയത്തിനകം സിഗ്നൽ ലഭിക്കും...", "#FFD700", "#332B00"
    
    # സീരീസിൽ നിന്ന് അവസാനത്തെ കൃത്യമായ വാല്യൂ എടുക്കുന്നു
    try:
        rsi = float(rsi_series.dropna().iloc[-1])
    except:
        return "⚖️ WAITING: മാർക്കറ്റ് വിശകലനം ചെയ്യുന്നു...", "#FFD700", "#332B00"
    
    if rsi < 35:
        return "🔥 AI BUY SIGNAL: മാർക്കറ്റ് താഴെയാണ്, ഇപ്പോൾ വാങ്ങുന്നത് ലാഭകരമാകും!", "#00FFA3", "#003322"
    elif rsi > 65:
        return "⚡ AI SELL SIGNAL: വില ഉയർന്നിട്ടുണ്ട്, ഇപ്പോൾ വിൽക്കാൻ റെഡി ആയിക്കോളൂ!", "#FF3131", "#330000"
    elif price > ema:
        return "📈 TREND: മാർക്കറ്റ് മുകളിലോട്ടാണ്. ഹോൾഡ് ചെയ്യുന്നത് നല്ലതായിരിക്കും.", "#00D1FF", "#002B36"
    return "⚖️ MARKET WATCH: പുതിയ അവസരത്തിനായി ബോട്ട് നിരീക്ഷിക്കുന്നു...", "#FFD700", "#332B00"

# --- 4. മെയിൻ ഡിസ്‌പ്ലേ ലൂപ്പ് ---
st.sidebar.title("🤖 Faisal AI Control")
asset_choice = st.sidebar.selectbox("Select Asset", ["Gold (Live)", "Nifty 50", "Crude Oil"])

inr, aed, gold_spot = get_exchange_rates()
placeholder = st.empty()

while True:
    with placeholder.container():
        ticker = {"Gold (Live)": "GC=F", "Nifty 50": "^NSEI", "Crude Oil": "CL=F"}[asset_choice]
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        if not df.empty:
            last_p = float(df['Close'].iloc[-1])
            # Technical Indicators
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / loss)))
            ema = df['Close'].ewm(span=20).mean().iloc[-1]

            advice, text_col, bg_col = get_ai_advice(rsi_series, last_p, ema)

            st.metric("Live Wallet Balance", f"₹{st.session_state.balance:,.2f}")

            # AI Advisor Box
            st.markdown(f"""
                <div style="background-color:{bg_col}; padding:20px; border-radius:15px; border: 2px solid {text_col}; margin-bottom: 20px;">
                    <h3 style="color:{text_col}; margin:0;">🚀 Faisal AI Advisor</h3>
                    <p style="color:white; font-size:17px; margin-top:10px;">{advice}</p>
                </div>
            """, unsafe_allow_html=True)

            # Gold Rates (India & Dubai)
            if "Gold" in asset_choice:
                gram_usd = last_p / 31.1035
                pavan_aed = (gram_usd * aed) * 8
                pavan_inr = (gram_usd * inr) * 8
                
                c1, c2 = st.columns(2)
                with c1: st.metric("🇦🇪 Dubai 8g (AED)", f"{pavan_aed:,.2f}")
                with c2: st.metric("🇮🇳 India 8g (INR)", f"₹{pavan_inr:,.2f}")

            # Live Chart
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=450)
            st.plotly_chart(fig, use_container_width=True)

    time.sleep(30)
    st.rerun()
