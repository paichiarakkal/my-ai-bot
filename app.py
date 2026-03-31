import subprocess
import sys
import os

# 1. ആവശ്യമായ ലൈബ്രറികൾ സെർവറിൽ ഇൻസ്റ്റാൾ ചെയ്യാൻ ഇത് സഹായിക്കും
def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except:
        pass

# പ്രധാനപ്പെട്ട ലൈബ്രറികൾ ഉണ്ടെന്ന് ഉറപ്പുവരുത്തുന്നു
try:
    import plotly
    import pandas_ta
    import telebot
except ImportError:
    install('plotly')
    install('pandas-ta')
    install('pyTelegramBotAPI')
    install('yfinance')

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import pandas_ta as ta
import telebot
import threading
from datetime import datetime

# 2. ടെലിഗ്രാം ബോട്ട് സെറ്റപ്പ്
API_TOKEN = '8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "നമസ്കാരം ഫൈസൽ! നിങ്ങളുടെ ട്രേഡിംഗ് ബോട്ട് ഇപ്പോൾ ഓൺലൈൻ ആണ്. 🚀")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"നിങ്ങൾ പറഞ്ഞത്: {message.text}. ചാർട്ടുകൾക്കായി വെബ് ലിങ്ക് നോക്കുക.")

def run_bot():
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot Error: {e}")

if "bot_started" not in st.session_state:
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.session_state.bot_started = True

# 3. സ്റ്റ്രീംലിറ്റ് ഡാഷ്‌ബോർഡ്
st.set_page_config(page_title="Faisal Pro Smart Bot", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📊 ഫൈസൽ പ്രോ ട്രേഡിംഗ് & ബോട്ട്</h1>", unsafe_allow_html=True)

# സൈഡ് ബാർ
st.sidebar.success("✅ ബോട്ട് ബാക്ക്ഗ്രൗണ്ടിൽ പ്രവർത്തിക്കുന്നുണ്ട്!")

# ചാർട്ട് ഫങ്ക്ഷൻ
def draw_supertrend_chart(name, symbol):
    try:
        df = yf.Ticker(symbol).history(period="5d", interval="5m")
        if not df.empty:
            # സൂപ്പർ ട്രെൻഡ് കണക്കാക്കുന്നു
            sti = df.ta.supertrend(length=7, multiplier=3)
            df['ST'] = sti['SUPERT_7_3.0']
            
            fig = go.Figure()
            # Candlestick
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='വില'))
            # Supertrend Line
            fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='yellow', width=2), name='Supertrend'))
            
            fig.update_layout(title=f"{name} ലൈവ് ചാർട്ട്", xaxis_rangeslider_visible=False, template='plotly_dark', height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"{name} ഡാറ്റ ലഭ്യമായില്ല.")
    except Exception as e:
        st.error(f"ചാർട്ട് ലോഡ് ചെയ്യുന്നതിൽ പിശക്: {e}")

# ചാർട്ടുകൾ
draw_supertrend_chart("Nifty 50", "^NSEI")
draw_supertrend_chart("Crude Oil", "CL=F")

st.info("💡 മഞ്ഞ ലൈനിന് മുകളിൽ കാൻഡിൽ വന്നാൽ 'Buy' എന്നും താഴെ വന്നാൽ 'Sell' എന്നും മനസ്സിലാക്കാം.")
