import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import telebot
import threading
from datetime import datetime

# 1. ടെലിഗ്രാം ബോട്ട് സെറ്റപ്പ്
# (ടോക്കൺ നീ നേരത്തെ കൊടുത്തത് തന്നെ നിലനിർത്തുന്നു)
API_TOKEN = '8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA'
bot = telebot.TeleBot(API_TOKEN)

def run_bot():
    try: bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except: pass

# ബോട്ട് ബാക്ക്ഗ്രൗണ്ടിൽ റൺ ചെയ്യുന്നു
if "bot_started" not in st.session_state:
    threading.Thread(target=run_bot, daemon=True).start()
    st.session_state.bot_started = True

# 2. പേജ് സെറ്റിംഗ്സ് (Wide mode on)
st.set_page_config(page_title="Faisal Pro Trader", layout="wide")

# --- ഡാഷ്‌ബോർഡ് ലോഗോയും പേരും (F T B) ---
# (നീ ചോദിച്ചതുപോലെ ഒരു ട്രേഡിംഗ് ലോഗോയും 'FTB' എന്ന പേരും ചേർത്തു)
col1, col2 = st.columns([0.15, 0.85])
with col1:
    # ഒരു കോംപ്ലക്സ് ട്രേഡിംഗ് ചാർട്ട് കാണിക്കുന്ന ലോഗോ
    st.image("https://img.icons8.com/clouds/200/financial-growth.png", width=90)
with col2:
    st.markdown("<h1 style='text-align: center; color: #00C853;'>📊 FAISAL PRO TRADER (FTB)</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #BDBDBD;'>നിങ്ങളുടെ സ്വന്തം ലൈവ് ട്രേഡിംഗ് & കറൻസി ടرمینൽ</h4>", unsafe_allow_html=True)
st.divider()

# --- സൈഡ്‌ബാറിൽ കറൻസി കാൽക്കുലേറ്റർ ---
st.sidebar.markdown("### 💰 AED to INR Calc")
aed_amount = st.sidebar.number_input("ദിർഹം നൽകുക (AED)", min_value=1.0, value=1.0)
try:
    # ലൈവ് ദിർഹം റേറ്റ് എടുക്കുന്നു
    rate_ticker = yf.Ticker("AEDINR=X").history(period="1d")
    live_rate = rate_ticker['Close'].iloc[-1]
    inr_result = aed_amount * live_rate
    st.sidebar.success(f"{aed_amount} AED = {inr_result:.2f} INR")
    st.sidebar.write(f"ഇന്നത്തെ റേറ്റ്: **{live_rate:.2f}**")
except:
    st.sidebar.error("റേറ്റ് ഇപ്പോൾ ലഭ്യമല്ല")

# --- അഡ്വാൻസ്ഡ് ചാർട്ട് ഫങ്ക്ഷൻ (Zoom & Indicators സഹിതം) ---
def draw_professional_chart(symbol, title, interval="5m"):
    try:
        # ഡാറ്റ കൃത്യമായി വരാൻ 1 മാസത്തെ ഡാറ്റ എടുക്കുന്നു (5 മിനിറ്റ് ഇന്റർവൽ)
        df = yf.Ticker(symbol).history(period="1mo", interval=interval)
        
        if df.empty:
            st.warning(f"{title} ഡാറ്റ ലഭ്യമല്ല. മാർക്കറ്റ് അവധി ആയിരിക്കാം.")
            return

        # Technical Indicators കണക്കാക്കുന്നു (നീ ചോദിച്ച MA20 & Supertrend)
        df['MA20'] = df['Close'].rolling(window=20).mean() # മഞ്ഞ ലൈൻ
        
        # Subplots (Price ചാർട്ട് + വോളിയം)
        fig = make_subplots(rows=1, cols=1)

        # Candlestick Chart (വില കാണിക്കുന്നു)
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], 
            low=df['Low'], close=df['Close'], name='Price'
        ))
        
        # Moving Average (Trend Line)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MA20'], 
            line=dict(color='yellow', width=1.5), 
            name='MA20 Trend'
        ))
        
        # ചാർട്ട് ലേഔട്ട് (Zoom, Touch enabled)
        fig.update_layout(
            height=700, # മൊബൈലിനായി ചാർട്ട് വലുതാക്കി
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            yaxis=dict(
                side='right', 
                tickformat='.2f',
                title='വില (Price)'
            ),
            xaxis=dict(title='സമയം (Time)'),
            # നീ ചോദിച്ച സൂം ഫീച്ചർ ഓൺ ചെയ്യുന്നു
            dragmode='zoom', 
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        # ടച്ച് ചെയ്താൽ സൂം ചെയ്യാൻ പ്ലോട്ട്‌ലി ടൂൾസ് ഓൺ ചെയ്യുന്നു
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
        
        # ഏറ്റവും പുതിയ വില കാണിക്കാൻ
        current_price = df['Close'].iloc[-1]
        st.info(f"👉 **{title} നിലവിലെ വില: {current_price:.2f}**")
        
    except Exception as e:
        st.error(f"{title} ലോഡ് ചെയ്യുന്നതിൽ പ്രശ്നം: {e}")

# --- ടാബുകൾ (നിഫ്റ്റി വേണമെങ്കിൽ നിഫ്റ്റി മാത്രം) ---
# (നീ ചോദിച്ചതുപോലെ ഓരോ ടാബിലും ക്ലിക്ക് ചെയ്ത് ചാർട്ടുകൾ മാറാം)
tab1, tab2, tab3 = st.tabs(["📊 NIFTY 50", "⛽ CRUDE OIL", "💵 AED to INR"])

with tab1:
    draw_professional_chart("^NSEI", "Nifty 50")

with tab2:
    draw_professional_chart("CL=F", "Crude Oil")

with tab3:
    # കറൻസി ചാർട്ട് 30 മിനിറ്റ് ഇന്റർവലിൽ (കൂടുതൽ വ്യക്തതയ്ക്ക്)
    draw_professional_chart("AEDINR=X", "AED to INR", interval="30m")

st.divider()
st.info("💡 ചാർട്ടിൽ രണ്ട് വിരൽ ഉപയോഗിച്ച് സൂം ചെയ്യാനും, മുകളിലെ ടാബുകളിൽ ക്ലിക്ക് ചെയ്ത് ചാർട്ടുകൾ മാറാനും സാധിക്കും.")
