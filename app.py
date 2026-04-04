import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    .stButton>button { width: 100%; border-radius: 4px; height: 2.2em; background-color: #000 !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; font-size: 14px !important; font-weight: bold; margin-bottom: 2px; }
    .main-title { color: #FFF; font-size: 26px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .conv-box { background-color: #d1e7dd; padding: 10px; border-radius: 8px; color: #0f5132; font-weight: bold; text-align: center; border: 1px solid #badbcc; font-size: 14px; }
    .metric-card { background: rgba(255, 255, 255, 0.2); padding: 15px; border-radius: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_pro_trader_v1")
FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period='1d', interval='1m')
        return data['Close'].iloc[-1]
    except: return 0.0

def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'sel_ticker' not in st.session_state:
    st.session_state.sel_ticker = ("^NSEI", "NIFTY 50")

# --- 2. സൈഡ് ബാർ (All Tools Included) ---
with st.sidebar:
    st.markdown("### 🚀 Paichi Pro")
    
    # കറൻസി കൺവെർട്ടർ
    st.write("AED (Dirham)")
    aed_val = st.number_input("", min_value=0.0, value=1.0, step=1.0)
    ex_rate = get_live_price("AEDINR=X")
    if ex_rate > 0:
        st.markdown(f'<div class="conv-box">₹ {aed_val * ex_rate:,.2f} (INR)</div>', unsafe_allow_html=True)
    
    st.divider()
    # മെയിൻ മെനു
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()

    if mode == "MARKET":
        st.write("🎯 **Indices:**")
        # ഇൻഡക്സ് ബട്ടണുകൾ
        if st.button("📈 NIFTY 50"): st.session_state.sel_ticker = ("^NSEI", "NIFTY 50"); st.rerun()
        if st.button("🏦 BANK NIFTY"): st.session_state.sel_ticker = ("^NSEBANK", "BANK NIFTY"); st.rerun()
        if st.button("💳 FIN NIFTY"): st.session_state.sel_ticker = ("NIFTY_FIN_SERVICE.NS", "FIN NIFTY"); st.rerun()
        if st.button("⛽ CRUDE OIL"): st.session_state.sel_ticker = ("CL=F", "CRUDE OIL"); st.rerun()
        if st.button("📊 SENSEX"): st.session_state.sel_ticker = ("^BSESN", "SENSEX"); st.rerun()

# --- 3. മെയിൻ കണ്ടന്റ് ---
if mode == "MARKET":
    st.markdown(f'<p class="main-title">🚀 {st.session_state.sel_ticker[1]}</p>', unsafe_allow_html=True)
    symbol, name = st.session_state.sel_ticker
    price = get_live_price(symbol)
    if price > 0:
        st.metric(label=f"{name} Live Price", value=f"₹ {price:,.2f}")
    else: st.error("Market Data Unavailable")

elif mode == "JOURNAL":
    st.markdown('<p class="main-title">📝 OPTION TRADING JOURNAL</p>', unsafe_allow_html=True)
    
    # ഓപ്ഷൻ ട്രേഡർക്കുള്ള സെക്ഷൻ
    col_a, col_b = st.columns(2)
    underlying = col_a.selectbox("Index", ["NIFTY", "BANKNIFTY", "FINNIFTY", "CRUDE OIL"])
    strike = col_b.text_input("Strike & Type", placeholder="Ex: 22400 CE")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    entry = col1.number_input("Entry Premium", value=0.0, format="%.2f", step=0.05)
    exit_p = col2.number_input("Exit Premium", value=0.0, format="%.2f", step=0.05)
    qty = col1.number_input("Total Qty (Lots)", value=1, step=1)
    t_type = col2.selectbox("Order Type", ["BUY (Long)", "SELL (Short)"])
    
    mood = st.selectbox("Trading Mood", ["Calm", "Disciplined", "Fear", "Greedy"])

    if st.button("SAVE OPTION TRADE"):
        # ലാഭനഷ്ടം കണക്കാക്കുന്നു
        pnl = (exit_p - entry) * qty if "BUY" in t_type else (entry - exit_p) * qty
        save_trade(f"{underlying} {strike}", t_type, entry, exit_p, qty, pnl, mood)
        st.success(f"Trade Saved! P&L: ₹{pnl:,.2f}")
        st.rerun()

    if os.path.isfile(FILE_NAME):
        st.divider()
        st.write("### 📜 Recent Trades")
        df = pd.read_csv(FILE_NAME)
        st.table(df.iloc[::-1].head(5))

elif mode == "DASHBOARD":
    st.markdown('<p class="main-title">📊 PERFORMANCE DASHBOARD</p>', unsafe_allow_html=True)
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        total_pnl = df['P&L'].sum()
        
        # സംഗ്രഹം കാണിക്കുന്നു
        c1, c2 = st.columns(2)
        c1.metric("Total Net P&L", f"₹ {total_pnl:,.2f}")
        c2.metric("Total Trades", len(df))
        
        st.write("### Detailed History")
        st.dataframe(df.iloc[::-1], use_container_width=True)
    else:
        st.warning("No data found in Journal.")

st.markdown(f'<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
