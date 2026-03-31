import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import telebot
import threading

# 1. ടെലിഗ്രാം ബോട്ട്
API_TOKEN = '8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA'
bot = telebot.TeleBot(API_TOKEN)

def run_bot():
    try: bot.infinity_polling(timeout=10)
    except: pass

if "bot_started" not in st.session_state:
    threading.Thread(target=run_bot, daemon=True).start()
    st.session_state.bot_started = True

# 2. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Faisal Pro Trader", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00E676;'>📈 ഫൈസൽ പ്രോ ട്രേഡിംഗ് ടرمینൽ</h1>", unsafe_allow_html=True)

# --- സൈഡ്‌ബാറിലെ കാൽക്കുലേറ്റർ ---
st.sidebar.header("💰 Currency Calc")
aed_val = st.sidebar.number_input("AED നൽകുക", min_value=0.0, value=1.0)
try:
    rate = yf.Ticker("AEDINR=X").history(period="1d")['Close'].iloc[-1]
    st.sidebar.success(f"{aed_val} AED = {aed_val*rate:.2f} INR")
except: st.sidebar.error("Rate Error")

# --- ചാർട്ട് ഫങ്ക്ഷൻ (Zoom & Indicators സഹിതം) ---
def draw_advanced_chart(symbol, title):
    try:
        df = yf.Ticker(symbol).history(period="1mo", interval="5m")
        if df.empty:
            st.warning("ഡാറ്റ ലഭ്യമല്ല.")
            return

        # Indicators കണക്കാക്കുന്നു
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        
        # Subplots (Price + RSI)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, row_heights=[0.7, 0.3])

        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                   low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
        
        # Moving Averages
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='yellow', width=1.5), name='MA20'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], line=dict(color='cyan', width=1.5), name='MA50'), row=1, col=1)

        # Chart Layout (Zoom Enable)
        fig.update_layout(
            height=700,
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            dragmode='zoom', # സൂം ചെയ്യാൻ സഹായിക്കുന്നു
            yaxis=dict(side='right', title='Price'),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        # ടച്ച് ചെയ്താൽ സൂം ചെയ്യാൻ പ്ലോട്ട്‌ലി ടൂൾസ് ഓൺ ചെയ്യുന്നു
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
        st.write(f"**നിലവിലെ {title} വില: {df['Close'].iloc[-1]:.2f}**")
        
    except Exception as e:
        st.error(f"Error: {e}")

# --- ടാബുകൾ (നിഫ്റ്റി വേണമെങ്കിൽ നിഫ്റ്റി മാത്രം) ---
tab1, tab2, tab3 = st.tabs(["📊 NIFTY 50", "⛽ CRUDE OIL", "💵 AED to INR"])

with tab1:
    draw_advanced_chart("^NSEI", "Nifty 50")

with tab2:
    draw_advanced_chart("CL=F", "Crude Oil")

with tab3:
    draw_advanced_chart("AEDINR=X", "AED to INR")

st.info("💡 ചാർട്ടിൽ രണ്ട് വിരൽ ഉപയോഗിച്ച് സൂം ചെയ്യാനും (Zoom), മുകളിലെ ടാബുകളിൽ ക്ലിക്ക് ചെയ്ത് ചാർട്ടുകൾ മാറാനും സാധിക്കും.")
