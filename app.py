import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import telebot
import threading
from datetime import datetime

# 1. ടെലിഗ്രാം ബോട്ട് സെറ്റപ്പ്
API_TOKEN = '8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "നമസ്കാരം ഫൈസൽ! നിങ്ങളുടെ ട്രേഡിംഗ് ബോട്ട് ഇപ്പോൾ ഓൺലൈൻ ആണ്. 🚀")

def run_bot():
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot Error: {e}")

if "bot_started" not in st.session_state:
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.session_state.bot_started = True

# 2. ട്രേഡിംഗ് ഡാഷ്‌ബോർഡ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Faisal Pro Trading Bot", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📊 ഫൈസൽ പ്രോ ട്രേഡിംഗ് & കറൻസി ഡാഷ്‌ബോർഡ്</h1>", unsafe_allow_html=True)

# ചാർട്ട് കാണിക്കാനുള്ള ഫങ്ക്ഷൻ
def draw_chart(name, symbol, is_currency=False):
    try:
        # ഡാറ്റ ലോഡ് ചെയ്യുന്നു (1 മാസത്തെ ഡാറ്റ)
        df = yf.Ticker(symbol).history(period="1mo", interval="5m")
        
        if not df.empty:
            # ട്രെൻഡ് ലൈനിനായി 20 പിരീഡ് മൂവിംഗ് ആവറേജ്
            df['MA20'] = df['Close'].rolling(window=20).mean()
            
            fig = go.Figure()
            
            # Candlestick Chart
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], 
                low=df['Low'], close=df['Close'], name='Price'
            ))
            
            # Trend Line (മഞ്ഞ ലൈൻ)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MA20'], 
                line=dict(color='yellow', width=2), 
                name='Trend Line (MA20)'
            ))
            
            fig.update_layout(
                title=f"{name} ലൈവ് ചാർട്ട്", 
                xaxis_rangeslider_visible=False, 
                template='plotly_dark',
                height=500,
                yaxis=dict(
                    side='right', 
                    tickformat='.2f', 
                    title='വില (Price)'
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # ഏറ്റവും പുതിയ വില കാണിക്കാൻ
            current_price = df['Close'].iloc[-1]
            st.write(f"**നിലവിലെ {name} വില: {current_price:.2f}**")
            st.divider()
        else:
            st.warning(f"{name} ഡാറ്റ ഇപ്പോൾ ലഭ്യമല്ല. മാർക്കറ്റ് അവധി ആയിരിക്കാം.")
            
    except Exception as e:
        st.error(f"{name} ലോഡ് ചെയ്യുന്നതിൽ പ്രശ്നം: {e}")

# ലൈവ് ചാർട്ടുകൾ താഴെ നൽകുന്നു
draw_chart("Nifty 50", "^NSEI")
draw_chart("Crude Oil", "CL=F")
draw_chart("AED to INR (ദിർഹം - രൂപ)", "AEDINR=X")

st.info("💡 മഞ്ഞ ലൈനിന് മുകളിൽ കാൻഡിൽ വന്നാൽ 'Buy' എന്നും, താഴെ വന്നാൽ 'Sell' എന്നും മനസ്സിലാക്കാം.")
