import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
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
st.set_page_config(page_title="FTB AI Terminal", layout="wide")

# --- സൈഡ്‌ബാറിലെ വിവരങ്ങൾ ---
st.sidebar.image("https://img.icons8.com/clouds/200/financial-growth.png", width=100)
st.sidebar.title("FTB PRO SETTINGS")

# യുഎഇ സമയം
uae_tz = pytz.timezone('Asia/Dubai')
st.sidebar.markdown(f"### 🕒 UAE Time: **{datetime.now(uae_tz).strftime('%H:%M:%S')}**")

# കറൻസി കാൽക്കുലേറ്റർ
st.sidebar.divider()
aed_val = st.sidebar.number_input("AED to INR", min_value=1.0, value=1.0)
try:
    c_rate = yf.Ticker("AEDINR=X").history(period="1d")['Close'].iloc[-1]
    st.sidebar.success(f"{aed_val} AED = {aed_val*c_rate:.2f} INR")
except: pass

# ഇൻഡിക്കേറ്റർ കൺട്രോൾ
st.sidebar.divider()
show_st = st.sidebar.checkbox("Show SuperTrend", value=True)
chart_int = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h"], index=1)

# --- SuperTrend Function ---
def get_st(df, period=10, mult=3):
    hl2 = (df['High'] + df['Low']) / 2
    tr = pd.concat([df['High'] - df['Low'], abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    up = hl2 + (mult * atr)
    lo = hl2 - (mult * atr)
    st_dir = [True] * len(df)
    for i in range(1, len(df)):
        if df['Close'][i] > up[i-1]: st_dir[i] = True
        elif df['Close'][i] < lo[i-1]: st_dir[i] = False
        else:
            st_dir[i] = st_dir[i-1]
            if st_dir[i] and lo[i] < lo[i-1]: lo[i] = lo[i-1]
            if not st_dir[i] and up[i] > up[i-1]: up[i] = up[i-1]
    return [lo[i] if st_dir[i] else up[i] for i in range(len(df))]

# --- മെയിൻ ഡാഷ്‌ബോർഡ് ---
st.markdown("<h1 style='text-align: center; color: #00E676;'>📊 FTB SMART AI TERMINAL</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📈 Trading Charts", "💬 FTB AI Chat", "⚙️ Options Analysis"])

with tab1:
    m_choice = st.selectbox("Select Asset", ["Nifty 50", "Bank Nifty", "Crude Oil", "Reliance", "Tata Motors"])
    tickers = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Oil": "CL=F", "Reliance": "RELIANCE.NS", "Tata Motors": "TATAMOTORS.NS"}
    
    try:
        data = yf.Ticker(tickers[m_choice]).history(period="5d", interval=chart_int)
        if not data.empty:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Price')])
            if show_st:
                fig.add_trace(go.Scatter(x=data.index, y=get_st(data), line=dict(color='#FFEB3B', width=2), name='SuperTrend'))
            fig.update_layout(height=600, template='plotly_dark', xaxis_rangeslider_visible=False, dragmode='pan', yaxis=dict(side='right'))
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
            st.success(f"Current Price: {data['Close'].iloc[-1]:.2f}")
    except: st.error("Data Load Error")

with tab2:
    st.subheader("🤖 FTB AI Assistant")
    st.write("നിനക്ക് എന്ത് സംശയമുണ്ടെങ്കിലും താഴെ ചോദിക്കാം (ഉദാഹരണത്തിന്: 'What is Nifty?', 'How to trade Crude Oil?')")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("ഇവിടെ ചോദിക്കൂ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # സിംപിൾ മറുപടി (ഇവിടെ നിനക്ക് ഭാവിയിൽ OpenAI പോലുള്ളവ കണക്ട് ചെയ്യാം)
        response = f"ഫൈസൽ, നീ ചോദിച്ച '{prompt}' എന്നതിനെക്കുറിച്ച് ഞാൻ പഠിച്ചു കൊണ്ടിരിക്കുകയാണ്. നിലവിൽ മാർക്കറ്റ് ചാർട്ടുകൾ ശ്രദ്ധിക്കൂ!"
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

with tab3:
    st.write("Options Analysis Coming Soon...")
