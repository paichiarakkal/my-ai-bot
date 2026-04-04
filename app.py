import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide", initial_sidebar_state="auto")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #000 !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; font-weight: bold; margin-bottom: 5px; }
    .main-title { color: #FFF; font-size: 28px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .gold-box { background: #000; color: #FFD700; padding: 10px; border-radius: 10px; border: 2px solid #FFD700; text-align: center; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=30000, key="faisal_sidebar_fix")
FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def get_live_price_only(ticker):
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

# --- 2. സൈഡ് ബാർ (ബട്ടൺ അമർത്തിയാൽ മെയിൻ പേജിലേക്ക് മാറാൻ) ---
with st.sidebar:
    st.markdown("### 🚀 Paichi Pro")
    # മോഡ് മാറുമ്പോൾ പേജ് റീഫ്രഷ് ആകും, സ്ലൈഡ് ബാർ തനിയെ ഉള്ളിലേക്ക് പോകും
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL"])
    st.divider()

    if mode == "MARKET":
        st.write("### 📊 MARKET INDEX")
        
        # ഓരോ ബട്ടണിലും st.rerun() നൽകിയാൽ മൊബൈലിൽ സ്ലൈഡ് ബാർ തനിയെ ക്ലോസ് ആകും
        if st.button("📈 NIFTY 50"):
            st.session_state.sel_ticker = ("^NSEI", "NIFTY 50")
            st.rerun()
        if st.button("🏦 BANK NIFTY"):
            st.session_state.sel_ticker = ("^NSEBANK", "BANK NIFTY")
            st.rerun()
        if st.button("💳 FIN NIFTY"):
            st.session_state.sel_ticker = ("NIFTY_FIN_SERVICE.NS", "FIN NIFTY")
            st.rerun()
        if st.button("📊 SENSEX"):
            st.session_state.sel_ticker = ("^BSESN", "SENSEX")
            st.rerun()
        if st.button("📉 MIDCAP GROWTH"):
            st.session_state.sel_ticker = ("^NSEMDCP50", "MIDCAP 50")
            st.rerun()
        
        st.write("### 🛢️ COMMODITY")
        if st.button("⛽ CRUDE OIL"):
            st.session_state.sel_ticker = ("CL=F", "CRUDE OIL")
            st.rerun()
        
        st.divider()
        raw_gold_usd = get_live_price_only("GC=F")
        usd_inr = get_live_price_only("USDINR=X")
        if raw_gold_usd > 0:
            shop_price = ((raw_gold_usd / 31.1035) * 8 * usd_inr) * 1.15
            st.markdown(f'<div class="gold-box"><h3>₹ {shop_price:,.0f}</h3><p style="margin:0; font-size:10px;">(8g Shop Price)</p></div>', unsafe_allow_html=True)

# --- 3. മെയിൻ കണ്ടന്റ് ---
st.markdown(f'<p class="main-title">🚀 {st.session_state.sel_ticker[1]}</p>', unsafe_allow_html=True)

if mode == "MARKET":
    symbol, name = st.session_state.sel_ticker
    current_p = get_live_price_only(symbol)
    
    if current_p > 0:
        st.write(f"### ലൈവ് വില")
        st.metric(label=name, value=f"₹ {current_p:,.2f}")
        # ഗ്രാഫ് ഒഴിവാക്കി
    else:
        st.error("ഡാറ്റ ലഭ്യമായില്ല.")

elif mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ")
    s = st.text_input("Item", value=st.session_state.sel_ticker[1])
    col1, col2 = st.columns(2)
    en = col1.number_input("Entry Price", value=0.0)
    ex = col2.number_input("Exit Price", value=0.0)
    q = col1.number_input("Qty", value=1, step=1)
    a = col2.selectbox("Action", ["BUY", "SELL"])
    mood = st.selectbox("മൂഡ്", ["Calm", "Happy", "Fear", "Greedy"])
    
    if st.button("Save Trade"):
        pnl = (ex - en) * q
        save_trade(s, a, en, ex, q, pnl, mood)
        st.success("സേവ് ചെയ്തു!")
        st.rerun()

    st.divider()
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.table(df.iloc[::-1]) # ജേണൽ ടേബിൾ
        st.write("---")
        del_idx = st.number_input("ഡിലീറ്റ് ചെയ്യേണ്ട ഇൻഡക്സ് (Index) നൽകുക:", min_value=0, max_value=len(df)-1, step=1)
        if st.button("Delete Entry"):
            df = df.drop(del_idx)
            df.to_csv(FILE_NAME, index=False)
            st.rerun()

# --- FOOTER ---
st.markdown(f'<p style="text-align: center; color: #FFF; margin-top: 50px;">Created by <b>Faisal Arakkal</b></p>', unsafe_allow_html=True)
