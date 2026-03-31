import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import pandas_ta as ta
import telebot
import threading
from datetime import datetime

# 1. ടെലിഗ്രാം ബോട്ട് സെറ്റപ്പ്
# നിങ്ങളുടെ ടോക്കൺ ഇവിടെ കൃത്യമായി നൽകിയിട്ടുണ്ട്
API_TOKEN = '8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA'
bot = telebot.TeleBot(API_TOKEN)

# ബോട്ട് മെസ്സേജുകൾ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "നമസ്കാരം ഫൈസൽ! നിങ്ങളുടെ ട്രേഡിംഗ് ബോട്ട് ഇപ്പോൾ ഓൺലൈൻ ആണ്. 🚀")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"നിങ്ങൾ പറഞ്ഞത്: {message.text}. ലൈവ് ചാർട്ടുകൾക്കായി വെബ് ലിങ്ക് നോക്കുക.")

# ബോട്ട് ബാക്ക്ഗ്രൗണ്ടിൽ റൺ ചെയ്യാനുള്ള ഫങ്ക്ഷൻ
def run_bot():
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot Error: {e}")

# ബോട്ട് ഒരു തവണ മാത്രം സ്റ്റാർട്ട് ചെയ്യുന്നു
if "bot_started" not in st.session_state:
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.session_state.bot_started = True

# 2. സ്റ്റ്രീംലിറ്റ് ഡാഷ്‌ബോർഡ് UI സെറ്റിംഗ്സ്
st.set_page_config(page_title="Faisal Pro Smart Bot", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📊 ഫൈസൽ പ്രോ ട്രേഡിംഗ് & ബോട്ട്</h1>", unsafe_allow_html=True)

# സൈഡ് ബാർ വിവരങ്ങൾ
st.sidebar.success("✅ ബോട്ട് ഇപ്പോൾ പ്രവർത്തിക്കുന്നുണ്ട്!")
st.sidebar.info("നാളെ രാവിലെ മാർക്കറ്റ് തുറക്കുമ്പോൾ ലൈവ് സിഗ്നലുകൾ ഇവിടെ കാണാം.")

# സൂപ്പർ ട്രെൻഡ് ചാർട്ട് വരയ്ക്കാനുള്ള ഫങ്ക്ഷൻ
def draw_supertrend_chart(name, symbol):
    try:
        # കഴിഞ്ഞ 5 ദിവസത്തെ 5 മിനിറ്റ് ഇന്റർവെൽ ഡാറ്റ എടുക്കുന്നു
        df = yf.Ticker(symbol).history(period="5d", interval="5m")
        
        if not df.empty:
            # സൂപ്പർ ട്രെൻഡ് കണക്കാക്കുന്നു (7, 3)
            # pandas_ta ഉപയോഗിക്കുമ്പോൾ ഇത് ഡാറ്റാഫ്രെയിമിലേക്ക് നേരിട്ട് ചേർക്കാം
            sti = df.ta.supertrend(length=7, multiplier=3)
            
            # SUPERT_7_3.0 എന്ന കോളമാണ് സൂപ്പർ ട്രെൻഡ് ലൈൻ
            df['ST'] = sti['SUPERT_7_3.0']
            
            fig = go.Figure()

            # കാൻഡിൽസ്റ്റിക് ചാർട്ട്
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ))

            # സൂപ്പർ ട്രെൻഡ് ലൈൻ (മഞ്ഞ നിറം)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['ST'],
                line=dict(color='yellow', width=2),
                name='Supertrend'
            ))

            fig.update_layout(
                title=f"{name} ലൈവ് ചാർട്ട് (5 Min)",
                xaxis_rangeslider_visible=False,
                template='plotly_dark',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"{name} ഡാറ്റ ലഭ്യമല്ല. മാർക്കറ്റ് സമയം പരിശോധിക്കുക.")
            
    except Exception as e:
        st.error(f"Error loading {name}: {e}")

# നിഫ്റ്റി ചാർട്ട്
draw_supertrend_chart("Nifty 50", "^NSEI")

# ക്രൂഡ് ഓയിൽ ചാർട്ട്
draw_supertrend_chart("Crude Oil", "CL=F")

st.markdown("---")
st.info("💡 **ട്രേഡിംഗ് ടിപ്പ്:** മഞ്ഞ ലൈനിന് മുകളിൽ കാൻഡിൽ ക്ലോസ് ചെയ്താൽ അത് ബൈ (Buy) സിഗ്നലായും, താഴെ പോയാൽ സെൽ (Sell) സിഗ്നലായും കരുതാം.")
