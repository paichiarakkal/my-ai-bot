import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import re, urllib.parse, threading, base64
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE, WA_API_KEY = "+971551347989", "7463030"
IMGBB_API_KEY = "7b08945ff15a43258cc137387e6038d5" 

USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI PRO v7.5", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 PREMIUM STYLING ---
def apply_style(colors):
    st.markdown(f"""<style>
        @keyframes grad {{ 0% {{background-position: 0% 50%;}} 50% {{background-position: 100% 50%;}} 100% {{background-position: 0% 50%;}} }}
        .stApp {{ background: linear-gradient(-45deg, {colors}); background-size: 400% 400%; animation: grad 15s ease infinite; color: white; }}
        [data-testid="stSidebar"] {{ background: rgba(0,0,0,0.85) !important; }}
        .purple-box {{ background: rgba(0,0,0,0.25); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,215,0,0.3); backdrop-filter: blur(15px); text-align: center; margin-bottom: 20px; }}
        h1, h2, h3, p, label {{ color: white !important; font-weight: bold !important; }}
        .stButton>button {{ background: #FFD700; color: black; border-radius: 12px; font-weight: bold; width: 100%; border: none; height: 45px; transition: 0.3s; }}
    </style>""", unsafe_allow_html=True)

# --- 3. 📊 CORE ENGINES ---
def upload_bill(file):
    try:
        img_data = base64.b64encode(file.getvalue())
        res = requests.post("https://api.imgbb.com/1/upload", data={"key": IMGBB_API_KEY, "image": img_data})
        json_data = res.json()
        if json_data['success']:
            return json_data['data']['url']
        return None
    except: return None

def send_wa(msg):
    try: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}", timeout=10)
    except: pass

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

# --- 4. APP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    apply_style("#0f0c29, #302b63, #24243e")
    st.markdown("<h1 style='text-align:center;'>🚀 PAICHI AI PRO</h1>", unsafe_allow_html=True)
    u, p = st.text_input("Username").lower(), st.text_input("Password", type="password")
    if st.button("LOG IN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
else:
    curr_user = st.session_state.user
    menu = ["💰 Add Entry", "🤝 Debt Tracker"] if curr_user == "shabana" else ["📊 Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    page = st.sidebar.radio("Menu", menu)
    
    themes = {"📊 Advisor":"#0f0c29, #302b63", "🏠 Dashboard":"#1a1a00, #4d4d00", "💰 Add Entry":"#41295a, #2f0743", "📊 Report":"#004d40, #002424", "🔍 History":"#1e3c72, #2a5298", "🤝 Debt Tracker":"#4b1212, #2d0b0b"}
    apply_style(themes.get(page, "#2D0844, #1A0521"))

    df_main = get_data()
    if not df_main.empty:
        credit = pd.to_numeric(df_main['Credit'], errors='coerce').fillna(0).sum()
        debit = pd.to_numeric(df_main['Debit'], errors='coerce').fillna(0).sum()
        balance = credit - debit
    else: balance = 0
    
    st.markdown(f'<div class="purple-box"><p style="opacity:0.8;">CURRENT AVAILABLE BALANCE</p><h1 style="color:#FFD700 !important; font-size:40px;">₹{balance:,.2f}</h1></div>', unsafe_allow_html=True)

    if page == "💰 Add Entry":
        st.title("New Entry & Bill 🎙️")
        v_raw = speech_to_text(language='ml', key='v_entry')
        with st.form("entry_fm", clear_on_submit=True):
            it = st.text_input("Item Name", value=v_raw if v_raw else "")
            am_input = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            bill = st.file_uploader("Upload Bill Photo", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("SAVE TRANSACTION"):
                if it and am_input:
                    try:
                        am = float(am_input)
                        with st.spinner("Processing & Uploading Bill..."):
                            link = upload_bill(bill) if bill else ""
                            final_desc = f"[{curr_user.capitalize()}] {it}"
                            if link: final_desc += f" | 📂 Bill: {link}"
                            
                            d, c = (am, 0) if ty=="Debit" else (0, am)
                            new_bal = balance - am if ty == "Debit" else balance + am
                            
                            requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": final_desc, "entry.1460982454": d, "entry.1221658767": c})
                            
                            wa_msg = f"✅ *Paichi Entry*\n👤 {curr_user.capitalize()}\n💰 ₹{am} - {it}\n💳 *Balance: ₹{new_bal:,.2f}*"
                            if link: wa_msg += f"\n📂 Bill: {link}"
                            
                            threading.Thread(target=send_wa, args=(wa_msg,)).start()
                            st.success(f"സേവ് ആയി! പുതിയ ബാലൻസ്: ₹{new_bal:,.2f}"); st.rerun()
                    except: st.error("Amount കൃത്യമായി നൽകുക!")

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management 🤝")
        with st.form("debt_fm", clear_on_submit=True):
            n = st.text_input("Person Name")
            a_input = st.number_input("Amount", min_value=0.0)
            t = st.selectbox("Category", ["Borrowed (കടം വാങ്ങിയത്)", "Lent (കടം കൊടുത്തത്)"])
            if st.form_submit_button("SAVE DEBT"):
                if n and a_input > 0:
                    d, c = (a_input, 0) if "Lent" in t else (0, a_input)
                    new_bal = balance - a_input if "Lent" in t else balance + a_input
                    requests.post(FORM_API, data={"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{curr_user.capitalize()}] DEBT: {t}-{n}", "entry.1460982454": d, "entry.1221658767": c})
                    wa_msg = f"🤝 *Debt Update*\n👤 {n}\n📝 {t}\n💰 ₹{a_input}\n💳 *Balance: ₹{new_bal:,.2f}*"
                    threading.Thread(target=send_wa, args=(wa_msg,)).start()
                    st.success("Debt Saved!"); st.rerun()

    elif page == "🔍 History":
        st.title("Transaction History 🔍")
        if not df_main.empty:
            st.dataframe(df_main.iloc[::-1], use_container_width=True)
        else: st.write("No transactions found.")

    elif page == "📊 Advisor":
        st.title("Market Advisor 📈")
        for name, sym in {"Nifty 50":"^NSEI", "Bank Nifty":"^NSEBANK"}.items():
            px_val = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
            st.markdown(f'<div class="purple-box"><h3>{name}</h3><h1 style="color:#00FF00 !important;">₹{px_val:,.2f}</h1></div>', unsafe_allow_html=True)

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
