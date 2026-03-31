import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import telebot
import threading
from datetime import datetime
import pytz

# 1. ടെലിഗ്രാം ബോട്ട് സെറ്റപ്പ്
API_TOKEN = '8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA'
bot = telebot.TeleBot(API_TOKEN)

def run_bot():
    try: bot.infinity_polling(timeout=10)
    except: pass

if "bot_started" not in st.session_state:
    threading.Thread(target=run_bot, daemon=True).start()
    st.session_state.bot_started = True

# 2. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="FTB Pro Trader", layout="wide")

# --- ലോഗോയും പേരും ---
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image("https://img.icons8.com/clouds/200/financial-growth.png", width=80)
with col2:
    st.markdown("<h1 style='text-align: center; color: #00C853;'>📊 FAISAL PRO TRADER (FTB)</h1>", unsafe_allow_html=True)

# സൈഡ്‌ബാറിൽ സമയം കാണിക്കാൻ (Dubai Time)
uae_tz = pytz.timezone('Asia/Dubai')
now_uae = datetime.now(uae_tz).strftime("%H:%M:%S")
st.sidebar.markdown(f"### 🕒 UAE Time: **{now_uae}**")

# --- കറൻസി കാൽക്കുലേറ്റർ ---
st.sidebar.divider()
st.sidebar.header("💰 AED to INR")
aed_in = st.sidebar.number_input("AED", min_value=1.0, value=1.0)
try:
    c_rate = yf.Ticker("AEDINR=X").history(period="1d")['Close'].iloc[-1]
    st.sidebar.success(f"{aed_in} AED = {aed_in*c_rate:.2f} INR")
except: pass

# --- SuperTrend കണക്കാക്കുന്ന ഫങ്ക്ഷൻ ---
def get_supertrend(df, period=10, multiplier=3):
    hl2 = (df['High'] + df['Low']) / 2
    # ATR കണക്കാക്കുന്നു
    tr = pd.concat([df['High'] - df['Low'], 
                    abs(df['High'] - df['Close'].shift(1)), 
                    abs(df['Low'] - df['Close'].shift(1))], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    
    supertrend = [True] * len(df)
    for i in range(1, len(df)):
        if df['Close'][i] > upperband[i-1]: supertrend[i] = True
        elif df['Close'][i] < lowerband[i-1]: supertrend[i] = False
        else:
            supertrend[i] = supertrend[i-1]
            if supertrend[i] and lowerband[i] < lowerband[i-1]: lowerband[i] = lowerband[i-1]
            if not supertrend[i] and upperband[i] > upperband[i-1]: upperband[i] = upperband[i-1]
    
    st_line = [lowerband[i] if supertrend[i] else upperband[i] for i in range(len(df))]
    return st_line, supertrend

# --- അഡ്വാൻസ്ഡ് ചാർട്ട് ഫങ്ക്ഷൻ ---
def draw_ftb_chart(symbol, title):
    try:
        # 1 മിനിറ്റ് ചാർട്ട് വേണമെങ്കിൽ interval="1m", period="7d" നൽകാം
        df = yf.Ticker(symbol).history(period="7d", interval="1m")
        if df.empty:
            st.warning(f"{title} ഡാറ്റ ലഭ്യമല്ല.")
            return

        st_line, st_dir = get_supertrend(df)
        
        fig = go.Figure()
        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                   low=df['Low'], close=df['Close'], name='Price'))
        # SuperTrend Line
        fig.add_trace(go.Scatter(x=df.index, y=st_line, line=dict(color='#FFEB3B', width=2), name='SuperTrend'))

        fig.update_layout(
            height=750,
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            dragmode='pan', # മൊബൈലിൽ നീക്കാൻ എളുപ്പത്തിന് 'pan'
            hovermode='x unified',
            xaxis=dict(type='date', tickformat='%H:%M\n%d %b', showgrid=True),
            yaxis=dict(side='right', autorange=True, fixedrange=False),
            uirevision='constant'
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
        st.info(f"💡 നിലവിലെ {title} വില: {df['Close'].iloc[-1]:.2f}")
        
    except Exception as e:
        st.error(f"Error: {e}")

# --- ടാബുകൾ ---
t1, t2, t3 = st.tabs(["📊 NIFTY 50", "⛽ CRUDE OIL", "💵 AED-INR"])
with t1: draw_ftb_chart("^NSEI", "Nifty 50")
with t2: draw_ftb_chart("CL=F", "Crude Oil")
with t3: draw_ftb_chart("AEDINR=X", "AED to INR")
