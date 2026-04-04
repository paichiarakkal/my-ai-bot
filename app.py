import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്‌സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

# --- ലോഗിൻ ഫംഗ്ഷൻ ---
def login():
    st.markdown("""
    <style>
        .stApp { background: #f0f2f6; }
        .login-card { 
            background: white; padding: 40px; border-radius: 15px; 
            box-shadow: 0px 4px 15px rgba(0,0,0,0.2); border-top: 5px solid #BF953F;
            max-width: 400px; margin: auto; margin-top: 100px; text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#BF953F;">🔒 Faisal Pro Login</h2>', unsafe_allow_html=True)
    
    user = st.text_input("Username", placeholder="Username")
    pw = st.text_input("Password", type="password", placeholder="Password")
    
    if st.button("ENTER APP"):
        # ഇവിടെ നിനക്ക് ഇഷ്ടമുള്ള യൂസർനെയിമും പാസ്‌വേഡും നൽകാം
        if user == "faisal" and pw == "trader123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("തെറ്റായ വിവരങ്ങൾ!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'sel_ticker' not in st.session_state:
    st.session_state.sel_ticker = ("^NSEI", "NIFTY 50")

# ലോഗിൻ ചെയ്തിട്ടില്ലെങ്കിൽ ലോഗിൻ പേജ് കാണിക്കുക
if not st.session_state.logged_in:
    login()
else:
    # --- മെയിൻ ആപ്പ് ഡിസൈൻ (ലോഗിൻ ചെയ്ത ശേഷം) ---
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
        section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
        .stButton>button { width: 100%; border-radius: 4px; height: 2.2em; background-color: #000 !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; font-size: 14px !important; font-weight: bold; margin-bottom: 2px; }
        .main-title { color: #FFF; font-size: 26px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
        .info-box { background-color: #f8f9fa; padding: 10px; border-radius: 8px; color: #333; font-weight: bold; text-align: center; border: 1px solid #ddd; font-size: 14px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

    st_autorefresh(interval=30000, key="faisal_v3_refresh")
    FILE_NAME = 'trade_history_v2.csv'

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

    # --- സൈഡ് ബാർ ---
    with st.sidebar:
        st.markdown("### 🚀 Paichi Pro")
        
        # Currency
        st.write("💰 **AED to INR**")
        ex_rate = get_live_price("AEDINR=X")
        st.markdown(f'<div class="info-box" style="color:green;">₹ {ex_rate:,.2f}</div>', unsafe_allow_html=True)
        
        # Gold
        st.write("🟡 **Gold (8g/1 Pawan)**")
        gold_price_per_gram = get_live_price("GC=F")
        gold_8g_inr = (gold_price_per_gram / 31.1035) * 8 * ex_rate * 1.15 
        st.markdown(f'<div class="info-box" style="color:#B8860B;">₹ {gold_8g_inr:,.0f}</div>', unsafe_allow_html=True)
        
        st.divider()
        mode = st.radio("മെനു:", ["MARKET", "JOURNAL", "DASHBOARD"])
        st.divider()

        if mode == "MARKET":
            st.write("🎯 **Indices:**")
            if st.button("📈 NIFTY 50"): st.session_state.sel_ticker = ("^NSEI", "NIFTY 50"); st.rerun()
            if st.button("🏦 BANK NIFTY"): st.session_state.sel_ticker = ("^NSEBANK", "BANK NIFTY"); st.rerun()
            if st.button("⛽ CRUDE OIL"): st.session_state.sel_ticker = ("CL=F", "CRUDE OIL"); st.rerun()
        
        if st.button("🚪 LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    # --- മെയിൻ ബോഡി ---
    if mode == "MARKET":
        st.markdown(f'<p class="main-title">🚀 {st.session_state.sel_ticker[1]}</p>', unsafe_allow_html=True)
        symbol, name = st.session_state.sel_ticker
        price = get_live_price(symbol)
        st.metric(label=name, value=f"₹ {price:,.2f}")

    elif mode == "JOURNAL":
        st.markdown('<p class="main-title">📝 OPTION JOURNAL</p>', unsafe_allow_html=True)
        underlying = st.selectbox("Index", ["NIFTY", "BANKNIFTY", "FINNIFTY", "CRUDE OIL"])
        strike = st.text_input("Strike & Type", placeholder="Ex: 22400 CE")
        col1, col2 = st.columns(2)
        entry_raw = col1.text_input("Entry Premium", value="", placeholder="0.00")
        exit_raw = col2.text_input("Exit Premium", value="", placeholder="0.00")
        qty_raw = col1.text_input("Total Qty", value="", placeholder="0")
        t_type = col2.selectbox("Order Type", ["BUY (Long)", "SELL (Short)"])
        mood = st.selectbox("Mood", ["Calm", "Disciplined", "Fear", "Greedy"])

        if st.button("SAVE TRADE"):
            try:
                entry = float(entry_raw) if entry_raw else 0.0
                exit_p = float(exit_raw) if exit_raw else 0.0
                qty = int(qty_raw) if qty_raw else 0
                pnl = (exit_p - entry) * qty if "BUY" in t_type else (entry - exit_p) * qty
                save_trade(f"{underlying} {strike}", t_type, entry, exit_p, qty, pnl, mood)
                st.success(f"Saved! P&L: ₹{pnl:,.2f}")
                st.rerun()
            except: st.error("Numbers only please!")

    elif mode == "DASHBOARD":
        st.markdown('<p class="main-title">📊 DASHBOARD</p>', unsafe_allow_html=True)
        if os.path.isfile(FILE_NAME):
            df = pd.read_csv(FILE_NAME)
            st.write(f"### Net P&L: ₹ {df['P&L'].sum():,.2f}")
            st.dataframe(df.iloc[::-1], use_container_width=True)

    st.markdown(f'<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
