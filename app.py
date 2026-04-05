import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
import plotly.graph_objects as go
import plotly.express as px
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
    }
    .main-title { color: #FFF; font-size: 30px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .news-ticker { background:#000; color:#BF953F; padding:10px; font-weight:bold; border-bottom:2px solid #BF953F; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=20000, key="faisal_ultimate_v2")
FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---

def get_live_aed_rate():
    try:
        res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
        return res['chart']['result'][0]['meta']['regularMarketPrice']
    except: return 22.75

def get_live_news_malayalam():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search?q=Nifty,Crude%20Oil,Gold&newsCount=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        news_list = [item['title'] for item in res['news']]
        full_news = "  |  ".join(news_list)
        return translate(full_news, "ml", "en")
    except: return "വാർത്തകൾ ലോഡ് ചെയ്യുന്നു..."

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

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- ന്യൂസ് ടിക്കർ (TOP) ---
st.markdown(f'<div class="news-ticker"><marquee scrollamount="5">📢 വാർത്തകൾ: {get_live_news_malayalam()}</marquee></div>', unsafe_allow_html=True)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🚀 Paichi Pro</h1>", unsafe_allow_html=True)
    live_aed = get_live_aed_rate()
    aed_input = st.number_input("AED (Dirham)", value=1.0)
    st.success(f"₹ {aed_input * live_aed:,.2f} (INR)")
    st.divider()
    mode = st.radio("Menu:", ["MARKET ANALYSIS", "JOURNAL", "DASHBOARD"])
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
        c1, c2, c3 = st.columns(3)
        c1.metric(f"{name}", f"₹{live_p * multi:,.2f}")
        signal = "BUY 🟢" if df['Close'].iloc[-1] > df['Close'].iloc[-2] else "SELL 🔴"
        c2.markdown(f"<div class='indicator-box'>AI SIGNAL<br><b>{signal}</b></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='indicator-box'>TREND<br><b>Stable</b></div>", unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=df['Time'], open=df['Open']*multi, high=df['High']*multi, low=df['Low']*multi, close=df['Close']*multi)])
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450, paper_bgcolor='black', plot_bgcolor='black')
        st.plotly_chart(fig, use_container_width=True)

elif mode == "JOURNAL":
    st.subheader("📝 Trading Journal")
    with st.expander("Add New Trade", expanded=True):
        col1, col2 = st.columns(2)
        item = col1.text_input("Item", value=st.session_state.sel[1])
        act = col2.selectbox("Action", ["BUY", "SELL"])
        en = col1.number_input("Entry Price")
        ex = col2.number_input("Exit Price")
        q = col1.number_input("Qty", value=1)
        mood = col2.selectbox("Mood", ["Calm", "Happy", "Fear"])
        if st.button("Save Trade"):
            pnl = (ex - en) * q if act == "BUY" else (en - ex) * q
            save_trade(item, act, en, ex, q, pnl, mood)
            st.success("Saved!")
            st.rerun()
    if os.path.isfile(FILE_NAME): st.dataframe(pd.read_csv(FILE_NAME), use_container_width=True)

elif mode == "DASHBOARD":
    st.subheader("📊 Performance Dashboard")
    if os.path.isfile(FILE_NAME):
        df_log = pd.read_csv(FILE_NAME)
        c1, c2 = st.columns(2)
        c1.metric("Total P&L", f"₹{df_log['P&L'].sum():,.2f}")
        c2.metric("Total Trades", len(df_log))
        st.plotly_chart(px.bar(df_log, x='Date', y='P&L', color='P&L', title="Profit/Loss Trend"), use_container_width=True)
        st.plotly_chart(px.pie(df_log, names='Mood', title="Trading Psychology (Mood)"), use_container_width=True)
    else: st.info("No trade history found.")
