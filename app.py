import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import yfinance as yf
import random
import re, urllib.parse, threading, base64
import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & SETTINGS ---
# ഷീറ്റിലെ ഡാറ്റ വായിക്കാൻ മാത്രം CSV_URL ഉപയോഗിക്കുന്നു
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"

# ഫൈസൽ നൽകിയ ഏറ്റവും പുതിയ ഗൂഗിൾ സ്ക്രിപ്റ്റ് URL
SCRIPT_API = "https://script.google.com/macros/s/AKfycbzmbiWOQ-vpyOtaM6n4fosAkHRIaXyno-JyGPbxG9uZIl4W-6QzFy3hVVb-o7ctD7hl/exec"

WA_PHONE, WA_API_KEY = "+971551347989", "7463030"
IMGBB_API_KEY = "7b08945ff15a43258cc137387e6038d5" 

# Password Faisal: faisal147 | Shabana: shabana123
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI AI PRO v11.0", layout="wide")
st_autorefresh(interval=60000, key="auto_refresh")

# --- 2. 🎨 BLACK GLASS STYLING ---
def apply_style(colors):
    st.markdown(f"""<style>
        @keyframes grad {{ 0% {{background-position: 0% 50%;}} 50% {{background-position: 100% 50%;}} 100% {{background-position: 0% 50%;}} }}
        .stApp {{ background: linear-gradient(-45deg, {colors}); background-size: 400% 400%; animation: grad 15s ease infinite; color: white; }}
        
        [data-testid="stSidebar"] {{
            background: rgba(0, 0, 0, 0.7) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 215, 0, 0.1);
        }}
        
        .purple-box {{ 
            background: rgba(0, 0, 0, 0.2); 
            padding: 25px; 
            border-radius: 20px; 
            border: 1px solid rgba(255,215,0,0.3); 
            backdrop-filter: blur(10px); 
            text-align: center; 
            margin-bottom: 20px; 
        }}
        h1, h2, h3, p, label {{ color: white !important; font-weight: bold !important; }}
        .stButton>button {{ background: #FFD700; color: black; border-radius: 12px; font-weight: bold; width: 100%; height: 45px; }}
    </style>""", unsafe_allow_html=True)

# --- 3. 📊 UTILITY FUNCTIONS ---
def upload_bill(file):
    try:
        img_data = base64.b64encode(file.getvalue())
        res = requests.post("https://api.imgbb.com/1/upload", data={"key": IMGBB_API_KEY, "image": img_data})
        if res.json()['success']: return res.json()['data']['url']
        return ""
    except: return ""

def send_wa(msg):
    try: requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}", timeout=10)
    except: pass

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

# --- 4. LOGIN & AUTH ---
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
    
    # 🛡️ ROLE LOGIC
    if curr_user == "shabana":
        menu = ["💰 Add Entry", "🤝 Debt Tracker"]
    else:
        menu = ["📊 Trading Advisor", "🏠 Dashboard", "💰 Add Entry", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
    
    page = st.sidebar.radio("Menu", menu)
    apply_style({"📊 Trading Advisor":"#0f0c29, #302b63", "🏠 Dashboard":"#1a1a00, #4d4d00", "💰 Add Entry":"#41295a, #2f0743", "📊 Report":"#004d40, #002424", "🔍 History":"#1e3c72, #2a5298", "🤝 Debt Tracker":"#4b1212, #2d0b0b"}.get(page, "#2D0844"))

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
            category = st.text_input("Category")
            am_input = st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            bill = st.file_uploader("Upload Bill Photo", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("SAVE TRANSACTION"):
                if it and am_input:
                    try:
                        am = float(am_input)
                        with st.spinner("Processing..."):
                            link = upload_bill(bill) if bill else ""
                            # ആപ്പിൽ നിന്നുള്ള എൻട്രിയാണെന്ന് ഷീറ്റിൽ കാണാൻ
                            display_name = f"[{curr_user.capitalize()}] {it}"
                            if link: display_name += f" | Bill: {link}"
                            
                            # പുതിയ ഗൂഗിൾ സ്ക്രിപ്റ്റിലേക്ക് അയക്കുന്നു
                            text_p = f"{display_name} {am} {ty[0].lower()}"
                            requests.get(f"{SCRIPT_API}?text={urllib.parse.quote(text_p)}")
                            
                            new_bal = balance - am if ty == "Debit" else balance + am
                            wa_msg = f"✅ *Paichi Entry*\n👤 {curr_user.capitalize()}\n💰 ₹{am} - {it}\n💳 *Balance Updated*"
                            threading.Thread(target=send_wa, args=(wa_msg,)).start()
                            st.success("Entry Saved!"); st.rerun()
                    except: st.error("Check Amount!")

    elif page == "🤝 Debt Tracker":
        st.title("Debt Management 🤝")
        with st.form("debt_fm", clear_on_submit=True):
            n = st.text_input("Person Name")
            a_input = st.text_input("Amount")
            t = st.selectbox("Category", ["Borrowed (കടം വാങ്ങിയത്)", "Lent (കടം കൊടുത്തത്)"])
            
            if st.form_submit_button("SAVE DEBT"):
                if n and a_input:
                    try:
                        am = float(a_input)
                        # പുതിയ സ്ക്രിപ്റ്റിലേക്ക് അയക്കുന്നു
                        debt_tag = "Lent" if "Lent" in t else "Borrowed"
                        text_p = f"[DEBT-{debt_tag}] {n} {am} {'d' if 'Lent' in t else 'c'}"
                        requests.get(f"{SCRIPT_API}?text={urllib.parse.quote(text_p)}")
                        
                        wa_msg = f"🤝 *Debt Update*\n👤 {n}\n💰 ₹{am} ({t})"
                        threading.Thread(target=send_wa, args=(wa_msg,)).start()
                        st.success("Debt Saved!"); st.rerun()
                    except: st.error("Check Amount!")

    elif page == "📊 Trading Advisor" and curr_user != "shabana":
        st.title("🛢️ Market Tracker")
        for name, sym in {"Crude Oil": "CL=F", "Nifty 50": "^NSEI"}.items():
            try:
                val = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
                if "Crude" in name: val *= 83.5 
                st.markdown(f'<div class="purple-box"><h3>{name}</h3><h1 style="color:#00FF00 !important;">₹{val:,.2f}</h1></div>', unsafe_allow_html=True)
            except: pass

    elif page == "🔍 History" and curr_user != "shabana":
        st.title("History 🔍")
        st.dataframe(df_main.iloc[::-1], use_container_width=True)

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
