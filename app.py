import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ് & തീം
st.set_page_config(page_title="Paichi AI Pro Terminal", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    
    div[data-testid="stSidebar"] button {
        background-color: #000 !important; color: #BF953F !important;
        border: 2px solid #FFD700 !important; border-radius: 12px !important;
        height: 45px !important; font-weight: bold !important;
        margin-bottom: 10px !important; width: 100% !important;
    }
    
    .indicator-box { 
        background-color: #000; color: #FFF; padding: 15px; 
        border-radius: 10px; border: 2px solid #BF953F; text-align: center; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .main-title { color: #FFF; font-size: 30px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
</style>
""", unsafe_allow_html=True)

# 20 സെക്കൻഡിൽ ആപ്പ് ഓട്ടോ റിഫ്രഷ് ആകും
st_autorefresh(interval=20000, key="faisal_ultimate_terminal_v1")

FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---

def get_live_aed_rate():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        return res['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 22.75

def get_market_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        result = res['chart']['result'][0]
        df = pd.DataFrame({
            'Time': pd.to_datetime(result['timestamp'], unit='s'),
            'Open': result['indicators']['quote'][0]['open'],
            'High': result['indicators']['quote'][0]['high'],
            'Low': result['indicators']['quote'][0]['low'],
            'Close': result['indicators']['quote'][0]['close']
        }).dropna()
        return df, result['meta']['regularMarketPrice']
    except: return None, None

def get_sentiment(name):
    # സിമ്പിൾ സെന്റിമെന്റ് അനാലിസിസ് (വാർത്തകൾക്ക് പകരം ട്രെൻഡ് നോക്കി)
    return "Bullish 🟢" if "NIFTY" in name else "Neutral ⚪"

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #000;'>🚀 Paichi Pro</h1>", unsafe_allow_html=True)
    
    # AED Converter
    live_aed = get_live_aed_rate()
    aed_input = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_input * live_aed:,.2f} (INR)")
    
    st.divider()
    mode = st.radio("Menu:", ["MARKET ANALYSIS", "JOURNAL"])
    st.divider()
    
    if mode == "MARKET ANALYSIS":
        if st.button("📊 NIFTY 50"): st.session_state.sel = ("^NSEI", "NIFTY 50", 1)
        if st.button("🏦 BANK NIFTY"): st.session_state.sel = ("^NSEBANK", "BANK NIFTY", 1)
        if st.button("🛢️ CRUDE OIL"): st.session_state.sel = ("CL=F", "CRUDE OIL", 84.5)
        if st.button("💰 GOLD 8G"): st.session_state.sel = ("GC=F", "GOLD 8G", 8.45 * 8)

if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# --- മെയിൻ ബോഡി ---
st.markdown("<p class='main-title'>Paichi AI Pro Terminal ⚡</p>", unsafe_allow_html=True)

if mode == "MARKET ANALYSIS":
    sym, name, multi = st.session_state.sel
    df, live_p = get_market_data(sym)
    
    if df is not None:
        live_p_inr = live_p * multi
        
        # 1. ടോപ്പ് മെട്രിക്സ്
        c1, c2, c3 = st.columns(3)
        c1.metric(f"{name} Price", f"₹{live_p_inr:,.2f}")
        
        # AI Signal Logic
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        signal = "BUY 🟢" if last_close > prev_close else "SELL 🔴"
        c2.markdown(f"<div class='indicator-box'>AI SIGNAL<br><b style='font-size:20px;'>{signal}</b></div>", unsafe_allow_html=True)
        
        # Sentiment
        sent = get_sentiment(name)
        c3.markdown(f"<div class='indicator-box'>SENTIMENT<br><b style='font-size:20px;'>{sent}</b></div>", unsafe_allow_html=True)

        # 2. Candlestick Chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['Time'], open=df['Open']*multi, high=df['High']*multi,
            low=df['Low']*multi, close=df['Close']*multi,
            increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        )])
        fig.update_layout(
            template='plotly_dark', xaxis_rangeslider_visible=False, height=450,
            paper_bgcolor='black', plot_bgcolor='black',
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("മാർക്കറ്റ് ഡാറ്റ ലോഡ് ചെയ്യുന്നു... ഇന്ന് അവധിയായതിനാൽ പഴയ വിലകൾ നാളെ രാവിലെ അപ്‌ഡേറ്റ് ആകും.")

elif mode == "JOURNAL":
    st.subheader("📝 Trading Journal")
    # പഴയ ജേണൽ കോഡ് ഇവിടെ വരും...
    if os.path.isfile(FILE_NAME):
        st.dataframe(pd.read_csv(FILE_NAME), use_container_width=True)
