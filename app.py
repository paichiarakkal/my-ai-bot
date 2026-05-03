import streamlit as st
import pandas as pd
import requests
import random, urllib.parse, threading
import yfinance as yf
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
    .balance-banner { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 10px solid #FFD700; text-align: center; margin-bottom: 25px; }
    .purple-box { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 20px; border: 1px solid rgba(255,215,0,0.3); text-align: center; margin-bottom: 20px; }
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

def add_to_sheet(item, amount, typ, cat, user="App"):
    # ഗൂഗിൾ സ്ക്രിപ്റ്റിലേക്ക് Item, Amount, Type, Category എല്ലാം വെവ്വേറെ അയക്കുന്നു
    t_p = "d" if typ.lower() == "debit" else "c"
    url = f"{SCRIPT_API}?item={urllib.parse.quote(item)}&amount={amount}&type={t_p}&cat={urllib.parse.quote(cat)}&user={user}"
    try: requests.get(url, timeout=10)
    except: pass

def get_market_data():
    try:
        results = []
        for name, sym in {"Crude Oil": "CL=F", "Nifty 50": "^NSEI"}.items():
            val = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
            if "Crude" in name: val *= 83.5 
            results.append({"name": name, "price": val})
        return results
    except: return []

# --- 4. MAIN ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
else:
    curr_user = st.session_state.user
    df = get_data()
    t_in = df['Credit'].sum() if not df.empty else 0
    t_out = df['Debit'].sum() if not df.empty else 0
    bal = t_in - t_out
    
    st.markdown(f'<div class="balance-banner"><h3>Available Balance</h3><h1 style="color:#FFD700; font-size:45px;">₹{bal:,.2f}</h1></div>', unsafe_allow_html=True)

    menu = ["💰 Add Entry", "🤝 Debt Tracker"] if curr_user == "shabana" else ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    page = st.sidebar.radio("Menu", menu)

    if page == "📊 Advisor":
        st.title("🚀 Market Advisor")
        markets = get_market_data()
        for m in markets:
            st.markdown(f'<div class="purple-box"><h2>{m["name"]}</h2><h1 style="color:#00FF00;">₹{m["price"]:,.2f}</h1></div>', unsafe_allow_html=True)

    elif page == "🏠 Dashboard":
        st.title("🏠 Dashboard")
        col1, col2 = st.columns(2)
        col1.markdown(f'<div class="purple-box"><h3 style="color:#00FF00;">Total Income</h3><h2>₹{t_in:,.2f}</h2></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="purple-box"><h3 style="color:#FF3131;">Total Expense</h3><h2>₹{t_out:,.2f}</h2></div>', unsafe_allow_html=True)

    elif page == "💰 Add Entry":
        st.title("New Entry 🎙️")
        v = speech_to_text(language='ml', key='voice')
        with st.form("fm", clear_on_submit=True):
            it = st.text_input("Item Name", value=v if v else "")
            cat_options = ["Food", "Transport", "Salary", "Shopping", "Rent", "Others"]
            cat = st.selectbox("Category", cat_options)
            am = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                add_to_sheet(it, float(am), ty, cat, user=curr_user.capitalize())
                st.success(f"Saved: {it} in {cat} ✅"); st.rerun()

    elif page == "📊 Report":
        st.title("Expense Analysis")
        # ഷീറ്റിലെ 'Category' കോളം ഉപയോഗിച്ച് റിപ്പോർട്ട് ഉണ്ടാക്കുന്നു
        if not df.empty and 'Category' in df.columns:
            exp = df[df['Debit'] > 0]
            if not exp.empty:
                st.plotly_chart(px.pie(exp, values='Debit', names='Category', hole=0.4))
        else:
            st.info("Category വിവരങ്ങൾ ഷീറ്റിൽ ലഭ്യമല്ല.")

    elif page == "🔍 History":
        st.title("History")
        st.dataframe(df.iloc[::-1], use_container_width=True)

    elif page == "🤝 Debt Tracker":
        st.title("Debt Tracker 🤝")
        with st.form("d_fm", clear_on_submit=True):
            p_n, p_a = st.text_input("Name"), st.text_input("Amount")
            cat_debt = st.selectbox("Type", ["Lent (കൊടുത്തത്)", "Borrowed (വാങ്ങിയത്)"])
            if st.form_submit_button("SAVE DEBT"):
                ty = "Debit" if "Lent" in cat_debt else "Credit"
                add_to_sheet(f"DEBT: {p_n}", float(p_a), ty, "Debt", user=curr_user.capitalize())
                st.success("Debt Saved! ✅"); st.rerun()

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
