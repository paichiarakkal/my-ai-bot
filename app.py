import streamlit as st
import pandas as pd
import requests
import random, urllib.parse, threading
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
SCRIPT_API = "https://script.google.com/macros/s/AKfycbzmbiWOQ-vpyOtaM6n4fosAkHRIaXyno-JyGPbxG9uZIl4W-6QzFy3hVVb-o7ctD7hl/exec"

WA_PHONE, WA_API_KEY = "971551347989", "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD v8.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. STYLE ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #2D0844, #1A0521); color: #fff; }
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border-left: 8px solid #FFD700; text-align: center; margin-bottom: 20px; }
    .stButton>button { background-color: #FFD700; color: #000; font-weight: bold; border-radius: 10px; }
    h1, h2, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCTIONS ---
def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

def add_to_sheet(item, amount, typ, user="App"):
    t_p = "d" if typ.lower() == "debit" else "c"
    url = f"{SCRIPT_API}?item={urllib.parse.quote(item)}&amount={amount}&type={t_p}&user={user}"
    try: requests.get(url, timeout=10)
    except: pass

def send_wa(msg):
    try: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}")
    except: pass

# --- 4. MAIN ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 LOGIN")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
else:
    curr_user = st.session_state.user
    df = get_data()
    bal = df['Credit'].sum() - df['Debit'].sum() if not df.empty else 0
    
    st.markdown(f'<div class="balance-banner"><h3>Available Balance</h3><h1>₹{bal:,.2f}</h1></div>', unsafe_allow_html=True)

    menu = ["💰 Add Entry", "🤝 Debt Tracker"] if curr_user == "shabana" else ["🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    page = st.sidebar.radio("Menu", menu)

    if page == "💰 Add Entry":
        st.title("New Entry 🎙️")
        v = speech_to_text(language='ml', key='voice')
        with st.form("fm", clear_on_submit=True):
            it = st.text_input("Item", value=v if v else "")
            am = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                add_to_sheet(it, float(am), ty, user=curr_user.capitalize())
                threading.Thread(target=send_wa, args=(f"✅ {it} - ₹{am} ({curr_user})",)).start()
                st.success("Saved!"); st.rerun()

    elif page == "📊 Report":
        st.title("Report")
        exp = df[df['Debit'] > 0]
        if not exp.empty:
            st.plotly_chart(px.pie(exp, values='Debit', names='Item', hole=0.4))

    elif page == "🔍 History":
        st.title("History")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "🤝 Debt Tracker":
        st.title("Debt Tracker")
        with st.form("d_fm", clear_on_submit=True):
            p_n, p_a = st.text_input("Name"), st.text_input("Amount")
            cat = st.selectbox("Type", ["Lent", "Borrowed"])
            if st.form_submit_button("SAVE DEBT"):
                ty = "Debit" if cat == "Lent" else "Credit"
                add_to_sheet(f"DEBT: {p_n}", float(p_a), ty, user=curr_user.capitalize())
                st.success("Debt Saved!"); st.rerun()

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
