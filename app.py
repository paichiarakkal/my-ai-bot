import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import telebot
import threading

# 1. ടെലിഗ്രാം ബോട്ട് സെറ്റപ്പ്
API_TOKEN = '8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA'
bot = telebot.TeleBot(API_TOKEN)

def run_bot():
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except: pass

if "bot_started" not in st.session_state:
    threading.Thread(target=run_bot, daemon=True).start()
    st.session_state.bot_started = True

# 2. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Faisal Pro Smart Bot", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🚀 ഫൈസൽ പ്രോ സ്മാർട്ട് ഡാഷ്‌ബോർഡ്</h1>", unsafe_allow_html=True)

# --- കറൻസി കാൽക്കുലേറ്റർ (Currency Calculator) ---
st.sidebar.header("💰 Currency Calculator")
aed_input = st.sidebar.number_input("ദിർഹം നൽകുക (AED)", min_value=0.0, value=1.0)

try:
    # ലൈവ് റേറ്റ് എടുക്കുന്നു
    rate_data = yf.Ticker("AEDINR=X").history(period="1d")
    current_rate = rate_data['Close'].iloc[-1]
    inr_result = aed_input * current_rate
    st.sidebar.success(f"{aed_input} AED = {inr_result:.2f} INR")
    st.sidebar.write(f"ഇന്നത്തെ റേറ്റ്: **{current_rate:.2f}**")
except:
    st.sidebar.error("റേറ്റ് ലഭ്യമായില്ല")

# --- ചാർട്ട് സെലക്ഷൻ (Tabs) ---
st.write("### 📈 ലൈവ് ചാർട്ടുകൾ")
tab1, tab2, tab3 = st.tabs(["Nifty 50", "Crude Oil", "AED to INR"])

def draw_chart(symbol, title):
    try:
        df = yf.Ticker(symbol).history(period="1mo", interval="5m")
        if not df.empty:
            df['MA20'] = df['Close'].rolling(window=20).mean()
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='yellow', width=2), name='Trend Line'))
            
            fig.update_layout(
                title=title,
                xaxis_rangeslider_visible=False,
                template='plotly_dark',
                height=650, # ചാർട്ട് വലുതാക്കി
                yaxis=dict(side='right', tickformat='.2f')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"**നിലവിലെ വില: {df['Close'].iloc[-1]:.2f}**")
        else:
            st.warning("ഡാറ്റ ലഭ്യമല്ല.")
    except Exception as e:
        st.error(f"Error: {e}")

with tab1:
    draw_chart("^NSEI", "Nifty 50 Live")

with tab2:
    draw_chart("CL=F", "Crude Oil Live")

with tab3:
    draw_chart("AEDINR=X", "AED to INR Live")

st.divider()
st.info("💡 ഓരോ ടാബിലും ക്ലിക്ക് ചെയ്ത് നിനക്ക് ആവശ്യമുള്ള ചാർട്ട് മാത്രം കാണാൻ സാധിക്കും.")
