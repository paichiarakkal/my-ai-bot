import os
# പ്ലോട്ട്‌ലി ലൈബ്രറി മിസ്സിംഗ് ആണെങ്കിൽ ഇൻസ്റ്റാൾ ചെയ്യാൻ ഇത് സഹായിക്കും
os.system("pip install plotly pandas_ta pyTelegramBotAPI")

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import pandas_ta as ta
import telebot
import threading
from datetime import datetime

# 1. ടെലിഗ്രാം ബോട്ട് സെറ്റപ്പ് (നിങ്ങളുടെ പുതിയ ടോക്കൺ)
API_TOKEN = '8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA'
bot = telebot.TeleBot(API_TOKEN)

# ബോട്ട് കമാൻഡുകൾ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "നമസ്കാരം ഫൈസൽ! നിങ്ങളുടെ ട്രേഡിംഗ് ബോട്ട് ഇപ്പോൾ ഓൺലൈൻ ആണ്. 🚀")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"നിങ്ങൾ പറഞ്ഞത്: {message.text}. ചാർട്ടുകൾ കാണാൻ വെബ് ലിങ്ക് നോക്കുക.")

# ബോട്ട് ബാക്ക്ഗ്രൗണ്ടിൽ റൺ ചെയ്യാനുള്ള ഫങ്ക്ഷൻ
def run_bot():
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot Error: {e}")

# ബോട്ട് ഒരു തവണ മാത്രം സ്റ്റാർട്ട് ചെയ്യുന്നു എന്ന് ഉറപ്പാക്കുന്നു
if "bot_started" not in st.session_state:
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.session_state.bot_started = True

# 2. സ്റ്റ്രീംലിറ്റ് ഡാഷ്‌ബോർഡ് (UI)
st.set_page_config(page_title="Faisal Pro Smart Bot", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📊 ഫൈസൽ പ്രോ ട്രേഡിംഗ് & ബോട്ട്</h1>", unsafe_allow_html=True)

# സൈഡ് ബാർ
st.sidebar.success("✅ ടെലിഗ്രാം ബോട്ട് ഇപ്പോൾ പ്രവർത്തിക്കുന്നുണ്ട്!")

# ചാർട്ട് ഫങ്ക്ഷൻ (Supertrend ഉൾപ്പെടുത്തിയത്)
def draw_supertrend_chart(name, symbol):
    try:
        # ഡാറ്റ എടുക്കുന്നു
        df = yf.Ticker(symbol).history(period="5d", interval="5m")
        
        if not df.empty:
            # സൂപ്പർ ട്രെൻഡ് കണക്കാക്കുന്നു (7, 3)
            sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3)
            
            # സൂപ്പർ ട്രെൻഡ് ഡാറ്റ ചേർക്കുന്നു
            df['ST'] = sti['SUPERT_7_3.0']
            
            fig = go.Figure()
            # Candlestick Chart
            fig.add_trace(go.Candlestick(
                x=df.index, 
                open=df['Open'], 
                high=df['High'], 
                low=df['Low'], 
                close=df['Close'], 
                name='Price'
            ))
            
            # Supertrend Line (Yellow)
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=df['ST'], 
                line=dict(color='yellow', width=2), 
                name='Supertrend'
            ))
            
            fig.update_layout(
                title=f"{name} ലൈവ് ചാർട്ട്", 
                xaxis_rangeslider_visible=False, 
                template='plotly_dark', 
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"{name} ഡാറ്റ ലഭ്യമല്ല.")
    except Exception as e:
        st.error(f"Error loading {name}: {e}")

# ചാർട്ടുകൾ കാണിക്കുന്നു
draw_supertrend_chart("Nifty 50", "^NSEI")
draw_supertrend_chart("Crude Oil", "CL=F")

st.info("💡 മഞ്ഞ ലൈനിന് മുകളിൽ കാൻഡിൽ വന്നാൽ 'Buy' എന്നും താഴെ വന്നാൽ 'Sell' എന്നും മനസ്സിലാക്കാം.")
