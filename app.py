import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
import os
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
from mtranslate import translate

# 1. പേജ് സെറ്റിംഗ്സ് & ഗോൾഡൻ തീം
st.set_page_config(page_title="Paichi AI Trader Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C); color: #000; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A9A9A9, #C0C0C0, #808080) !important; }
    div[data-testid="stSidebar"] button { width: 100%; background-color: #000 !important; color: #BF953F !important; border: 1px solid #FFD700 !important; margin-bottom: 5px; font-weight: bold; }
    .main-title { color: #FFF; font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px #000; }
    .news-box { background-color: #000; padding: 10px; border-radius: 5px; border: 1px solid #BF953F; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=15000, key="faisal_custom_logic_v1")
FILE_NAME = 'trade_history_v2.csv'

# --- ഫംഗ്ഷനുകൾ ---
def save_trade(symbol, action, entry_p, exit_p, qty, pnl, mood):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([[date, symbol, action, entry_p, exit_p, qty, pnl, mood]], 
                          columns=['Date', 'Item', 'Type', 'Entry', 'Exit', 'Qty', 'P&L', 'Mood'])
    if not os.path.isfile(FILE_NAME): df_new.to_csv(FILE_NAME, index=False)
    else: df_new.to_csv(FILE_NAME, mode='a', header=False, index=False)

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.title("🚀 Paichi Pro")
    mode = st.radio("മെനു തിരഞ്ഞെടുക്കുക:", ["MARKET", "JOURNAL", "DASHBOARD"])

if 'sel' not in st.session_state: st.session_state.sel = ("^NSEI", "NIFTY 50", 1)

# --- മെയിൻ കണ്ടന്റ് ---
st.markdown('<p class="main-title">🚀 Paichi AI Trader</p>', unsafe_allow_html=True)

if mode == "JOURNAL":
    st.subheader("📝 ട്രേഡിംഗ് ജേണൽ")
    
    # ഇൻപുട്ട് ഫീൽഡുകൾ
    s = st.text_input("Item", value=st.session_state.sel[1])
    en = st.number_input("Entry Price", value=0.0)
    ex = st.number_input("Exit Price", value=0.0)
    q = st.number_input("Qty", value=1, step=1)
    a = st.selectbox("Action", ["BUY", "SELL"])
    mood = st.selectbox("മൂഡ്", ["Calm", "Happy", "Fear", "Greedy"])
    
    if st.button("Save Trade"):
        # നീ ആവശ്യപ്പെട്ട ലോജിക്: എപ്പോഴും (Exit - Entry) ലാഭമായി വരണം
        pnl = (ex - en) * q
            
        save_trade(s, a, en, ex, q, pnl, mood)
        st.success(f"സേവ് ചെയ്തു! P&L: ₹{pnl}")
        st.rerun()

    st.divider()

    # ടേബിൾ രൂപത്തിൽ ലിസ്റ്റ് ചെയ്യുക
    if os.path.isfile(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        st.write("### സേവ് ചെയ്ത ട്രേഡുകൾ")
        st.table(df.iloc[::-1]) # നിനക്ക് വേണ്ട ടേബിൾ രൂപം
        
        # ഡിലീറ്റ് ഓപ്ഷൻ
        st.write("---")
        del_idx = st.number_input("ഡിലീറ്റ് ചെയ്യേണ്ട ഇൻഡക്സ് (Index) നൽകുക:", min_value=0, max_value=len(df)-1, step=1)
        if st.button("Delete Entry"):
            df = df.drop(del_idx)
            df.to_csv(FILE_NAME, index=False)
            st.rerun()
