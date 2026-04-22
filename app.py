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
    .info-box { background-color: #f8f9fa; padding: 10px; border-radius: 8px; color: #333; font-weight: bold; text-align: center; border: 1px solid #ddd; font-size: 14px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_full_app_v3")
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

# --- 2. സൈഡ് ബാർ ---
with st.sidebar:
    st.markdown("### 🚀 Paichi Pro")
    st.markdown("[💬 Contact on WhatsApp](https://wa.me/918714752210)")
    
    # Alert System
    st.divider()
    st.write("🔔 **Premium Alert**")
    alert_val = st.number_input("Alert Price Set ചെയ്യുക", value=0.0)
    
    # Currency
    st.write("💰 **AED to INR**")
    aed_val = st.number_input("Dirham Amount", min_value=0.0, value=1.0)
    ex_rate = get_live_price("AEDINR=X")
    if ex_rate > 0:
        st.markdown(f'<div class="info-box" style="color:green;">₹ {aed_val * ex_rate:,.2f} INR</div>', unsafe_allow_html=True)
    
    st.divider()
    mode = st.radio("മെനു:", ["MARKET", "JOURNAL", "DASHBOARD"])
    st.divider()

    if mode == "MARKET":
        st.write("🎯 **Indices:**")
        if st.button("📈 NIFTY 50"): st.session_state.sel_ticker = ("^NSEI", "NIFTY 50"); st.rerun()
        if st.button("🏦 BANK NIFTY"): st.session_state.sel_ticker = ("^NSEBANK", "BANK NIFTY"); st.rerun()
        if st.button("⛽ CRUDE OIL"): st.session_state.sel_ticker = ("CL=F", "CRUDE OIL"); st.rerun()

# --- 3. മെയിൻ കണ്ടന്റ് ---
if mode == "MARKET":
    symbol, name = st.session_state.sel_ticker
    price = get_live_price(symbol)
    
    # Alert Logic
    if alert_val > 0 and price >= alert_val:
        st.error(f"🚨 ALERT: {name} വില {alert_val} കടന്നു! ഇപ്പോഴത്തെ വില: {price:,.2f}")
        st.toast("Price Alert Hit!", icon='🚨')

    st.markdown(f'<p class="main-title">🚀 {name}</p>', unsafe_allow_html=True)
    st.metric(label=name, value=f"₹ {price:,.2f}")
    
    # Live Chart for Crude Oil
    if name == "CRUDE OIL":
        st.write("### 📈 Crude Oil 5-Min Trend")
        c_data = yf.download(symbol, period='1d', interval='5m')
        if not c_data.empty:
            st.line_chart(c_data['Close'])

elif mode == "JOURNAL":
    st.markdown('<p class="main-title">📝 OPTION JOURNAL</p>', unsafe_allow_html=True)
    underlying = st.selectbox("Index", ["NIFTY", "BANKNIFTY", "CRUDE OIL"])
    strike = st.text_input("Strike", placeholder="Ex: 22400 CE")
    entry_raw = st.text_input("Entry Premium")
    exit_raw = st.text_input("Exit Premium")
    qty_raw = st.text_input("Qty")
    t_type = st.selectbox("Type", ["BUY", "SELL"])
    mood = st.selectbox("Mood", ["Calm", "Fear", "Greedy"])

    if st.button("SAVE TRADE"):
        try:
            pnl = (float(exit_raw) - float(entry_raw)) * int(qty_raw)
            save_trade(f"{underlying} {strike}", t_type, entry_raw, exit_raw, qty_raw, pnl, mood)
            st.success(f"സേവ് ചെയ്തു! P&L: ₹{pnl}")
        except: st.error("വിവരങ്ങൾ കൃത്യമായി നൽകുക")

elif mode == "DASHBOARD":
    st.markdown('<p class="main-title">📊 DASHBOARD</p>', unsafe_allow_html=True)
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.write(f"### Net P&L: ₹ {df['P&L'].sum():,.2f}")
        st.dataframe(df.iloc[::-1], use_container_width=True)

st.markdown(f'<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
