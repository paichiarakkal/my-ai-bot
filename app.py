import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
import re, urllib.parse, threading

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE, WA_API_KEY = "+971551347989", "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI v5.5", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 ANIMATION ENGINE ---
def apply_style(colors):
    st.markdown(f"""
        <style>
        @keyframes gradient {{ 0% {{background-position: 0% 50%;}} 50% {{background-position: 100% 50%;}} 100% {{background-position: 0% 50%;}} }}
        .stApp {{ background: linear-gradient(-45deg, {colors}); background-size: 400% 400%; animation: gradient 15s ease infinite; color: white; }}
        [data-testid="stSidebar"] {{ background: rgba(0,0,0,0.8) !important; }}
        .purple-box {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 20px; border: 1px solid rgba(255,215,0,0.3); backdrop-filter: blur(10px); text-align: center; margin-bottom: 15px; }}
        h1, h2, h3, p, label {{ color: white !important; font-weight: bold !important; }}
        .stButton>button {{ background: #FFD700; color: black; border-radius: 10px; font-weight: bold; width: 100%; border: none; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. 📊 CORE ENGINES ---
def send_wa(msg):
    try: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}", timeout=10)
    except: pass

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

def process_voice(text):
    if not text: return "", None, ""
    nums = re.findall(r'\d+', text)
    amt = float(nums[0]) if nums else None
    cat = "Food" if any(x in text.lower() for x in ["food", "ഭക്ഷണം"]) else "Shop" if any(x in text.lower() for x in ["shop", "കട"]) else "Others"
    return cat, amt, text

# --- 4. APP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    apply_style("#0f0c29, #302b63, #24243e")
    st.markdown("<h2 style='text-align:center;'>🔐 PAICHI LOGIN</h2>", unsafe_allow_html=True)
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
else:
    curr_user = st.session_state.user
    menu = ["💰 Add Entry", "🤝 Debt Tracker"] if curr_user == "shabana" else ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    page = st.sidebar.radio("Menu", menu)
    
    # Dynamic Colors
    themes = {"📊 Advisor":"#0f0c29, #302b63", "🏠 Dashboard":"#1a1a00, #4d4d00", "💰 Add Entry":"#41295a, #2f0743", "📊 Report":"#004d40, #002424", "🔍 History":"#1e3c72, #2a5298", "🤝 Debt Tracker":"#4b1212, #2d0b0b"}
    apply_style(themes.get(page, "#2D0844, #1A0521"))

    # Balance Banner
    df_main = get_data()
    bal = pd.to_numeric(df_main['Credit'], errors='coerce').sum() - pd.to_numeric(df_main['Debit'], errors='coerce').sum() if not df_main.empty else 0
    st.markdown(f'<div class="purple-box"><p>BALANCE</p><h1 style="color:#FFD700 !important;">₹{bal:,.2f}</h1></div>', unsafe_allow_html=True)

    if page == "📊 Advisor":
        st.title("Smart Advisor")
        # Simplified Advisor
        for n, s in {"Nifty 50":"^NSEI", "Bank Nifty":"^NSEBANK"}.items():
            px_val = yf.Ticker(s).history(period="1d")['Close'].iloc[-1]
            st.markdown(f'<div class="purple-box"><h3>{n}</h3><h2>₹{px_val:,.0f}</h2></div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("Add Entry 🎙️")
        v_raw = speech_to_text(language='ml', key='v1')
        v_cat, v_amt, v_txt = process_voice(v_raw)
        with st.form("fm", True):
            it = st.text_input("Item", value=v_txt)
            am = st.text_input("Amount", value=str(int(v_amt)) if v_amt else "")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty=="Debit" else (0, am)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] {it}", "entry.1460982454": d, "entry.1221658767": c})
                threading.Thread(target=send_wa, args=(f"✅ ₹{am} - {it}",)).start()
                st.success("Saved!"); st.rerun()

    elif page == "🤝 Debt Tracker":
        st.title("Debt Tracker")
        with st.form("dfm", True):
            n, a = st.text_input("Name"), st.number_input("Amount", min_value=0.0)
            t = st.selectbox("Type", ["Borrowed (കടം വാങ്ങിയത്)", "Lent (കടം കൊടുത്തത്)"])
            if st.form_submit_button("SAVE DEBT"):
                d, c = (a, 0) if "Lent" in t else (0, a)
                requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] DEBT: {t}-{n}", "entry.1460982454": d, "entry.1221658767": c})
                st.success("Debt Saved!"); st.rerun()

    elif page == "🔍 History":
        st.title("History")
        st.dataframe(df_main.iloc[::-1], use_container_width=True)

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
