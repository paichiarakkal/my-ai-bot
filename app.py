import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import urllib.parse
import threading
import re
from streamlit_mic_recorder import speech_to_text

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123"}

st.set_page_config(page_title="PAICHI GOLD", layout="wide")

# --- 2. 🎨 DESIGN (Back to Classic Look) ---
st.markdown("""
    <style>
    /* ബാക്ക്ഗ്രൗണ്ട് ഗ്രേഡിയന്റ് */
    .stApp { background: linear-gradient(135deg, #2D0844, #4B0082, #1A0521); color: white; }
    
    /* സൈഡ് ബാർ പഴയതുപോലെ ഡാർക്ക് */
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    
    /* ബാലൻസ് ബാനർ */
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; margin-bottom: 25px; text-align: center; }
    
    /* ബട്ടണുകൾ പഴയ മഞ്ഞ നിറത്തിൽ */
    .stButton>button { background-color: #FFD700; color: #000; border-radius: 10px; font-weight: bold; }
    
    /* ടേബിൾ വെള്ള ബാക്ക്ഗ്രൗണ്ടിൽ */
    .stDataFrame { background: white; border-radius: 10px; color: black; }
    
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 3. FUNCTIONS ---
def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        for col in ['Debit', 'Credit']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

def send_data(item, d, c, user):
    payload = {
        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
        "entry.2013476337": f"[{user.capitalize()}] {item}",
        "entry.1460982454": d,
        "entry.1221658767": c
    }
    threading.Thread(target=lambda: requests.post(FORM_API, data=payload)).start()

def get_trading_signals():
    results = []
    for name, sym in {"Nifty": "^NSEI", "Crude": "CL=F"}.items():
        try:
            df = yf.Ticker(sym).history(period="1d", interval="5m")
            price = df['Close'].iloc[-1]
            if name == "Crude": price = price * 83.5 * 1.15
            results.append({"name": name, "price": price})
        except: pass
    return results

# --- 4. MAIN APP ---
if not st.session_state.auth:
    st.title("🔐 Login")
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if USERS.get(u) == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
else:
    curr_user = st.session_state.user
    df = get_data()
    balance = df['Credit'].sum() - df['Debit'].sum()
    
    st.markdown(f'<div class="balance-banner"><h3>Total Balance: ₹{balance:,.2f}</h3></div>', unsafe_allow_html=True)
    
    # ശബാനയുടെ മെനു നിയന്ത്രണം
    if curr_user == "shabana":
        menu = ["💰 Add Entry", "🔍 History"]
    else:
        menu = ["📊 Advisor", "💰 Add Entry", "🔍 History"]
    
    page = st.sidebar.radio("Menu", menu)
    
    if page == "📊 Advisor":
        st.title("📊 Market Watch")
        signals = get_trading_signals()
        for s in signals:
            st.metric(s['name'], f"₹{s['price']:,.2f}")

    elif page == "💰 Add Entry":
        st.title("Add Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='voice_input')
        with st.form("entry_form", clear_on_submit=True):
            it = st.text_input("Item/Description", value=v_raw if v_raw else "")
            am = st.number_input("Amount", min_value=0.0)
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                send_data(it, d, c, curr_user)
                st.success("Entry Saved Successfully! ✅")

    elif page == "🔍 History":
        st.title("Transaction History")
        if not df.empty:
            def highlight(x):
                style_df = pd.DataFrame('', index=x.index, columns=x.columns)
                style_df.loc[x['Debit'] > 0, 'Debit'] = 'background-color: #ffe6e6; color: red; font-weight: bold;'
                style_df.loc[x['Credit'] > 0, 'Credit'] = 'background-color: #e6ffed; color: green; font-weight: bold;'
                return style_df

            styled_df = df.iloc[::-1].style.apply(highlight, axis=None).format({'Debit': "{:.2f}", 'Credit': "{:.2f}"})
            st.dataframe(styled_df, use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
